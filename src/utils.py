import json

def read_json(path):
    with open(path) as json_file:
        # check if the file is valid json
        try:
            data = json.load(json_file)
            return data
        except json.JSONDecodeError:
            print("Invalid JSON file.") 
            return None