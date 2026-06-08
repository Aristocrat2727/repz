import asyncio
import sqlite3
import os
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    BufferedInputFile, LabeledPrice,
    PreCheckoutQuery
)
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ========== ПЕРЕМЕННЫЕ ==========

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "")
STARS_PRICE = int(os.getenv("STARS_PRICE", 75))
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_URL = os.getenv("CHANNEL_URL")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
DB_PATH = os.getenv("DB_PATH", "/app/data/database.db")

ADMIN_CONTACT = "@Withoutx4"

# Создаём директорию для БД
db_dir = os.path.dirname(DB_PATH)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ========== БАЗА ДАННЫХ ==========

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    payment_method TEXT,
    amount TEXT,
    order_status TEXT,
    created_at TEXT,
    completed_at TEXT,
    crypto_invoice_id TEXT,
    crypto_invoice_url TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    joined_at TEXT,
    is_banned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mailing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    status TEXT,
    created_at TEXT
)
""")

conn.commit()

# ========== КОНФИГ ==========

CONFIG_TEXT = """[Interface]
Address = 172.16.0.2/32, 2606:4700:110:8edc:ef5d:17ec:2624:4a72/128
DNS = 141.95.97.120, 185.211.245.131, 45.155.204.190, 37.230.192.51
MTU = 1280
Jc = 4
Jmin = 8
Jmax = 80
H1 = 1
H2 = 2
H3 = 3
H4 = 4
I1 = <b 0xce000000010897a297ecc34cd6dd000044d0ec2e2e1ea2991f467ace4222129b5a098823784694b4897b9986ae0b7280135fa85e196d9ad980b150122129ce2a9379531b0fd3e871ca5fdb883c369832f730e272d7b8b74f393f9f0fa43f11e510ecb2219a52984410c204cf875585340c62238e14ad04dff382f2c200e0ee22fe743b9c6b8b043121c5710ec289f471c91ee414fca8b8be8419ae8ce7ffc53837f6ade262891895f3f4cecd31bc93ac5599e18e4f01b472362b8056c3172b513051f8322d1062997ef4a383b01706598d08d48c221d30e74c7ce000cdad36b706b1bf9b0607c32ec4b3203a4ee21ab64df336212b9758280803fcab14933b0e7ee1e04a7becce3e2633f4852585c567894a5f9efe9706a151b615856647e8b7dba69ab357b3982f554549bef9256111b2d67afde0b496f16962d4957ff654232aa9e845b61463908309cfd9de0a6abf5f425f577d7e5f6440652aa8da5f73588e82e9470f3b21b27b28c649506ae1a7f5f15b876f56abc4615f49911549b9bb39dd804fde182bd2dcec0c33bad9b138ca07d4a4a1650a2c2686acea05727e2a78962a840ae428f55627516e73c83dd8893b02358e81b524b4d99fda6df52b3a8d7a5291326e7ac9d773c5b43b8444554ef5aea104a738ed650aa979674bbed38da58ac29d87c29d387d80b526065baeb073ce65f075ccb56e47533aef357dceaa8293a523c5f6f790be90e4731123d3c6152a70576e90b4ab5bc5ead01576c68ab633ff7d36dcde2a0b2c68897e1acfc4d6483aaaeb635dd63c96b2b6a7a2bfe042f6aed82e5363aa850aace12ee3b1a93f30d8ab9537df483152a5527faca21efc9981b304f11fc95336f5b9637b174c5a0659e2b22e159a9fed4b8e93047371175b1d6d9cc8ab745f3b2281537d1c75fb9451871864efa5d184c38c185fd203de206751b92620f7c369e031d2041e152040920ac2c5ab5340bfc9d0561176abf10a147287ea90758575ac6a9f5ac9f390d0d5b23ee12af583383d994e22c0cf42383834bcd3ada1b3825a0664d8f3fb678261d57601ddf94a8a68a7c273a18c08aa99c7ad8c6c42eab67718843597ec9930457359dfdfbce024afc2dcf9348579a57d8d3490b2fa99f278f1c37d87dad9b221acd575192ffae1784f8e60ec7cee4068b6b988f0433d96d6a1b1865f4e155e9fe020279f434f3bf1bd117b717b92f6cd1cc9bea7d45978bcc3f24bda631a36910110a6ec06da35f8966c9279d130347594f13e9e07514fa370754d1424c0a1545c5070ef9fb2acd14233e8a50bfc5978b5bdf8bc1714731f798d21e2004117c61f2989dd44f0cf027b27d4019e81ed4b5c31db347c4a3a4d85048d7093cf16753d7b0d15e078f5c7a5205dc2f87e330a1f716738dce1c6180e9d02869b5546f1c4d2748f8c90d9693cba4e0079297d22fd61402dea32ff0eb69ebd65a5d0b687d87e3a8b2c42b648aa723c7c7daf37abcc4bb85caea2ee8f55bec20e913b3324ab8f5c3304f820d42ad1b9f2ffc1a3af9927136b4419e1e579ab4c2ae3c776d293d397d575df181e6cae0a4ada5d67ecea171cca3288d57c7bbdaee3befe745fb7d634f70386d873b90c4d6c6596bb65af68f9e5121e67ebf0d89d3c909ceedfb32ce9575a7758ff080724e1ab5d5f43074ecb53a479af21ed03d7b6899c36631c0166f9d47e5e1d4528a5d3d3f744029c4b1c190cbfbad06f5f83f7ad0429fa9a2719c56ffe3783460e166de2d8>
PrivateKey = j046lIy8qhue8ZLbudxTiZeZcSwfvWu2HjtUBYXFfIE=

