import subprocess
import os
import json
from PyQt5.QtCore import QThread, pyqtSignal
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

class MonitorWorker(QThread):
    scraped_data = pyqtSignal(str)
    parsed_data = pyqtSignal(str)
    ai_results = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ai_model = None
        self.load_or_train_model()

    def load_or_train_model(self):
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(app_dir, 'threat_classifier.pkl')
            
            if os.path.exists(model_path):
                print("Loading existing AI model...")
                self.ai_model = joblib.load(model_path)
                print("AI model loaded successfully")
            else:
                print("Training new AI model...")
                self.train_model()
        except Exception as e:
            print(f"Error loading/training AI model: {e}")
            self.ai_model = None

    def train_model(self):
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            train_path = os.path.join(app_dir, 'model/train.json')
            
            if not os.path.exists(train_path):
                print("train.json not found, creating basic model")
                self.create_basic_model()
                return

            with open(train_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            texts = [item["text"] for item in data["data"]]
            labels = [item["label"] for item in data["data"]]
            

            self.ai_model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 3),
                    stop_words='english',
                    lowercase=True
                )),
                ('classifier', LogisticRegression(
                    random_state=42,
                    class_weight='balanced'
                ))
            ])
            
            self.ai_model.fit(texts, labels)
            

            model_path = os.path.join(app_dir, 'threat_classifier.pkl')
            joblib.dump(self.ai_model, model_path)
            print("AI model trained and saved")
            
        except Exception as e:
            print(f"Error training model: {e}")
            self.create_basic_model()

    def create_basic_model(self):
        basic_texts = [
            "weapon dealing discussion", "selling guns", "terrorist funding",
            "normal discussion", "technology news", "cooking recipes"
        ]
        basic_labels = ["suspicious", "suspicious", "suspicious", 
                       "not suspicious", "not suspicious", "not suspicious"]
        
        self.ai_model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, lowercase=True)),
            ('classifier', LogisticRegression(random_state=42))
        ])
        
        self.ai_model.fit(basic_texts, basic_labels)
        print("Basic AI model created")

    def analyze_with_ai(self, results_data):
        try:
            data = json.loads(results_data) if isinstance(results_data, str) else results_data
            if not data:
                return "No data to analyze"
            
            WEAPON_KEYWORDS = ['weapon', 'gun', 'rifle', 'pistol', 'ammunition', 'bomb', 'explosive', 'toy']
            TERROR_KEYWORDS = ['terrorist', 'jihad', 'attack', 'kill', 'assassination', 'hitman']
            ANTI_INDIA = ['anti-india', 'separatist', 'kashmir liberation', 'pakistan intelligence', 'aid']
            
            analysis_results = []
            suspicious_count = 0
            
            for i, entry in enumerate(data, 1):
                url = entry.get("url", "unknown") 
                text = entry.get("text", "").lower()
                
                weapon_score = sum(1 for word in WEAPON_KEYWORDS if word in text)
                terror_score = sum(1 for word in TERROR_KEYWORDS if word in text)
                anti_india_score = sum(1 for word in ANTI_INDIA if word in text)
                
                total_score = weapon_score * 3 + terror_score * 4 + anti_india_score * 2
                
                if total_score >= 3:
                    status = "SUSPICIOUS"
                    classification = "SUSPICIOUS"
                    suspicious_count += 1
                elif total_score >= 1:
                    status = "POTENTIALLY SUSPICIOUS"
                    classification = "POTENTIALLY SUSPICIOUS"
                else:
                    status = "SAFE"
                    classification = "NOT SUSPICIOUS"
                
                analysis_results.append(f"""
    Entry {i}: {status}
    URL: {url}
    Classification: {classification}
    Threat Score: {total_score}
    Text Preview: {entry.get('text', '')[:100]}{'...' if len(entry.get('text', '')) > 100 else ''}
    {'-' * 60}""")
            
            threat_level = "HIGH" if suspicious_count > len(data) * 0.5 else "MEDIUM" if suspicious_count > 0 else "LOW"
            
            summary = f"""
    THREAT ANALYSIS SUMMARY  
    {'=' * 60}
    Total Entries: {len(data)}
    Suspicious Content: {suspicious_count}
    Threat Level: {threat_level}

    {'=' * 60}
    DETAILED ANALYSIS:
    """
            
            return summary + "\n".join(analysis_results)
            
        except Exception as e:
            return f"Analysis Error: {str(e)}"


    def run(self):
        print("MonitorWorker started")
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(f"Running scraper from: {app_dir}")
            
            result = subprocess.run(
                ["python", "run.py"],
                cwd=app_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"Scraper return code: {result.returncode}")
            if result.stdout:
                print(f"Scraper stdout: {result.stdout}")
            if result.stderr:
                print(f"Scraper stderr: {result.stderr}")

            if result.returncode == 0:
                print("Scraper completed, now processing data")
                self.process_scraped_data()
                self.load_and_display_data()
            else:
                self.scraped_data.emit(f"Error running scraper: {result.stderr}")

        except subprocess.TimeoutExpired:
            print("Scraper timeout")
            self.scraped_data.emit("Scraper timeout after 60 seconds")
        except Exception as e:
            print(f"Monitor error: {e}")
            self.scraped_data.emit(f"Monitoring error: {str(e)}")

    def process_scraped_data(self):
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(f"Processing data from: {app_dir}")
            
            result = subprocess.run(
                ["python", "read.py"],
                cwd=app_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print(f"Data processing return code: {result.returncode}")
            if result.stdout:
                print(f"Processing stdout: {result.stdout}")
            if result.stderr:
                print(f"Processing stderr: {result.stderr}")
                
        except Exception as e:
            print(f"Error processing data: {e}")

    def load_and_display_data(self):
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(app_dir)
            scraper_dir = os.path.join(project_root, "scraper")
            data_path = os.path.join(scraper_dir, "data.json")

            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    scraped_content = f.read()
                self.scraped_data.emit(scraped_content)
                print("Emitted scraped data")
            else:
                self.scraped_data.emit("data.json not found")
                print("data.json not found")


            results_path = os.path.join(app_dir, "results.json")
            if os.path.exists(results_path):
                with open(results_path, 'r', encoding='utf-8') as f:
                    parsed_content = f.read()
                self.parsed_data.emit(parsed_content)
                print("Emitted parsed data")
                

                print("Starting AI analysis...")
                ai_analysis = self.analyze_with_ai(parsed_content)
                self.ai_results.emit(ai_analysis)
                print("AI analysis completed")
            else:
                self.parsed_data.emit("results.json not found")
                self.ai_results.emit("No results.json found for AI analysis")
                print("results.json not found")

        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            print(error_msg)
            self.scraped_data.emit(error_msg)
            self.parsed_data.emit(error_msg)
            self.ai_results.emit(f"AI analysis error: {str(e)}")

