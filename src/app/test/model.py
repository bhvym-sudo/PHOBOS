import json
from llama_cpp import Llama

# Load the Q2 GGUF model with optimized settings
llm = Llama(
    model_path="./model/mistral-7b-instruct-v0.2.Q2_K.gguf",
    n_ctx=512,         # smaller context for speed
    n_threads=8,       # CPU threads
    n_batch=128,       # process tokens in batches
    use_mmap=True,     # memory-mapped file, low RAM
    use_mlock=False    # disable locking
)

# Load scraped JSON data
with open("results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Prompt template
template = """You are a cybersecurity analyst.

Forum Post:
URL: {url}
Content: {content}

Task:
1. Summarize in 2–3 sentences.
2. Identify any dangerous/illegal activity.
3. Give a danger rating (0–10).
4. Provide concise reasoning.

Keep your response structured and concise.
"""


results = []

for entry in data:
    url = entry.get("url", "")
    text = entry.get("text", "")

    content = text[:800]

    prompt = template.format(url=url, content=content)

    # Run model
    output = llm(
        prompt,
        max_tokens=150,     
        temperature=0.3,    
        top_p=0.95,         
        repeat_penalty=1.1  
    )

    result_text = output["choices"][0]["text"].strip()

    # Save structured output
    results.append({
        "url": url,
        "summary_report": result_text
    })

# Save results to a JSON file
with open("analysis_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ Analysis complete. Results saved to 'analysis_results.json'")

