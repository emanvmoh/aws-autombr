import pdfplumber
from typing import Optional

class PDFExtractor:
    """Extract text content from PDF files."""
    
    @staticmethod
    def extract_text(pdf_path: str) -> Optional[str]:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a single string, or None if extraction fails
        """
        try:
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            return "\n\n".join(text_content) if text_content else None
            
        except Exception as e:
            print(f"PDF extraction error for {pdf_path}: {e}")
            return None
    
    @staticmethod
    def extract_text_with_metadata(pdf_path: str) -> dict:
        """
        Extract text and metadata from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with 'text', 'pages', and 'metadata'
        """
        try:
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                metadata = pdf.metadata
                page_count = len(pdf.pages)
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            return {
                'text': "\n\n".join(text_content) if text_content else "",
                'pages': page_count,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"PDF extraction error for {pdf_path}: {e}")
            return {
                'text': "",
                'pages': 0,
                'metadata': {},
                'error': str(e)
            }
