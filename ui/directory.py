import os
import json
import argparse

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    root_name = os.path.basename(rootdir)
    structure = {'name': root_name, 'type': 'directory', 'children': []}

    for root, dirs, files in os.walk(rootdir):
        current_dir = structure

        # Split the root path
        path_parts = root.split(os.sep)

        # Skip the root directory part to avoid duplication
        for part in path_parts[1:]:
            found = False
            for child in current_dir['children']:
                if child['name'] == part:
                    current_dir = child
                    found = True
                    break
            
            if not found:
                # Create a new directory entry
                new_dir = {'name': part, 'type': 'directory', 'children': []}
                current_dir['children'].append(new_dir)
                current_dir = new_dir

        # Add files to the current directory
        for file in files:
            current_dir['children'].append({'name': file, 'type': 'file'})

    return structure

def save_directory_structure_to_json(structure, filename):
    """
    Saves the directory structure to a JSON file
    """
    with open(filename, 'w') as json_file:
        json.dump(structure, json_file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traverse a directory and output its structure to a JSON file. The command structure is python3 directory.py [RELATIVE PATH TO LOG FOLDER WITHOUT / AT THE END] output.json")
    parser.add_argument('directory_path', type=str, help="The path of the directory to traverse")
    parser.add_argument('output_file', type=str, help="The name of the output JSON file")

    args = parser.parse_args()

    directory_structure = get_directory_structure(args.directory_path)
    save_directory_structure_to_json(directory_structure, args.output_file)
    print(f"Directory structure has been saved to {args.output_file}")
