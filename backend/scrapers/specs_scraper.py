import requests
import re
import os
import time
import random
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

ua = UserAgent()

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[403, 429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# This function gets the html content
def get_html_content(url):
    accepted_domains = ["newegg.ca", "newegg.com", "canadacomputers.com", "bestbuy.ca"]
    
    if not any(domain in url for domain in accepted_domains):
        return None, "Invalid URL. Only Newegg, Canadian Computers, and Best Buy links are allowed."
    
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(response.text)
            return None, f"Failed to fetch page content. Status code: {response.status_code}"
        
        html_content = response.content
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching page content: {e}"
    
    is_prebuilt_pc = check_if_prebuilt_pc(html_content)
    if not is_prebuilt_pc:
        return None, "The URL does not appear to be a gaming desktop or prebuilt PC. Only prebuilt PCs are allowed."
    
    return html_content, None

def check_if_prebuilt_pc(html_content):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an AI that determines if a webpage HTML describes a prebuilt gaming desktop PC."},
            {"role": "user", "content": (
                "Analyze the HTML content and determine if the page describes a prebuilt gaming desktop PC. "
                "If it does, respond with 'yes'. If not, respond with 'no'. Only consider pages that describe prebuilt desktop PCs."
                f"\nHere is the HTML: {html_content[:10000]}"
            )}
        ]
    }
    
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            classification = result['choices'][0]['message']['content'].strip().lower()
            return classification == 'yes'
        else:
            print(f"Failed to fetch classification from AI. Status code: {response.status_code}")
            return False
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        print(f"Error during AI classification: {e}")
        return False

# This function gets the relevvant content of the page and the price of the prebuilt pc
def extract_relevant_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    specs_section = None
    possible_sections = ['spec', 'details', 'specs', 'product-description', 'product-specs', 'product-details', 'product-bullets']

    for section_class in possible_sections:
        specs_section = soup.find('div', class_=section_class) or soup.find('table', class_=section_class)
        if specs_section:
            break

    if not specs_section:
        specs_section = soup.find('ul', class_='product-specs') or soup.find('div', class_='product-details')

    if not specs_section:
        print("Specs section not found, returning the first 5000 characters of HTML as fallback.")
        return None, str(soup)[:5000]

    cleaned_specs_html = str(specs_section)

    price_patterns = [
        {'site': 'newegg', 'class': ['price-current', 'price', 'price-value']},
        {'site': 'bestbuy', 'class': ['priceView-customer-price', 'pricing-price__regular-price']},
        {'site': 'canadiancomputers', 'class': ['pq-hdr-price', 'price']},
    ]
    
    prebuilt_price = None

    for pattern in price_patterns:
        for price_class in pattern['class']:
            price_element = soup.find('li', class_=price_class) or soup.find('div', class_=price_class) or soup.find('span', class_=price_class)
            
            if price_element:
                price_text = price_element.get_text(strip=True).replace("CAD", "").replace("$", "").replace(",", "").strip()
                
                try:
                    prebuilt_price = float(price_text)
                    if prebuilt_price:
                        return prebuilt_price, cleaned_specs_html
                except ValueError:
                    continue

    if not prebuilt_price:
        possible_price_elements = soup.find_all(text=lambda text: "CAD $" in text or "$" in text)
        for element in possible_price_elements:
            try:
                price_text = element.strip().replace("CAD", "").replace("$", "").replace(",", "").strip()
                prebuilt_price = float(price_text)

                if prebuilt_price:
                    break
            except ValueError:
                continue

    return prebuilt_price, cleaned_specs_html

