import telebot
import requests
import json
import os
import datetime
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = "8275855750:AAGxudXXWSGu56bC4d1tF3Url2DGCGBEbbs"  # ⚠️ APNA BOT TOKEN YAHIN DAALEIN
ADMIN_ID = 7945122206               # ⚠️ APNA TELEGRAM USER ID (Numeric) YAHIN DAALEIN
ADMIN_USERNAME = "@tg_jacker"       # ⚠️ APNA TELEGRAM USERNAME YAHIN DAALEIN
DEFAULT_CREDITS = 10                # Naye users ko default credits

# Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)

# --- DATABASE SETUP ---
DB_FILE = "database.json"

default_db = {
    "users": {},
    "banned": [],
    "special": [],
    "history": []
}

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump(default_db, f, indent=4)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- HELPERS ---
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

def is_banned(user_id):
    db = load_db()
    return str(user_id) in db["banned"]

def is_special(user_id):
    db = load_db()
    return str(user_id) in db["special"] or is_admin(user_id)

def get_user_credits(user_id):
    db = load_db()
    return db["users"].get(str(user_id), {}).get("credits", 0)

def refund_credit(user_id):
    db = load_db()
    uid = str(user_id)
    if uid in db["users"]:
        db["users"][uid]["credits"] += 1
        save_db(db)
        return True
    return False

def get_buy_credits_text(user_id):
    try:
        current_credits = get_user_credits(user_id)
    except:
        current_credits = 0

    admin_username = "tg_jacker"   # 👈 yaha apna username daal do (without @)

    text = (
        "💳 *KAIFU OSINT*\n"
        "💳 *Credit Packs and Pricing*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        "💎 *1 – 100 Credits*\n"
        "₹2 per Credit\n"
        "Example: 50 Credits = ₹100\n\n"
        
        "💎 *101 – 499 Credits*\n"
        "₹1.5 per Credit\n"
        "Example: 200 Credits = ₹300\n\n"
        
        "💎 *500+ Credits*\n"
        "₹1 per Credit\n"
        "Example: 500 Credits = ₹500\n\n"
        
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📥 *Payment Method:*\n"
        "UPI: `mohd.kaifu@sbi`\n\n"
        
        f"After payment, send screenshot to Admin: @{admin_username}\n\n"
        f"💰 *Your Current Credits:* `{current_credits}`"
    )

    return text

# --- KEYBOARDS ---

def user_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_services = types.KeyboardButton("🔍 Available Services")
    btn_credits = types.KeyboardButton("💰 My Credits")
    btn_id = types.KeyboardButton("🆔 My ID")
    btn_rate = types.KeyboardButton("📊 Credit Rate Chart") 
    
    if is_admin(user_id):
        btn_admin = types.KeyboardButton("🔐 Admin Panel")
        markup.add(btn_services, btn_credits, btn_id, btn_rate, btn_admin)
    else:
        markup.add(btn_services, btn_credits, btn_id, btn_rate)
    return markup

def services_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_ind = types.KeyboardButton("🇮🇳 India Number Info")
    btn_pak = types.KeyboardButton("🇵🇰 Pakistan Number Info")
    btn_aadhar = types.KeyboardButton("🪪 Aadhar Card Info") # NEW BUTTON
    btn_pin = types.KeyboardButton("📮 Pincode Info")
    btn_veh = types.KeyboardButton("🚘 Vehicle Info")
    btn_track = types.KeyboardButton("🔍 IND Number Tracker")
    btn_ifsc = types.KeyboardButton("🏦 IFSC Code Info")
    btn_gst = types.KeyboardButton("📋 GST Info")
    btn_cnic = types.KeyboardButton("🆔 Pakistan CNIC Info")
    btn_back = types.KeyboardButton("🔙 Back to Main Menu")
    
    # Added btn_aadhar in layout
    markup.add(btn_ind, btn_pak, btn_aadhar, btn_pin, btn_veh, btn_track, btn_ifsc, btn_gst, btn_cnic, btn_back)
    return markup

