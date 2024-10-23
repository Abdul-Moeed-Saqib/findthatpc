import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# This function gets the connecting to the SQL database
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),  
        database=os.getenv('DB_NAME')
    )

def insert_comparison(url, prebuilt_price, total_parts_price, difference, parts):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO comparisons (url, prebuilt_price, total_parts_price, price_difference, parts)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    parts_str = ', '.join([f"{part['name']}: ${part['price']}" for part in parts])

    cursor.execute(query, (url, prebuilt_price, total_parts_price, difference, parts_str))
    
    connection.commit()
    cursor.close()
    connection.close()