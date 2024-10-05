import re
from telegram_app.bot.lang import SERBIAN_CYRILLIC_ALPHABET

# Function to separate settlement, streets, and house numbers
def parse_street_and_numbers(streets_str):
    # Split by comma to get individual items
    parts = [part.strip() for part in streets_str.split(',')]
    
    # List to store street, settlement, and house number objects
    result = []
    
    # Regex to detect settlement and street in the format "Насеље МАКИШ: БОРЕ СТАНКОВИЋА:"
    settlement_street_pattern = re.compile(r'Насеље\s*(.+):\s*(.+):')

    # Regex to detect if part is a street name with a colon at the end
    street_pattern = re.compile(r'(.+):')
    
    # Variables to track current settlement and street names
    settlement = ""
    street = ""
    
    # Check if the string has a settlement and street pattern
    settlement_match = settlement_street_pattern.match(parts[0])
    if settlement_match:
        # Extract the settlement and street from the first part
        settlement = settlement_match.group(1).strip()
        street = settlement_match.group(2).strip()
        # Remove this part since it's already handled
        parts.pop(0)
    
    # Iterate through the remaining parts to extract street and house numbers
    for part in parts:
        street_match = street_pattern.match(part)
        if street_match:
            # If a street name is found, update the street variable
            street = street_match.group(1).strip()
            # Also handle the case where the first house number comes after the colon (like "ББ")
            remaining = part.split(':')[-1].strip()
            if remaining:
                result.append({
                    'settlement': settlement,
                    'street': street,
                    'house_range': remaining
                })
        else:
            # Otherwise, it's a house number or range
            result.append({
                'settlement': settlement,
                'street': street,
                'house_range': part
            })
    
    return result

def split_settlement_and_street(street_str):
    """Split settlement and street if there's a colon, otherwise return street only."""
    if street_str.count(':') == 1:
        settlement, street = street_str.split(':')
        return settlement.strip(), street.strip().upper()
    return None, street_str.strip()

def clean_address_parts(settlement, street):
    """Clean the settlement and street strings by removing unnecessary words."""
    if settlement:
        settlement = settlement.replace('Насеље', '').strip().upper()
    
    if street:
        street = street.replace('УЛИЦА', '').strip()
    
    return settlement, street

def get_numeric_and_alpha_parts(house_number):
    """
    Splits the house number into numeric and alphabetic parts.
    
    Args:
        house_number (str): The house number (can be alphanumeric).
    
    Returns:
        tuple: A tuple of (numeric_part, alpha_part) where numeric_part is an int or None and alpha_part is a string.
    """
    numeric_part = re.match(r"^\d+", house_number)  # Extracts numeric part
    alpha_part = re.search(r"[А-Ш]+", house_number)  # Extracts Cyrillic alphabet part
    
    numeric_part = int(numeric_part.group()) if numeric_part else None
    alpha_part = alpha_part.group() if alpha_part else ''
    
    return numeric_part, alpha_part

def is_cyrillic_within_range(user_alpha, start_alpha, end_alpha):
    """
    Compares Cyrillic alphabetic parts to determine if the user's alphabetic part is within the given range.
    
    Args:
        user_alpha (str): The user's house number alphabetic part.
        start_alpha (str): The start of the range alphabetic part.
        end_alpha (str): The end of the range alphabetic part.
    
    Returns:
        bool: True if user_alpha is within the range, False otherwise.
    """
    if not user_alpha:
        return True  # No alphabetic part, so it's within any range
    if not start_alpha and not end_alpha:
        return False  # Both range limits lack alphabetic parts
    
    # Find indices of the alphabetic parts in the Cyrillic alphabet
    user_index = SERBIAN_CYRILLIC_ALPHABET.index(user_alpha) if user_alpha else -1
    start_index = SERBIAN_CYRILLIC_ALPHABET.index(start_alpha) if start_alpha else -1
    end_index = SERBIAN_CYRILLIC_ALPHABET.index(end_alpha) if end_alpha else -1
    
    return start_index <= user_index <= end_index

def is_within_range(user_address, scheduled_address):
    """
    Compares user-provided address with a scheduled address.
    
    Args:
        user_address (dict): User's address entry as dictionary.
        scheduled_address (dict): Scheduled address entry from the database as dictionary.
    
    Returns:
        bool: True if the user's address is within the scheduled address range, False otherwise.
    """
    # Check if area and street match exactly
    if (user_address['area'] == scheduled_address['municipality'] and
        user_address['street'] == scheduled_address['street']):
        
        # Extract house number and range
        user_numeric, user_alpha = get_numeric_and_alpha_parts(user_address['house_number'])
        
        # Check if the scheduled house_range contains a hyphen (range)
        if "-" in scheduled_address['house_range']:
            range_start, range_end = scheduled_address['house_range'].split("-")
            
            # Get numeric and alphabetic parts from the range
            start_numeric, start_alpha = get_numeric_and_alpha_parts(range_start)
            end_numeric, end_alpha = get_numeric_and_alpha_parts(range_end)
            
            # If no numeric part exists, directly compare the alphabetic parts
            if user_numeric is None and start_numeric is None and end_numeric is None:
                return is_cyrillic_within_range(user_alpha, start_alpha, end_alpha)
            
            # Check if the user's numeric part is within the range
            if start_numeric is not None and end_numeric is not None and user_numeric is not None:
                if start_numeric <= user_numeric <= end_numeric:
                    # If numeric parts match, check the alphabetic parts
                    if user_numeric == start_numeric == end_numeric:
                        return is_cyrillic_within_range(user_alpha, start_alpha, end_alpha)
                    return True
            return False
        else:
            # If there's no range, compare directly with the house number
            return user_address['house_number'] == scheduled_address['house_range']
    return False

def remove_duplicate_addresses(user_data):
    # Initialize an empty set to track seen addresses
    seen_addresses = set()
    
    # Create a new list to hold unique addresses
    unique_addresses = []
    
    # Iterate over each address in the 'addresses' list
    for address in user_data["addresses"]:
        # Convert the address dict to a tuple of items (to make it hashable)
        address_tuple = tuple(address.items())
        
        # If the address hasn't been seen yet, add it to the list of unique addresses
        if address_tuple not in seen_addresses:
            unique_addresses.append(address)
            seen_addresses.add(address_tuple)
    
    # Update the user_data with the list of unique addresses
    user_data["addresses"] = unique_addresses
    
    return user_data