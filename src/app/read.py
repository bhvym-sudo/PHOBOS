import json
from bs4 import BeautifulSoup
import os

def process_scraped_data():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(app_dir)
    scraper_dir = os.path.join(project_root, "scraper")
    data_path = os.path.join(scraper_dir,"data.json")
    
    print(f"Looking for data.json at: {data_path}")
    print(f"File exists: {os.path.exists(data_path)}")
    
    if os.path.exists(data_path):
        print(f"File size: {os.path.getsize(data_path)} bytes")
    
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Data type: {type(data)}")
        print(f"Data content: {data}")
        
        results = []
        if isinstance(data, dict):
            print("Processing dict")
            soup = BeautifulSoup(data["html"], "html.parser")
            all_text = soup.get_text(separator="\n\n", strip=True)
            results.append({
                "url": data["url"],
                "text": all_text
            })
        elif isinstance(data, list):
            print(f"Processing list with {len(data)} items")
            for item in data:
                soup = BeautifulSoup(item["html"], "html.parser")
                all_text = soup.get_text(separator="\n\n", strip=True)
                results.append({
                    "url": item["url"],
                    "text": all_text
                })
        
        print(f"Results count: {len(results)}")
        
        results_path = os.path.join(app_dir, "results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"Written to: {results_path}")
            
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    process_scraped_data()

