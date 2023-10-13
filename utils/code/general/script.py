import os

def read_gitignore(gitignore_path='.gitignore'):
    """Reads the .gitignore file and returns a list of patterns to ignore."""
    with open(gitignore_path, 'r') as file:
        # Filter out comments and empty lines, and strip whitespace
        lines = [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#')]
    return lines

def write_to_python_script(ignore_list, output_script='./utils/code/general/scripts/ignore_list.py'):
    """Writes the ignore list to another Python script."""
    with open(output_script, 'w') as file:
        file.write("IGNORE_LIST = [\n")
        for item in ignore_list:
            file.write(f"    '{item}',\n")
        file.write("]\n")

def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def create_llm_result(folder):
    ensure_folder_exists(folder)
    num = len(os.listdir(folder))
    filenaming = f'query{num}.md'
    with open(os.path.join(folder, filenaming), 'w') as f:
        f.write(folder)