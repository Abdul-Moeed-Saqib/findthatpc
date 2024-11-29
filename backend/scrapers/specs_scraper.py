import requests
import re
import os
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from scrapers.conversion import get_user_country, get_conversion_rate, detect_currency_with_ai

load_dotenv()

ua = UserAgent()

# This function gets the html content
def get_html_content(url):
    accepted_domains = [
        "microcenter.com", "canadacomputers.com", "bestbuy.ca", "bestbuy.com"
    ]

    if not any(domain in url for domain in accepted_domains):
        return None, "Invalid URL. Only Micro Center, Memory Express, Canada Computers, and Best Buy links are allowed."
    
    try:
        headers = {
            'User-Agent': ua.random
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
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
def extract_relevant_html(html_content, hostname):
    soup = BeautifulSoup(html_content, 'html.parser')

    user_country, user_currency = get_user_country()

    print(f"{user_currency}")

    detected_currency = detect_currency_with_ai(hostname)
    print(f"{detected_currency}")

    specs_section = None
    possible_sections = [
        'spec', 'details', 'SpecTable', 'specs', 'product-description', 
        'product-specs', 'product-details', 'product-bullets',
    ]

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
        {'site': 'bestbuy', 'class': ['priceView-customer-price', 'pricing-price__regular-price']},
        {'site': 'canadacomputers', 'class': ['pq-hdr-price', 'price']},
        {'site': 'microcenter', 'class': ['big-price', 'price__regular']}
    ]
    
    prebuilt_price = None

    # Extract price based on defined classes
    for pattern in price_patterns:
        for price_class in pattern['class']:
            price_element = soup.find('li', class_=price_class) or soup.find('div', class_=price_class) or soup.find('span', class_=price_class)

            if price_element and 'microcenter' not in hostname:
                price_text = price_element.get_text(strip=True).replace("CAD", "").replace("$", "").replace(",", "").strip()
                try:
                    prebuilt_price = float(price_text)
                    break
                except ValueError:
                    continue

            if 'microcenter' in pattern['site']:
                    price_container = soup.find('p', class_=price_class)
                    if price_container:
                        dollar_element = price_container.find('span', id='pricing')

                        if dollar_element:
                            try:
                                dollar = dollar_element.get("content")
                                price_text = dollar.replace(',', '')
                                prebuilt_price = float(price_text)
                                break
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

    if detected_currency != user_currency and prebuilt_price:
        conversion_rate = get_conversion_rate(detected_currency, user_currency)
        prebuilt_price *= conversion_rate
        
    return prebuilt_price, cleaned_specs_html

# This function requests to an AI from OpenAI to find the parts of the prebuilt pc
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
    base_url = "https://www.microcenter.com/search/search_results.aspx?"
    component_category = {
        "CPU": "N=4294966995",
        "GPU": "N=4294966937",
        "Motherboard": "N=4294966996",
        "RAM": "N=4294966965",
        "Storage": "N=4294822457+4294966998",
        "Cooling": "N=4294819366",
        "Power Supply": "N=4294822457+4294966998",
        "Case": "N=4294964318",
    }
    
    category_filter = component_category.get(part_name, "")
    search_url = f"{base_url}{category_filter}&Ntt={component_type.replace(' ', '+')}&searchButton=search"

    headers = {'User-Agent': ua.random}

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            part_features = extract_features(component_type)
            products = soup.find_all('li', class_='product_wrapper')

            user_country, user_currency = get_user_country()

            for product in products:
                product_title_element = product.find('a', class_='productClickItemV2')
                if product_title_element:
                    product_title = product_title_element['data-name'].lower()

                    matches = sum(feature in product_title for feature in part_features)
                    if matches < len(part_features) * 0.75:
                        continue

                    if verify_part_match(part_name, product_title, component_type):
                        price_element = product.find('span', itemprop='price')
                        if price_element:
                            price_text = price_element.text.strip()

                            try: 
                                price_value = float(re.sub(r'[^\d.]', '', price_text))

                                if user_currency != "USD":
                                    conversion_rate = get_conversion_rate("USD", user_currency)
                                    price_value *= conversion_rate

                                product_link = "https://www.microcenter.com" + product_title_element['href']
                                return price_value, product_link
                            except ValueError:
                                print(f"Invalid price format: {price_text}")
                                continue
                                
            print(f"No valid match found for part: {part_name}")
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
            {"role": "system", "content": (
                "You are a component verification AI. Your role is to determine if a product is a standalone component, "
                "not a PC, laptop, gaming desktop, or system."
            )},
            {"role": "user", "content": (
                f"Does '{product_title}' accurately describe a standalone '{component_type or part_name}'? "
                "Do not consider anything that mentions PC, system, desktop, or laptop. "
                "Only respond 'yes' if it is a guaranteed standalone component, and 'no' otherwise."
            )}
        ]
    }
    
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content'].strip().lower()
            return "yes" in ai_response
        else:
            print(f"AI verification failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error verifying part match with OpenAI: {e}")
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
                        'price': price,
                        'link': link
                    })
            except ValueError:
                continue

    return prebuilt_name, parts