[Peer]
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = 162.159.192.1:2408
PersistentKeepalive = 15
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="""

# ========== КЛАВИАТУРЫ ==========

class Keyboards:
    @staticmethod
    def main_menu():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ КУПИТЬ SHADOWVPN", callback_data="buy_menu")],
            [InlineKeyboardButton(text="❓ КАК ПОДКЛЮЧИТЬСЯ", callback_data="help")],
            [InlineKeyboardButton(text="📢 НАШ КАНАЛ", url=CHANNEL_URL)]
        ])

    @staticmethod
    def buy_menu():
        buttons = [
            [InlineKeyboardButton(text=f"⭐ {STARS_PRICE} STARS", callback_data="pay_stars")],
            [InlineKeyboardButton(text="💳 КАРТА РФ (100₽)", callback_data="pay_card")]
        ]
        if CRYPTOBOT_TOKEN:
            buttons.append([InlineKeyboardButton(text="🪙 CRYPTO (USDT)", callback_data="pay_crypto")])
        buttons.append([InlineKeyboardButton(text="◀️ НАЗАД", callback_data="back_main")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def admin_main():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 ЗАКАЗЫ", callback_data="admin_orders")],
            [InlineKeyboardButton(text="➕ НОВЫЙ ЗАКАЗ", callback_data="admin_new_order")],
            [InlineKeyboardButton(text="📊 СТАТИСТИКА", callback_data="admin_stats")],
            [InlineKeyboardButton(text="👥 ПОЛЬЗОВАТЕЛИ", callback_data="admin_users")],
            [InlineKeyboardButton(text="📢 РАССЫЛКА", callback_data="admin_mailing")],
            [InlineKeyboardButton(text="⚙️ НАСТРОЙКИ", callback_data="admin_settings")],
            [InlineKeyboardButton(text="🔙 ВЫХОД", callback_data="admin_back")]
        ])

# ========== ФУНКЦИИ ==========

async def check_subscription(user_id: int) -> bool:
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

async def send_config(user_id: int, order_id: int):
    file = BufferedInputFile(CONFIG_TEXT.encode(), filename="shadow.conf")
    
    caption_text = """✅ <b>ТВОЙ КОНФИГ SHADOWVPN</b>

📲 <b>КАК ПОДКЛЮЧИТЬСЯ:</b>

━━━━━━━━━━━━━━━━━━━━
🤖 <b>ANDROID:</b>
• <a href="https://play.google.com/store/apps/details?id=org.amnezia.vpn">AmneziaWG (рекомендуется)</a>
• <a href="https://play.google.com/store/apps/details?id=com.wireguard.android">WireGuard (альтернатива)</a>

