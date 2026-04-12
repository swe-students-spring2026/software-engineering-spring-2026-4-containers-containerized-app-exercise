import json
import os

def write_json(path, results):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data = {"results": results}

    with open(path, "w") as f:
        json.dump(data, f, indent=2)