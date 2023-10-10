import os
import json
import datetime

from run_localALGO import process_query, process_specific_query 


STATE_FILE = 'current_state.json'
RESTRICT = ""
GENERATE_QUESTION = "Generate a new question."



def log_op(operation, *args, **kwargs) -> None:
    """Log operations to a file."""
    log_dir = "./logs"
    log_file_path = os.path.join(log_dir, "logs.txt")
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    details = ', '.join(map(str, args)) + ', '.join(f"{k}={v}" for k, v in kwargs.items())
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{operation}: {details}\n")



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