🍏 <b>IPHONE / IOS:</b>
• <a href="https://apps.apple.com/ru/app/amneziawg/id6478942365">AmneziaWG (рекомендуется)</a>
• <a href="https://apps.apple.com/app/wireguard/id1441195209">WireGuard (альтернатива)</a>
━━━━━━━━━━━━━━━━━━━━

3️⃣ Открой приложение
4️⃣ Нажми «Импортировать файл» → выбери shadow.conf
5️⃣ Включи туннель 🟢

🔒 <b>ShadowVPN — свободный интернет без границ!</b>"""
    
    await bot.send_document(user_id, document=file, caption=caption_text, parse_mode="HTML")
    
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"✅ Конфиг #{order_id} отправлен пользователю")

async def register_user(user_id, username, first_name):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at, is_banned) VALUES (?, ?, ?, ?, 0)",
                   (user_id, username or "no_username", first_name or "unknown", datetime.now().isoformat()))
    conn.commit()

async def is_banned(user_id: int) -> bool:
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] == 1

# ========== ПОЛЬЗОВАТЕЛЬСКИЕ ХЕНДЛЕРЫ ==========

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    await register_user(user_id, message.from_user.username, message.from_user.first_name)

    if await is_banned(user_id):
        await message.answer("❌ <b>ДОСТУП ЗАБЛОКИРОВАН</b>\n\nОбратись к администратору.", parse_mode="HTML")
        return

    if REQUIRED_CHANNEL and not await check_subscription(user_id):
        sub_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 ПОДПИСАТЬСЯ", url=CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ ПРОВЕРИТЬ", callback_data="check_sub")]
        ])
        await message.answer(f"🔮 <b>SHADOWVPN</b>\n\nПодпишись на канал:\n{CHANNEL_URL}", parse_mode="HTML", reply_markup=sub_btn)
        return

    start_text = """🔮 <b>ДОБРО ПОЖАЛОВАТЬ В SHADOWVPN!</b>

🛡️ <b>Что это?</b>
Безопасный и анонимный доступ в интернет из любой точки мира

✨ <b>Преимущества:</b>
✅ Полная анонимность
✅ Высокая скорость
✅ Безлимитный трафик
✅ Поддержка 24/7

Выбери действие в меню ниже 👇"""

    await message.answer(start_text, parse_mode="HTML", reply_markup=Keyboards.main_menu())

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        start_text = """🔮 <b>ДОБРО ПОЖАЛОВАТЬ В SHADOWVPN!</b>

✨ <b>Преимущества:</b>
✅ Полная анонимность
✅ Высокая скорость
✅ Безлимитный трафик
✅ Поддержка 24/7

Выбери действие в меню ниже 👇"""
        await callback.message.edit_text(start_text, parse_mode="HTML", reply_markup=Keyboards.main_menu())
    else:
        await callback.answer("❌ Ты не подписан!", show_alert=True)

@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    start_text = """🔮 <b>ДОБРО ПОЖАЛОВАТЬ В SHADOWVPN!</b>

✨ <b>Преимущества:</b>
✅ Полная анонимность
✅ Высокая скорость
✅ Безлимитный трафик
✅ Поддержка 24/7

Выбери действие в меню ниже 👇"""
    await callback.message.edit_text(start_text, parse_mode="HTML", reply_markup=Keyboards.main_menu())

@dp.callback_query(lambda c: c.data == "buy_menu")
async def show_buy(callback: types.CallbackQuery):
    buy_text = """💎 <b>ВЫБЕРИ СПОСОБ ОПЛАТЫ</b>

⭐ <b>STARS</b> — моментально, сразу получаешь конфиг
💳 <b>КАРТА РФ</b> — 100₽, проверяется админом
🪙 <b>CRYPTO</b> — USDT через CryptoBot

Какой способ тебе удобнее?"""
    
    await callback.message.edit_text(buy_text, parse_mode="HTML", reply_markup=Keyboards.buy_menu())

@dp.callback_query(lambda c: c.data == "help")
async def show_help(callback: types.CallbackQuery):
    help_text = f"""❓ <b>КАК ПОДКЛЮЧИТЬСЯ</b>

<b>1️⃣ ОПЛАТИ</b>
Выбери удобный способ оплаты (⭐ Stars, 💳 Карта или 🪙 Крипто)

