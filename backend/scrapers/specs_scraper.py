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

    # searching the specifications section based on common tags
    specs_section = None
    possible_sections = ['spec', 'details', 'specs', 'description', 'product-specs', 'product-details']

    for section_class in possible_sections:
        specs_section = soup.find('div', class_=section_class) or soup.find('table', class_=section_class)
        if specs_section:
            break 

    # search for the tables in the page
    if not specs_section:
        specs_section = soup.find('ul', class_='product-specs') or soup.find('div', class_='product-details')

    if not specs_section:
        print("Specs section not found, returning the first 5000 characters of HTML as fallback.")
        return None, str(soup)[:5000]

    cleaned_specs_html = str(specs_section)
    
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

    return prebuilt_price, cleaned_specs_html

# This function requests to an AI from GroqCloud to find the parts of the prebuilt pc
def scrape_specs_from_html(cleaned_html_content):
    groq_api_key = os.getenv('GROQ_API_KEY')

    headers = {
        'Authorization': f'Bearer {groq_api_key}',  
        'Content-Type': 'application/json'
    }

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are an AI that extracts computer parts, their names, types, and the prebuilt PC name from HTML."},
            {"role": "user", "content": (
                "Extract the **unique components** and the **prebuilt PC name** from this HTML content. "
                "Ensure each component is listed only once, with no duplicates. Format the components as follows:\n\n"
                "Component: Type\n\n"
                "For example:\n"
                "CPU: Intel Core i9\n"
                "GPU: NVIDIA RTX 3080\n"
                "RAM: 16GB DDR4\n"
                "Motherboard: ASUS ROG Strix B450-F\n"
                "Do not repeat any information or mention unnecessary details like CPU Name vs CPU Type. Only return the component name and its type in one line, with no duplicates. "
                "Ensure the Prebuilt Name is extracted first, followed by the list of components in this format."
                f"\nHere is the HTML: {cleaned_html_content}"
            )}
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
    
# This function extract features of the component and it can be for any component.
def extract_features(part_name):
    features = []

    size_or_capacity_match = re.findall(r'\d+\s*(gb|tb|mhz|w)', part_name.lower())
    features.extend(size_or_capacity_match)

    type_match = re.findall(r'(ddr\d|pcie|nvme|sata|gddr\d)', part_name.lower())
    features.extend(type_match)

    model_match = re.findall(r'(i\d|ryzen\s*\d|rtx\s*\d{3,4}|gtx\s*\d{3,4})', part_name.lower())
    features.extend(model_match)

    return features

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
            
            part_features = extract_features(part_name)

            products = soup.find_all('div', class_='item-cell')

            for product in products:
                product_title_element = product.find('a', class_='item-title')
                if product_title_element:
                    product_title = product_title_element.text.lower()

                    matches = sum(feature in product_title for feature in part_features) # Checking to see if any features are found in the product
                    if matches >= len(part_features) // 2: 
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

# This function parses the parts with the prices from the AI response
def parse_parts_and_prices(parts_text):
    parts = []
    prebuilt_name = None
    lines = parts_text.split('\n')
    
    for line in lines:
        if ':' in line and "Prebuilt Name" not in line and "Prebuilt PC Name" not in line:
            try:
                name, part_type = line.split(':', 1)
                name = name.strip()
                part_type = part_type.strip()
                
                price, link = search_part_price(part_type)  
                
                if price is not None and link is not None:
                    cleaned_price = re.sub(r'[^\d.]', '', price)
                    try:
                        float_price = float(cleaned_price)
                        parts.append({'name': name, 'type': part_type, 'price': float_price, 'link': link})
                    except ValueError:
                        print(f"Error converting price to float: {cleaned_price}")
            except (IndexError, ValueError):
                continue
        elif "Prebuilt Name" in line or "Prebuilt PC Name" in line:
            prebuilt_name = line.replace('Prebuilt Name:', '').strip()

    return prebuilt_name, parts