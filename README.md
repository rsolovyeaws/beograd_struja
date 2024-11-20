# Project goal
The goal of this project is to create notification system for planned power outages in Belgrade. The system will scrape the data from the website of the power distribution company and send the notifications to the users.

# Sample scenario:
## User signups for the address to be monitored:
![image](https://github.com/user-attachments/assets/5d1cd58b-7874-495d-9f01-05e6c6373975)

## Data on the ... web site
![image](https://github.com/user-attachments/assets/82bb9834-ba23-456f-bc72-7397e155966f)

## User gets notified (address is provided for demonstration purpose)
![image](https://github.com/user-attachments/assets/46aea1f5-2128-4460-9bed-39a77b929461)



# Current state of the project
1. Telegram bot can notify users, that provided their addresses to the telegram bot, if there is a planned power outage in their area within 24 hours
2. Users can provide their address to the bot via interactions with the bot 
3. Backend is scraping the data from the website of the power distribution company, stores data in the database and sends notifications to the users
4. Every day the bot scrapes the data from the power distribution company website and sends notifications to the users if there are any planned power outages in their address.
5. Via interaction with the bot, users can ask the bot for the list of addresses that they currently monitor
6. Users can remove the address from the list of addresses that they monitor via interaction with the bot

# Future plans for the project
1. Expand notification system to other cities in Serbia
2. Notify users about the planned power outages in their area 48 hours before the power outage
3. Provide users with statistics that shows how many times the power outage happened in their area
4. Add multiple notification systems for the users (email, sms, whatsapp)
5. Add the possibility for the users to choose the notification system that they want to use
6. Add web interface for the users to interact with the bot

# Installation for development

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
```

## Run the following commands

```
set -a; source telegram_app/.env; set +a
docker compose up --build -d
```
