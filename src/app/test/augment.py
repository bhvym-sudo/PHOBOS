import json
import random

replace_map = {
    "destroy": ["wipe out", "eliminate", "annihilate"],
    "love": ["enjoy", "like", "appreciate"],
    "India": ["this country", "India", "the nation"]
}

def augment(text):
    words = text.split()
    new_words = []
    for w in words:
        if w in replace_map:
            new_words.append(random.choice(replace_map[w]))
        else:
            new_words.append(w)
    return " ".join(new_words)


with open("D:\\projects\\PHOBOS\\src\\app\\modeldata.json","r",encoding="utf8") as f:
    data = json.load(f)

augmented = []
for item in data:
    augmented.append(item)  
    for _ in range(2):      
        aug_text = augment(item["text"])
        augmented.append({"text": aug_text, "label": item["label"]})


with open("modeldata_big.json","w",encoding="utf8") as f:
    json.dump(augmented, f, ensure_ascii=False, indent=2)

print("Saved", len(augmented), "examples to data_big.json")
