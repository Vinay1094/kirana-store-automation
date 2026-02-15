"""Kirana Store Automation - Source Package

Core modules for Kirana store automation system.
"""

__version__ = "0.1.0"

from .database import InventoryDB
from .order_parser import OrderParser

try:
    from .invoice_generator import GSTInvoiceGenerator
except ImportError:
    GSTInvoiceGenerator = None

try:
    from .ocr_engine import LedgerOCR
except ImportError:
    LedgerOCR = None

__all__ = [
    "InventoryDB",
    "OrderParser",
    "GSTInvoiceGenerator",
    "LedgerOCR",
]
