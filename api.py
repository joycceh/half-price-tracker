from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from tracker import check_prices

app = Flask(__name__)
CORS(app)

PRODUCTS_FILE = "products.json"

def load_products():
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

def save_products(data):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Get all watched products ──────────────────────────────────────────────────
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(load_products())

# ── Add a product ─────────────────────────────────────────────────────────────
@app.route("/products", methods=["POST"])
def add_product():
    body = request.json
    url = body.get("url", "").strip()

    if not url:
        return jsonify({"error": "No URL provided"}), 400
    if "woolworths.com.au" not in url and "coles.com.au" not in url:
        return jsonify({"error": "Only Woolworths and Coles URLs are supported"}), 400

    data = load_products()
    urls = [p["url"] for p in data["products"]]
    if url in urls:
        return jsonify({"error": "Product already in watchlist"}), 400

    data["products"].append({"url": url})
    save_products(data)
    return jsonify({"success": True})

# ── Remove a product ──────────────────────────────────────────────────────────
@app.route("/products", methods=["DELETE"])
def remove_product():
    body = request.json
    url = body.get("url", "").strip()

    data = load_products()
    data["products"] = [p for p in data["products"] if p["url"] != url]
    save_products(data)
    return jsonify({"success": True})

# ── Update alert email ────────────────────────────────────────────────────────
@app.route("/alert-email", methods=["POST"])
def set_alert_email():
    body = request.json
    email = body.get("email", "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "Invalid email"}), 400

    data = load_products()
    data["alert_email"] = email
    save_products(data)
    return jsonify({"success": True})

# ── Manually trigger a price check ───────────────────────────────────────────
@app.route("/check", methods=["POST"])
def manual_check():
    check_prices()
    return jsonify({"success": True, "message": "Price check complete!"})

if __name__ == "__main__":
    app.run(port=5001, debug=True)