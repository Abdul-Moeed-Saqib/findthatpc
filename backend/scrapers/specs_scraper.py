import requests
import re
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# This function gets the html content
def get_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch page content. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page content: {e}")
        return None

# This function gets the relevvant content of the page and the price of the prebuilt pc
def extract_relevant_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    possible_price_elements = soup.find_all(text=lambda text: "CAD $" in text or "$" in text)

    prebuilt_price = None

    for element in possible_price_elements:
        try:
            price_text = element.strip().replace("CAD", "").replace("$", "").replace(",", "").strip()
            prebuilt_price = float(price_text) 

            if prebuilt_price:
                break
        except ValueError:
            continue  

    return prebuilt_price, str(soup)[:5000] 

# This function requests to an AI from GroqCloud to find the parts of the prebuilt pc
def scrape_specs_from_html(cleaned_html_content):
    groq_api_key = os.getenv('GROQ_API_KEY')

    headers = {
        'Authorization': 'Bearer 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',  
        'Content-Type': 'application/json'
    }

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are an AI that extracts computer parts, their names, types, and the prebuilt PC name from HTML."},
            {"role": "user", "content": f"Extract the **names and types** of computer parts from this HTML content. For example, CPU: Intel Core i9, GPU: NVIDIA RTX 3080. Return also the prebuilt PC name as 'Prebuilt Name: XYZ PC'. Here is the HTML: {cleaned_html_content}"}
        ]
    }

    response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        try:
            result = response.json()
            parts_text = result['choices'][0]['message']['content']
            return parts_text
        except (ValueError, KeyError):
            print("Error processing Groq response")
            return None
    else:
        print(f"Failed to fetch data from Groq API. Status code: {response.status_code}")
        return None

# This function searches prices of the parts using web scraping
def search_part_price(part_name):
    search_url = f"https://www.newegg.com/p/pl?d={part_name.replace(' ', '+')}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            price_element = soup.find('li', class_='price-current')
            
            if price_element:
                price_text = price_element.text.strip()
                return price_text 
            else:
                print(f"Price not found for part: {part_name}")
                return None
        else:
            print(f"Failed to fetch page for {part_name}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching part price: {e}")
        return None

# This function parses the parts with the prices from the AI response
def parse_parts_and_prices(parts_text):
    parts = []
    prebuilt_name = None
    lines = parts_text.split('\n')
    
    for line in lines:
        if ':' in line and "Prebuilt Name" not in line:
            try:
                name, part_type = line.split(':', 1)
                name = name.strip()
                part_type = part_type.strip()
                
                price = search_part_price(part_type)
                
                if price is not None:
                    cleaned_price = re.sub(r'[^\d.]', '', price)
                    try:
                        float_price = float(cleaned_price)
                        parts.append({'name': name, 'type': part_type, 'price': float_price})
                    except ValueError:
                        print(f"Error converting price to float: {cleaned_price}")
            except (IndexError, ValueError):
                continue
        elif "Prebuilt Name" in line:
            prebuilt_name = line.replace('Prebuilt Name:', '').strip()

    return prebuilt_name, parts