def admin_panel():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_ban = types.KeyboardButton("🚫 Ban User")
    btn_unban = types.KeyboardButton("✅ Unban User")
    btn_add = types.KeyboardButton("➕ Add Credits")
    btn_remove = types.KeyboardButton("➖ Remove Credits")
    
    # NEW BUTTONS ADDED HERE
    btn_total_users = types.KeyboardButton("👥 Total Users")
    btn_user_history = types.KeyboardButton("📜 User All History")
    btn_active_status = types.KeyboardButton("📈 User Active Status")
    
    btn_broadcast = types.KeyboardButton("📢 Broadcast")
    btn_special = types.KeyboardButton("🌟 Add Special User")
    btn_rmspecial = types.KeyboardButton("❌ Remove Special User")
    btn_history = types.KeyboardButton("📜 Check History")
    btn_back = types.KeyboardButton("🔙 Back to Main Menu")
    
    markup.add(btn_ban, btn_unban, btn_add, btn_remove, 
               btn_total_users, btn_user_history, btn_active_status, # Added in layout
               btn_broadcast, btn_special, btn_rmspecial, btn_history, btn_back)
    return markup

# --- SAFE DELETE FUNCTION ---
def safe_delete(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

# --- HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    db = load_db()

    if user_id not in db["users"]:
        db["users"][user_id] = {
            "credits": DEFAULT_CREDITS,
            "name": message.from_user.first_name
        }
        save_db(db)

    if is_banned(user_id):
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return

    welcome_text = (
        f"👋 Welcome {message.from_user.first_name}!\n\n"
        f"🔍 I am an OSINT Bot. Use the buttons below to fetch info.\n\n"
        f"⚡ Powered by: @tg_jacker"
    )
    bot.send_message(user_id, welcome_text, reply_markup=user_menu(user_id))

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_id = str(message.chat.id)
    text = message.text
    db = load_db()

    if is_banned(user_id) and not is_admin(user_id):
        bot.reply_to(message, "🚫 You are banned.")
        return

    # --- MAIN MENU BUTTONS ---
    if text == "🔍 Available Services":
        services_text = (
            "🔍 *Available Services*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ 🇮🇳 India Number Info\n"
            "✅ 🇵🇰 Pakistan Number Info\n"
            "✅ 🪪 Aadhar Card Info\n"  # ADDED IN LIST
            "✅ 📮 Pincode Info\n"
            "✅ 🚘 Vehicle Info\n"
            "✅ 🔍 IND Number Tracker\n"
            "✅ 🏦 IFSC Code Info\n"
            "✅ 📋 GST Info\n"
            "✅ 🆔 Pakistan CNIC Info\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 *Select a service below:*"
        )
        bot.send_message(user_id, services_text, parse_mode="Markdown", reply_markup=services_menu())

    elif text == "💰 My Credits":
        credits = db["users"].get(user_id, {}).get("credits", 0)
        special_status = "Yes 🌟" if is_special(user_id) else "No"
        bot.reply_to(message, f"💰 Your Credits: {credits}\n🌟 Special User: {special_status}")

    elif text == "🆔 My ID":
        bot.reply_to(message, f"🆔 *Your Telegram ID:*\n`{user_id}`\n\n_Copy this ID and send it to Admin for credits._", parse_mode="Markdown")

    elif text == "📊 Credit Rate Chart":
        bot.send_message(user_id, get_buy_credits_text(user_id))

    elif text == "🔙 Back to Main Menu":
        bot.send_message(user_id, "🏠 Main Menu Opened.", reply_markup=user_menu(user_id))

    # --- SERVICES LOGIC ---
    elif text in ["🇮🇳 India Number Info", "🇵🇰 Pakistan Number Info", "🪪 Aadhar Card Info", "📮 Pincode Info", 
                  "🚘 Vehicle Info", "🔍 IND Number Tracker", "🏦 IFSC Code Info", 
                  "📋 GST Info", "🆔 Pakistan CNIC Info"]:
        
        # Check Credits
        if not is_special(user_id):
            if db["users"].get(user_id, {}).get("credits", 0) <= 0:
                bot.reply_to(message, "❌ *Insufficient Credits!*\nPlease buy credits to use this service.", parse_mode="Markdown")
                bot.send_message(user_id, get_buy_credits_text(user_id), parse_mode="Markdown")
                return

        prompt_msg = "Send your query:"
        
        if text == "🇮🇳 India Number Info":
            prompt_msg = "📩 Send 10-digit Mobile Number:\n\nExample: `9876543210`"
        elif text == "🇵🇰 Pakistan Number Info":
            prompt_msg = "📩 Send Pakistan Mobile Number:\n\nExample: `923001234567`"
        elif text == "🪪 Aadhar Card Info":
            prompt_msg = "📩 Send 12-digit Aadhar Number:\n\nExample: `222222222222`"
        elif text == "📮 Pincode Info":
            prompt_msg = "📩 Send Pincode:\n\nExample: `110001`"
        elif text == "🚘 Vehicle Info":
            prompt_msg = "📩 Send Vehicle Number:\n\nExample: `HR26EV0001`"
        elif text == "🔍 IND Number Tracker":
            prompt_msg = "📩 Send Mobile Number for Tracking:\n\nExample: `9876543210`"
        elif text == "🏦 IFSC Code Info":
            prompt_msg = "📩 Send IFSC Code:\n\nExample: `SBIN0001234`"
        elif text == "📋 GST Info":
            prompt_msg = "📩 Send GST Number:\n\nExample: `29AABCU9603R1ZM`"
        elif text == "🆔 Pakistan CNIC Info":
            prompt_msg = "📩 Send CNIC Number:\n\nExample: `3520112345671`"
            
        bot.reply_to(message, prompt_msg, parse_mode="Markdown")
        bot.register_next_step_handler(message, process_service_query_wrapper, text)

    # --- ADMIN PANEL BUTTON ---
    elif text == "🔐 Admin Panel":
        if is_admin(user_id):
            bot.send_message(user_id, "👑 Admin Panel Opened.", reply_markup=admin_panel())
        else:
            bot.reply_to(message, "🚫 Unauthorized.")

    # --- ADMIN FUNCTIONS ---
    elif is_admin(user_id):
        if text == "🚫 Ban User":
            bot.reply_to(message, "Enter User ID to BAN:")
            bot.register_next_step_handler(message, ban_user)
        elif text == "✅ Unban User":
            bot.reply_to(message, "Enter User ID to UNBAN:")
            bot.register_next_step_handler(message, unban_user)
        elif text == "➕ Add Credits":
            bot.reply_to(message, "Enter User ID:")
            bot.register_next_step_handler(message, ask_credits_add)
        elif text == "➖ Remove Credits":
            bot.reply_to(message, "Enter User ID:")
            bot.register_next_step_handler(message, ask_credits_remove)
        
        # --- NEW ADMIN FUNCTIONS ---
        elif text == "👥 Total Users":
            show_total_users(message)
        elif text == "📜 User All History":
            bot.reply_to(message, "📩 Send User ID to view their history:")
            bot.register_next_step_handler(message, show_user_history)
        elif text == "📈 User Active Status":
            check_active_status(message)
            
        elif text == "🌟 Add Special User":
            bot.reply_to(message, "Enter User ID:")
            bot.register_next_step_handler(message, add_special_user)
        elif text == "❌ Remove Special User":
            bot.reply_to(message, "Enter User ID:")
            bot.register_next_step_handler(message, remove_special_user)
        elif text == "📢 Broadcast":
            bot.reply_to(message, "Enter message to broadcast:")
            bot.register_next_step_handler(message, broadcast_message)
        elif text == "📜 Check History":
            show_full_history(message)
        else:
            bot.reply_to(message, "⚠️ Unknown Command. Use the buttons.")
    else:
        bot.reply_to(message, "⚠️ Please use the buttons provided.")

def process_service_query_wrapper(message, service_name):
    process_service_query(message, service_name)

# --- SERVICE PROCESSOR ---
def process_service_query(message, service_name):
    user_id = str(message.chat.id)
    query = message.text.strip()
    db = load_db()
    
    # Deduct Credit
    if not is_special(user_id):
        if db["users"].get(user_id, {}).get("credits", 0) <= 0:
            bot.reply_to(message, "❌ No credits left.")
            return
        db["users"][user_id]["credits"] -= 1
        save_db(db)

    # Save History
    current_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db["history"].append({"user_id": user_id, "service": service_name, "query": query, "time": current_time})
    save_db(db)

    status_msg = bot.send_message(user_id, "⏳ Fetching data...")

    try:
        # --- 1. INDIA NUMBER INFO ---
        if service_name == "🇮🇳 India Number Info":
            url = f"https://kaifu-ind-num-tucq.vercel.app/api/number_info?number={query}&key=kaifu"
            try:
                res = requests.get(url, timeout=20).json()
                if "data" in res and len(res["data"]) > 0:
                    count = res.get('total_results', 0)
                    summary_msg = (
                        f"✅ *DATA FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📱 *Number:* `{query}`\n"
                        f"📊 *Total Results:* {count}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"_Sending detailed info below..._"
                    )
                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, summary_msg, parse_mode="Markdown")
                    
                    for d in res["data"]:
                        single_result_msg = (
                            f"👤 *Name:* `{d.get('name', 'N/A')}`\n"
                            f"👨‍👩‍👦 *Father:* `{d.get('father_name', 'N/A')}`\n"
                            f"🪪 *ID Number:* `{d.get('id_number', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📱 *Mobile:* `{d.get('mobile', 'N/A')}`\n"
                            f"📞 *Alt Num:* `{d.get('alt_number', 'N/A')}`\n"
                            f"📧 *Email:* `{d.get('email', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📍 *Address:*\n`{d.get('address', 'N/A')}`\n"
                            f"🗺 *Circle:* `{d.get('circle', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━"
                        )
                        bot.send_message(user_id, single_result_msg, parse_mode="Markdown")
                    bot.send_message(user_id, f"⚡ *Credit:* {res.get('api_credit', 'N/A')}")
                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ No data found. 💸 Credit Refunded.")
            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

        # --- 2. PAKISTAN NUMBER INFO ---
        elif service_name == "🇵🇰 Pakistan Number Info":
            url = f"https://kaifu-pak-num-cnic-info.vercel.app/api/lookup?mobile={query}&key=nawab&pretty=1"
            try:
                res = requests.get(url, timeout=20).json()
                if "results" in res and len(res["results"]) > 0:
                    count = res.get('results_count', 0)
                    summary_msg = (
                        f"✅ *DATA FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📱 *Number:* `{query}`\n"
                        f"📊 *Total Records:* {count}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"_Sending detailed info below..._"
                    )
                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, summary_msg, parse_mode="Markdown")
                    
                    for r in res["results"]:
                        single_result_msg = (
                            f"👤 *Name:* `{r.get('name', 'N/A')}`\n"
                            f"🆔 *CNIC:* `{r.get('cnic', 'N/A')}`\n"
                            f"📱 *Mobile:* `{r.get('mobile', 'N/A')}`\n"
                            f"📍 *Address:* `{r.get('address', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━"
                        )
                        bot.send_message(user_id, single_result_msg, parse_mode="Markdown")
                    bot.send_message(user_id, f"👉🏻 {res.get('copyright', '')}")
                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ No data found. 💸 Credit Refunded.")
            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

        # --- 3. AADHAR CARD INFO (NEW SERVICE) ---
        elif service_name == "🪪 Aadhar Card Info":
            url = f"https://aadhar-info-lime.vercel.app/api/aadhar_info?key=kaifu&number={query}"
            try:
                res = requests.get(url, timeout=20).json()
                if "data" in res and len(res["data"]) > 0:
                    count = res.get('total_results', 0)
                    summary_msg = (
                        f"✅ *AADHAR DATA FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🪪 *Aadhar:* `{query}`\n"
                        f"📊 *Total Results:* {count}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"_Sending detailed info below..._"
                    )
                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, summary_msg, parse_mode="Markdown")
                    
                    for d in res["data"]:
                        single_result_msg = (
                            f"👤 *Name:* `{d.get('NAME', 'N/A')}`\n"
                            f"👨‍👩‍👦 *Father:* `{d.get('FATHER_NAME', 'N/A')}`\n"
                            f"🪪 *Aadhar:* `{d.get('AADHAR CARD', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📱 *Mobile:* `{d.get('MOBILE', 'N/A')}`\n"
                            f"📞 *Alt Num:* `{d.get('ALT_NUMBER', 'N/A')}`\n"
                            f"📧 *Email:* `{d.get('EMAIL', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📍 *Address:*\n`{d.get('ADDRESS', 'N/A')}`\n"
                            f"🗺 *Circle:* `{d.get('CIRCLE', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━"
                        )
                        bot.send_message(user_id, single_result_msg, parse_mode="Markdown")
                    
                    bot.send_message(user_id, f"⚡ *Credit:* {res.get('api_credit', 'N/A')}\n👑 *Owner:* {res.get('api_owner', 'N/A')}")
                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ No data found for this Aadhar. 💸 Credit Refunded.")
            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

        # --- 4. PAKISTAN CNIC INFO ---
        elif service_name == "🆔 Pakistan CNIC Info":
            url = f"https://kaifu-pak-num-cnic-info.vercel.app/api/lookup?cnic={query}&key=nawab&pretty=1"
            try:
                res = requests.get(url, timeout=20).json()
                if "results" in res and len(res["results"]) > 0:
                    count = res.get('results_count', 0)
                    summary_msg = (
                        f"✅ *CNIC DATA FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 *CNIC:* `{query}`\n"
                        f"📊 *Total Records:* {count}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"_Sending detailed info below..._"
                    )
                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, summary_msg, parse_mode="Markdown")
                    
                    for r in res["results"]:
                        single_result_msg = (
                            f"👤 *Name:* `{r.get('name', 'N/A')}`\n"
                            f"📱 *Mobile:* `{r.get('mobile', 'N/A')}`\n"
                            f"📍 *Address:* `{r.get('address', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━"
                        )
                        bot.send_message(user_id, single_result_msg, parse_mode="Markdown")
                    bot.send_message(user_id, f"👉🏻 {res.get('copyright', '')}")
                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ No data found for this CNIC. 💸 Credit Refunded.")
            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

        # --- 5. PINCODE INFO ---
        elif service_name == "📮 Pincode Info":
            url = f"https://kaifu-pin.vercel.app/api/lookup?pin={query}&key=kaifu"
            try:
                res = requests.get(url, timeout=20).json()
                if res.get("status") == "ok" and "records" in res and len(res["records"]) > 0:
                    count = res.get('count', 0)
                    summary_msg = (
                        f"✅ *PINCODE INFO FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📍 *Pincode:* `{query}`\n"
                        f"📊 *Total Offices:* {count}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"_Sending detailed info below..._"
                    )
                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, summary_msg, parse_mode="Markdown")
                    
                    for r in res["records"]:
                        single_result_msg = (
                            f"🏢 *Office:* `{r.get('post_office', 'N/A')}`\n"
                            f"🏷 *Status:* `{r.get('post_office_status', 'N/A')}`\n"
                            f"📞 *Phone:* `{r.get('telephone', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🏙 *Taluk:* `{r.get('town_taluk', 'N/A')}`\n"
                            f"📍 *District:* `{r.get('district', 'N/A')}`\n"
                            f"🗺 *State:* `{r.get('state', 'N/A')}`\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📩 *Division:* `{r.get('postal_division', 'N/A')}`\n"
                            f"📍 *Region:* `{r.get('postal_region', 'N/A')}`"
                        )
                        bot.send_message(user_id, single_result_msg, parse_mode="Markdown")
                    bot.send_message(user_id, f"⚡ *Credit:* {res['meta'].get('author', '')}")
                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ Invalid Pincode. 💸 Credit Refunded.")
            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

       # --- 6. VEHICLE INFO ---
        elif service_name == "🚘 Vehicle Info":

            url = f"https://kaifu-vehicle-info.vercel.app/api/lookup?rc={query}&key=NAWAB"

            try:
                response = requests.get(url, timeout=20)
                res = response.json()

                if res.get("Owner Name"):

                    result_data = (
                        f"🚘 VEHICLE INFO FOUND!\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 Owner: {res.get('Owner Name', 'N/A')}\n"
                        f"🔄 Owner Serial: {res.get('Owner Serial No', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🚗 Model: {res.get('Modal Name', 'N/A')}\n"
                        f"🏭 Maker: {res.get('Model Name', 'N/A')}\n"
                        f"🔢 Reg No: {res.get('Registration Number', 'N/A')}\n"
                        f"🏷 Vehicle Class: {res.get('Vehicle Class', 'N/A')}\n"
                        f"⛽ Fuel Type: {res.get('Fuel Type', 'N/A')}\n"
                        f"🛡 Fuel Norms: {res.get('Fuel Norms', 'N/A')}\n"
                        f"⚙ Cubic Cap: {res.get('Cubic Capacity', 'N/A')}\n"
                        f"🪑 Seats: {res.get('Seating Capacity', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📅 Reg Date: {res.get('Registration Date', 'N/A')}\n"
                        f"⏳ Vehicle Age: {res.get('Vehicle Age', 'N/A')}\n"
                        f"📍 RTO: {res.get('Registered RTO', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🛡 Insurance: {res.get('Insurance Company', 'N/A')}\n"
                        f"⏰ Ins Upto: {res.get('Insurance Upto', 'N/A')}\n"
                        f"⚠ Ins Status: {res.get('Insurance Expiry In', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💪 Fitness Upto: {res.get('Fitness Upto', 'N/A')}\n"
                        f"🚗 PUC Upto: {res.get('PUC Upto', 'N/A')}\n"
                        f"⚠ PUC Status: {res.get('PUC Expiry In', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔩 Chassis: {res.get('Chassis Number', 'N/A')}\n"
                        f"⚙ Engine: {res.get('Engine Number', 'N/A')}\n"
                        f"🏦 Financier: {res.get('Financier Name', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📜 Permit: {res.get('Permit Type', 'N/A')}\n"
                        f"🚫 Blacklist: {res.get('Blacklist Status', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ Credit: {res.get('credits', 'N/A')}"
                    )

                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, result_data)

                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ Vehicle data not found. 💸 Credit Refunded.")

            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")
        
        # --- 7. IND NUMBER TRACKER ---
        elif service_name == "🔍 IND Number Tracker":
            url = f"https://kaifu-tracker.vercel.app/track/{query}?key=kaifu"
            try:
                res = requests.get(url, timeout=20).json()

                if res.get("status") == "ok" and "data" in res:
                    d = res["data"]

                    result_data = (
                        f"🔍 TRACKER INFO FOUND!\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📱 Number: {d.get('Number', 'N/A')}\n"
                        f"📡 SIM: {d.get('SIM card', 'N/A')}\n"
                        f"🏙 City: {d.get('City', 'N/A')}\n"
                        f"🌍 Country: {d.get('Country', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📍 Mobile Locs:\n{d.get('Mobile Locations', 'N/A')}\n"
                        f"📶 Tower Locs:\n{d.get('Tower Locations', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📞 Helpline: {d.get('Helpline', 'N/A')}\n"
                        f"🚨 Complaints: {d.get('Complaints', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📍 Google Map:\n{d.get('Google_Map_Link', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ Credit: {res.get('meta', {}).get('author', 'N/A')}"
                    )

                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, result_data, disable_web_page_preview=True)

                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ Tracker data not found. 💸 Credit Refunded.")

            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

        # --- 8. GST INFO ---
        elif service_name == "📋 GST Info":
            url = f"https://kaifu-gst.vercel.app/api/lookup?gst={query}&key=kaifu"
            try:
                res = requests.get(url, timeout=20).json()

                if res.get("status") == "ok" and "data" in res:
                    d = res["data"]

                    result_data = (
                        f"📋 GST DETAILS FOUND!\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏢 Legal Name: {d.get('legal_name_of_business', 'N/A')}\n"
                        f"🏷 Trade Name: {d.get('trade_name', 'N/A')}\n"
                        f"🆔 GSTIN: {d.get('gstin_uin_number', 'N/A')}\n"
                        f"✅ Status: {d.get('gstin_uin_status', 'N/A')}\n"
                        f"🏢 Business Type: {d.get('constitution_of_business', 'N/A')}\n"
                        f"👥 Taxpayer Type: {d.get('taxpayer_type', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📍 Address:\n{d.get('address', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📅 Registration Date: {d.get('registration_date', 'N/A')}\n"
                        f"🏛 State Jurisdiction: {d.get('state_jurisdiction', 'N/A')}\n"
                        f"🏛 Centre Jurisdiction: {d.get('centre_jurisdiction', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💼 Nature of Business:\n{d.get('nature_of_business_activities', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━"
                    )

                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, result_data)

                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ GST data not found. 💸 Credit Refunded.")

            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

        # --- 9. IFSC CODE INFO ---
        elif service_name == "🏦 IFSC Code Info":
            url = f"https://kaifu-ifsc.vercel.app/api/ifsc?ifsc={query}&key=kaifu"
            try:
                res = requests.get(url, timeout=20).json()

                if "BANK" in res:
                    result_data = (
                        f"🏦 BANK DETAILS FOUND!\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏢 Bank Name: {res.get('BANK', 'N/A')}\n"
                        f"🏢 Branch: {res.get('BRANCH', 'N/A')}\n"
                        f"🆔 IFSC Code: {res.get('IFSC', 'N/A')}\n"
                        f"🔢 Bank Code: {res.get('BANKCODE', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📍 Address: {res.get('ADDRESS', 'N/A')}\n"
                        f"🏙 City: {res.get('CITY', 'N/A')}\n"
                        f"🗺 State: {res.get('STATE', 'N/A')}\n"
                        f"📍 District: {res.get('DISTRICT', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📞 Contact: {res.get('CONTACT', 'N/A')}\n"
                        f"🔢 MICR Code: {res.get('MICR', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ UPI: {res.get('UPI', 'N/A')}\n"
                        f"✅ NEFT: {res.get('NEFT', 'N/A')}\n"
                        f"✅ RTGS: {res.get('RTGS', 'N/A')}\n"
                        f"✅ IMPS: {res.get('IMPS', 'N/A')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ Credit: {res.get('credits', 'N/A')}"
                    )

                    safe_delete(user_id, status_msg.message_id)
                    bot.send_message(user_id, result_data)
                else:
                    safe_delete(user_id, status_msg.message_id)
                    refund_credit(user_id)
                    bot.send_message(user_id, "⚠️ Invalid IFSC Code. 💸 Credit Refunded.")

            except Exception as e:
                safe_delete(user_id, status_msg.message_id)
                refund_credit(user_id)
                bot.send_message(user_id, f"⚠️ API Error/Timeout. 💸 Credit Refunded.\nError: {e}")

    except Exception as e:
        safe_delete(user_id, status_msg.message_id)
        refund_credit(user_id)
        bot.send_message(user_id, f"⚠️ Unexpected Error. 💸 Credit Refunded.\n{e}")

