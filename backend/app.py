from flask import Flask, request, jsonify
from scrapers.specs_scraper import get_html_content, extract_relevant_html, scrape_specs_from_html, parse_parts_and_prices
from models.database import insert_comparison

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
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
    app.run(debug=True)