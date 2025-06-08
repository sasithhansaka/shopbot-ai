# 🛍️ AI-Powered Customer Support Chatbot – ShopBot AI

A FastAPI-based backend chatbot that integrates with OpenAI to provide intelligent customer support responses for an e-commerce platform. MongoDB is used for storing product data, and the chatbot can understand user queries and reply with relevant product or support information.

## 📁 Folder Structure

```
chatbot/
│
├── Routers/
│   └── routes.py          # API route for chatbot interaction
│
├── models/
│   └── model.py        # Pydantic models (e.g., ChatRequest)
|
├── Service/
│   └── ai_service.py
│   └── product_service.py
│
├── .env                   # Environment variables
├── .gitignore
├── config.py                # FastAPI app entry point
├── main.py                # FastAPI app entry point
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/sasithhansaka/shopbot-ai.git
cd chatbot
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Update the `.env` file

```env
OPENAI_API_KEY="your-openai-api-key"
SITE_URL="https://your-ecommerce.com"
SITE_NAME="MyEcommerce"
MONGODB_URI="your-mongodb-uri"
MONGO_DB_NAME="e_commerce"
MONGO_COLLECTION_NAME="products"
```

## ▶️ Run the App

```bash
uvicorn main:app --reload
```

The API will be available at:  
`http://127.0.0.1:8000`

## 📨 API Endpoint

### POST `/chat`

Send a message to the chatbot.

#### ✅ Request Body (JSON):

```json
{
  "message": "Do you have any Apple ipone is available?",
}
```

#### 🔁 Response:

```json
{
  "response": "there is an Apple product available. The \"Apple iPhone 15\" is in stock and ready for purchase. Here are the details:\n\n- Product Name: Apple iPhone 15\n- Price: $289,900\n- Stock: 39\n- Brand: Apple\n- Discount Percentage: 5%\n\nIf you need more information or assistance with this product or any other product from the catalog, feel free to ask!"
}
```

## 🧠 Features

- 💬 Chat with an AI-powered assistant
- 📦 Product info sourced from MongoDB
- 🤖 Powered by OpenAI GPT
- 🧑 Includes user details for personalized responses
- 🚀 FastAPI framework for quick API development

## 🧪 Testing with Postman

1. Open Postman
2. Set method to `POST`
3. URL: `http://localhost:8000/chat`
4. Headers:
   - `Content-Type: application/json`
5. Body (JSON):

```json
{
  "message": "Do you have any Apple ipone is available?",
}
```

## 📌 Dependencies

See `requirements.txt`:

```txt
fastapi
uvicorn
openai
motor
pydantic
python-dotenv
```

