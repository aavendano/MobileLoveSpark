import os
import re

def replace_in_file(filepath):
    print(f"Processing {filepath}")
    with open(filepath, 'r') as file:
        content = file.read()
    
    # Replace all occurrences of experimental_rerun with rerun
    new_content = content.replace('st.experimental_rerun()', 'st.rerun()')
    
    if new_content != content:
        with open(filepath, 'w') as file:
            file.write(new_content)
        print(f"  Updated {filepath}")
    else:
        print(f"  No changes in {filepath}")

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                replace_in_file(filepath)

# Process the pages directory
process_directory('./pages')
# Process the utils directory
process_directory('./utils')