# --- ADMIN FUNCTIONS (OLD) ---
def ban_user(message):
    target_id = str(message.text.strip())
    db = load_db()
    if target_id not in db["banned"]:
        db["banned"].append(target_id)
        save_db(db)
        bot.reply_to(message, f"✅ User {target_id} BANNED.")
        # Notify User
        try:
            bot.send_message(int(target_id), "🚫 *Attention!*\n\nYou have been **BANNED** from using this bot by the Admin.", parse_mode="Markdown")
        except:
            pass
    else:
        bot.reply_to(message, "User already banned.")

def unban_user(message):
    target_id = str(message.text.strip())
    db = load_db()
    if target_id in db["banned"]:
        db["banned"].remove(target_id)
        save_db(db)
        bot.reply_to(message, f"✅ User {target_id} UNBANNED.")
        # Notify User
        try:
            bot.send_message(int(target_id), "✅ *Good News!*\n\nYou have been **UNBANNED**. You can use the bot now.", parse_mode="Markdown")
        except:
            pass
    else:
        bot.reply_to(message, "User not banned.")

def ask_credits_add(message):
    target_id = str(message.text.strip())
    bot.reply_to(message, "Enter amount to ADD:")
    bot.register_next_step_handler(message, lambda m: change_credits(m, target_id, "add"))

