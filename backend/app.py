from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers.specs_scraper import get_html_content, extract_relevant_html, scrape_specs_from_html, parse_parts_and_prices
from models.database import insert_comparison
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

frontend_url = os.getenv('FRONTEND_URL') or '*'

@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        response = app.make_response(('OK', 204))
        response.headers["Access-Control-Allow-Origin"] = frontend_url or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Content-Type-Options, Accept, X-Requested-With, Origin, "
            "Access-Control-Request-Method, Access-Control-Request-Headers"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "7200"
        return response

@app.route('/api/scrape', methods=['POST'])
def scrape():
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
        return jsonify({"error": "Failed to extract parts and prices"}), 500

    prebuilt_name, parts = parse_parts_and_prices(parts_text)
    if not prebuilt_name or not prebuilt_price or not parts:
        return jsonify({"error": "Failed to extract valid parts, prebuilt name, or prebuilt price"}), 400

    total_parts_price = sum([part['price'] for part in parts])
    difference = prebuilt_price - total_parts_price

    # insert_comparison(url, prebuilt_price, total_parts_price, difference, parts)

    response = jsonify({
        "prebuilt_name": prebuilt_name,
        "prebuilt_price": prebuilt_price,
        "parts": parts,
        "total_parts_price": total_parts_price,
        "price_difference": difference
    })

    response.headers["Access-Control-Allow-Origin"] = frontend_url or "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))