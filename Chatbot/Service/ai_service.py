import json
from openai import OpenAI
from config import settings
from services.product_service import get_allowed_products

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def extract_keywords(story: str):
    keywords = []
    for word in [
        "car", "driving", "automotive", "vehicle", "drive", "sport", "game", "phone", "laptop", "toy",
        "console", "controller", "gamer", "joystick", "pc gaming", "playstation", "xbox", "nintendo", "steam",
        "mouse", "keyboard", "monitor", "headset", "VR", "virtual reality",
        "mobile", "mobilephone", "smartphone", "android", "iphone", "cellphone", "ios",
        "samsung", "galaxy", "xiaomi", "oneplus", "oppo", "vivo", "huawei", "apple",
        "notebook", "ultrabook", "macbook", "chromebook", "windows laptop", "business laptop", "gaming laptop",
        "asus", "hp", "dell", "lenovo", "acer", "msi", "surface",
        "earbud", "earbuds", "headphone", "headphones", "bluetooth", "noise cancelling"
    ]:
        if word in story.lower():
            keywords.append(word)
    return keywords

async def generate_ai_response(user_query: str):
    allowed_products = await get_allowed_products(limit=10)
    catalog = json.dumps([
        {
            "short_title": p.get("short_title"),
            "long_title": p.get("long_title"),
            "description": p.get("description"),
            "category": p.get("category"),
            "price": p.get("price"),
            "stock": p.get("stock"),
            "brand": p.get("brand"),
            "discountPercentage": p.get("discountPercentage"),
        } for p in allowed_products
    ], indent=2, ensure_ascii=False)

    prompt = f"Your prompt including catalog and query: \nCatalog:\n{catalog}\nUser: {user_query}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()