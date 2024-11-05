from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from scrapers.specs_scraper import get_html_content, extract_relevant_html, scrape_specs_from_html, parse_parts_and_prices
from models.database import insert_comparison
from dotenv import load_dotenv
import os

load_dotenv()


def crossdomain(origin='*', methods=None, headers=None):
    if methods is None:
        methods = ['GET', 'POST', 'PUT', 'DELETE']
    if headers is None:
        headers = ['Content-Type', 'Authorization']

    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            response = f(*args, **kwargs)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = ', '.join(methods)
            response.headers['Access-Control-Allow-Headers'] = ', '.join(headers)
            return response

        return wrapped_function
    return decorator

app = Flask(__name__)

CORS(app)

@app.route('/api/scrape', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def scrape():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    html_content, error = get_html_content(url)
    if error:
        return jsonify({"error": error}), 400

    prebuilt_price, cleaned_html_content = extract_relevant_html(html_content)

    parts_text = scrape_specs_from_html(cleaned_html_content)
    if not parts_text:
        return jsonify({"error": "Failed to extract parts and prices from Groq"}), 500

    prebuilt_name, parts = parse_parts_and_prices(parts_text)
    if not prebuilt_name or not prebuilt_price or not parts:
        return jsonify({"error": "Failed to extract valid parts, prebuilt name, or prebuilt price"}), 400

    total_parts_price = sum([part['price'] for part in parts])
    difference = prebuilt_price - total_parts_price

    #insert_comparison(url, prebuilt_price, total_parts_price, difference, parts) Saves it to the database

    return jsonify({
        "prebuilt_name": prebuilt_name,
        "prebuilt_price": prebuilt_price,
        "parts": parts,
        "total_parts_price": total_parts_price,
        "price_difference": difference
    }), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))