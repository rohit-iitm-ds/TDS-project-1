import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')
    
    # Discourse Configuration
    DISCOURSE_BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
    TDS_COURSE_URL = f"{DISCOURSE_BASE_URL}/c/jan-2025-tools-in-data-science"
    
    # Date ranges for scraping
    START_DATE = "2025-01-01"
    END_DATE = "2025-04-14"
    
    # Model Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    OPENAI_MODEL = "gpt-3.5-turbo-0125"
    
    # Search Configuration
    MAX_SIMILAR_POSTS = 5
    SIMILARITY_THRESHOLD = 0.3