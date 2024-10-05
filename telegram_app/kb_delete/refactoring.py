# REFACTORING


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Starts the conversation, describes bot functionality, and asks the user to choose a language."""
#     reply_keyboard = [['Serbian', "English", "Russian"]]
#     await update.message.reply_text(
#         f'<b>{PHRASES["English"]["welcome"]}</b>',
#         parse_mode='HTML',
#         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
#     )
#     return LANGUAGE

# async def prompt_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Prompt the user to choose an action after an operation like delete."""
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]

#     keyboard = [
#         [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
#         [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
#         [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     # Prompt the user to choose the next action
#     await update.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)

#     return ACTION
# async def prompt_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Prompt the user to choose an action."""
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]
#     reply_markup = get_action_keyboard(user_language)
#     await send_message(update, phrases["choose_action"], reply_markup=reply_markup)
#     return ACTION 
# async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the user's language and provides options based on the selected language."""
#     user_language = update.message.text
#     context.user_data['language'] = user_language
#     if user_language not in PHRASES:
#         await update.message.reply_text(PHRASES['English']['invalid_language'])
#         return LANGUAGE

#     phrases = PHRASES[user_language]
#     await update.message.reply_text(
#         f'<b>{phrases["choose_action"]}</b>',
#         parse_mode='HTML',
#         reply_markup=ReplyKeyboardRemove(),
#     )

#     keyboard = [
#         [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
#         [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
#         [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)
#     return ACTION


# async def area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]
  
#     if not validate_area(update.message.text):
#         await update.message.reply_text(phrases['enter_area'])
#         return AREA
    
#     context.user_data['area'] = update.message.text
#     await update.message.reply_text(phrases['enter_street'])
#     return STREET

# async def street(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]
    
#     if not validate_street(update.message.text):
#         await update.message.reply_text(phrases['enter_street'])
#         return STREET
    
#     context.user_data['street'] = update.message.text
#     await update.message.reply_text(phrases['enter_house'])
#     return HOUSE


# async def house(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]
    
#     if not validate_house(update.message.text):
#         await update.message.reply_text(phrases['enter_house'])
#         return HOUSE
    
#     # Store the house number in user_data
#     context.user_data['house'] = update.message.text
    
#     # Move directly to the summary after house number is entered
#     return await summary(update, context)

# async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]
#     area = context.user_data.get('area', 'N/A')
#     street = context.user_data.get('street', 'N/A')
#     house = context.user_data.get('house', 'N/A')
    
#     summary_message = f"{area}, {street}, {house}"
    
#     # User:
#     user_data = update.effective_user
#     telegram_id = user_data.id
#     first_name = user_data.first_name
#     last_name = user_data.last_name
#     username = user_data.username
#     is_bot = user_data.is_bot
#     language_code = user_data.language_code
    
#     # Address
#     full_address = summary_message
#     area = area
#     street = street
#     house_number = house
#     confirmed_geolocation = False
    
#     # Open database session
#     db: Session = SessionLocal()
#     try:
#         # Check if the user exists
#         user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
#         if user:
#             print(f"User {user.telegram_id} exists: {user.first_name} {user.last_name}")
#         else:
#             user = User(
#                 telegram_id=telegram_id,
#                 first_name=first_name,
#                 last_name=last_name,
#                 username=username,
#                 is_bot=is_bot,
#                 language_code=language_code
#             )
#             db.add(user)
#             db.commit()
#             db.refresh(user)

#         address = Address(
#             full_address=summary_message,
#             area=area,  
#             street=street,
#             house_number=house,
#             confirmed_geolocation=False,
#             user_id=user.id
#         )
#         db.add(address)
#         db.commit()
#         db.refresh(address)

#         db: Session = SessionLocal()
#         try:
#             # TODO:  REMOVE 
#             # Check if the user exists
#             user = db.query(User).filter(User.telegram_id == telegram_id).first()
            
#             if not user:
#                 return "User not found. Please subscribe first."
            
#             # Fetch all addresses linked to the user
#             addresses = db.query(Address).filter(Address.user_id == user.id).all()
            
#             # TODO: CHANGE TO MESSAGE
#             if not addresses:
#                 return "No addresses found for this user."
            
#             # Prepare the response with all addresses
#             address_list = "\n".join([f"{addr.full_address}" for addr in addresses])
#             response_message = f"{phrases['subscribed']}\n{address_list}"
            
#             await update.message.reply_text(response_message, parse_mode="Markdown")

#         except Exception as e:
#             db.rollback()
#             print(f"Error occurred: {e}")
#             raise e
#         finally:
#             db.close()
        
#     except Exception as e:
#         db.rollback()
#         print(f"Error occurred: {e}")
#         raise e
#     finally:
#         db.close()
    
#     # REPROMPT
#     keyboard = [
#         [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
#         [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
#         [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     # Prompt the user to choose the next action
#     await update.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)
    
#     return ACTION


# async def list_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """List all addresses for the user and return to the choose action state."""
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]
#     user_data = update.effective_user
#     telegram_id = user_data.id

#     db: Session = SessionLocal()
#     try:
#         # Check if the user exists
#         user = db.query(User).filter(User.telegram_id == telegram_id).first()

#         if not user:
#             await update.callback_query.message.reply_text("User not found. Please subscribe first.")
#             return ACTION

#         addresses = db.query(Address).filter(Address.user_id == user.id).all()

#         if not addresses:
#             await update.callback_query.message.reply_text("No addresses found for this user.")
#             return ACTION
        
#         address_list = "\n".join([f"{addr.full_address}" for addr in addresses])
#         response_message = f"{phrases['subscribed']}\n{address_list}"

#         await update.callback_query.message.reply_text(response_message, parse_mode="Markdown")

#     except Exception as e:
#         db.rollback()
#         await update.callback_query.message.reply_text(f"An error occurred: {e}")
#         raise e
#     finally:
#         db.close()

#     # REPROMPT:
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]

#     keyboard = [
#         [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
#         [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
#         [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     # Prompt the user to choose the next action
#     await update.callback_query.message.reply_text(f'<b>{phrases["choose_action"]}</b>', parse_mode='HTML', reply_markup=reply_markup)

#     return ACTION



# async def delete_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Show all addresses with numbers and delete the selected one."""
#     user_language = context.user_data['language']
#     phrases = PHRASES[user_language]
#     user_data = update.effective_user
#     telegram_id = user_data.id

#     # Open database session
#     db: Session = SessionLocal()
#     try:
#         # Check if the user exists
#         user = db.query(User).filter(User.telegram_id == telegram_id).first()

#         if not user:
#             await update.callback_query.message.reply_text("User not found. Please subscribe first.")
#             return ACTION

#         addresses = db.query(Address).filter(Address.user_id == user.id).all()

#         if not addresses:
#             await update.callback_query.message.reply_text("No addresses found for this user.")
#             return ACTION

#         # Store the addresses in the context to use later for deletion
#         context.user_data['addresses'] = addresses

#         # Prepare the response with numbered addresses
#         address_list = "\n".join([f"{i+1}. {addr.full_address}" for i, addr in enumerate(addresses)])
#         response_message = f"{phrases['subscribed']}\n{address_list}\n\n{phrases['enter_number_delete']}"

#         # Send the message to the user
#         await update.callback_query.message.reply_text(response_message)

#         return DELETE

#     except Exception as e:
#         db.rollback()
#         await update.callback_query.message.reply_text(f"An error occurred: {e}")
#         raise e
#     finally:
#         db.close()