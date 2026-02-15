"""FastAPI App - Kirana Store Automation WhatsApp Webhook

This module provides the main API server for handling WhatsApp webhooks,
processing Hinglish orders, and managing inventory interactions.

Endpoints:
    GET /health - Health check
    POST /webhook/whatsapp - Process incoming WhatsApp orders
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime

# Import core modules (to be created)
try:
    from src.database import InventoryDB
    from src.order_parser import OrderParser
    from src.invoice_generator import GSTInvoiceGenerator
except ImportError:
    # Graceful fallback for development
    InventoryDB = None
    OrderParser = None
    GSTInvoiceGenerator = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Kirana Store Automation API",
    description="WhatsApp order automation with OCR inventory & GST invoicing",
    version="0.1.0"
)

# Initialize core components
db = InventoryDB() if InventoryDB else None
order_parser = OrderParser() if OrderParser else None
invoice_gen = GSTInvoiceGenerator() if GSTInvoiceGenerator else None


class WhatsAppMessage(BaseModel):
    """WhatsApp incoming message model"""
    message: str
    customer_name: str
    customer_phone: Optional[str] = None
    timestamp: Optional[str] = None


class OrderResponse(BaseModel):
    """Order processing response model"""
    success: bool
    reply_text: str
    order_id: Optional[str] = None
    invoice_path: Optional[str] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Kirana Store Automation",
        "version": "0.1.0",
        "status": "active",
        "endpoints": ["/health", "/webhook/whatsapp"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db is not None,
            "order_parser": order_parser is not None,
            "invoice_generator": invoice_gen is not None
        }
    }


@app.post("/webhook/whatsapp", response_model=OrderResponse)
async def process_whatsapp_order(message: WhatsAppMessage):
    """
    Process incoming WhatsApp order message
    
    Args:
        message: WhatsAppMessage with customer details and order text
    
    Returns:
        OrderResponse with reply text and order details
    """
    try:
        logger.info(f"Processing order from {message.customer_name}: {message.message}")
        
        # Validate components are loaded
        if not all([db, order_parser, invoice_gen]):
            return OrderResponse(
                success=False,
                reply_text="System initialization in progress. Please try again.",
                error="Core components not initialized"
            )
        
        # Parse Hinglish order
        parsed_order = order_parser.parse_hinglish_order(message.message)
        
        if not parsed_order or not parsed_order.get("items"):
            return OrderResponse(
                success=False,
                reply_text="Sorry, I couldn't understand the order. Please specify items and quantities.\n\nExample: '2 kg atta, 1 litre milk'",
                error="Failed to parse order"
            )
        
        # Check inventory availability
        unavailable_items = []
        available_items = []
        
        for item in parsed_order["items"]:
            db_item = db.get_item_by_name(item["name"])
            if db_item and db_item["stock"] >= item["quantity"]:
                available_items.append(item)
            else:
                unavailable_items.append(item["name"])
        
        # Generate reply
        if unavailable_items:
            reply = f"Sorry {message.customer_name}, these items are out of stock: {', '.join(unavailable_items)}\n\n"
            if available_items:
                reply += f"Available items: {', '.join([f"{i['quantity']} {i['unit']} {i['name']}" for i in available_items])}"
            else:
                reply += "Please try ordering other items."
            
            return OrderResponse(
                success=False,
                reply_text=reply,
                error="Some items unavailable"
            )
        
        # Generate invoice
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        invoice_path = f"invoices/{order_id}.pdf"
        
        invoice_gen.create_invoice(
            order_data=parsed_order,
            customer_data={
                "name": message.customer_name,
                "phone": message.customer_phone
            },
            output_path=invoice_path
        )
        
        # Update inventory
        for item in available_items:
            db.update_stock(item["name"], -item["quantity"])
        
        # Generate confirmation reply
        reply = order_parser.generate_reply(parsed_order, message.customer_name)
        
        logger.info(f"Order {order_id} processed successfully")
        
        return OrderResponse(
            success=True,
            reply_text=reply,
            order_id=order_id,
            invoice_path=invoice_path
        )
    
    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        return OrderResponse(
            success=False,
            reply_text=f"Sorry {message.customer_name}, there was an error processing your order. Please try again.",
            error=str(e)
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
