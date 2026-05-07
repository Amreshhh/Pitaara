# 💍 Jewellery Price Calculator Backend - Complete Setup

## 📋 Overview

A FastAPI backend service that calculates and compares jewellery prices across 4 major Indian brands:
- **Kalyan** (16% making charges)
- **Malabar** (15% making charges)
- **Senco** (15% making charges)
- **Tanishq** (20% making charges)

The service fetches live product data from MongoDB and performs real-time price calculations including gold value, making charges, wastage, and GST.

---

## 🎯 Quick Start

### 1. Prerequisites
- Python 3.9+
- MongoDB running locally or accessible via connection string
- `pip` package manager

### 2. Installation
```bash
# Clone/Navigate to project
cd connection/

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 3. Start Server
```bash
# Development (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Test API
```bash
# Windows
test_api.bat

# Linux/Mac
bash test_api.sh

# Or access Swagger UI
# Open: http://localhost:8000/docs
```

---

## 📁 Files in This Directory

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application with all endpoints |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variables template |
| `API_GUIDE.md` | Detailed API documentation |
| `IMPLEMENTATION_GUIDE.md` | Implementation details & customization |
| `test_api.bat` | Windows API testing script |
| `test_api.sh` | Linux/Mac API testing script |
| `Jewellery_API_Postman_Collection.json` | Postman collection for API testing |
| `scrapper.py` | Web scraping functionality |
| `vercel.json` | Deployment configuration |

---

## 🚀 Main Endpoint: Calculate Price

### Request
```bash
POST /api/calculate-price
Content-Type: application/json

{
  "weight": 10,
  "purity": "22K",
  "jewellery_type": "Chain",
  "metal_type": "Gold"
}
```

### Response
```json
{
  "status": "success",
  "input_parameters": {
    "weight": 10,
    "purity": "22K",
    "jewellery_type": "Chain",
    "metal_type": "Gold"
  },
  "results": [
    {
      "brand": "Malabar",
      "per_gram_rate": 7000,
      "gold_value": 70000,
      "making_charges": 10500,
      "making_charges_percentage": 15.0,
      "wastage_charges": 350,
      "subtotal": 80850,
      "gst": 324.3,
      "total_estimated_price": 81174.3
    },
    {
      "brand": "Tanishq",
      "per_gram_rate": 7000,
      "gold_value": 70000,
      "making_charges": 14000,
      "making_charges_percentage": 20.0,
      "wastage_charges": 350,
      "subtotal": 84350,
      "gst": 437.4,
      "total_estimated_price": 84787.4
    }
  ],
  "lowest_price_brand": "Malabar",
  "highest_price_brand": "Tanishq"
}
```

---

## 📊 All Available Endpoints

### Info Endpoints
- `GET /` - API documentation
- `GET /api/health` - Health check

### Metadata Endpoints
- `GET /api/categories` - Get all jewellery categories
- `GET /api/purities` - Get all available purities
- `GET /api/brands` - Get all brands
- `GET /api/products/{category}` - Get products by category

### Calculation Endpoint
- `POST /api/calculate-price` - Main price calculation (accepts JSON body)

---

## 🔧 Configuration

### Gold Rate
Currently using placeholder rates. Update in `get_live_gold_rate()` function:

**Current (Placeholder):**
```python
today_rates = {
    "24K": 7500,
    "22K": 7000,
    "18K": 5625,
    "14K": 4092,
    "20K": 6250
}
```

**To use MongoDB rates:**
```python
async def get_live_gold_rate(purity: str) -> float:
    rate_doc = await db.get_collection("live_gold_rates").find_one(
        {"date": datetime.datetime.now().strftime("%Y-%m-%d")}
    )
    return rate_doc["rates"].get(purity, 7000)
```

### Making Charges
Edit `MAKING_CHARGES` dictionary:
```python
MAKING_CHARGES = {
    "Kalyan": 16.0,    # Change these percentages
    "Malabar": 15.0,
    "Senco": 15.0,
    "Tanishq": 20.0
}
```

### Wastage & GST
```python
WASTAGE_PERCENTAGE = 0.5   # 0.5% of gold value
GST_PERCENTAGE = 3.0       # 3% on making + wastage
```

---

## 🧪 Testing

### Method 1: Postman
1. Import `Jewellery_API_Postman_Collection.json` into Postman
2. Set `base_url` variable to `http://localhost:8000`
3. Run pre-built requests

### Method 2: Swagger UI
Visit: `http://localhost:8000/docs` (interactive API explorer)

### Method 3: cURL Script
```bash
# Windows
test_api.bat

# Linux/Mac
bash test_api.sh
```

### Method 4: Manual cURL
```bash
curl -X POST http://localhost:8000/api/calculate-price \
  -H "Content-Type: application/json" \
  -d '{"weight":10,"purity":"22K","jewellery_type":"Chain","metal_type":"Gold"}'
```

---

## 📦 Pydantic Models

### CalculatorRequest (What frontend sends)
```python
{
    "weight": float,           # grams (required, > 0)
    "purity": str,             # "22K", "18K", "14K", "24K", "20K"
    "jewellery_type": str,     # category name
    "metal_type": str          # "Gold" (default)
}
```

