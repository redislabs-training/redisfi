SPECIAL_CHARS = ",.<>{}[]\"':;!@#$%^&*()-+=~"

def escape_special_characters(input: str) -> str:
    ret = ''
    for char in input:
        if char in SPECIAL_CHARS:
            ret += '\\'
        ret += char

    return ret 
