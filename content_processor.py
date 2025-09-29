import PyPDF2
from docx import Document as DocxDocument
import re
import os

# Simple tokenization without NLTK
def simple_sent_tokenize(text):
    """Simple sentence tokenizer that doesn't require NLTK"""
    # Split on common sentence endings
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

def simple_word_tokenize(text):
    """Simple word tokenizer that doesn't require NLTK"""
    return re.findall(r'\b\w+\b', text.lower())

# Common English stopwords
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", 
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 
    'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 
    'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 
    'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 
    'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', 
    "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 
    'wouldn', "wouldn't"
}

# Optional imports for OCR functionality
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# Fallback to pytesseract if available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# PIL Image import (required for both OCR methods)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class ContentProcessor:
    def __init__(self):
        self.stop_words = STOPWORDS
    
    def extract_pdf_content(self, file_path):
        """
        Extract text content from PDF files
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return self.clean_text(text)
        except Exception as e:
            raise Exception(f"Error extracting PDF content: {str(e)}")
    
    def extract_docx_content(self, file_path):
        """
        Extract text content from DOCX files
        """
        try:
            doc = DocxDocument(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self.clean_text(text)
        except Exception as e:
            raise Exception(f"Error extracting DOCX content: {str(e)}")
    
    def clean_text(self, text):
        """
        Clean and preprocess extracted text
        """
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:]', '', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_concepts(self, text):
        """
        Extract key concepts from text using simple frequency analysis
        """
        # Tokenize words using simple tokenizer
        words = simple_word_tokenize(text)
        
        # Remove stopwords and non-alphabetic tokens
        filtered_words = [word for word in words if word.isalpha() and word not in self.stop_words]
        
        # Get frequency distribution
        from collections import Counter
        freq_dist = Counter(filtered_words)
        
        # Extract most common concepts (top 20)
        concepts = [word for word, freq in freq_dist.most_common(20)]
        
        return concepts
    
    def identify_document_structure(self, text):
        """
        Identify document structure (headings, sections, etc.)
        """
        # Simple heuristic for identifying headings
        lines = text.split('\n')
        structure = {
            'headings': [],
            'paragraphs': [],
            'sections': []
        }
        
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                # Check if line might be a heading (short, ends with colon, or all caps)
                if (len(line) < 100 and 
                    (line.endswith(':') or line.isupper() or 
                     re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:', line))):
                    structure['headings'].append(line)
                else:
                    structure['paragraphs'].append(line)
        
        return structure
    
    def chunk_text(self, text, chunk_size=500):
        """
        Split text into manageable chunks for processing
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def extract_image_content(self, file_path):
        """
        Extract text content from image files using OCR
        """
        try:
            # Check if PIL is available
            if not PIL_AVAILABLE:
                raise Exception("PIL/Pillow is not installed. Please install Pillow: pip install Pillow")
            
            # Open image using PIL
            image = Image.open(file_path)
            
            # Try EasyOCR first (no system dependencies)
            if EASYOCR_AVAILABLE:
                reader = easyocr.Reader(['en'])
                result = reader.readtext(file_path)
                text = ' '.join([item[1] for item in result])
                return self.clean_text(text)
            
            # Fallback to Tesseract if available
            elif TESSERACT_AVAILABLE:
                text = pytesseract.image_to_string(image)
                return self.clean_text(text)
            
            else:
                raise Exception("No OCR engine available. Please install EasyOCR (recommended) or Tesseract OCR.")
                
        except Exception as e:
            if "No OCR engine available" in str(e):
                raise Exception("OCR functionality not available. Please install EasyOCR (recommended):\n\npip install easyocr\n\nOr install Tesseract OCR:\n\nWindows: Download from https://github.com/UB-Mannheim/tesseract/wiki\nmacOS: brew install tesseract\nLinux: sudo apt-get install tesseract-ocr")
            elif "PIL/Pillow is not installed" in str(e):
                raise Exception("PIL/Pillow is required for image processing. Please install: pip install Pillow")
            else:
                raise Exception(f"Error extracting image content: {str(e)}")
    
    def process_document(self, file_path, file_type):
        """
        Main method to process documents based on file type
        """
        if file_type.lower() == 'pdf':
            content = self.extract_pdf_content(file_path)
        elif file_type.lower() == 'docx':
            content = self.extract_docx_content(file_path)
        elif file_type.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            # Handle image files using OCR
            content = self.extract_image_content(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Extract concepts and structure
        concepts = self.extract_concepts(content)
        structure = self.identify_document_structure(content)
        chunks = self.chunk_text(content)
        
        processed_data = {
            'content': content,
            'concepts': concepts,
            'structure': structure,
            'chunks': chunks,
            'word_count': len(content.split()),
            'character_count': len(content),
            'processing_method': 'ocr' if file_type.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] else 'standard'
        }
        
        return processed_data
    
    def get_document_metadata(self, file_path, file_type):
        """
        Extract metadata about the document
        """
        metadata = {
            'file_type': file_type,
            'file_size': os.path.getsize(file_path),
            'processing_capabilities': ['text_extraction', 'basic_analysis']
        }
        
        # Add OCR capabilities if available
        if TESSERACT_AVAILABLE:
            metadata['processing_capabilities'].append('ocr_processing')
        
        return metadata
