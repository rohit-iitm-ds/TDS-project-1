import re
import html
from bs4 import BeautifulSoup
import base64
from PIL import Image
import io

class TextProcessor:
    @staticmethod
    def clean_html(html_content):
        """Clean HTML content and extract text"""
        if not html_content:
            return ""
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    @staticmethod
    def preprocess_text(text):
        """Preprocess text for better matching"""
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\?\!\,\-\(\)]', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def extract_code_blocks(text):
        """Extract code blocks from text"""
        code_blocks = []
        
        # Find code blocks between triple backticks
        code_pattern = r'```[\s\S]*?```'
        matches = re.findall(code_pattern, text)
        code_blocks.extend(matches)
        
        # Find inline code
        inline_code_pattern = r'`[^`]+`'
        matches = re.findall(inline_code_pattern, text)
        code_blocks.extend(matches)
        
        return code_blocks
    
    @staticmethod
    def process_image(base64_image):
        """Process base64 encoded image"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    @staticmethod
    def extract_keywords(text, min_length=3):
        """Extract keywords from text"""
        if not text:
            return []
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + ',}\b', text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        keywords = [word for word in words if word not in stop_words]
        
        return list(set(keywords))  # Remove duplicates