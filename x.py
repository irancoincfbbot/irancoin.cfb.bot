from datetime import datetime
import telebot
import json
from telebot import types
import os

# تنظیمات اولیه ربات
TOKEN = '7274984245:AAHX4GdWGniq0onVgZWs0LGQCZhZwkt7ymQ'
bot = telebot.TeleBot(TOKEN)

# آیدی ادمین - بعد از اجرای ربات و ارسال دستور /myid این مقدار را جایگزین کنید
ADMIN_CHAT_ID = "7477369404"

# فایل‌های تنظیمات
CONFIG_FILE = 'pair.json'
USERS_FILE = 'users.json'
TRANSACTIONS_FILE = 'transactions.json'

# تنظیمات کارمزد شبکه‌ها
NETWORK_FEES = {
    "TRC20": 1,
    "ERC20": 15,
    "BEP20": 2
}

# آدرس‌های کیف پول
WALLET_ADDRESSES = {
    "TRC20": "TPm9iyNFShxuVi74d8mc3PXdNJirE1UZXv",
    "ERC20": "0x792304df0d22937d4a5c16e6daccf2efde120481",
    "BEP20": "0xac636956031a944eac8fd4e3b0bce7a40f806187"
}

# اطلاعات بانکی
BANK_INFO = {
    "card": "5022291504998210",
    "name": "علی خانی",
    "sheba": "IR230570077700000621703001"
}

# تنظیمات پشتیبانی
SUPPORT_INFO = {
    "telegram": "@support_irancointetherbot",
    "hours": "9 صبح تا 12 شب"
}


