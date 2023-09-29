import json
import os
import datetime

from qa_memo import retrieval_qa_pipline
from utils import log_op


# RESTRICT = "format your answer like ''' {{'answer': 'your answer', 'thoughts': 'how you came to the answer'}} }} '''."
RESTRICT = ""
STATE_FILE = 'current_state.json'
DEFAULT_PROBLEM = "what makes great software as a service?"
MAX_LOOP_COUNT = 99
GENERATE_QUESTION = "Generate a new question."

device_type = 'cpu'
show_sources = False
use_history = True

def get_problem():
    """
    Retrieve the current problem from current_state.json or generate a new one if none exist.
    """
    try:
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            current_problems = [item for item in data if item['status'] in ['current', 'answered']]
            if current_problems:
                return current_problems[0]['problem']
            else:
                new_problem = GENERATE_QUESTION
                data.append({"problem": new_problem, "status": "current"})
                with open(STATE_FILE, 'w') as f:
                    json.dump(data, f, indent=4)
                return new_problem
    except FileNotFoundError:
        default_problem = "what makes great software as a service?"
        with open(STATE_FILE, 'w') as f:
            json.dump([{
                "problem": default_problem, 
                "status": "current", 
                "time_question": f"{datetime.datetime.now()}"
                }], f, indent=4)
        return default_problem
    
def write_answer(answer):
    """
    Write the answer to the current problem in current_state.json.
    """
    re_run = False
    with open(STATE_FILE, 'r') as f:
        data = json.load(f)
        for item in data:
            if item['status'] == 'current':
                if item['problem'] == GENERATE_QUESTION:
                    item['problem'] = answer
                    item['time_questioned'] = f"{datetime.datetime.now()}"
                    re_run = True
                    break
                else:
                    item['answer'] = answer
                    item['status'] = 'answered'
                    item['time_answer'] = f"{datetime.datetime.now()}"
                    break
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    if re_run:
        process_query()

def remove_path(path):
    """
    Remove './code/' from the given path.
    """
    return path.replace('./code/', '')

def get_context():
    """
    Retrieve the context from the application.json and other code files.
    """
    with open(STATE_FILE, 'r') as f:
        data = json.load(f)
    
    # Filter out the items that have answers
    answered_items = [item for item in data if 'answer' in item]
    
    # If there are no answered items, return an empty string
    if not answered_items:
        return """
            Consider the following:
            We are building a nextjs and laravel application.
            """
    
    # Only consider the last 10 questions and answers
    last_10_qa = answered_items[-10:]
    
    question_answers = [{"question": item['problem'], "answer": item['answer']} for item in last_10_qa]

    context_items = []
    for qa in question_answers:
        context_items.append(f"Question: {qa['question']}")
        context_items.append(f"Answer: {qa['answer']}")
    
    tree = f"""
    Consider the following:
    We are building a nextjs application.

    Previous Questions and Answers:
    {context_items}
    """
    return tree

def create_question_dict(query):
    """
    Create the question string based on the query.
    """
    context = get_context()
    if query == "Generate a new question based on previous answers.":
        return f"Generate a new question based on the information you have. \n\n{RESTRICT} \n\n{context}"
    else:
        return f"Answer this question as best you can. Break down the question and explain your thinking. If you do not know the answer, admit that you do not know the answer. \n\n{RESTRICT} \n\n{context} \n\n{query}"

def write_evaluation(answer):
    """
    Write the evaluation to the current problem's answer in current_state.json.
    """
    with open(STATE_FILE, 'r') as f:
        data = json.load(f)
        for item in data:
            if item['status'] == 'answered':
                item['evaluate'] = answer
                item['status'] = 'evaluated'
                item['time_evaluate'] = f"{datetime.datetime.now()}"
                break
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_evaluation_data():
    """
    Get the question and answer.
    """
    with open(STATE_FILE, 'r') as f:
        data = json.load(f)
    filtered = [x for x in data if x['status'] == 'answered'][0]
    
    return {
        "question": filtered['problem'],
        "answer": filtered['answer']
    }
    
def create_evaluation_dict():
    """
    Create the evaluation string based on the query.
    """
    eval_data = get_evaluation_data()
    return f"Evaluate the given answer. \n\n{RESTRICT} \n\nQuestion: {eval_data['question']} \n\nAnswer: {eval_data['answer']}"

def process_query():
    """
    Process a single query, generate an answer, and evaluate the answer.
    """
    query = get_problem()
    try:
        send = create_question_dict(query)
        qa = retrieval_qa_pipline(device_type, use_history, memory_unit='create', promptTemplate_type="llama")
        res = qa(send)
        
        # Check if the result is an empty string
        if res in ["", " ", "\n"]:
            log_op(f'\nEmpty response for method:\n{query}\nRetrying...\n')
            return process_query()

        write_answer(res)

        eval_send = create_evaluation_dict()
        qa = retrieval_qa_pipline(device_type, use_history, memory_unit='evaluate', promptTemplate_type="llama")
        eval_res = qa(eval_send)

        # Check if the evaluation result is an empty string
        if eval_res in ["", " ", "\n"]:
            log_op(f'\nEmpty evaluation for method:\n{query}\nRetrying...\n')
            return process_query()

        write_evaluation(eval_res)

        log_op(f'\n success on method:\n{query} \n answer:\n{res}\n evaluation:\n{eval_res}\n')
    except Exception as e:
        log_op(f'\n\nfailed to method:\n{query}\nwith:\n{e}\n\n')

def get_unprocessed_problems():
    """
    Retrieve problems from the STATE_FILE that haven't been answered or evaluated.
    """
    try:
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            
            # Filter problems that have the status 'current' or 'answered'
            unprocessed = [item for item in data if item['status'] in ['current', 'answered']]
            
            return unprocessed
    except FileNotFoundError:
        print(f"{STATE_FILE} not found!")
        return []

def process_specific_query(problem):
    """
    Process a specific problem, generate an answer, and evaluate the answer.
    """
    try:
        send = create_question_dict(problem['problem'])
        qa = retrieval_qa_pipline(device_type, use_history, memory_unit='create', promptTemplate_type="llama")
        res = qa(send)
        
        # Check if the result is an empty string
        if res in ["", " ", "\n"]:
            log_op(f'\nEmpty response for method:\n{problem}\nRetrying...\n')
            return process_specific_query(problem)

        write_answer(res)

        eval_send = create_evaluation_dict()
        qa = retrieval_qa_pipline(device_type, use_history, memory_unit='evaluate', promptTemplate_type="llama")
        eval_res = qa(eval_send)

        # Check if the evaluation result is an empty string
        if eval_res in ["", " ", "\n"]:
            log_op(f'\nEmpty evaluation for method:\n{problem}\nRetrying...\n')
            return process_specific_query(problem)

        write_evaluation(eval_res)

        log_op(f'\n success on method:\n{problem} \n answer:\n{res}\n evaluation:\n{eval_res}\n')
    except Exception as e:
        log_op(f'\n\nfailed to method:\n{problem}\nwith:\n{e}\n\n')

def main():
    # First, process problems that haven't been answered or evaluated
    unprocessed_problems = get_unprocessed_problems()
    for problem in unprocessed_problems:
        process_specific_query(problem)
    
    # Then, continue with the rest of the script
    for _ in range(MAX_LOOP_COUNT):
        process_query()

if __name__ == "__main__":
    main()

