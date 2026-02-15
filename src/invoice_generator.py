"""Invoice Generator - GST Invoice with UPI QR Code

Generates PDF invoices with GST calculations and UPI QR codes.
"""

import logging
from datetime import datetime
from typing import Dict, List
import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    import qrcode
    from io import BytesIO
except ImportError:
    logging.warning("ReportLab or qrcode not installed. Invoice generation will not work.")

logger = logging.getLogger(__name__)


class GSTInvoiceGenerator:
    """Generate GST-compliant invoices with UPI payment QR codes"""
    
    def __init__(self, store_name="Rajesh Kirana Store", store_gstin="", upi_id="rajesh@upi"):
        self.store_name = store_name
        self.store_gstin = store_gstin
        self.upi_id = upi_id
    
    def create_invoice(self, order_data: Dict, customer_data: Dict, output_path: str):
        """
        Create GST invoice PDF
        
        Args:
            order_data: Dict with 'items' list
            customer_data: Dict with 'name', 'phone'
            output_path: Path to save PDF
        """
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, self.store_name)
        
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, height - 1.3*inch, f"GSTIN: {self.store_gstin or 'Not Registered'}")
        c.drawString(1*inch, height - 1.5*inch, f"Date: {datetime.now().strftime('%d-%m-%Y')}")
        
        # Customer details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, height - 2*inch, "Bill To:")
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, height - 2.3*inch, customer_data.get('name', 'Customer'))
        c.drawString(1*inch, height - 2.5*inch, f"Phone: {customer_data.get('phone', 'N/A')}")
        
        # Items table
        y = height - 3.5*inch
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, y, "Item")
        c.drawString(3*inch, y, "Qty")
        c.drawString(4*inch, y, "Rate")
        c.drawString(5*inch, y, "Amount")
        
        y -= 0.3*inch
        c.setFont("Helvetica", 10)
        
        total = 0
        for item in order_data.get('items', []):
            name = item.get('name', 'Item')
            qty = item.get('quantity', 0)
            rate = item.get('price', 50)  # Default price
            amount = qty * rate
            total += amount
            
            c.drawString(1*inch, y, f"{name} ({item.get('unit', 'unit')})")
            c.drawString(3*inch, y, str(qty))
            c.drawString(4*inch, y, f"₹{rate:.2f}")
            c.drawString(5*inch, y, f"₹{amount:.2f}")
            y -= 0.25*inch
        
        # Total
        y -= 0.3*inch
        c.line(1*inch, y, 6*inch, y)
        y -= 0.3*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(4*inch, y, "Total:")
        c.drawString(5*inch, y, f"₹{total:.2f}")
        
        # UPI QR Code
        try:
            upi_string = f"upi://pay?pa={self.upi_id}&pn={self.store_name}&am={total}&cu=INR"
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(upi_string)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            c.drawString(1*inch, 2*inch, "Scan to Pay:")
            c.drawInlineImage(img_buffer, 1*inch, 0.5*inch, width=1.5*inch, height=1.5*inch)
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
        
        c.save()
        logger.info(f"Invoice saved to {output_path}")
        return output_path


if __name__ == "__main__":
    # Test
    gen = GSTInvoiceGenerator()
    order = {
        'items': [
            {'name': 'atta', 'quantity': 2, 'unit': 'kg', 'price': 45},
            {'name': 'milk', 'quantity': 1, 'unit': 'litre', 'price': 60}
        ]
    }
    customer = {'name': 'Test Customer', 'phone': '9876543210'}
    gen.create_invoice(order, customer, 'test_invoice.pdf')
    print("Test invoice generated!")
