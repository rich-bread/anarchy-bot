import json

def open_json(filename):
    f = open(filename,'r',encoding="utf-8_sig")
    data = json.load(f)

    return data
