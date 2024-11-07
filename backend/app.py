from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers.specs_scraper import get_html_content, extract_relevant_html, scrape_specs_from_html, parse_parts_and_prices
from models.database import insert_comparison
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

frontend_url = os.getenv('FRONTEND_URL') or '*'

def handle_options_request():
    
    response = jsonify({'status': 'OK'})
    response.headers["Access-Control-Allow-Origin"] = frontend_url or "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Authorization, X-Content-Type-Options, Accept, X-Requested-With, Origin, "
        "Access-Control-Request-Method, Access-Control-Request-Headers"
    )
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "7200"
    return response

def detect_browser(user_agent):
    if "Chrome" in user_agent and "Edg" not in user_agent:
        return "chrome"
    elif "Firefox" in user_agent:
        return "firefox"
    elif "Edg" in user_agent:
        return "edge"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        return "safari"
    else:
        return "chrome" 

@app.route('/api/scrape', methods=['POST', 'OPTIONS'])
def scrape():
    if request.method == 'OPTIONS': 
        return handle_options_request()

    if request.method == 'POST':
        data = request.json
        url = data.get('url')
        user_agent = data.get('userAgent')

        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        browser = detect_browser(user_agent)

        html_content, error = get_html_content(url)
        if error:
            return jsonify({"error": error}), 400

        prebuilt_price, cleaned_html_content = extract_relevant_html(html_content)

        parts_text = scrape_specs_from_html(cleaned_html_content)
        if not parts_text:
            return jsonify({"error": "Failed to extract parts and prices"}), 500

        prebuilt_name, parts = parse_parts_and_prices(parts_text, browser)
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