import logging
from typing import Final
from sqlalchemy.orm import Session
from models import User, Address
from database import SessionLocal

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup, Bot)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)

TOKEN: Final = "7524028999:AAGu1jGYt6pKxbLC5Z7ENdC_wqPyxw1Wz6A"
BOT_USERNAME: Final = "@beograd_struja_bot"

# STATES
LANGUAGE, ACTION, AREA, STREET, HOUSE, SUMMARY, DELETE, SHOW, LIST = range(9)

# Phrases dictionary for multi-language support
PHRASES = {
    'Serbian': {
        'welcome': 'Добродошли у бот за струју у Београду!\nИзаберите језик\n',
        'choose_action': 'Изаберите акцију',
        'enter_address': 'Молимо вас да унесете адресу',
        'enter_area': 'Молимо вас да унесете вашу област (нпр. земун)',
        'enter_street': 'Молимо вас да унесете вашу улицу',
        'enter_house': 'Молимо вас да унесете ваш број куће:',
        'summary': 'Ваша пуна адреса',
        'subscribed': 'Добијаћете обавештења на следеће адресе:',
        'list_addresses': 'Приказујемо све ваше адресе',
        'delete_address': 'Коју адресу желите да обришете?)',
        'bye': 'Збогом! Надам се да ћемо поново разговарати ускоро.',
        'invalid_language': 'Изабрани језик није валидан. Покушајте поново.',
        'invalid_input': 'Невалидан унос. Унесите валидан број.',
        'enter_number_delete': 'Молимо вас да унесете број адресе коју желите да обришете.',
        'address': 'Адреса',
        'was_deleted': 'је обрисана.',
    },
    'English': {
        'welcome': 'Welcome to the Beograd Electricity Bot!\nChoose your language\n',
        'choose_action': 'Please choose an action',
        'enter_address': 'Please enter the address',
        'enter_area': 'Please enter your area (e.g., part of the city)',
        'enter_street': 'Please enter your street',
        'enter_house': 'Please enter your house number:',
        'summary': "Your full address",
        'subscribed': 'You will receive notifications for the following addresses',
        'list_addresses': 'Listing all your addresses',
        'delete_address': 'Which address would you like to delete?',
        'bye': 'Bye! Hope to talk to you again soon.',
        'invalid_language': 'Invalid language selected. Please try again.',
        'invalid_input': 'Invalid input. Please enter a valid number.',
        'enter_number_delete': 'Please enter the number of the address you want to delete.',
        'address': 'Address',
        'was_deleted': 'was deleted.',
    },
    'Russian': {
        'welcome': 'Добро пожаловать в бота для электроэнергии Белграда!\nВыберите ваш язык\n',
        'choose_action': 'Пожалуйста, выберите действие:',
        'enter_address': 'Пожалуйста, введите ваш адрес:',
        'enter_area': 'Пожалуйста, введите ваш район (например, часть города):',
        'enter_street': 'Пожалуйста, введите вашу улицу:',
        'enter_house': 'Пожалуйста, введите номер вашего дома:',
        'summary': 'Ваш полный адрес',
        'subscribed': 'Вы будете получать уведомления по следующим адресам',
        'list_addresses': 'Показать все ваши адреса',
        'delete_address': 'Какой адрес вы хотите удалить?',
        'bye': 'До свидания! Надеюсь, мы снова поговорим.',
        'invalid_language': 'Выбран неверный язык. Пожалуйста, попробуйте еще раз.',
        'invalid_input': 'Неверный ввод. Пожалуйста, введите действительный номер.',
        'enter_number_delete': 'Пожалуйста, введите номер адреса, который вы хотите удалить.',
        'address': 'Адрес',
        'was_deleted': 'был удален.',
    }
}

def validate_area(area: str) -> bool:
    """ WIP - Validate the area input."""
    if area == 'test':
        return False
    return True if area else False  

def validate_street(street: str) -> bool:
    """ WIP - Validate the area input."""
    if street == 'test':
        return False
    return True if street else False  

