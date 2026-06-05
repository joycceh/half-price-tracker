import requests
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
PRODUCTS_FILE = "products.json"

def load_products():
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

def save_products(data):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_woolworths_price(url):
    try:
        # clean URL - strip tracking params
        clean_url = url.split("?")[0]
        stockcode = clean_url.split("/productdetails/")[1].split("/")[0]

        api_url = f"https://www.woolworths.com.au/apis/ui/product/detail/{stockcode}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-AU,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.woolworths.com.au/",
            "Origin": "https://www.woolworths.com.au",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }

        session = requests.Session()
        # first visit homepage to get cookies
        session.get("https://www.woolworths.com.au", headers=headers, timeout=10)
        # then fetch the product
        resp = session.get(api_url, headers=headers, timeout=15)
        data = resp.json()
        product = data.get("Product", {})
        return {
            "name": product.get("Name"),
            "price": product.get("Price"),
            "was_price": product.get("WasPrice"),
        }
    except Exception as e:
        print(f"Woolworths error: {e}")
        return None

def get_coles_price(url):
    try:
        clean_url = url.split("?")[0]
        slug = clean_url.split("/product/")[1].split("/")[0]
        api_url = f"https://www.coles.com.au/api/2.0.0/page/products/{slug}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-AU,en;q=0.9",
            "Referer": "https://www.coles.com.au/",
            "Origin": "https://www.coles.com.au",
        }

        session = requests.Session()
        # first visit homepage to get cookies
        session.get("https://www.coles.com.au", headers=headers, timeout=10)
        # then fetch the product
        resp = session.get(api_url, headers=headers, timeout=15)
        data = resp.json()
        pricing = data.get("pricing", {})
        return {
            "name": data.get("name"),
            "price": pricing.get("now"),
            "was_price": pricing.get("was"),
        }
    except Exception as e:
        print(f"Coles error: {e}")
        return None

def is_half_price(price, was_price):
    if not price or not was_price:
        return False
    discount = (1 - float(price) / float(was_price)) * 100
    return 45 <= discount <= 55

def send_email(alert_email, hits):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔥 {len(hits)} item(s) are HALF PRICE!"
        msg["From"] = EMAIL
        msg["To"] = alert_email

        items_html = ""
        for hit in hits:
            items_html += f"""
            <tr>
                <td style="padding:12px;">{hit['name']}</td>
                <td style="padding:12px;color:#e65100;font-weight:bold;">${hit['price']}</td>
                <td style="padding:12px;text-decoration:line-through;color:#aaa;">${hit['was_price']}</td>
                <td style="padding:12px;"><a href="{hit['url']}">View →</a></td>
            </tr>
            """

        html = f"""
        <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;">
            <h2>🏷️ Half Price Tracker</h2>
            <p>{len(hits)} item(s) on your watchlist are half price right now!</p>
            <table style="width:100%;border-collapse:collapse;border:1px solid #eee;">
                <thead>
                    <tr style="background:#f5f5f5;">
                        <th style="padding:12px;text-align:left;">Product</th>
                        <th style="padding:12px;text-align:left;">Now</th>
                        <th style="padding:12px;text-align:left;">Was</th>
                        <th style="padding:12px;text-align:left;">Link</th>
                    </tr>
                </thead>
                <tbody>{items_html}</tbody>
            </table>
        </body></html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, alert_email, msg.as_string())

        print(f"✅ Alert sent to {alert_email}")
    except Exception as e:
        print(f"Email error: {e}")

def check_prices():
    data = load_products()
    products = data.get("products", [])
    alert_email = data.get("alert_email", EMAIL)
    hits = []

    if not products:
        print("No products in watchlist")
        return

    for item in products:
        url = item["url"]
        print(f"Checking {url}...")

        if "woolworths.com.au" in url:
            result = get_woolworths_price(url)
        elif "coles.com.au" in url:
            result = get_coles_price(url)
        else:
            print("  Unknown store, skipping")
            continue

        if result:
            print(f"  {result['name']} — ${result['price']} (was ${result['was_price']})")
            if is_half_price(result["price"], result["was_price"]):
                print(f"  🔥 HALF PRICE!")
                hits.append({**result, "url": url})
            else:
                print(f"  Not on half price sale")
        else:
            print(f"  Could not fetch price")

    if hits:
        send_email(alert_email, hits)
    else:
        print("No half price items found")

if __name__ == "__main__":
    check_prices()