<b>2️⃣ ПОЛУЧИ КОНФИГ</b>
• Для ⭐ Stars — конфиг приходит автоматически
• Для 💳 Карты — напиши админу после оплаты
• Для 🪙 Крипто — нажми проверить оплату

<b>3️⃣ СКАЧАЙ ПРИЛОЖЕНИЕ</b>
🤖 Android: <a href="https://play.google.com/store/apps/details?id=org.amnezia.vpn">AmneziaWG</a>
🍏 iPhone: <a href="https://apps.apple.com/ru/app/amneziawg/id6478942365">AmneziaWG</a>

<b>4️⃣ ПОДКЛЮЧИСЬ</b>
Импортируй файл shadow.conf в приложение и наслаждайся! 🟢

❓ <b>ВОПРОСЫ?</b>
Напиши администратору: {ADMIN_CONTACT}"""
    
    await callback.message.edit_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="back_main")]]))

# ========== ОПЛАТА ЗВЁЗДАМИ ==========

@dp.callback_query(lambda c: c.data == "pay_stars")
async def stars_pay(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?,?,?,?,?,?)",
                   (user_id, callback.from_user.username or "no_user", "stars", str(STARS_PRICE), "waiting", datetime.now().isoformat()))
    conn.commit()
    order_id = cursor.lastrowid

    try:
        await bot.send_invoice(
            chat_id=user_id,
            title="SHADOWVPN",
            description=f"Доступ навсегда | {STARS_PRICE} Stars",
            payload=f"order_{order_id}",
            currency="XTR",
            prices=[LabeledPrice(label="SHADOWVPN", amount=STARS_PRICE)],
            provider_token=""
        )
        await callback.answer("⭐ Счёт отправлен!")
    except Exception as e:
        await callback.answer("❌ Ошибка, сообщи админу", show_alert=True)
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, f"Stars ошибка: {e}")

@dp.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def on_successful_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload
    order_id = int(payload.split("_")[1])
    cursor.execute("UPDATE orders SET order_status = ?, completed_at = ? WHERE id = ?", ("completed", datetime.now().isoformat(), order_id))
    conn.commit()
    await send_config(message.chat.id, order_id)
    await message.answer("⭐ Спасибо за покупку! Конфиг выше 👆")

# ========== ОПЛАТА КАРТОЙ ==========

@dp.callback_query(lambda c: c.data == "pay_card")
async def card_pay(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "no_username"

    cursor.execute(
        "INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?,?,?,?,?,?)",
        (user_id, username, "card", "100₽", "waiting", datetime.now().isoformat())
    )
    conn.commit()
    order_id = cursor.lastrowid

    # Уведомление админу
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"💳 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
            f"👤 Пользователь: @{username}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"💰 Сумма: 100₽\n\n"
            f"📝 Команда для отправки конфига:\n<code>/send_config {order_id}</code>",
            parse_mode="HTML"
        )

    # Клавиатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 НАПИСАТЬ АДМИНУ", url="https://t.me/Withoutx4")],
        [InlineKeyboardButton(text="✅ Я ОПЛАТИЛ", callback_data=f"paid_card_{order_id}")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="buy_menu")]
    ])

    card_text = f"""💳 <b>ОПЛАТА КАРТОЙ РФ</b>

📦 Заказ: <code>#{order_id}</code>
💰 Сумма: <b>100₽</b>

━━━━━━━━━━━━━━━━━━━━

<b>📋 ИНСТРУКЦИЯ:</b>

1️⃣ Нажми кнопку «НАПИСАТЬ АДМИНУ»
2️⃣ Попроси реквизиты для оплаты
3️⃣ Отправь 100₽ на указанные реквизиты
4️⃣ Вернись сюда и нажми «Я ОПЛАТИЛ»
5️⃣ Админ проверит платёж и отправит конфиг

━━━━━━━━━━━━━━━━━━━━

⚠️ <b>ВАЖНО!</b> Упомяни админу номер заказа: <code>#{order_id}</code>

