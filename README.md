# 🛒 Kirana Store Automation - Open Source AI Solution

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen.svg)](https://github.com/Vinay1094/kirana-store-automation)

Complete open-source AI automation system for Kirana (small retail) stores in India. Handles WhatsApp orders in Hinglish, digitizes handwritten inventory ledgers using OCR, checks stock levels, and generates GST-compliant invoices with UPI QR codes.

**Built for Rajesh** and thousands of Kirana store owners across India 🇮🇳

## 🌟 Features

### 1️⃣ WhatsApp Order Automation
- **Hinglish NLP**: Parse mixed Hindi-English orders like "2kg chini 1kg atta 1 lux soap"
- **Real-time Inventory Check**: Instant stock verification
- **Smart Suggestions**: Auto-suggest alternatives for out-of-stock items
- **Automated Replies**: Generate professional responses in customer's language

### 2️⃣ Magic Photo Uploader (OCR)
- **Tesseract OCR** with Hindi + English language support
- **OpenCV Preprocessing**: Handles handwritten ledgers and low-quality images
- **Fuzzy Matching**: Auto-maps recognized items to inventory database
- **Verification UI**: Review and correct OCR results before importing

### 3️⃣ Intelligent Inventory Management
- **SQLite Database**: Lightweight, zero-config database
- **GST Tracking**: Per-item GST rates (0%, 5%, 12%, 18%)
- **Preference Learning**: Remembers Rajesh's favorite brands
- **Multi-unit Support**: kg, g, liters, pieces, packets

### 4️⃣ GST Invoice Generator
- **ReportLab PDF**: Professional invoice layout
- **GST Compliant**: CGST/SGST breakdown, HSN codes
- **UPI QR Code**: Embedded payment QR for instant checkout
- **Downloadable**: Send via WhatsApp or email

### 5️⃣ Self-Hosted WhatsApp Integration
- **Evolution API** or **WAHA** support
- **Webhook Ready**: Real-time message processing
- **No Official API Needed**: Completely free and open-source

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **OCR Engine** | Tesseract + Indic Language Models |
| **Image Processing** | OpenCV |
| **Database** | SQLite |
| **Fuzzy Matching** | RapidFuzz |
| **PDF Generation** | ReportLab |
| **QR Codes** | python-qrcode |
| **NLP (Optional)** | Llama-3 / Mistral via Transformers |
| **WhatsApp API** | Evolution API / WAHA (self-hosted) |
| **Backend** | FastAPI / Flask |

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install Tesseract OCR
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-eng

# macOS
brew install tesseract tesseract-lang

# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### Installation

```bash
# Clone the repository
git clone https://github.com/Vinay1094/kirana-store-automation.git
cd kirana-store-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Demo

```bash
# Run the complete end-to-end demo
python demo.py

# This will:
# 1. Create sample inventory database
# 2. Parse a sample WhatsApp order
# 3. Generate invoice PDF with UPI QR code
# 4. Download invoice_demo.pdf
```

---

## 📚 Documentation

### Project Structure

```
kirana-store-automation/
├── src/
│   ├── database.py           # SQLite inventory management
│   ├── ocr_engine.py         # Tesseract OCR + fuzzy matching
│   ├── order_parser.py       # Hinglish NLP order parsing
│   ├── invoice_generator.py  # GST invoice + UPI QR
│   └── whatsapp_webhook.py   # WhatsApp integration
├── examples/
│   ├── sample_orders.txt
│   ├── sample_ledger.jpg
│   └── demo.py
├── docs/
│   ├── DEPLOYMENT.md
│   ├── WHATSAPP_SETUP.md
│   └── ARCHITECTURE.md
├── requirements.txt
├── README.md
└── LICENSE
```

### Usage Examples

#### 1. Process WhatsApp Order

```python
from src.order_parser import OrderParser
from src.database import InventoryDB

# Initialize
db = InventoryDB()
parser = OrderParser(db)

# Parse Hinglish order
message = "2kg sugar 1kg atta 1 lux soap"
parsed_order = parser.parse_hinglish_order(message)

# Generate reply
reply, billing = parser.generate_reply(parsed_order, "Amit")
print(reply)
```

#### 2. OCR Inventory Ledger

```python
from src.ocr_engine import LedgerOCR
from src.database import InventoryDB

db = InventoryDB()
ocr = LedgerOCR(db)

# Process handwritten ledger
results = ocr.process_ledger("path/to/ledger.jpg")

for item in results:
    print(f"Found: {item['item_name']} - {item['quantity']}{item['unit']}")
```

#### 3. Generate GST Invoice

```python
from src.invoice_generator import GSTInvoiceGenerator

store_details = {
    'name': 'Rajesh Kirana Store',
    'address': 'Shop 12, Main Market, Indore, MP',
    'gstin': '23XXXXX1234X1Z5',
    'phone': '+91-9876543210',
    'upi_id': 'rajesh@paytm'
}

invoice_gen = GSTInvoiceGenerator(store_details)
invoice_gen.create_invoice(order_data, customer_data, 'invoice.pdf')
```

---

## 🌐 Production Deployment

### Option 1: Google Cloud Run (Free Tier)

```bash
# Deploy to GCP
gcloud run deploy kirana-automation \
    --source . \
    --region asia-south1 \
    --allow-unauthenticated
```

### Option 2: Railway.app (Free Tier)

1. Connect GitHub repository
2. Railway auto-detects Python
3. Add environment variables
4. Deploy with one click

### Option 3: Self-Hosted VPS (₹500-1000/month)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Run with Docker Compose
docker-compose up -d
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 💬 WhatsApp Integration

### Using Evolution API

1. **Deploy Evolution API** (Docker-based)
   ```bash
   docker run -d \
     -p 8080:8080 \
     --name evolution-api \
     atendai/evolution-api:latest
   ```

2. **Connect WhatsApp**
   - Scan QR code via Evolution API dashboard
   - Configure webhook to your server

3. **Process Messages**
   ```python
   @app.route('/webhook/whatsapp', methods=['POST'])
   def whatsapp_webhook():
       data = request.json
       # Process with order_parser
       # Send reply via Evolution API
   ```

See [WHATSAPP_SETUP.md](docs/WHATSAPP_SETUP.md) for complete guide.

---

## 📊 Demo & Screenshots

### Sample Order Flow

**Customer Message:**
```
2kg chini 1kg atta 1 lux soap
```

**Automated Reply:**
```
Namaste Customer! 🙏

✅ Available items:
  • Sugar (Madhur) - 2kg @ ₹45/kg = ₹90.00
  • Atta (Aashirvaad) - 1kg @ ₹40/kg = ₹40.00
  • Soap (Lux) - 1piece @ ₹35/piece = ₹35.00

💰 Bill Summary:
Subtotal: ₹165.00
GST: ₹11.55
Total: ₹176.55

Reply 'confirm' to place order! 🙏
```

### Invoice Sample

![Invoice Sample](docs/images/invoice_sample.png)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Vinay Singh** | Databloom AI & Tech

- GitHub: [@Vinay1094](https://github.com/Vinay1094)
- LinkedIn: [Vinay Singh](https://linkedin.com/in/vinay-singh)
- Website: [Databloom AI & Tech](https://databloom.ai)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Vinay1094/kirana-store-automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Vinay1094/kirana-store-automation/discussions)
- **Email**: vinay@databloom.ai

---

## 🚀 Roadmap

- [ ] Multi-language support (Marathi, Gujarati, Tamil)
- [ ] Mobile app (React Native)
- [ ] Cloud sync for inventory
- [ ] Analytics dashboard
- [ ] WhatsApp catalog integration
- [ ] Payment gateway integration
- [ ] Voice order support
- [ ] Multi-store management

---

## 💼 Business Value

**For Kirana Store Owners:**
- Save 2-3 hours daily on manual order processing
- Reduce order errors by 90%
- Professional invoicing at zero cost
- Instant payment collection via UPI

**Pricing for Implementation:**
- Setup: ₹25,000 - ₹50,000 per store
- Monthly: ₹500 - ₹1,000 (hosting only)
- **Training Available**: Contact for Databloom training programs

---

**Made with ❤️ for Bharat's Kirana stores** 🇮🇳
