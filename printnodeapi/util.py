import re

def camel_to_underscore(text):
    letters = list(text.strip())
    indexes = [i for i,
               l in enumerate(letters) if l.upper() == l and not re.match('_',l)]
    for i in reversed(indexes):
        letters[i] = letters[i].lower()
        if i != 0:
            letters.insert(i, '_')
    return ''.join(letters)