✅ Конфиг придёт сюда после проверки"""

    await callback.message.edit_text(card_text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("paid_card_"))
async def paid_card(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    username = callback.from_user.username or "no_username"

    # Проверяем статус заказа
    cursor.execute("SELECT order_status FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()

    if not row:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return

    if row[0] == "completed":
        await callback.answer("✅ Конфиг уже отправлен!", show_alert=True)
        return

    # Отправляем уведомление админам
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"🔔 <b>ЗАЯВКА ОБ ОПЛАТЕ</b>\n\n"
            f"📦 Заказ: #{order_id}\n"
            f"👤 Пользователь: @{username}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"💰 Сумма: 100₽\n\n"
            f"📝 Команда для отправки конфига:\n<code>/send_config {order_id}</code>",
            parse_mode="HTML"
        )

    # Клавиатура после нажатия
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ ГЛАВНОЕ МЕНЮ", callback_data="back_main")]
    ])

    success_text = f"""✅ <b>ЗАЯВКА ОТПРАВЛЕНА!</b>

📦 Заказ: <code>#{order_id}</code>

━━━━━━━━━━━━━━━━━━━━

👨‍💻 <b>Админ получил уведомление</b>

⏳ Конфиг придёт сюда после проверки оплаты

━━━━━━━━━━━━━━━━━━━━

⚠️ <b>ЕСЛИ КОНФИГ НЕ ПРИШЁЛ ЧЕРЕЗ 15 МИНУТ:</b>

📞 Напиши админу: {ADMIN_CONTACT}

🕐 <b>Время ответа:</b> обычно 5-15 минут"""

    await callback.message.edit_text(success_text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer("✅ Уведомление отправлено! Админ скоро проверит платёж")

# ========== ОПЛАТА КРИПТОЙ ==========

@dp.callback_query(lambda c: c.data == "pay_crypto")
async def crypto_pay(callback: types.CallbackQuery):
    if not CRYPTOBOT_TOKEN:
        await callback.answer("❌ CryptoBot не настроен", show_alert=True)
        return

    user_id = callback.from_user.id
    username = callback.from_user.username or "no_username"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?,?,?,?,?,?)",
                   (user_id, username, "crypto", "1 USDT", "waiting", datetime.now().isoformat()))
    conn.commit()
    order_id = cursor.lastrowid

    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    payload = {"asset": "USDT", "amount": "1", "description": f"ShadowVPN #{order_id}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://pay.crypt.bot/api/createInvoice", json=payload, headers=headers) as response:
                data = await response.json()
                print("CREATE:", data)

                if not data.get("ok"):
                    await callback.answer(f"Ошибка: {data}", show_alert=True)
                    return

                invoice = data["result"]
                invoice_id = str(invoice["invoice_id"])
                invoice_url = invoice["bot_invoice_url"]

                cursor.execute("UPDATE orders SET crypto_invoice_id = ?, crypto_invoice_url = ? WHERE id = ?", 
                               (invoice_id, invoice_url, order_id))
                conn.commit()

                keyboard = InlineKeyboardBuilder()
                keyboard.button(text="💳 ОПЛАТИТЬ ЧЕРЕЗ CRYPTOBOT", url=invoice_url)
                keyboard.button(text="🔄 ПРОВЕРИТЬ ОПЛАТУ", callback_data=f"check_crypto_{invoice_id}")
                keyboard.button(text="◀️ НАЗАД", callback_data="buy_menu")
                keyboard.adjust(1)

                crypto_text = f"""🪙 <b>ОПЛАТА КРИПТОЙ (USDT)</b>

📦 Заказ: <code>#{order_id}</code>
💰 Сумма: <b>1 USDT</b>

━━━━━━━━━━━━━━━━━━━━

<b>📋 ИНСТРУКЦИЯ:</b>

1️⃣ Нажми кнопку «ОПЛАТИТЬ ЧЕРЕЗ CRYPTOBOT»
2️⃣ Выполни платёж в @CryptoBot
3️⃣ Вернись сюда и нажми «ПРОВЕРИТЬ ОПЛАТУ»
4️⃣ Если платёж прошёл, конфиг придёт автоматически

━━━━━━━━━━━━━━━━━━━━

