import re

# Serbian Cyrillic alphabet list for comparison
SERBIAN_CYRILLIC_ALPHABET = ['А', 'Б', 'В', 'Г', 'Д', 'Ђ', 'Е', 'Ж', 'З', 'И', 'Ј', 'К', 'Л', 'Љ', 'М', 'Н', 'Њ', 'О', 'П', 'Р', 'С', 'Т', 'Ћ', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Џ', 'Ш']

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

# Simulated data using dictionaries
addresses = [
    {"area": "ЗВЕЗДАРА", "street": "СМЕДЕРЕВСКИ ПУТ", "house_number": "17"},
    {"area": "ЗВЕЗДАРА", "street": "СМЕДЕРЕВСКИ ПУТ", "house_number": "2А"},
    {"area": "ЗВЕЗДАРА", "street": "СТЕВАНА СИНЂЕЛИЋА", "house_number": "75Ж"},
    {"area": "ЗВЕЗДАРА", "street": "СТЕВАНА СИНЂЕЛИЋА", "house_number": "ББ"}
]

scheduled_addresses = [
    {"municipality": "ЗВЕЗДАРА", "street": "СМЕДЕРЕВСКИ ПУТ", "house_range": "16-26В"},
    {"municipality": "ЗВЕЗДАРА", "street": "СМЕДЕРЕВСКИ ПУТ", "house_range": "2Д-2X"},
    {"municipality": "ЗВЕЗДАРА", "street": "СТЕВАНА СИНЂЕЛИЋА", "house_range": "75-87"},
    {"municipality": "ЗВЕЗДАРА", "street": "СТЕВАНА СИНЂЕЛИЋА", "house_range": "ББ"}
]

# Running the simulation with dicts
results = []
for user_addr in addresses:
    matched = False
    for sched_addr in scheduled_addresses:
        if is_within_range(user_addr, sched_addr):
            matched = True
            break
    results.append((user_addr['area'], user_addr['street'], user_addr['house_number'], matched))

# Displaying the results
results