def ask_credits_remove(message):
    target_id = str(message.text.strip())
    bot.reply_to(message, "Enter amount to REMOVE:")
    bot.register_next_step_handler(message, lambda m: change_credits(m, target_id, "remove"))

def change_credits(message, target_id, mode):
    try:
        amount = int(message.text.strip())
        db = load_db()
        if target_id in db["users"]:
            if mode == "add":
                db["users"][target_id]["credits"] += amount
                save_db(db)
                new_bal = db["users"][target_id]["credits"]
                bot.reply_to(message, f"✅ Done. New Balance: {new_bal}")
                # Notify User
                try:
                    bot.send_message(int(target_id), f"💰 *Credits Added!*\n\n✅ Amount: +{amount}\n💳 New Balance: {new_bal}", parse_mode="Markdown")
                except: pass
            else:
                db["users"][target_id]["credits"] = max(0, db["users"][target_id]["credits"] - amount)
                save_db(db)
                new_bal = db["users"][target_id]["credits"]
                bot.reply_to(message, f"✅ Done. New Balance: {new_bal}")
                # Notify User
                try:
                    bot.send_message(int(target_id), f"💸 *Credits Removed!*\n\n❌ Amount: -{amount}\n💳 New Balance: {new_bal}", parse_mode="Markdown")
                except: pass
        else:
            bot.reply_to(message, "User not found in DB.")
    except:
        bot.reply_to(message, "Invalid number.")

