import json

try:
    with open("info.json", "w") as json_file:
        json.dump("h", json_file, indent=4)
    print("info.json written!")
except Exception as e:
    print("Failed to write info.json:", e)