# This function requests to an AI from GroqCloud to find the parts of the prebuilt pc
def scrape_specs_from_html(cleaned_html_content):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": (
                "You are an AI that extracts and cleans computer parts from HTML. "
                "Remove unnecessary details like percentage values or descriptors unrelated to core component specs."
            )},
            {"role": "user", "content": (
                "Extract all unique components, including CPU, GPU, RAM, Storage, Cooling, Motherboard, Power Supply, Case, "
                "and the prebuilt PC name from this HTML content. "
                "Ensure each component is listed once without duplicates. "
                "If a component is missing, skip it rather than guessing. "
                "Format as follows:\n\n"
                "Prebuilt Name: [Prebuilt PC Name]\n"
                "CPU: [Component]\n"
                "GPU: [Component]\n"
                "Cooling: [Component]\n\n"
                f"Here is the HTML: {cleaned_html_content}"
            )},
            {"role": "assistant", "content": (
                "Please ensure each component name is essential and remove extraneous information, "
                "like wattage ratings beyond the primary value (e.g., '500W' rather than '500W 85%'), "
                "and extra terms like 'RGB' or 'Cooling' unless essential to the component's identity."
            )}
        ]
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        try:
            result = response.json()
            parts_text = result['choices'][0]['message']['content']
            return parts_text

        except (ValueError, KeyError):
            print("Error processing OpenAI response.")
            return None
    else:
        print(f"Failed to fetch data from OpenAI API. Status code: {response.status_code}")
        return None
    
# This function extract features of the component and it can be for any component.
def extract_features(part_name):
    features = []

    size_or_capacity_match = re.findall(r'\d+\s*(gb|tb|mhz|w)', part_name.lower())
    features.extend(size_or_capacity_match)

    type_match = re.findall(r'(ddr\d|pcie|nvme|sata|gddr\d|motherboard|cpu|ram|gpu|power\s*supply)', part_name.lower())
    features.extend(type_match)

    model_match = re.findall(r'(i\d|ryzen\s*\d|rtx\s*\d{3,4}|gtx\s*\d{3,4}|b\d{3}|x\d{3})', part_name.lower())
    features.extend(model_match)

    return features

# This function searches prices of the parts using web scraping
def search_part_price(part_name, component_type=None):
    search_url = f"https://www.newegg.com/p/pl?d={component_type.replace(' ', '+')}"
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive'
    }
    
    try:
        response = session.get(search_url, headers=headers)
        time.sleep(random.uniform(1.5, 3.0))  

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            part_features = extract_features(component_type)
            products = soup.find_all('div', class_='item-cell')

            for product in products:
                product_title_element = product.find('a', class_='item-title')
                if product_title_element:
                    product_title = product_title_element.text.lower()
                    
                    # Verification
                    matches = sum(feature in product_title for feature in part_features)
                    if matches >= len(part_features) // 2:
                        if verify_part_match(part_name, product_title, component_type):
                            price_element = product.find('li', class_='price-current')
                            if price_element:
                                price_text = price_element.text.strip()
                                product_link = product_title_element['href']
                                return price_text, product_link
            print(f"No close match found for part: {part_name}")
            return None, None
        else:
            print(f"Failed to fetch page for {part_name}. Status code: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Error fetching part price: {e}")
        return None, None

# This function verify if product matches with the component using AI
def verify_part_match(part_name, product_title, component_type=None):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        'Authorization': f'Bearer {openai_api_key}',  
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You accurately classify components as standalone or prebuilt systems."},
            {"role": "user", "content": (
                f"Does '{product_title}' accurately describe a standalone '{component_type or part_name}' "
                "and NOT a prebuilt PC, Gaming Desktop, Laptop, System, or unrelated item? Respond 'yes' only if it is definitely a standalone component, "
                "not a system, prebuilt, or anything unrelated to standalone parts. Reply 'no' otherwise."
            )}
        ]
    }
    
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    
    if response.status_code == 200:
        ai_response = response.json()['choices'][0]['message']['content']
        return "yes" in ai_response.lower()
    else:
        print("Error verifying part match with OpenAI.")
        return False
    

# This function parses the parts with the prices from the AI response
def parse_parts_and_prices(ai_output):
    parts = []
    prebuilt_name = None
    lines = ai_output.split('\n')
    
    for line in lines:
        if 'Prebuilt Name' in line:
            prebuilt_name = line.split(':', 1)[1].strip()
        else:
            try:
                name, part_type = line.split(':', 1)
                name, part_type = name.strip(), part_type.strip()
                price, link = search_part_price(name, part_type)
                
                if price and link:
                    parts.append({
                        'name': name,
                        'type': part_type,
                        'price': float(re.sub(r'[^\d.]', '', price)),
                        'link': link
                    })
            except ValueError:
                continue

    return prebuilt_name, parts