def read_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        default_config = {
            "price": 81000,
            "buy_price": 81000,
            "sell_price": 81000,
            "min_amount": 10,
            "max_amount": 100000
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def save_user(user_id, phone_number):
    users = {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except FileNotFoundError:
        pass
    
    users[str(user_id)] = {
        "phone_number": phone_number,
        "registered_at": str(datetime.now()),
        "username": None,
        "transactions": []
    }
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def is_admin(chat_id):
    return str(chat_id) == ADMIN_CHAT_ID

def save_transaction(user_id, transaction_type, amount, network, status="pending"):
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
    except FileNotFoundError:
        transactions = []
    
    transaction = {
        "id": len(transactions) + 1,
        "user_id": user_id,
        "type": transaction_type,
        "amount": amount,
        "network": network,
        "status": status,
        "created_at": str(datetime.now())
    }
    
    transactions.append(transaction)
    
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=4)
    
    return transaction["id"]

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_btn = types.KeyboardButton("ارسال شماره تلفن", request_contact=True)
    markup.add(contact_btn)
    
    welcome_text = """
🌟 به ربات خرید و فروش تتر خوش آمدید!

برای شروع، لطفا شماره تلفن خود را با کلیک بر روی دکمه زیر ارسال کنید.

⚠️ نکته: شماره تلفن شما فقط برای احراز هویت استفاده می‌شود و محرمانه باقی می‌ماند.
"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup
    )

@bot.message_handler(commands=['myid'])
def show_id(message):
    bot.reply_to(message, f"Your Chat ID is: {message.chat.id}")

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    if message.contact is not None:
        phone_number = message.contact.phone_number
        save_user(message.chat.id, phone_number)
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "❌ خطا در دریافت شماره تماس. لطفا مجدداً تلاش کنید.")

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buy_btn = types.KeyboardButton("🟢 خرید تتر")
    sell_btn = types.KeyboardButton("🔴 فروش تتر")
    price_btn = types.KeyboardButton("💰 قیمت لحظه‌ای")
    guide_btn = types.KeyboardButton("📚 راهنما")
    support_btn = types.KeyboardButton("👨‍💻 پشتیبانی")
    
    markup.add(buy_btn, sell_btn)
    markup.add(price_btn)
    markup.add(guide_btn, support_btn)
    
    # اضافه کردن دکمه پنل ادمین برای ادمین
    if is_admin(message.chat.id):
        admin_btn = types.KeyboardButton("👨‍💼 پنل ادمین")
        markup.add(admin_btn)
    
    bot.send_message(
        message.chat.id,
        "🏠 منوی اصلی\nلطفا گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=markup
    )

def buy_tether_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)
    
    config = read_config()
    current_price = config['price']
    
    sent_msg = bot.send_message(
        message.chat.id,
        f"💵 قیمت فعلی هر تتر: {current_price:,} تومان\n\n"
        "🔹 لطفا مقدار تتر مورد نظر خود را وارد کنید.\n"
        "حداقل مقدار خرید: 10 تتر\n"
        "مثال: 50",
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, buy_tether_amount)

def buy_tether_amount(message):
    if message.text == "🔙 بازگشت":
        main_menu(message)
        return
        
    try:
        amount = float(message.text)
        if amount < 10:
            raise ValueError("مقدار کمتر از حد مجاز")
            
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        trc20_btn = types.KeyboardButton("TRC20")
        erc20_btn = types.KeyboardButton("ERC20")
        bep20_btn = types.KeyboardButton("BEP20")
        back_btn = types.KeyboardButton("🔙 بازگشت")
        markup.add(trc20_btn, erc20_btn, bep20_btn)
        markup.add(back_btn)
        
        sent_msg = bot.send_message(
            message.chat.id,
            f"✅ مقدار {amount} تتر تایید شد.\n"
            "لطفا شبکه مورد نظر خود را انتخاب کنید:",
            reply_markup=markup
        )
        bot.register_next_step_handler(sent_msg, buy_tether_network, amount)
        
    except ValueError:
        sent_msg = bot.send_message(
            message.chat.id,
            "❌ مقدار وارد شده معتبر نیست. لطفا مجددا تلاش کنید."
        )
        bot.register_next_step_handler(sent_msg, buy_tether_amount)

def buy_tether_network(message, amount):
    if message.text == "🔙 بازگشت":
        buy_tether_start(message)
        return

    if message.text not in NETWORK_FEES:
        sent_msg = bot.send_message(
            message.chat.id,
            "❌ شبکه انتخابی نامعتبر است. لطفا از دکمه‌های زیر استفاده کنید."
        )
        bot.register_next_step_handler(sent_msg, buy_tether_network, amount)
        return

    config = read_config()
    network = message.text
    fee = NETWORK_FEES[network]
    total_amount = amount + fee
    total_price = total_amount * config['price']

    payment_text = (
        f"🔹 جزئیات سفارش:\n\n"
        f"📌 مقدار تتر: {amount} USDT\n"
        f"📌 کارمزد شبکه {network}: {fee} USDT\n"
        f"📌 مجموع: {total_amount} USDT\n"
        f"📌 قیمت کل: {total_price:,} تومان\n\n"
        "💳 اطلاعات واریز:\n"
        f"📍 شماره کارت: {BANK_INFO['card']}\n"
        f"📍 به نام: {BANK_INFO['name']}\n"
        f"📍 شماره شبا: {BANK_INFO['sheba']}\n\n"
        "پس از واریز، لطفا تصویر رسید را ارسال کنید."
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)

    sent_msg = bot.send_message(
        message.chat.id,
        payment_text,
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, buy_tether_receipt, amount, network)

def buy_tether_receipt(message, amount, network):
    if message.text == "🔙 بازگشت":
        buy_tether_network(message, amount)
        return

    if not message.photo:
        sent_msg = bot.send_message(
            message.chat.id,
            "❌ لطفا تصویر رسید پرداخت را ارسال کنید."
        )
        bot.register_next_step_handler(sent_msg, buy_tether_receipt, amount, network)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)

    sent_msg = bot.send_message(
        message.chat.id,
        f"لطفا آدرس کیف پول {network} خود را وارد کنید:",
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, buy_tether_wallet, amount, network, message.photo[-1].file_id)

def buy_tether_wallet(message, amount, network, receipt_file_id):
    if message.text == "🔙 بازگشت":
        buy_tether_receipt(message, amount, network)
        return

    wallet_address = message.text

    # ذخیره تراکنش
    transaction_id = save_transaction(message.chat.id, "buy", amount, network)

    # ارسال اطلاعات به ادمین
    admin_msg = (
        f"🟢 سفارش جدید خرید تتر:\n\n"
        f"🔹 شناسه تراکنش: {transaction_id}\n"
        f"👤 کاربر: {message.from_user.username}\n"
        f"📱 شناسه: {message.chat.id}\n"
        f"💰 مقدار: {amount} USDT\n"
        f"🌐 شبکه: {network}\n"
        f"📍 آدرس کیف پول:\n{wallet_address}\n"
    )
    
    bot.send_photo(ADMIN_CHAT_ID, receipt_file_id, caption=admin_msg)

    # ارسال پیام تایید به کاربر
    confirm_text = (
        "✅ سفارش شما با موفقیت ثبت شد.\n\n"
        f"📌 شناسه تراکنش: {transaction_id}\n"
        "⏱ تتر شما حداکثر تا 30 دقیقه دیگر ارسال خواهد شد.\n\n"
        "با تشکر از خرید شما 🙏"
    )
    bot.send_message(message.chat.id, confirm_text)
    main_menu(message)

def sell_tether_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)
    
    config = read_config()
    current_price = config['price']
    
    sent_msg = bot.send_message(
        message.chat.id,
        f"💵 قیمت فعلی هر تتر: {current_price:,} تومان\n\n"
        "🔹 لطفا مقدار تتر مورد نظر برای فروش را وارد کنید.\n"
        "حداقل مقدار فروش: 10 تتر\n"
        "مثال: 50",
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, sell_tether_amount)

def sell_tether_amount(message):
    if message.text == "🔙 بازگشت":
        main_menu(message)
        return
        
    try:
        amount = float(message.text)
        if amount < 10:
            raise ValueError("مقدار کمتر از حد مجاز")
            
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        trc20_btn = types.KeyboardButton("TRC20")
        erc20_btn = types.KeyboardButton("ERC20")
        bep20_btn = types.KeyboardButton("BEP20")
        back_btn = types.KeyboardButton("🔙 بازگشت")
        markup.add(trc20_btn, erc20_btn, bep20_btn)
        markup.add(back_btn)
        
        sent_msg = bot.send_message(
            message.chat.id,
            f"✅ مقدار {amount} تتر تایید شد.\n"
            "لطفا شبکه مورد نظر خود را انتخاب کنید:",
            reply_markup=markup
        )
        bot.register_next_step_handler(sent_msg, sell_tether_network, amount)
        
    except ValueError:
        sent_msg = bot.send_message(
            message.chat.id,
            "❌ مقدار وارد شده معتبر نیست. لطفا مجددا تلاش کنید."
        )
        bot.register_next_step_handler(sent_msg, sell_tether_amount)

def sell_tether_network(message, amount):
    if message.text == "🔙 بازگشت":
        sell_tether_start(message)
        return

    if message.text not in NETWORK_FEES:
        sent_msg = bot.send_message(
            message.chat.id,
            "❌ شبکه انتخابی نامعتبر است. لطفا از دکمه‌های زیر استفاده کنید."
        )
        bot.register_next_step_handler(sent_msg, sell_tether_network, amount)
        return

    network = message.text
    config = read_config()
    total_price = amount * config['price']

    sell_text = (
        f"🔹 جزئیات فروش:\n\n"
        f"📌 مقدار تتر: {amount} USDT\n"
        f"📌 شبکه: {network}\n"
        f"📌 مبلغ قابل دریافت: {total_price:,} تومان\n\n"
        f"🔸 آدرس کیف پول {network} جهت ارسال تتر:\n"
        f"{WALLET_ADDRESSES[network]}\n\n"
        "پس از ارسال تتر، لطفا هش تراکنش را ارسال کنید."
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)

    sent_msg = bot.send_message(
        message.chat.id,
        sell_text,
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, sell_tether_hash, amount, network)

def sell_tether_hash(message, amount, network):
    if message.text == "🔙 بازگشت":
        sell_tether_network(message, amount)
        return

    transaction_hash = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)

    sent_msg = bot.send_message(
        message.chat.id,
        "لطفا شماره کارت خود را جهت واریز وجه وارد کنید:",
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, sell_tether_card, amount, network, transaction_hash)

def sell_tether_card(message, amount, network, transaction_hash):
    if message.text == "🔙 بازگشت":
        sell_tether_hash(message, amount, network)
        return

    card_number = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)

    sent_msg = bot.send_message(
        message.chat.id,
        "لطفا نام و نام خانوادگی صاحب حساب را وارد کنید:",
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, sell_tether_final, amount, network, transaction_hash, card_number)

def sell_tether_final(message, amount, network, transaction_hash, card_number):
    if message.text == "🔙 بازگشت":
        sell_tether_card(message, amount, network, transaction_hash)
        return

    account_name = message.text

    # ذخیره تراکنش
    transaction_id = save_transaction(message.chat.id, "sell", amount, network)

    # ارسال اطلاعات به ادمین
    admin_msg = (
        f"🔴 سفارش جدید فروش تتر:\n\n"
        f"🔹 شناسه تراکنش: {transaction_id}\n"
        f"👤 کاربر: {message.from_user.username}\n"
        f"📱 شناسه: {message.chat.id}\n"
        f"💰 مقدار: {amount} USDT\n"
        f"🌐 شبکه: {network}\n"
        f"🔗 هش تراکنش:\n{transaction_hash}\n"
        f"💳 شماره کارت:\n{card_number}\n"
        f"👨‍💼 صاحب حساب: {account_name}"
    )
    
    bot.send_message(ADMIN_CHAT_ID, admin_msg)

    # ارسال پیام تایید به کاربر
    confirm_text = (
        "✅ سفارش فروش شما با موفقیت ثبت شد.\n\n"
        f"📌 شناسه تراکنش: {transaction_id}\n"
        "⏱ وجه شما حداکثر تا 30 دقیقه دیگر واریز خواهد شد.\n\n"
        "با تشکر از اعتماد شما 🙏"
    )
    bot.send_message(message.chat.id, confirm_text)
    main_menu(message)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "🟢 خرید تتر":
        buy_tether_start(message)
    elif message.text == "🔴 فروش تتر":
        sell_tether_start(message)
    elif message.text == "💰 قیمت لحظه‌ای":
        show_price(message)
    elif message.text == "📚 راهنما":
        show_guide(message)
    elif message.text == "👨‍💻 پشتیبانی":
        show_support(message)
    elif message.text == "👨‍💼 پنل ادمین" and is_admin(message.chat.id):
        show_admin_panel(message)
    elif message.text == "🔙 بازگشت":
        main_menu(message)
    # دستورات پنل ادمین
    elif message.text == "💰 تنظیم قیمت" and is_admin(message.chat.id):
        set_price_step1(message)
    elif message.text == "📊 آمار ربات" and is_admin(message.chat.id):
        show_stats(message)
    elif message.text == "📨 ارسال پیام همگانی" and is_admin(message.chat.id):
        broadcast_step1(message)
    elif message.text == "📋 لیست تراکنش‌ها" and is_admin(message.chat.id):
        show_transactions(message)

def show_admin_panel(message):
    if not is_admin(message.chat.id):
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    price_btn = types.KeyboardButton("💰 تنظیم قیمت")
    stats_btn = types.KeyboardButton("📊 آمار ربات")
    transactions_btn = types.KeyboardButton("📋 لیست تراکنش‌ها")
    broadcast_btn = types.KeyboardButton("📨 ارسال پیام همگانی")
    back_btn = types.KeyboardButton("🔙 بازگشت")
    
    markup.add(price_btn, stats_btn)
    markup.add(transactions_btn)
    markup.add(broadcast_btn)
    markup.add(back_btn)
    
    bot.send_message(
        message.chat.id,
        "👨‍💼 پنل مدیریت ربات\nلطفا گزینه مورد نظر را انتخاب کنید:",
        reply_markup=markup
    )

def set_price_step1(message):
    if not is_admin(message.chat.id):
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)
    
    msg = bot.send_message(
        message.chat.id,
        "💰 لطفا قیمت جدید تتر را به تومان وارد کنید:",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, set_price_step2)

def set_price_step2(message):
    if message.text == "🔙 بازگشت":
        show_admin_panel(message)
        return
    
    try:
        new_price = float(message.text)
        config = read_config()
        config['price'] = new_price
        config['buy_price'] = new_price
        config['sell_price'] = new_price
        save_config(config)
        
        bot.reply_to(
            message,
            f"✅ قیمت جدید با موفقیت ثبت شد:\n💰 {new_price:,} تومان"
        )
        show_admin_panel(message)
    except ValueError:
        msg = bot.reply_to(message, "❌ لطفا یک عدد معتبر وارد کنید.")
        bot.register_next_step_handler(msg, set_price_step2)

def show_stats(message):
    if not is_admin(message.chat.id):
        return
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
        
        total_users = len(users)
        total_transactions = len(transactions)
        pending_transactions = len([t for t in transactions if t['status'] == 'pending'])
        completed_transactions = len([t for t in transactions if t['status'] == 'completed'])
        
        stats_text = (
            "📊 آمار ربات:\n\n"
            f"👥 تعداد کل کاربران: {total_users:,}\n"
            f"🔄 کل تراکنش‌ها: {total_transactions:,}\n"
            f"⏳ تراکنش‌های در انتظار: {pending_transactions}\n"
            f"✅ تراکنش‌های تکمیل شده: {completed_transactions}\n\n"
            f"📅 تاریخ گزارش: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        bot.reply_to(message, stats_text)
    except FileNotFoundError:
        bot.reply_to(message, "❌ خطا در خواندن اطلاعات")

def broadcast_step1(message):
    if not is_admin(message.chat.id):
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton("🔙 بازگشت")
    markup.add(back_btn)
    
    msg = bot.send_message(
        message.chat.id,
        "📝 پیام مورد نظر برای ارسال به همه کاربران را وارد کنید:",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, broadcast_step2)

def broadcast_step2(message):
    if message.text == "🔙 بازگشت":
        show_admin_panel(message)
        return
    
    broadcast_text = message.text
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        success = 0
        failed = 0
        
        progress_msg = bot.send_message(
            message.chat.id,
            "⏳ در حال ارسال پیام به کاربران..."
        )
        
        for user_id in users:
            try:
                bot.send_message(user_id, broadcast_text)
                success += 1
            except:
                failed += 1
        
        report = (
            "📨 گزارش ارسال پیام:\n\n"
            f"✅ موفق: {success}\n"
            f"❌ ناموفق: {failed}"
        )
        bot.edit_message_text(
            report,
            message.chat.id,
            progress_msg.message_id
        )
        show_admin_panel(message)
    except FileNotFoundError:
        bot.reply_to(message, "❌ خطا در خواندن لیست کاربران")

def show_transactions(message):
    if not is_admin(message.chat.id):
        return
    
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
        
        if not transactions:
            bot.reply_to(message, "📝 هیچ تراکنشی ثبت نشده است.")
            return
        
        # نمایش 10 تراکنش آخر
        recent_transactions = transactions[-10:]
        
        trans_text = "📋 لیست آخرین تراکنش‌ها:\n\n"
        for t in recent_transactions:
            trans_text += (
                f"🔹 شناسه: {t['id']}\n"
                f"👤 کاربر: {t['user_id']}\n"
                f"💰 مقدار: {t['amount']} USDT\n"
                f"🌐 شبکه: {t['network']}\n"
                f"📅 تاریخ: {t['created_at']}\n"
                f"📌 وضعیت: {t['status']}\n"
                "➖➖➖➖➖➖➖➖➖➖\n"
            )
        
        bot.reply_to(message, trans_text)
    except FileNotFoundError:
        bot.reply_to(message, "❌ خطا در خواندن تراکنش‌ها")

def show_price(message):
    config = read_config()
    price_text = (
        f"💰 قیمت لحظه‌ای تتر:\n\n"
        f"💵 قیمت خرید: {config['buy_price']:,} تومان\n"
        f"💵 قیمت فروش: {config['sell_price']:,} تومان\n\n"
        "🔄 بروزرسانی هر 5 دقیقه"
    )
    bot.send_message(message.chat.id, price_text)

def show_guide(message):
    guide_text = """
📚 راهنمای استفاده از ربات:

1️⃣ خرید تتر:
• انتخاب گزینه "🟢 خرید تتر"
• وارد کردن مقدار تتر (حداقل 10)
• انتخاب شبکه مورد نظر
• واریز وجه به شماره کارت اعلام شده
• ارسال تصویر رسید
• دریافت تتر در آدرس کیف پول شما

2️⃣ فروش تتر:
• انتخاب گزینه "🔴 فروش تتر"
• وارد کردن مقدار تتر (حداقل 10)
• انتخاب شبکه مورد نظر
• ارسال تتر به آدرس اعلام شده
• ارسال هش تراکنش
• دریافت وجه در حساب بانکی شما

⚠️ نکات مهم:
• قبل از واریز وجه، حتما قیمت را چک کنید
• در انتخاب شبکه دقت کنید
• کارمزد شبکه‌ها متفاوت است
• زمان پردازش تراکنش‌ها حداکثر 30 دقیقه

🔰 در صورت نیاز به راهنمایی بیشتر با پشتیبانی در تماس باشید.
"""
    bot.send_message(message.chat.id, guide_text)

def show_support(message):
    support_text = f"""
👨‍💻 پشتیبانی ربات:

📱 تلگرام: {SUPPORT_INFO['telegram']}
⏰ ساعت پاسخگویی: {SUPPORT_INFO['hours']}

🔰 پشتیبانی در سریع‌ترین زمان ممکن پاسخگوی شما خواهد بود.
"""
    bot.send_message(message.chat.id, support_text)

# راه‌اندازی ربات
if __name__ == "__main__":
    print("🤖 ربات با موفقیت راه‌اندازی شد...")
    print("✅ برای دریافت Chat ID خود، دستور /myid را در ربات وارد کنید.")
    bot.infinity_polling()