### PriceBreakdown (Per brand result)
```python
{
    "brand": str,
    "per_gram_rate": float,
    "gold_value": float,
    "making_charges": float,
    "making_charges_percentage": float,
    "wastage_charges": float,
    "subtotal": float,
    "gst": float,
    "total_estimated_price": float
}
```

### CalculatorResponse (API response)
```python
{
    "status": str,                          # "success"
    "input_parameters": dict,               # Echo of request
    "results": List[PriceBreakdown],        # Sorted by price
    "lowest_price_brand": str,
    "highest_price_brand": str
}
```

---

## 🔗 Database Connection

### MongoDB Collections
```
jewelry_database/
├── kalyan_products
├── malabar_products
├── senco_products
└── tanishq_products
```

### Document Structure
```json
{
  "_id": ObjectId,
  "Brand": "Kalyan",
  "product_url": "https://...",
  "sku": "12345",
  "type": "Gold Jewelry",
  "purity": "22K",
  "net_weight": 3.5,
  "making_charges_percentage": "16%",
  "category": "Chain",
  "extraction_date": "2026-04-29 12:24:55"
}
```

### Environment Variables
```bash
MONGODB_URI=mongodb://localhost:27017
```

---

## 🎨 Frontend Integration

### React Example
```javascript
import { useState, useEffect } from 'react';

export function JewelleryCalculator() {
  const [weight, setWeight] = useState(10);
  const [purity, setPurity] = useState('22K');
  const [category, setCategory] = useState('Chain');
  const [results, setResults] = useState(null);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    // Load categories on mount
    fetch('http://localhost:8000/api/categories')
      .then(r => r.json())
      .then(data => setCategories(data.categories));
  }, []);

  const calculatePrice = async () => {
    const response = await fetch('http://localhost:8000/api/calculate-price', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        weight: parseFloat(weight),
        purity: purity,
        jewellery_type: category,
        metal_type: 'Gold'
      })
    });
    const data = await response.json();
    setResults(data);
  };

  return (
    <div>
      <input type="number" value={weight} onChange={(e) => setWeight(e.target.value)} />
      <select value={purity} onChange={(e) => setPurity(e.target.value)}>
        <option value="22K">22K</option>
        <option value="18K">18K</option>
        <option value="14K">14K</option>
      </select>
      <select value={category} onChange={(e) => setCategory(e.target.value)}>
        {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
      </select>
      <button onClick={calculatePrice}>Calculate</button>

      {results && (
        <div>
          {results.results.map(brand => (
            <div key={brand.brand}>
              <h3>{brand.brand}</h3>
              <p>Gold Value: ₹{brand.gold_value}</p>
              <p>Making: ₹{brand.making_charges}</p>
              <p>Total: ₹{brand.total_estimated_price}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Next.js Example
```javascript
// pages/api/calculate.js
export default async function handler(req, res) {
  if (req.method === 'POST') {
    const response = await fetch('http://localhost:8000/api/calculate-price', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    const data = await response.json();
    res.status(200).json(data);
  }
}

// In component:
const result = await fetch('/api/calculate', {
  method: 'POST',
  body: JSON.stringify({ weight: 10, purity: '22K', jewellery_type: 'Chain' })
}).then(r => r.json());
```

---

## 🐛 Troubleshooting

### "Connection refused" / MongoDB Error
```bash
# Check if MongoDB is running
mongod

# Verify connection string in .env
MONGODB_URI=mongodb://localhost:27017
```

### "No products found"
1. Check MongoDB collections exist:
   ```bash
   mongo
   > use jewelry_database
   > db.kalyan_products.count()
   ```
2. Verify documents have `category` and `purity` fields
3. Test with `GET /api/categories` to see available categories

### "Invalid purity"
- Only these purities are supported: 22K, 18K, 14K, 24K, 20K
- Update `get_live_gold_rate()` if you add more purities

### CORS Issues (Frontend)
Add CORS middleware to `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📈 Performance Notes

- **Caching**: Categories and purities rarely change - consider caching responses
- **Pagination**: For large product searches, add limit/offset parameters
- **Indexing**: Add MongoDB indexes on `category` and `purity` fields:
  ```javascript
  db.kalyan_products.createIndex({ "category": 1 });
  db.kalyan_products.createIndex({ "purity": 1 });
  ```

---

## 🚢 Deployment

### Vercel (Serverless)
```bash
# Uses vercel.json configuration
vercel deploy
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

---

## 📚 Documentation Files

- **API_GUIDE.md** - Complete endpoint documentation with examples
- **IMPLEMENTATION_GUIDE.md** - Architecture, calculation formulas, customization options

---

## 🤝 Support

### Common Issues
See IMPLEMENTATION_GUIDE.md > Troubleshooting section

### API Response Codes
- `200` - Success
- `400` - Invalid input
- `404` - No products found
- `500` - Server error
- `503` - Database connection failed

---

## 📞 Version Info

- **FastAPI**: 0.136.1
- **Motor**: 3.7.1 (Async MongoDB)
- **Pydantic**: 2.13.3
- **Python**: 3.9+

---

## 🎯 Next Steps

1. ✅ Start server: `uvicorn main:app --reload`
2. ✅ Test endpoints: Open `http://localhost:8000/docs`
3. ✅ Customize gold rates in `get_live_gold_rate()`
4. ✅ Integrate with frontend
5. ✅ Deploy to production

---

**Ready to calculate jewellery prices! 💎**
