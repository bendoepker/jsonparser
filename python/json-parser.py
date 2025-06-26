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
}


class JSONError(Exception):
    def __init__(self, type: str):
        self.type = type

    def __str__(self):
        return f"Error parsing JSON: {self.type}"


class JSON_Value:
    type: str

    def __init__(self, type: str, value: str):
        match type:
            case "Integer":
                self.value = int(value)


class JSON:
    fields: dict

    def __init__(self, key: str, value: JSON_Value):
        self.fields[key] = value


class JSON_Token:
    type: str  # Any in Tokens list
    value: int | float | str | bool | None

    def __init__(self, tok_str: str):
        if len(tok_str) == 1:
            if tok_str == "{":
                self.type = "OBrace"
                self.value = "{"
            elif tok_str == "}":
                self.type = "CBrace"
                self.value = "}"
            elif tok_str == "[":
                self.type = "OBracket"
                self.value = "["
            elif tok_str == "]":
                self.type = "CBracket"
                self.value = "]"
            elif tok_str == ":":
                self.type = "Colon"
                self.value = ":"
            elif tok_str == ",":
                self.type = "Comma"
                self.value = ","
            else:
                raise JSONError(f"Syntax Error: Unrecognized token {tok_str}")
        else:
            if tok_str[0] == "\"":
                # Could be "true" "false" or "null"
                if tok_str == "\"true\"":
                    self.type = "Boolean"
                    self.value = True
                elif tok_str == "\"false\"":
                    self.type = "Boolean"
                    self.value = False
                elif tok_str == "\"null\"":
                    self.type = "Null"
                    self.value = None
                else:
                    # String
                    if tok_str[-1] != "\"":
                        raise JSONError(f"Syntax error, expected \'\"\' at the end of {tok_str}")
                    self.type = "String"
                    self.value = tok_str[1:-1]
            elif tok_str[0].isnumeric() or tok_str[0] == "-":
                self.type = "Number"
                try:
                    # BUG: Technically this isn't to spec (for 018 or -0127 for example), but its good enough
                    self.value = float(tok_str)
                except Exception:
                    raise JSONError(f"Malformed Number: {tok_str} is not in JSON format")
            else:
                raise JSONError(f"Syntax Error: {tok_str} is an invalid token")


def JSONParse(json: str):
    # Order will always be:
    #   {
    #   Key
    #   :
    #   Value
    #   ,  or  unwind stack
    toks = tokenize(json)
    return
    tok_stk = []
    exp_tok = ["{"]
    tok_req = True
    for token in toks:
        if tok_req:
            if token not in exp_tok:
                raise JSONError(f"Syntax Error, expected \'{exp_tok}\' but got \'{token}\'")
            else:
                if token == "{":
                    tok_stk.append(token)
                    exp_tok.clear()
                    exp_tok.append("}", "string")
                    tok_req = False


def char_in_number(c: str):
    if c.isnumeric():
        return True
    if c == '.':
        return True
    if c == 'e':
        return True
    if c == 'E':
        return True
    if c == '-':
        return True
    if c == '+':
        return True
    return False


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
            elif c.isnumeric() or c == '-':
                in_number = True
                start_index = index
        elif in_string:
            if c == '"' and json[index - 1] != '\\':  # Closing " and not escaped \"
                tokens.append(json[start_index:index + 1])
                in_string = False
        else:  # in_number
            if not char_in_number(c):
                tokens.append(json[start_index:index])
                in_number = False
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
    json_tokens = []
    print("String                    | Type     | Value")
    for tok in tokens:
        t = JSON_Token(tok)
        print(f"{tok:<25.25} | {t.type:<8} | {t.value}")
        json_tokens.append(t)
    return json_tokens


if __name__ == '__main__':
    with open("../sample.json", mode='r') as f:
        json = f.read()
        JSONParse(json)

# Expect next token
#   Last Token     | Expected Token
# -----------------+---------------
#   {              | Key or }
#   Key            | :
#   :              | Value