✅ Платёж обрабатывается моментально"""

                await callback.message.edit_text(crypto_text, parse_mode="HTML", reply_markup=keyboard.as_markup())
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("check_crypto_"))
async def check_crypto(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("check_crypto_", "")
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}", headers=headers) as response:
                data = await response.json()
                print("CHECK:", data)

                if not data.get("ok"):
                    await callback.answer("❌ Ошибка проверки", show_alert=True)
                    return

                items = data["result"]["items"]
                if not items:
                    await callback.answer("❌ Счёт не найден", show_alert=True)
                    return

                status = items[0]["status"]

                if status == "paid":
                    cursor.execute("SELECT id FROM orders WHERE crypto_invoice_id = ?", (invoice_id,))
                    row = cursor.fetchone()
                    if row:
                        order_id = row[0]
                        cursor.execute("UPDATE orders SET order_status = ?, completed_at = ? WHERE id = ?", 
                                       ("completed", datetime.now().isoformat(), order_id))
                        conn.commit()
                        cursor.execute("SELECT user_id FROM orders WHERE id = ?", (order_id,))
                        user_row = cursor.fetchone()
                        if user_row:
                            await send_config(user_row[0], order_id)
                    
                    await callback.message.edit_text("✅ <b>ОПЛАТА ПОДТВЕРЖДЕНА!</b>\n\n🎉 Конфиг отправлен выше 👆", parse_mode="HTML")
                elif status == "active":
                    await callback.answer("⏳ Счёт ещё не оплачен", show_alert=True)
                elif status == "expired":
                    await callback.answer("❌ Счёт истёк", show_alert=True)
                else:
                    await callback.answer(f"ℹ️ Статус: {status}", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)

# ========== АДМИН-ПАНЕЛЬ ==========

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ <b>НЕТ ДОСТУПА</b>", parse_mode="HTML")
        return
    admin_text = """🔧 <b>АДМИН-ПАНЕЛЬ SHADOWVPN</b>

Выбери действие из меню ниже 👇"""
    await message.answer(admin_text, parse_mode="HTML", reply_markup=Keyboards.admin_main())

@dp.callback_query(lambda c: c.data == "admin_orders")
async def admin_orders(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет прав")
        return
    cursor.execute("SELECT id, username, payment_method, amount, order_status FROM orders ORDER BY id DESC LIMIT 30")
    rows = cursor.fetchall()
    if not rows:
        await callback.message.edit_text("📭 <b>ЗАКАЗОВ НЕТ</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))
        return
    text = "📋 <b>СПИСОК ЗАКАЗОВ</b>\n\n"
    for row in rows:
        emoji = "✅" if row[4] == "completed" else "⏳"
        text += f"{emoji} #{row[0]} | @{row[1]} | {row[2]} | {row[3]}\n"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))

@dp.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'completed'")
    completed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE payment_method = 'stars' AND order_status = 'completed'")
    stars_sales = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE payment_method = 'card' AND order_status = 'completed'")
    card_sales = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE payment_method = 'crypto' AND order_status = 'completed'")
    crypto_sales = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    users_total = cursor.fetchone()[0]

    stats_text = f"""📊 <b>СТАТИСТИКА SHADOWVPN</b>

👥 <b>Пользователей:</b> {users_total}
📦 <b>Всего заказов:</b> {total}
✅ <b>Выполнено:</b> {completed}
⏳ <b>Ожидают:</b> {total - completed}

━━━━━━━━━━━━━━━━━

⭐ <b>Stars продажи:</b> {stars_sales}
💳 <b>Карта продажи:</b> {card_sales}
🪙 <b>Crypto продажи:</b> {crypto_sales}"""

    await callback.message.edit_text(stats_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))

@dp.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    cursor.execute("SELECT user_id, username, first_name, joined_at, is_banned FROM users ORDER BY joined_at DESC LIMIT 20")
    rows = cursor.fetchall()
    if not rows:
        await callback.message.edit_text("📭 Нет пользователей", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))
        return
    text = "👥 <b>ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ</b>\n\n"
    for row in rows:
        ban_status = "🔴 БАН" if row[4] == 1 else "🟢 АКТИВЕН"
        text += f"{ban_status} | {row[0]} | @{row[1] or 'нет'} | {row[2]} | {row[3][:10]}\n"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))

@dp.callback_query(lambda c: c.data == "admin_new_order")
async def admin_new_order_prompt(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    prompt_text = """📝 <b>СОЗДАНИЕ ЗАКАЗА</b>

