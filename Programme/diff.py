import re
import random 

text = 

box = []

def replace_with_pattern(match):
    content = match.group(1)
    words = content.split()
    
    box.append(content)

    # Ein Wort → einzelne Unterstriche mit 1 Leerzeichen
    # Mehrere Wörter → Wörter durch 2 Leerzeichen getrennt
    replaced_words = [" ".join("_" for _ in word) for word in words]

    return "  ".join(replaced_words)   # 2 Leerzeichen zwischen Wörtern

result = re.sub(r"\[([^\]]+)\]", replace_with_pattern, text)

random.shuffle(box)

print(result)

print(", ".join(box))

pyperclip.copy(result)