def validate_house(house: str) -> bool:
    """ WIP - Validate the area input."""
    if house == 'test':
        return False
    return True if house else False  

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation, describes bot functionality, and asks the user to choose a language."""
    reply_keyboard = [['Serbian', "English", "Russian"]]
    await update.message.reply_text(
        f'<b>{PHRASES["English"]["welcome"]}</b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return LANGUAGE

async def prompt_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt the user to choose an action after an operation like delete."""
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    # Define inline buttons for the next action selection
    actions = {
        'Serbian': {
            'Add Address': 'Додајте адресу',
            'Show All Addresses': 'Покажи све моје адресе',
            'Delete Address': 'Обриши адресу',
        },
        'English': {
            'Add Address': 'Add Address',
            'Show All Addresses': 'Show All Addresses',
            'Delete Address': 'Delete Address',
        },
        'Russian': {
            'Add Address': 'Добавить адрес',
            'Show All Addresses': 'Показать все мои адреса',
            'Delete Address': 'Удалить адрес',
        },
    }

    keyboard = [
        [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
        [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
        [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Prompt the user to choose the next action
    await update.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)

    return ACTION


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user's language and provides options based on the selected language."""
    user_language = update.message.text
    context.user_data['language'] = user_language
    if user_language not in PHRASES:
        await update.message.reply_text(PHRASES['English']['invalid_language'])
        return LANGUAGE

    phrases = PHRASES[user_language]
    await update.message.reply_text(
        f'<b>{phrases["choose_action"]}</b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
    )

    # Define inline buttons for action selection based on language
    actions = {
        'Serbian': {
            'Add Address': 'Додајте адресу',
            'Show All Addresses': 'Покажи све моје адресе',
            'Delete Address': 'Обриши адресу',
        },
        'English': {
            'Add Address': 'Add Address',
            'Show All Addresses': 'Show All Addresses',
            'Delete Address': 'Delete Address',
        },
        'Russian': {
            'Add Address': 'Добавить адрес',
            'Show All Addresses': 'Показать все мои адреса',
            'Delete Address': 'Удалить адрес',
        },
    }

    keyboard = [
        [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
        [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
        [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)
    return ACTION

async def action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle action based on user input."""
    query = update.callback_query
    await query.answer()

    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    if query.data == 'Add':
        await query.edit_message_text(text=phrases['enter_area'])
        return AREA
    elif query.data == 'List':
        return await list_addresses(update, context)
        # await query.edit_message_text(text=phrases['list_addresses'])
        # return SHOW
    elif query.data == 'Delete':
        # await query.edit_message_text(text=phrases['delete_address'])
        # return DELETE
        # Call the delete_address function to start the deletion process
        return await delete_address(update, context)

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    context.user_data['address'] = update.message.text
    await update.message.reply_text(phrases['enter_area'])
    return AREA

async def area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
  
    if not validate_area(update.message.text):
        await update.message.reply_text(phrases['enter_area'])
        return AREA
    
    context.user_data['area'] = update.message.text
    await update.message.reply_text(phrases['enter_street'])
    return STREET

async def street(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    
    if not validate_street(update.message.text):
        await update.message.reply_text(phrases['enter_street'])
        return STREET
    
    context.user_data['street'] = update.message.text
    await update.message.reply_text(phrases['enter_house'])
    return HOUSE


async def house(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    
    if not validate_house(update.message.text):
        await update.message.reply_text(phrases['enter_house'])
        return HOUSE
    
    # Store the house number in user_data
    context.user_data['house'] = update.message.text
    
    # Move directly to the summary after house number is entered
    return await summary(update, context)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    # Retrieve user data
    area = context.user_data.get('area', 'N/A')
    print(f"Area: {area}")
    street = context.user_data.get('street', 'N/A')
    house = context.user_data.get('house', 'N/A')
    
    # Construct the summary message
    summary_message = f"{area}, {street}, {house}"
    
    # User:
    user_data = update.effective_user
    telegram_id = user_data.id
    first_name = user_data.first_name
    last_name = user_data.last_name
    username = user_data.username
    is_bot = user_data.is_bot
    language_code = user_data.language_code
    
    # Address
    full_address = summary_message
    area = area
    street = street
    house_number = house
    confirmed_geolocation = False
    
    # Open database session
    db: Session = SessionLocal()
    try:
        # Step 1: Check if the user exists
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if user:
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
            # DEBUG
            print(f"New user created: {user.first_name} {user.last_name}")
        
        # Step 2b or Step 3b: Add the new address to the user
        address = Address(
            full_address=summary_message,
            area=area,  
            street=street,
            house_number=house,
            confirmed_geolocation=False,
            user_id=user.id
        )
        db.add(address)
        db.commit()
        db.refresh(address)
        # DEBUG
        print(f"New address added for user {user.first_name}: {address.full_address}")
        
        # TESTING
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
            response_message = f"{phrases['subscribed']}\n{address_list}"
            
            # DEBUG
            print(f"Sending message to user: {response_message}")
            
            # send_message to the user
            await update.message.reply_text(response_message, parse_mode="Markdown")

        
        except Exception as e:
            db.rollback()
            print(f"Error occurred: {e}")
            raise e
        finally:
            db.close()
        
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        raise e
    finally:
        db.close()
    
    # REPROMPT


    # Define inline buttons for the next action selection
    actions = {
        'Serbian': {
            'Add Address': 'Додајте адресу',
            'Show All Addresses': 'Покажи све моје адресе',
            'Delete Address': 'Обриши адресу',
        },
        'English': {
            'Add Address': 'Add Address',
            'Show All Addresses': 'Show All Addresses',
            'Delete Address': 'Delete Address',
        },
        'Russian': {
            'Add Address': 'Добавить адрес',
            'Show All Addresses': 'Показать все мои адреса',
            'Delete Address': 'Удалить адрес',
        },
    }

    keyboard = [
        [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
        [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
        [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Prompt the user to choose the next action
    await update.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)
    
    return ACTION
    # ----
    # return ConversationHandler.END

async def list_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """List all addresses for the user and return to the choose action state."""
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    # Retrieve user data
    user_data = update.effective_user
    telegram_id = user_data.id

    # Open database session
    db: Session = SessionLocal()
    try:
        # Step 1: Check if the user exists
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            await update.callback_query.message.reply_text("User not found. Please subscribe first.")
            return ACTION  # Return to action state

        # Step 2: Fetch all addresses linked to the user
        addresses = db.query(Address).filter(Address.user_id == user.id).all()

        if not addresses:
            await update.callback_query.message.reply_text("No addresses found for this user.")
            return ACTION  # Return to action state

        # Step 3: Prepare the response with all addresses
        address_list = "\n".join([f"{addr.full_address}" for addr in addresses])
        response_message = f"{phrases['subscribed']}\n{address_list}"

        # Send the message to the user
        await update.callback_query.message.reply_text(response_message, parse_mode="Markdown")

    except Exception as e:
        db.rollback()
        await update.callback_query.message.reply_text(f"An error occurred: {e}")
        raise e
    finally:
        db.close()

    # REPROMPT: Return to the action selection after showing the addresses
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    # Define inline buttons for the next action selection
    actions = {
        'Serbian': {
            'Add Address': 'Додајте адресу',
            'Show All Addresses': 'Покажи све моје адресе',
            'Delete Address': 'Обриши адресу',
        },
        'English': {
            'Add Address': 'Add Address',
            'Show All Addresses': 'Show All Addresses',
            'Delete Address': 'Delete Address',
        },
        'Russian': {
            'Add Address': 'Добавить адрес',
            'Show All Addresses': 'Показать все мои адреса',
            'Delete Address': 'Удалить адрес',
        },
    }

    keyboard = [
        [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
        [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
        [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Prompt the user to choose the next action
    await update.callback_query.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)

    return ACTION

async def delete_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show all addresses with numbers and delete the selected one."""
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    user_data = update.effective_user
    telegram_id = user_data.id

    # Open database session
    db: Session = SessionLocal()
    try:
        # Step 1: Check if the user exists
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            await update.callback_query.message.reply_text("User not found. Please subscribe first.")
            return ACTION

        # Step 2: Fetch all addresses linked to the user
        addresses = db.query(Address).filter(Address.user_id == user.id).all()

        if not addresses:
            await update.callback_query.message.reply_text("No addresses found for this user.")
            return ACTION

        # Store the addresses in the context to use later for deletion
        context.user_data['addresses'] = addresses

        # Prepare the response with numbered addresses
        address_list = "\n".join([f"{i+1}. {addr.full_address}" for i, addr in enumerate(addresses)])
        response_message = f"{phrases['subscribed']}\n{address_list}\n\n{phrases['enter_number_delete']}"

        # Send the message to the user
        await update.callback_query.message.reply_text(response_message)

        return DELETE

    except Exception as e:
        db.rollback()
        await update.callback_query.message.reply_text(f"An error occurred: {e}")
        raise e
    finally:
        db.close()
        

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete the selected address after user input and return to action state."""
    
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    try:
        # Get the user's input (number) and the list of addresses from context
        user_input = int(update.message.text.strip())
        addresses = context.user_data.get('addresses', [])

        if user_input < 1 or user_input > len(addresses):
            await update.message.reply_text(phrases['invalid_input'])
            return DELETE

        # Get the address to delete based on the user's input
        address_to_delete = addresses[user_input - 1]

        # Open database session
        db: Session = SessionLocal()
        try:
            # Delete the selected address
            db.delete(address_to_delete)
            db.commit()

            await update.message.reply_text(f"{phrases['address']} '{address_to_delete.full_address}' {phrases['was_deleted']}")

        except Exception as e:
            db.rollback()
            await update.message.reply_text(f"An error occurred: {e}")
            raise e
        finally:
            db.close()

        # After deletion, return to the action state to allow user to select a new action
        return await prompt_action(update, context)

    except ValueError:
        await update.message.reply_text(phrases['invalid_input'])
        return DELETE




def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            ACTION: [CallbackQueryHandler(action)],
            AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, area)],
            STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, street)],
            HOUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, house)],
            SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, summary)],
            LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, list_addresses)],
            DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)], 
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))

    application.run_polling()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user_language = context.user_data.get('language', 'English')
    phrases = PHRASES[user_language]

    await update.message.reply_text(phrases['bye'], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    main()