def add_special_user(message):
    target_id = str(message.text.strip())
    db = load_db()
    if target_id not in db["special"]:
        db["special"].append(target_id)
        save_db(db)
        bot.reply_to(message, "🌟 Special User Added.")

def remove_special_user(message):
    target_id = str(message.text.strip())
    db = load_db()
    if target_id in db["special"]:
        db["special"].remove(target_id)
        save_db(db)
        bot.reply_to(message, "❌ Special User Removed.")

def broadcast_message(message):
    msg = message.text
    db = load_db()
    count = 0
    for uid in db["users"]:
        try:
            bot.send_message(int(uid), f"📢 *Broadcast:*\n\n{msg}", parse_mode="Markdown")
            count += 1
        except: pass
    bot.reply_to(message, f"✅ Sent to {count} users.")

def show_full_history(message):
    db = load_db()
    hist = db.get("history", [])
    if not hist:
        bot.reply_to(message, "No history.")
        return
    buff = "📜 *History:*\n\n"
    for h in hist:
        entry = f"User: `{h['user_id']}`\nService: {h['service']}\nQuery: `{h['query']}`\nTime: {h['time']}\n-------------------\n"
        if len(buff) + len(entry) > 3800:
            bot.send_message(message.chat.id, buff, parse_mode="Markdown")
            buff = ""
        buff += entry
    if len(buff) > 0:
        bot.send_message(message.chat.id, buff, parse_mode="Markdown")

