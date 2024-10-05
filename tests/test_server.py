import requests

# print(requests.get('http://localhost:8000').json())
# print("--------------------")


# response = requests.post(
#     'http://localhost:8000/', 
#     json={
#         "telegram_id": 123456789,
#         "first_name": "John",
#         "last_name": "Doe",
#         "username": "johndoe",
#         "is_bot": False,
#         "language_code": "en",
#         "full_address": "123 Main St, Anytown, USA",
#         "street": "Main St",
#         "house_number": "123",
#         "confirmed_geolocation": True
#     }
# )

# print(response.json())
# print("--------------------")


response = requests.post(
    'http://localhost:8000/', 
    json={
        "telegram_id": 123456789,
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "is_bot": False,
        "language_code": "en",
        "full_address": "123 Main St, Anytown, USA",
        "street": "Main St",
        "house_number": "123",
        "confirmed_geolocation": True,
        "is_active": True
    }
)

print(response.json())
print("-----------  ---------")