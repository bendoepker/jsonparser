from collections import defaultdict

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
    fields = defaultdict(list)

    def __init__(self):
        return

    def __str__(self):
        return "{\n" + self.fields.__str__() + "\n}\n"


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


def stack_unwind(stack: list, val: str):
    match val:
        case "CBracket":
            if stack[-1] == "OBracket":
                stack.pop()
            else:
                raise JSONError(f"Syntax error: expected CBracket but got {val}")
        case "CBrace":
            if stack[-1] == "OBrace":
                stack.pop()
            else:
                raise JSONError(f"Syntax error: expected CBracket but got {val}")
        case _:
            raise JSONError(f"Unexpected token: {val}")


def JSONParse(json: str):
    # Order will always be:
    #   {
    #   Key
    #   :
    #   Value
    #   ,  or  unwind stack
    output: JSON = None
    toks = tokenize(json)
    obj_stk = []  # The object stack
    tok_stk = []  # The token stack (contains OBracket and OBraces waiting for their pair)
    exp_tok_type = ["OBrace"]
    val_or_key = "Key"
    in_array = False # BUG: This doesn't support multidimensional arrays...Possibly could be fixed with an array stack holding the array indices
    last_key = ""
    for token in toks:
        if token.type != "Boolean" and token.type != "Null" and token.type != "Number":
            print(token.type + "   " + token.value + "   " + val_or_key + "   " + str(len(obj_stk)))
        if token.type not in exp_tok_type:
            raise JSONError(f"Syntax Error, expected \'{exp_tok_type}\' but got \'{token.type}\'")
        else:
            # Parse OBrace
            if token.type == "OBrace":
                obj_stk.append(JSON())
                if not output:
                    output = obj_stk[-1]
                else:
                    if in_array:
                        obj_stk[-2].fields[last_key].append(obj_stk[-1])
                    else:
                        obj_stk[-2].fields[last_key] = obj_stk[-1]
                tok_stk.append(token.type)
                exp_tok_type = ["CBrace", "String"]
                val_or_key = "Key"
            # Parse CBrace
            if token.type == "CBrace":
                exp_tok_type = ["CBrace", "CBracket", "Comma"]
                obj_stk.pop()
                stack_unwind(tok_stk, token.type)
            # Parse OBracket
            if token.type == "OBracket":
                exp_tok_type = ["String", "Number", "OBrace", "Boolean", "Null"]
                tok_stk.append(token.type)
                in_array = True
            # Parse CBracket
            if token.type == "CBracket":
                exp_tok_type = ["CBrace", "CBracket", "Comma"]
                stack_unwind(tok_stk, token.type)
                in_array = False
                last_key = ""
            # Parse Colon
            elif token.type == "Colon":
                exp_tok_type = ["String", "Number", "Boolean", "Null", "OBracket", "OBrace"]
                val_or_key = "Value"
            # Parse Comma
            elif token.type == "Comma":
                if not in_array:
                    val_or_key = "Key"
                exp_tok_type = ["String"]
            # Parse String
            elif token.type == "String":
                if val_or_key == "Key":
                    last_key = token.value
                    exp_tok_type = ["Colon"]
                else:
                    if last_key == "":
                        raise JSONError("Syntax Error: key names cannot be empty")
                    else:
                        if in_array:
                            obj_stk[-1].fields[last_key].append(token.value)
                        else:
                            obj_stk[-1].fields[last_key] = token.value
                            last_key = ""
                        exp_tok_type = ["Comma", "CBracket", "CBrace"]
            # Parse Number
            elif token.type == "Number":
                if val_or_key == "Key":
                    raise JSONError(f"Syntax Error: expected a string but got {token.type}")
                else:
                    if last_key == "":
                        raise JSONError("Syntax Error: key names cannot be empty")
                    else:
                        if in_array:
                            obj_stk[-1].fields[last_key].append(token.value)
                        else:
                            obj_stk[-1].fields[last_key] = token.value
                        last_key = ""
                        exp_tok_type = ["Comma", "CBracket", "CBrace"]
            # Parse Booleans
            elif token.type == "Boolean":
                if val_or_key == "Key":
                    raise JSONError(f"Syntax Error: expected a string but got {token.type}")
                else:
                    if last_key == "":
                        raise JSONError("Syntax Error: key names cannot be empty")
                    else:
                        if in_array:
                            obj_stk[-1].fields[last_key].append(token.value)
                        else:
                            obj_stk[-1].fields[last_key] = token.value
                        last_key = ""
                        exp_tok_type = ["Comma", "CBracket", "CBrace"]
            # Parse Null
            elif token.type == "Null":
                if val_or_key == "Key":
                    raise JSONError(f"Syntax Error: expected a string but got {token.type}")
                else:
                    if last_key == "":
                        raise JSONError("Syntax Error: key names cannot be empty")
                    else:
                        if in_array:
                            obj_stk[-1].fields[last_key].append(token.value)
                        else:
                            obj_stk[-1].fields[last_key] = token.value
                        last_key = ""
                        exp_tok_type = ["Comma", "CBracket", "CBrace"]
    return output



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
    # print("String                    | Type     | Value")
    for tok in tokens:
        t = JSON_Token(tok)
        # print(f"{tok:<25.25} | {t.type:<8} | {t.value}")
        json_tokens.append(t)
    return json_tokens


if __name__ == '__main__':
    with open("../sample.json", mode='r') as f:
        json = f.read()
        json_obj = JSONParse(json)
        print(json_obj)

# Expect next token
#   Last Token     | Expected Token
# -----------------+---------------
#   {              | Key or }
#   Key            | :
#   :              | Value
