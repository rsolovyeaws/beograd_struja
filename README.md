# Project goal
The goal of this project is to create notification system for planned power outages in Belgrade. The system will scrape the data from the website of the power distribution company and send the notifications to the users.

# User requirements:
1. User has to interact with the Bot via telegram(https://telegram.org/)
2. User has to signup for the telegram bot created by developer ![image](https://github.com/user-attachments/assets/fc7ff15e-3e71-4bda-be1c-2d945742af37)



# Sample scenario:
### 0. Backend scrapes data from the web site (next day power outage) (https://elektrodistribucija.rs/planirana-iskljucenja-beograd/Dan_1_Iskljucenja.htm)
![image](https://github.com/user-attachments/assets/82bb9834-ba23-456f-bc72-7397e155966f)
### 1. User chooses the language for interaction with bot
![image](https://github.com/user-attachments/assets/b530ea5b-b4d6-4ca9-b3ae-fee614136577)
### 2. User chooses to "Add address" that user wants to monitor
![image](https://github.com/user-attachments/assets/e425971b-c469-4b0c-b718-134914bbeb9e)
### 3. User signups for the address to be monitored
![image](https://github.com/user-attachments/assets/5d1cd58b-7874-495d-9f01-05e6c6373975)
### 4. System confirms address through GEOAPIFY API and asks user to confirm address on the map.
![image](https://github.com/user-attachments/assets/14b31f90-2fdf-4a14-8346-9043b5301a57)
### 4. Backend saves users address to the database
### 5. Backend matches user's address with the address planned for the power outage in database 
### 6. User gets notified (address is provided for demonstration purpose)
![image](https://github.com/user-attachments/assets/46aea1f5-2128-4460-9bed-39a77b929461)



# Current state of the project
1. Telegram bot can notify users, that provided their addresses to the telegram bot, if there is a planned power outage in their area within 24 hours
2. Users can provide their address to the bot via interactions with the bot 
3. Backend is scraping the data from the website of the power distribution company, stores data in the database and sends notifications to the users
4. Once per 24 hours the bot scrapes the data from the power distribution company website and sends notifications to the users if there are any planned power outages in their address.
5. Via interaction with the bot, users can ask the bot for the list of addresses that they currently monitor
6. Users can remove the address from the list of addresses that they monitor via interaction with the bot

# Future plans for the project
## High priority
- Add address verifictaion for user's input (e.g. user enters "Zimun" -> System asks: "Did you mean 'Zemun' etc.")
- Notify users about planned power outages in their area 0/24/48/72/96 hours before the power outage

## Moderate Priority
- Provide users with statistics that shows how many times the power outage happened in their area/address/overall (need to modify db to store history)
- Multiple notification systems for the users (other messengers, may be sms.., pigeons =P, viber )
- Add web interface for users that will allow users to choose the way of communication. 

# Installation instructions for development
## After cloning the repository
After cloning the repository, create .env file in the telegram_app folder of the project and fill it with the necessary data. The .env file should look like this:
```
TOKEN=""
BOT_USERNAME=""
HEADERS='{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}'

URL='https://elektrodistribucija.rs/planirana-iskljucenja-beograd/Dan_1_Iskljucenja.htm'
POSTGRES_USER=""
POSTGRES_PASSWORD=""
POSTGRES_DB=""
POSTGRES_HOST=""
POSTGRES_PORT=""


GEOAPIFY_API_KEY=""

REDIS_HOST=""
REDIS_PORT=""
```

## Run the following commands

```
set -a; source telegram_app/.env; set +a
docker compose up --build -d
```
