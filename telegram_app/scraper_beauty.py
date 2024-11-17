import requests
from bs4 import BeautifulSoup
from telegram_app.parser.utils import parse_street_and_numbers, split_settlement_and_street, clean_address_parts
from telegram_app.sql.models import ScheduledAddress
from telegram_app.sql.database import SessionLocal
from celery import shared_task
from telegram_app.sql.queries import save_parsed_scheduled_addresses_to_db
from typing import Final
from dotenv import load_dotenv
import os
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv(dotenv_path='telegram_app/.env')
URL: Final = os.getenv("URL")
HEADERS: Final = json.loads(os.getenv("HEADERS"))

def fetch_webpage(url, headers):
    """Fetch the webpage content and return the response."""
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    if response.status_code == 403:
        raise Exception("Access forbidden. Check headers or permissions.")
    return response.text

def parse_webpage(content):
    """Parse the webpage content and return the relevant table."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Look for all tables and find the one containing "Општина" in the header
    table = None
    for tbl in soup.find_all('table'):
        if tbl.find('font', text="Општина"):
            table = tbl
            break

    if table is None:
        raise Exception("Table not found")
    
    return table

def extract_data_from_table(table):
    """Extract data from the table and return a list of address dictionaries."""
    rows = table.find_all('tr')[1:]  # Skip header row
    data = []
    seen_entries = set()

    for row in rows:
        columns = row.find_all('td')
        addresses = parse_street_and_numbers(columns[2].text.strip())
        
        for address in addresses:
            # Split settlement and street using the helper function
            settlement, street = split_settlement_and_street(address['street'])
            
            # Clean the settlement and street using the helper function
            settlement, street = clean_address_parts(settlement, street)
            
            if address['house_range']:
                obj = {
                    'municipality': columns[0].text.strip().upper(),
                    'time_range': columns[1].text.strip().upper(),
                    'settlement': settlement,
                    'street': street.upper(),
                    'house_range': address['house_range'].upper()
                }

                # Create a unique key to avoid duplicates
                unique_key = (obj['municipality'], obj['time_range'], obj['settlement'], obj['street'], obj['house_range'])
                
                # Check for duplicates before adding to data
                if unique_key not in seen_entries:
                    seen_entries.add(unique_key)
                    data.append(obj)
    
    return data

@shared_task(name='telegram_app.scraper_beauty.scrape_beauty')
def scrape_beauty():
    """Web scraping and database saving."""
    try:
        content = fetch_webpage(URL, HEADERS)
        table = parse_webpage(content)
        data = extract_data_from_table(table)
        print((f"Extracted {len(data)} records from the webpage."))
        save_parsed_scheduled_addresses_to_db(data)

        return "Scraping task completed"
    except Exception as e:
        #TODO: Log the exception
        print(f"Error during scraping: {e}")
        return None 
