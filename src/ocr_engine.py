"""OCR Engine - Ledger Digitization Module

Processes images of handwritten ledgers using Tesseract OCR.
"""

import logging
from typing import List, Dict
import os

try:
    import pytesseract
    import cv2
    import numpy as np
except ImportError:
    logging.warning("pytesseract or opencv not installed. OCR will not work.")

logger = logging.getLogger(__name__)


class LedgerOCR:
    """OCR processor for handwritten ledger images"""
    
    def __init__(self):
        """Initialize OCR engine"""
        logger.info("Ledger OCR initialized")
    
    def process_ledger(self, image_path: str) -> List[Dict]:
        """
        Process ledger image and extract items
        
        Args:
            image_path: Path to ledger image
        
        Returns:
            List of extracted items with name, quantity, unit
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return []
        
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Preprocess: convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(thresh)
            
            logger.info(f"Extracted text: {text}")
            
            # Parse extracted text (simple parsing)
            items = self._parse_ledger_text(text)
            
            return items
        
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return []
    
    def _parse_ledger_text(self, text: str) -> List[Dict]:
        """
        Parse OCR text into structured items
        
        Args:
            text: Raw OCR text
        
        Returns:
            List of item dicts
        """
        items = []
        lines = text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Simple pattern matching
            # Expected format: "Item Name - Quantity Unit"
            parts = line.split('-')
            if len(parts) >= 2:
                item_name = parts[0].strip()
                quantity_unit = parts[1].strip().split()
                
                if len(quantity_unit) >= 2:
                    try:
                        quantity = float(quantity_unit[0])
                        unit = quantity_unit[1]
                        
                        items.append({
                            'name': item_name.lower(),
                            'quantity': quantity,
                            'unit': unit
                        })
                    except ValueError:
                        logger.warning(f"Could not parse line: {line}")
        
        return items


if __name__ == "__main__":
    # Test
    ocr = LedgerOCR()
    print("OCR engine initialized. Test with actual image.")
    # items = ocr.process_ledger('path/to/ledger.jpg')
    # print(f"Extracted items: {items}")
