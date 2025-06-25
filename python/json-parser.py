Tokens = {
    "OBrace": "{",
    "CBrace": "}",
    "OBracket": "[",
    "CBracket": "]",
    "Colon": ":",
    "Comma": ",",
    "Key": str,
    "String": str,
    "Integer": int,
    "Object": object,
    "Array": "array",
}


class JSON_Key:
    key: str

    def __init__(self, key: str):
        self.key = key

    def get_key(self):
        return self.key


class JSON_Value:
    type: str

    def __init__(self, type: str, value: str):
        match type:
            case "Integer":
                self.value = int(value)


def tokenize(json: str):
    json.strip()
    tokens = []
    in_string: bool = False
    in_number: bool = False
    index = -1
    start_index = 0
    for c in json:
        index += 1
        if not in_string and not in_number:
            if c == '{':
                tokens.append("{")
            elif c == '}':
                tokens.append("}")
            elif c == '[':
                tokens.append("[")
            elif c == ']':
                tokens.append("]")
            elif c == ':':
                tokens.append(":")
            elif c == ',':
                tokens.append(",")
            elif c == '"':
                in_string = True
                start_index = index
            elif c.isnumeric():
                in_number = True
                start_index = index
        elif in_string:
            if c == '"' and json[index - 1] != '\\':  # Closing " and not escaped \"
                tokens.append(json[start_index:index + 1])
                in_string = False
        elif in_number:
            if not c.isnumeric():
                tokens.append(json[start_index:index])
                in_number = False
    return tokens


if __name__ == '__main__':
    with open("../sample.json", mode='r') as f:
        json = f.read()
        print(tokenize(json))

# Expect next token
#   Last Token     | Expected Token
# -----------------+---------------
#   {              | Key or }
#   Key            | :
#   :              | Value