Используй команду:
<code>/neworder 123456789</code>

Где 123456789 — это ID пользователя"""
    await callback.message.edit_text(prompt_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing_prompt(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    mailing_text = """📢 <b>РАССЫЛКА ВСЕМ ПОЛЬЗОВАТЕЛЯМ</b>

Отправь любое сообщение (текст, фото, документ, стикер) — бот разошлёт ВСЕМ активным пользователям

🔴 <b>ДЛЯ ОТМЕНЫ:</b> /cancel_mailing"""
    await callback.message.edit_text(mailing_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_settings")
async def admin_settings(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    settings_text = f"""⚙️ <b>НАСТРОЙКИ БОТА</b>

⭐ <b>Цена Stars:</b> {STARS_PRICE}
📢 <b>Обязательный канал:</b> {REQUIRED_CHANNEL or '❌ НЕ ЗАДАН'}
🪙 <b>CryptoBot:</b> {'✅ ВКЛЮЧЕН' if CRYPTOBOT_TOKEN else '❌ ОТКЛЮЧЕН'}
👤 <b>Контакт админа:</b> {ADMIN_CONTACT}
📁 <b>База данных:</b> {DB_PATH}"""
    await callback.message.edit_text(settings_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))

@dp.callback_query(lambda c: c.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    admin_text = """🔧 <b>АДМИН-ПАНЕЛЬ SHADOWVPN</b>

Выбери действие из меню ниже 👇"""
    await callback.message.edit_text(admin_text, parse_mode="HTML", reply_markup=Keyboards.admin_main())

# ========== АДМИН КОМАНДЫ ==========

@dp.message(Command("send_config"))
async def send_config_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет прав")
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Использование: /send_config 123")
        return
    try:
        order_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID заказа должно быть числом")
        return

    cursor.execute("SELECT user_id, order_status FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        await message.answer("❌ Заказ не найден")
        return
    user_id, status = row
    if status == "completed":
        await message.answer("✅ Конфиг уже был отправлен этому пользователю")
        return
    cursor.execute("UPDATE orders SET order_status = ?, completed_at = ? WHERE id = ?", ("completed", datetime.now().isoformat(), order_id))
    conn.commit()
    await send_config(user_id, order_id)
    await message.answer(f"✅ Конфиг для заказа #{order_id} отправлен пользователю!")

@dp.message(Command("neworder"))
async def new_order_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Использование: /neworder 123456789")
        return
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID пользователя должно быть числом")
        return

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?,?,?,?,?,?)",
                   (user_id, "admin_created", "manual", "100₽", "waiting", datetime.now().isoformat()))
    conn.commit()
    order_id = cursor.lastrowid
    await message.answer(f"✅ Создан заказ #{order_id} для пользователя {user_id}\n\nКоманда для отправки конфига:\n<code>/send_config {order_id}</code>", parse_mode="HTML")

@dp.message(Command("orders"))
async def list_orders_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    cursor.execute("SELECT id, username, payment_method, amount, order_status FROM orders ORDER BY id DESC LIMIT 30")
    rows = cursor.fetchall()
    if not rows:
        await message.answer("📭 Нет заказов")
        return
    text = "📋 <b>ПОСЛЕДНИЕ ЗАКАЗЫ:</b>\n\n"
    for row in rows:
        emoji = "✅" if row[4] == "completed" else "⏳"
        text += f"{emoji} #{row[0]} | @{row[1]} | {row[2]} | {row[3]}\n"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'completed'")
    completed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    stats_text = f"""📊 <b>СТАТИСТИКА:</b>