# --- NEW ADMIN FUNCTIONS ---

# 1. Total Users
def show_total_users(message):
    db = load_db()
    total_users = len(db["users"])
    total_banned = len(db["banned"])
    total_special = len(db["special"])
    text = (
        f"👥 *Bot Statistics:*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Total Users: `{total_users}`\n"
        f"🚫 Banned Users: `{total_banned}`\n"
        f"🌟 Special Users: `{total_special}`"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# 2. User All History
def show_user_history(message):
    target_id = str(message.text.strip())
    db = load_db()
    user_history = [h for h in db.get("history", []) if h['user_id'] == target_id]
    
    if not user_history:
        bot.reply_to(message, f"⚠️ No history found for User ID: `{target_id}`", parse_mode="Markdown")
        return

    buff = f"📜 *History for User: `{target_id}`*\n\n"
    for h in user_history:
        entry = f"Service: {h['service']}\nQuery: `{h['query']}`\nTime: {h['time']}\n-------------------\n"
        if len(buff) + len(entry) > 3800:
            bot.send_message(message.chat.id, buff, parse_mode="Markdown")
            buff = ""
        buff += entry
    
    if len(buff) > 0:
        bot.send_message(message.chat.id, buff, parse_mode="Markdown")

# 3. User Active Status
def check_active_status(message):
    db = load_db()
    if not db["users"]:
        bot.reply_to(message, "No users in database.")
        return

    buff = "📈 *User Active Status (Last 24 Hours):*\n"
    buff += "━━━━━━━━━━━━━━━━━━━━\n"
    
    now = datetime.datetime.now()
    active_count = 0
    inactive_count = 0
    
    # We will only show the count summary to avoid flooding if users are many
    # But if you want a list, uncomment the lines below
    
    for uid in db["users"]:
        # Find last activity
        last_active_str = "Never"
        is_active = False
        
        # Check history for this user
        user_hist = [h for h in db["history"] if h['user_id'] == uid]
        if user_hist:
            last_time_str = user_hist[-1]['time'] # Get last entry
            try:
                last_time = datetime.datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
                if (now - last_time).total_seconds() < 86400: # 24 hours
                    is_active = True
            except:
                pass
        
        if is_active:
            active_count += 1
        else:
            inactive_count += 1

    buff += (
        f"🟢 Active Users (24h): `{active_count}`\n"
        f"🔴 Inactive Users: `{inactive_count}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_Active = Used bot in last 24 hours._"
    )
    
    bot.reply_to(message, buff, parse_mode="Markdown")

# --- START ---
print("Bot Running Successfully...")
bot.infinity_polling()