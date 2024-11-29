import requests
import os
import pycountry

def get_currency_by_country(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())  
        if country:
            currency = pycountry.currencies.get(numeric=country.numeric)
            if currency:
                return currency.alpha_3  
        return "USD"  
    except Exception as e:
        print(f"Error fetching currency for {country_code}: {e}")
        return "USD" 

def get_user_country():
    try:
        geo_api_url = "https://get.geojs.io/v1/ip/geo.json"
        response = requests.get(geo_api_url)
        response.raise_for_status()
        user_data = response.json()
        country_code = user_data.get("country_code", "US")
        currency = get_currency_by_country(country_code)
        return country_code, currency
    except Exception as e:
        print(f"Error fetching user location: {e}")
        return "US", "USD"

def get_conversion_rate(from_currency, to_currency):
    try:
        url = f"https://open.er-api.com/v6/latest/{from_currency}"
        response = requests.get(url)
        response.raise_for_status()
        rates = response.json().get('rates', {})
        return rates.get(to_currency, 1)  
    except Exception as e:
        print(f"Error fetching conversion rate: {e}")
        return 1 

def detect_currency_with_ai(hostname):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (
                    "Determine the currency used for transactions on the following website. "
                    "Respond only with the currency code (e.g., USD, CAD, EUR) and no extra text:\n\n"
                    f"Website hostname: {hostname}"
                ),
            },
        ],
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        ai_response = response.json()
        currency = ai_response['choices'][0]['message']['content'].strip()
        return currency
    except Exception as e:
        print(f"Error detecting currency with AI: {e}")
        return "USD"