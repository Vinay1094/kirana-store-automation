"""Order Parser Module - Hinglish NLP Order Processing

Parses Hinglish (Hindi + English) WhatsApp order messages and extracts
structured order data with items, quantities, and units.
"""

import re
import logging
from typing import List, Dict, Optional
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)


class OrderParser:
    """Hinglish order text parser with fuzzy matching"""
    
    # Common Hindi/Hinglish units and their standardized forms
    UNIT_MAPPINGS = {
        # Weight
        'kg': 'kg', 'kilo': 'kg', 'किलो': 'kg', 'keelo': 'kg',
        'gm': 'gm', 'gram': 'gm', 'ग्राम': 'gm',
        # Volume
        'litre': 'litre', 'liter': 'litre', 'लीटर': 'litre', 'l': 'litre',
        'ml': 'ml', 'millilitre': 'ml',
        # Count
        'piece': 'piece', 'pcs': 'piece', 'pc': 'piece', 'पीस': 'piece',
        'packet': 'packet', 'pkt': 'packet', 'पैकेट': 'packet',
        'bottle': 'bottle', 'बोतल': 'bottle',
        'box': 'box', 'बॉक्स': 'box',
        'dozen': 'dozen', 'दर्जन': 'dozen',
    }
    
    # Common product name variations
    PRODUCT_ALIASES = {
        'atta': ['aata', 'आटा', 'flour'],
        'milk': ['doodh', 'दूध'],
        'rice': ['chawal', 'चावल'],
        'sugar': ['cheeni', 'चीनी'],
        'oil': ['tel', 'तेल'],
        'dal': ['daal', 'दाल', 'lentils'],
        'salt': ['namak', 'नमक'],
        'tea': ['chai', 'चाय'],
        'biscuit': ['biskut', 'बिस्कुट'],
    }
    
    def __init__(self):
        """Initialize order parser"""
        self.known_products = list(self.PRODUCT_ALIASES.keys())
        logger.info("Order parser initialized")
    
    def normalize_unit(self, unit_text: str) -> str:
        """
        Normalize unit text to standard form
        
        Args:
            unit_text: Raw unit string
        
        Returns:
            Standardized unit
        """
        unit_lower = unit_text.lower().strip()
        return self.UNIT_MAPPINGS.get(unit_lower, unit_lower)
    
    def fuzzy_match_product(self, product_text: str, threshold: int = 70) -> Optional[str]:
        """
        Fuzzy match product name to known products
        
        Args:
            product_text: Raw product name
            threshold: Minimum similarity score (0-100)
        
        Returns:
            Matched product name or None
        """
        product_lower = product_text.lower().strip()
        
        # Check aliases
        for standard_name, aliases in self.PRODUCT_ALIASES.items():
            for alias in aliases:
                if fuzz.ratio(product_lower, alias) >= threshold:
                    return standard_name
        
        # Check known products directly
        match = process.extractOne(
            product_lower,
            self.known_products,
            scorer=fuzz.ratio,
            score_cutoff=threshold
        )
        
        if match:
            return match[0]
        
        # Return original if no match (allow new products)
        return product_text.lower()
    
    def parse_hinglish_order(self, order_text: str) -> Dict:
        """
        Parse Hinglish order text into structured data
        
        Args:
            order_text: Raw order message
        
        Returns:
            Parsed order dict with items list
        """
        logger.info(f"Parsing order: {order_text}")
        
        # Patterns to match:
        # - "2 kg atta"
        # - "1 litre milk"
        # - "500 gm sugar"
        # - "5 packet biscuit"
        
        # Regex pattern: number + optional unit + product name
        pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z\u0900-\u097F]+)?\s+([a-zA-Z\u0900-\u097F]+(?:\s+[a-zA-Z\u0900-\u097F]+)*)'
        
        matches = re.findall(pattern, order_text, re.IGNORECASE)
        
        items = []
        for match in matches:
            quantity_str, unit_str, product_str = match
            
            try:
                quantity = float(quantity_str)
            except ValueError:
                logger.warning(f"Invalid quantity: {quantity_str}")
                continue
            
            # If no unit provided, assume common defaults
            if not unit_str or unit_str.lower() in ['kg', 'litre', 'piece', 'packet']:
                unit = self.normalize_unit(unit_str) if unit_str else 'piece'
            else:
                # Unit might be part of product name
                product_str = f"{unit_str} {product_str}"
                unit = 'piece'
            
            # Fuzzy match product
            product = self.fuzzy_match_product(product_str)
            
            items.append({
                'name': product,
                'quantity': quantity,
                'unit': unit,
                'original_text': f"{quantity_str} {unit_str} {product_str}".strip()
            })
            
            logger.info(f"Parsed item: {quantity} {unit} {product}")
        
        return {
            'items': items,
            'original_text': order_text,
            'total_items': len(items)
        }
    
    def generate_reply(self, parsed_order: Dict, customer_name: str) -> str:
        """
        Generate confirmation reply message
        
        Args:
            parsed_order: Parsed order dict
            customer_name: Customer name
        
        Returns:
            Reply text
        """
        if not parsed_order or not parsed_order.get('items'):
            return f"Sorry {customer_name}, I couldn't understand your order. Please try again."
        
        items = parsed_order['items']
        
        # Build order summary
        summary_lines = [f"Thank you {customer_name}! Your order:"]
        
        for idx, item in enumerate(items, 1):
            summary_lines.append(
                f"{idx}. {item['quantity']} {item['unit']} {item['name'].title()}"
            )
        
        summary_lines.append("\nYour order is confirmed! ✅")
        summary_lines.append("We'll prepare it right away.")
        
        return "\n".join(summary_lines)


# Example usage
if __name__ == "__main__":
    parser = OrderParser()
    
    # Test cases
    test_orders = [
        "2 kg atta aur 1 litre milk chahiye",
        "5 packet biscuit and 500 gm sugar",
        "1 kg chawal, 2 litre doodh",
        "10 piece bread and 1 bottle oil"
    ]
    
    for order_text in test_orders:
        print(f"\n\nOrder: {order_text}")
        parsed = parser.parse_hinglish_order(order_text)
        print(f"Parsed: {parsed}")
        reply = parser.generate_reply(parsed, "Rajesh")
        print(f"Reply: {reply}")
