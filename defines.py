import json

def load(file_path):
    with open(f"defines/{file_path}.json") as f:
        return json.load(f)

text = load("text")

colors = {
    "flavor": 0x71B48D,
    "flavor2": 0x404E7C,
    "warning": 0x260F26,
    "action": 0x86CB92,
    "flavor3": 0x251F47
}
