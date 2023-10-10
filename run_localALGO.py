import os

from utils.agents.qa_memo import retrieval_qa_pipline
from utils.control_local.utils import log_op

from  utils.control_local.utils import get_unprocessed_problems, create_evaluation_dict, create_question_dict, write_answer, get_problem, get_context, write_evaluation



# RESTRICT = "format your answer like ''' {{'answer': 'your answer', 'thoughts': 'how you came to the answer'}} }} '''."
DEFAULT_PROBLEM = "what makes great software as a service?"
MAX_LOOP_COUNT = 99

device_type = 'cpu'
show_sources = False
use_history = True

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