👥 Пользователей: {users}
📦 Заказов всего: {total}
✅ Выполнено: {completed}
⏳ Ожидают: {total - completed}"""

    await message.answer(stats_text, parse_mode="HTML")

@dp.message(Command("check_crypto"))
async def check_crypto_bot(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет прав")
        return
    if not CRYPTOBOT_TOKEN:
        await message.answer("❌ CRYPTOBOT_TOKEN не задан в .env")
        return
    await message.answer("✅ CryptoBot настроен и готов к работе")

@dp.message(Command("cancel_order"))
async def cancel_order_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет прав")
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Использование: /cancel_order 123\n\n<code>123</code> — это ID заказа", parse_mode="HTML")
        return
    try:
        order_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID заказа должно быть числом")
        return

    cursor.execute("SELECT order_status, user_id FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Заказ не найден")
        return

    status, user_id = row

    if status == "cancelled":
        await message.answer(f"⚠️ Заказ #{order_id} уже отменён")
        return

    cursor.execute("UPDATE orders SET order_status = ?, completed_at = ? WHERE id = ?", 
                   ("cancelled", datetime.now().isoformat(), order_id))
    conn.commit()

    try:
        await bot.send_message(
            user_id,
            f"❌ <b>ЗАКАЗ ОТМЕНЁН</b>\n\n"
            f"📦 Заказ: #{order_id}\n\n"
            f"Если это ошибка, напиши админу: {ADMIN_CONTACT}",
            parse_mode="HTML"
        )
    except:
        pass

    await message.answer(f"✅ Заказ #{order_id} отменён\n\nПользователю отправлено уведомление")

# ========== БАН/РАЗБАН КОМАНДЫ ==========

@dp.message(Command("ban"))
async def ban_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет прав")
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Использование: /ban 123456789")
        return
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID пользователя должно быть числом")
        return

    cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    try:
        await bot.send_message(user_id, "❌ <b>ВАШ ДОСТУП ЗАБЛОКИРОВАН</b>\n\nОбратись к администратору: " + ADMIN_CONTACT, parse_mode="HTML")
    except:
        pass
    await message.answer(f"✅ Пользователь {user_id} забанен")

@dp.message(Command("unban"))
async def unban_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет прав")
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Использование: /unban 123456789")
        return
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID пользователя должно быть числом")
        return

    cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    try:
        await bot.send_message(user_id, "✅ <b>ВАШ ДОСТУП ВОССТАНОВЛЕН</b>\n\nТеперь ты можешь пользоваться ботом! 🎉", parse_mode="HTML")
    except:
        pass
    await message.answer(f"✅ Пользователь {user_id} разбанен")

@dp.message(Command("getid"))
async def get_id(message: types.Message):
    await message.answer(f"🆔 <b>Твой ID:</b> <code>{message.from_user.id}</code>", parse_mode="HTML")

# ========== РАССЫЛКА ==========

mailing_active = False

@dp.message(lambda msg: msg.from_user.id in ADMIN_IDS and not (msg.text and msg.text.startswith("/")))
async def process_mailing(message: types.Message):
    global mailing_active
    if mailing_active:
        await message.answer("⚠️ Рассылка уже идёт, подождите...")
        return

    mailing_active = True
    cursor.execute("SELECT user_id FROM users WHERE is_banned = 0")
    users = cursor.fetchall()
    sent = 0
    failed = 0
    status_msg = await message.answer("📢 <b>РАССЫЛКА НАЧАЛАСЬ...</b>\n\n⏳ Идёт отправка...", parse_mode="HTML")

    for user in users:
        try:
            await bot.copy_message(user[0], message.chat.id, message.message_id)
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.05)

    result_text = f"""✅ <b>РАССЫЛКА ЗАВЕРШЕНА!</b>

📤 Отправлено: {sent}
❌ Не доставлено: {failed}
👥 Всего пользователей: {len(users)}"""

    await status_msg.edit_text(result_text, parse_mode="HTML")
    mailing_active = False

@dp.message(Command("cancel_mailing"))
async def cancel_mailing(message: types.Message):
    global mailing_active
    if message.from_user.id not in ADMIN_IDS:
        return
    mailing_active = False
    await message.answer("❌ Рассылка отменена")

# ========== ЗАПУСК ==========

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("=" * 50)
    print("🚀 SHADOWVPN БОТ ЗАПУЩЕН")
    print("=" * 50)
    print(f"📁 База данных: {DB_PATH}")
    print(f"👥 Админы: {ADMIN_IDS}")
    print(f"⭐ Цена Stars: {STARS_PRICE}")
    print(f"🪙 CryptoBot: {'✅ ВКЛЮЧЕН' if CRYPTOBOT_TOKEN else '❌ ОТКЛЮЧЕН'}")
    print("=" * 50)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
