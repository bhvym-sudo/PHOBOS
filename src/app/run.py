import subprocess
import os

def run_go_scraper():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(app_dir)
    scraper_dir = os.path.join(project_root, "scraper")
    
    result = subprocess.run(
        ["go", "run", "main.go"],
        cwd=scraper_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")

if __name__ == "__main__":
    run_go_scraper()

