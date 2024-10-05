from typing import Final
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from sqlalchemy.orm import Session
from models import User, Address  # Assuming you have a UserAddress model defined in models.py
from database import SessionLocal  # Assuming you have a SessionLocal for database session


TOKEN: Final = "7524028999:AAGu1jGYt6pKxbLC5Z7ENdC_wqPyxw1Wz6A"
BOT_USERNAME: Final = "@beograd_struja_bot"
# Define the user's credentials
user = {
    'first_name': 'Robert',
    'id': 284764019,
    'is_bot': False,
    'language_code': 'en',
    'last_name': 'Solovyev',
    'username': 'rsolovye'
}

# Send message to the user
async def send_message(update: Update, response_message: str):
    bot = Bot(token=TOKEN)
    chat_id = update.effective_user.id
    message = f'{update.effective_user.first_name} {update.effective_user.last_name}\n {response_message}.'
    await bot.send_message(chat_id=chat_id, text=message)

# Command Handlers
async def start_command(update: Update, context):
    await update.message.reply_text("Hello! I'm Beograd Struja Bot. I will let you know when your electricity will be turned- off.")

async def help_command(update: Update, context):
    await update.message.reply_text("Enter your address in cyrillic letters. I will notify you 24 hrs before your electricity will be turned-off.")

async def custom_command(update: Update, context):
    await update.message.reply_text("This is a custom command.")
    
# Response Handlers
async def handle_response(text: str, update: Update | None) -> str:
    if "hello" in text.lower():
        return "Hello! How can I help you?"
    
    if "how are you" in text.lower():
        return "I'm fine, thank you."
    
    if "subscribe" in text.lower():
        address_str: str = text.replace("subscribe", "").strip().upper()

        # Extract user information from the update object
        user_data = update.effective_user
        telegram_id = user_data.id
        first_name = user_data.first_name
        last_name = user_data.last_name
        username = user_data.username
        is_bot = user_data.is_bot
        language_code = user_data.language_code

        print(f"User {telegram_id} is attempting to subscribe to notifications for address: {address_str}.")
        
        # Open database session
        db: Session = SessionLocal()
        try:
            # Step 1: Check if the user exists
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                # Step 2a: If user exists, print and proceed to add the address
                print(f"User {user.telegram_id} exists: {user.first_name} {user.last_name}")
            else:
                # Step 3a: If user doesn't exist, create a new user
                user = User(
                    telegram_id=telegram_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    is_bot=is_bot,
                    language_code=language_code
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"New user created: {user.first_name} {user.last_name}")
            
            # Step 2b or Step 3b: Add the new address to the user
            address = Address(
                full_address=address_str,
                street=f"WIP {address_str}",  # Assuming you need to parse this from the address
                house_number=f"WIP {address_str}",  # Assuming you need to parse this from the address
                confirmed_geolocation=False,  # Assuming default value
                user_id=user.id  # Link address to the user
            )
            db.add(address)
            db.commit()
            db.refresh(address)
            print(f"New address added for user {user.first_name}: {address.full_address}")
            
        except Exception as e:
            db.rollback()
            print(f"Error occurred: {e}")
            raise e
        finally:
            db.close()

        return f"User {first_name} has subscribed to notifications for address: {address_str}."
    
    if "clear" in text.lower():
        user_data = update.effective_user
        telegram_id = user_data.id
        print(f"User {telegram_id} requested to delete all addresses.")
        
        db: Session = SessionLocal()
        try:
            # Check if the user exists
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                return "User not found. Please subscribe first."
            
            # Delete all addresses linked to the user and get the number of rows deleted
            deleted = db.query(Address).filter(Address.user_id == user.id).delete(synchronize_session=False)
            db.commit()
            
            if deleted == 0:
                return f"No addresses found for user {user.first_name}."
            
        except Exception as e:
            db.rollback()
            print(f"Error occurred: {e}")
            return "An error occurred while trying to delete addresses. Please try again."
        finally:
            db.close()
        
        return f"Deleted {deleted} addresses for user {user.first_name}."
        
    if "send message" in text.lower():
        # Extract user information
        user_data = update.effective_user
        telegram_id = user_data.id
        
        print(f"User {telegram_id} requested to send a message.")

        # Open database session
        db: Session = SessionLocal()
        try:
            # Step 1: Check if the user exists
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                return "User not found. Please subscribe first."
            
            # Step 2: Fetch all addresses linked to the user
            addresses = db.query(Address).filter(Address.user_id == user.id).all()
            
            if not addresses:
                return "No addresses found for this user."
            
            # Step 3: Prepare the response with all addresses
            address_list = "\n".join([f"{addr.full_address}" for addr in addresses])
            response_message = f"User {user.first_name}, here are your subscribed addresses:\n{address_list}"
            
            print(f"Sending message to user: {response_message}")
            
            # Optional: You can also use the send_message function if required
            await send_message(update, response_message)
            return None
        
        except Exception as e:
            db.rollback()
            print(f"Error occurred: {e}")
            raise e
        finally:
            db.close()
    
    return "I'm sorry, I don't understand that command."

async def handle_message(update: Update, context):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f"User ({update.message.chat.id}) in {message_type} sent a message: {text}")
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = await handle_response(new_text, update)
        else:
            return 
    else: 
        response: str = await handle_response(text, update)
    
    print(f"Bot responded: {response}")
    
    await update.message.reply_text(response)
            
    
async def error(update: Update, context):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(error)
    
    # Polling
    print("Bot is running...")
    app.run_polling(poll_interval=3)