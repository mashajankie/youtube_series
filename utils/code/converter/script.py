import os

def convert_to_one_line(input_file: str, output_file: str):
    # Read the content of the markdown file
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Remove newline characters
    one_line_content = content.replace('\n', ' ')
    
    # Write the single line of text into the new document
    with open(output_file, 'w') as f:
        f.write(one_line_content)

path = './converter/to_convert'
final_path = './converter/converted'
for file in os.listdir(path):
    convert_to_one_line(os.path.join(path, file), os.path.join(final_path, file))
