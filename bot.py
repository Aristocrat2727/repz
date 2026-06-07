import asyncio
import sqlite3
import os
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    BufferedInputFile, LabeledPrice
)
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# ========== ПЕРЕМЕННЫЕ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "")
STARS_PRICE = int(os.getenv("STARS_PRICE", 75))
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_URL = os.getenv("CHANNEL_URL", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
DB_PATH = os.getenv("DB_PATH", "database.db")

# Контакт админа
ADMIN_CONTACT = "@Withoutx4"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ========== БАЗА ДАННЫХ ==========
conn = sqlite3.connect(DB_PATH)
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
    crypto_invoice_id TEXT
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
PrivateKey = T3n6Sdaijx8WLHYZ1wMlfFv769/DAbLINXqxonGw3r0=
Address = 172.16.0.2, 2606:4700:110:825f:c471:eeba:e0:da2f
DNS = 9.9.9.9, 149.112.112.112
MTU = 1280
S1 = 0
S2 = 0
Jc = 4
Jmin = 40
Jmax = 70
H1 = 1
H2 = 2
H3 = 3
H4 = 4
I1 = <b 0xce000000010897a297ecc34cd6dd000044d0ec2e2e1ea2991f467ace4222129b5a098823784694b4897b9986ae0b7280135fa85e196d9ad980b150122129ce2a9379531b0fd3e871ca5fdb883c369832f730e272d7b8b74f393f9f0fa43f11e510ecb2219a52984410c204cf875585340c62238e14ad04dff382f2c200e0ee22fe743b9c6b8b043121c5710ec289f471c91ee414fca8b8be8419ae8ce7ffc53837f6ade262891895f3f4cecd31bc93ac5599e18e4f01b472362b8056c3172b513051f8322d1062997ef4a383b01706598d08d48c221d30e74c7ce000cdad36b706b1bf9b0607c32ec4b3203a4ee21ab64df336212b9758280803fcab14933b0e7ee1e04a7becce3e2633f4852585c567894a5f9efe9706a151b615856647e8b7dba69ab357b3982f554549bef9256111b2d67afde0b496f16962d4957ff654232aa9e845b61463908309cfd9de0a6abf5f425f577d7e5f6440652aa8da5f73588e82e9470f3b21b27b28c649506ae1a7f5f15b876f56abc4615f49911549b9bb39dd804fde182bd2dcec0c33bad9b138ca07d4a4a1650a2c2686acea05727e2a78962a840ae428f55627516e73c83dd8893b02358e81b524b4d99fda6df52b3a8d7a5291326e7ac9d773c5b43b8444554ef5aea104a738ed650aa979674bbed38da58ac29d87c29d387d80b526065baeb073ce65f075ccb56e47533aef357dceaa8293a523c5f6f790be90e4731123d3c6152a70576e90b4ab5bc5ead01576c68ab633ff7d36dcde2a0b2c68897e1acfc4d6483aaaeb635dd63c96b2b6a7a2bfe042f6aed82e5363aa850aace12ee3b1a93f30d8ab9537df483152a5527faca21efc9981b304f11fc95336f5b9637b174c5a0659e2b22e159a9fed4b8e93047371175b1d6d9cc8ab745f3b2281537d1c75fb9451871864efa5d184c38c185fd203de206751b92620f7c369e031d2041e152040920ac2c5ab5340bfc9d0561176abf10a147287ea90758575ac6a9f5ac9f390d0d5b23ee12af583383d994e22c0cf42383834bcd3ada1b3825a0664d8f3fb678261d57601ddf94a8a68a7c273a18c08aa99c7ad8c6c42eab67718843597ec9930457359dfdfbce024afc2dcf9348579a57d8d3490b2fa99f278f1c37d87dad9b221acd575192ffae1784f8e60ec7cee4068b6b988f0433d96d6a1b1865f4e155e9fe020279f434f3bf1bd117b717b92f6cd1cc9bea7d45978bcc3f24bda631a36910110a6ec06da35f8966c9279d130347594f13e9e07514fa370754d1424c0a1545c5070ef9fb2acd14233e8a50bfc5978b5bdf8bc1714731f798d21e2004117c61f2989dd44f0cf027b27d4019e81ed4b5c31db347c4a3a4d85048d7093cf16753d7b0d15e078f5c7a5205dc2f87e330a1f716738dce1c6180e9d02869b5546f1c4d2748f8c90d9693cba4e0079297d22fd61402dea32ff0eb69ebd65a5d0b687d87e3a8b2c42b648aa723c7c7daf37abcc4bb85caea2ee8f55bec20e913b3324ab8f5c3304f820d42ad1b9f2ffc1a3af9927136b4419e1e579ab4c2ae3c776d293d397d575df181e6cae0a4ada5d67ecea171cca3288d57c7bbdaee3befe745fb7d634f70386d873b90c4d6c6596bb65af68f9e5121e67ebf0d89d3c909ceedfb32ce9575a7758ff080724e1ab5d5f43074ecb53a479af21ed03d7b6899c36631c0166f9d47e5e1d4528a5d3d3f744029c4b1c190cbfbad06f5f83f7ad0429fa9a2719c56ffe3783460e166de2d8>
I2 = <b 0x5349502f322e302031303020547279696e670d0a5669613a205349502f322e302f55445020706333332e61746c616e74612e636f6d3b6272616e63683d7a39684734624b3737366173646864730d0a546f3a20426f62203c7369703a626f624062696c6f78692e636f6d3e0d0a46726f6d3a20416c696365203c7369703a616c6963654061746c616e74612e636f6d3e3b7461673d313932383330313737340d0a43616c6c2d49443a20613834623463373665363637313040706333332e61746c616e74612e636f6d0d0a435365713a2033313431353920494e564954450d0a436f6e74656e742d4c656e6774683a20300d0a0d0a>

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = 162.159.195.6:2408
PersistentKeepalive = 15"""

# ========== ТЕКСТЫ ==========
START_TEXT = """🔮 <b>SHADOWVPN</b> — путь в свободный интернет

🌐 Обходим любые блокировки
🚀 Максимальная скорость
🛡️ Полная анонимность
♾️ Бессрочный доступ

💰 Цена: {stars_price} Stars / 100₽ / 1 USDT

📌 <b>Подпишись на канал:</b>
{channel_url}

После подписки нажми «ПРОВЕРИТЬ»"""

# ========== КЛАВИАТУРЫ ==========
class Keyboards:
    @staticmethod
    def main_menu():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 КУПИТЬ SHADOWVPN", callback_data="buy_menu")],
            [InlineKeyboardButton(text="❓ ПОМОЩЬ", callback_data="help")],
            [InlineKeyboardButton(text="📢 НАШ КАНАЛ", url=CHANNEL_URL if CHANNEL_URL else "https://t.me")]
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
            [InlineKeyboardButton(text="⚙️ НАСТРОЙКИ", callback_data="admin_settings")]
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

async def create_crypto_invoice(amount_usd: float, order_id: int):
    if not CRYPTOBOT_TOKEN:
        return None, None
    async with aiohttp.ClientSession() as session:
        payload = {
            "asset": "USDT",
            "amount": str(amount_usd),
            "description": f"ShadowVPN #{order_id}",
            "paid_btn_name": "openBot",
            "paid_btn_url": f"https://t.me/{BOT_USERNAME}"
        }
        headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN, "Content-Type": "application/json"}
        async with session.post("https://pay.crypt.bot/api/createInvoice", json=payload, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok"):
                return data["result"]["bot_url"], str(data["result"]["invoice_id"])
            return None, None

async def check_crypto_payment(invoice_id: str) -> str:
    if not CRYPTOBOT_TOKEN:
        return "unknown"
    async with aiohttp.ClientSession() as session:
        payload = {"invoice_ids": invoice_id}
        headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
        async with session.post("https://pay.crypt.bot/api/getInvoices", json=payload, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok") and data["result"]["items"]:
                return data["result"]["items"][0]["status"]
    return "unknown"

async def send_config(user_id: int, order_id: int):
    file = BufferedInputFile(CONFIG_TEXT.encode(), filename="shadow.conf")
    
    caption_text = """✅ <b>ТВОЙ КОНФИГ SHADOWVPN</b>

📲 <b>КАК ПОДКЛЮЧИТЬСЯ:</b>

━━━━━━━━━━━━━━━━━━━━
🤖 <b>ANDROID:</b>
• <a href="https://play.google.com/store/apps/details?id=org.amnezia.vpn">AmneziaWG (рекомендуется)</a>
• <a href="https://play.google.com/store/apps/details?id=com.wireguard.android">WireGuard (альтернатива)</a>

🍏 <b>IPHONE / IOS:</b>
• <a href="https://apps.apple.com/app/amneziawg/id6446746462">AmneziaWG (рекомендуется)</a>
• <a href="https://apps.apple.com/app/wireguard/id1441195209">WireGuard (альтернатива)</a>
━━━━━━━━━━━━━━━━━━━━

3️⃣ Открой приложение
4️⃣ Нажми «Импортировать файл» → выбери shadow.conf
5️⃣ Включи туннель 🟢

🔒 <b>ShadowVPN — свободный интернет без границ!</b>"""
    
    await bot.send_document(
        user_id,
        document=file,
        caption=caption_text,
        parse_mode="HTML"
    )
    
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
        await message.answer(START_TEXT.format(channel_url=CHANNEL_URL, stars_price=STARS_PRICE), parse_mode="HTML", reply_markup=sub_btn)
        return

    await message.answer("🔮 <b>SHADOWVPN</b>\n\nВыбери действие в меню ниже:", parse_mode="HTML", reply_markup=Keyboards.main_menu())

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text("🔮 <b>SHADOWVPN</b>\n\nВыбери действие:", parse_mode="HTML", reply_markup=Keyboards.main_menu())
    else:
        await callback.answer("❌ Ты не подписан!", show_alert=True)

@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text("🔮 <b>SHADOWVPN</b>\n\nВыбери действие:", parse_mode="HTML", reply_markup=Keyboards.main_menu())

@dp.callback_query(lambda c: c.data == "buy_menu")
async def show_buy(callback: types.CallbackQuery):
    await callback.message.edit_text("💎 <b>ВЫБЕРИ СПОСОБ ОПЛАТЫ</b>\n\n⭐ Stars — моментально\n💳 Карта РФ — напиши админу\n🪙 USDT — крипта через CryptoBot", parse_mode="HTML", reply_markup=Keyboards.buy_menu())

@dp.callback_query(lambda c: c.data == "help")
async def show_help(callback: types.CallbackQuery):
    help_text = f"""❓ <b>ПОМОЩЬ</b>

<b>Как получить конфиг?</b>
1. Оплати удобным способом
2. Для Stars — конфиг приходит автоматически
3. Для карты — напиши {ADMIN_CONTACT} после оплаты
4. Для крипты — нажми «Проверить оплату»

<b>Не приходит конфиг?</b>
Напиши {ADMIN_CONTACT}

<b>Что делать после получения конфига?</b>
1. Скачай AmneziaWG (ссылки выше)
2. Импортируй файл shadow.conf
3. Нажми подключиться"""
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
        await callback.answer("⭐ Счёт отправлен! Проверь диалог.")
    except Exception as e:
        await callback.answer("❌ Ошибка, сообщи админу", show_alert=True)
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, f"Stars ошибка: {e}")

@dp.pre_checkout_query()
async def pre_checkout_handler(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def on_successful_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload
    order_id = int(payload.split("_")[1])
    cursor.execute("UPDATE orders SET order_status = ?, completed_at = ? WHERE id = ?", ("completed", datetime.now().isoformat(), order_id))
    conn.commit()
    await send_config(message.chat.id, order_id)
    await message.answer("⭐ Спасибо за покупку!")

# ========== ОПЛАТА КАРТОЙ ==========
@dp.callback_query(lambda c: c.data == "pay_card")
async def card_pay(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "no_username"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?,?,?,?,?,?)",
                   (user_id, username, "card", "100₽", "waiting", datetime.now().isoformat()))
    conn.commit()
    order_id = cursor.lastrowid

    # Уведомление админам
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"💳 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>\n\n"
            f"👤 Пользователь: @{username}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"💰 Сумма: 100₽\n\n"
            f"📌 Статус: ожидает оплаты\n\n"
            f"💡 После проверки оплаты введи: /send_config {order_id}",
            parse_mode="HTML"
        )

    # Клавиатура с реквизитами и админом
    card_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 2200 1234 5678 9012", callback_data="noop")],
        [InlineKeyboardButton(text="🏦 Сбербанк / Тинькофф", callback_data="noop")],
        [InlineKeyboardButton(text="💰 Сумма: 100₽", callback_data="noop")],
        [InlineKeyboardButton(text="✅ Я ОПЛАТИЛ", callback_data=f"paid_card_{order_id}")],
        [InlineKeyboardButton(text="📞 НАПИСАТЬ АДМИНУ", url="https://t.me/Withoutx4")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="buy_menu")]
    ])

    # Сообщение пользователю
    await callback.message.edit_text(
        f"💳 <b>ОПЛАТА КАРТОЙ РФ</b>\n\n"
        f"📦 <b>ЗАКАЗ #{order_id}</b>\n"
        f"💰 <b>Сумма:</b> 100₽\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:</b>\n"
        f"<code>2200 1234 5678 9012</code>\n"
        f"🏦 Сбербанк / Тинькофф\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⬇️ <b>ПОСЛЕ ОПЛАТЫ НАЖМИ:</b> «Я ОПЛАТИЛ»\n"
        f"📞 <b>ИЛИ НАПИШИ АДМИНУ:</b> {ADMIN_CONTACT}\n\n"
        f"⚠️ <i>Укажи номер заказа #{order_id}, чтобы конфиг пришёл быстрее</i>\n\n"
        f"📲 <b>ПОСЛЕ ПОЛУЧЕНИЯ КОНФИГА:</b>\n"
        f"🤖 Android: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn'>AmneziaWG</a> | <a href='https://play.google.com/store/apps/details?id=com.wireguard.android'>WireGuard</a>\n"
        f"🍏 iPhone: <a href='https://apps.apple.com/app/amneziawg/id6446746462'>AmneziaWG</a> | <a href='https://apps.apple.com/app/wireguard/id1441195209'>WireGuard</a>",
        parse_mode="HTML",
        reply_markup=card_keyboard
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("paid_card_"))
async def paid_card(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    username = callback.from_user.username or "no_username"

    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"🔔 <b>ЗАЯВКА ОБ ОПЛАТЕ</b>\n\n"
            f"📦 Заказ: #{order_id}\n"
            f"👤 @{username}\n"
            f"🆔 ID: <code>{user_id}</code>\n\n"
            f"Проверь оплату и введи: /send_config {order_id}",
            parse_mode="HTML"
        )

    await callback.message.edit_text(
        f"✅ <b>ЗАЯВКА ОТПРАВЛЕНА!</b>\n\n"
        f"📦 Заказ: #{order_id}\n\n"
        f"Админ проверит оплату и отправит конфиг.\n"
        f"⏳ Обычно до 15 минут.\n\n"
        f"📞 Вопросы: {ADMIN_CONTACT}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ ГЛАВНОЕ МЕНЮ", callback_data="back_main")]
        ])
    )
    await callback.answer("✅ Уведомление отправлено")

# ========== ОПЛАТА КРИПТОЙ ==========
@dp.callback_query(lambda c: c.data == "pay_crypto")
async def crypto_pay(callback: types.CallbackQuery):
    if not CRYPTOBOT_TOKEN:
        await callback.answer("❌ Криптооплата недоступна", show_alert=True)
        return

    user_id = callback.from_user.id
    username = callback.from_user.username or "no_username"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?,?,?,?,?,?)",
                   (user_id, username, "crypto", "1 USDT", "waiting", datetime.now().isoformat()))
    conn.commit()
    order_id = cursor.lastrowid

    # Создаём счёт
    invoice_url, invoice_id = await create_crypto_invoice(1.0, order_id)

    if invoice_url and invoice_id:
        cursor.execute("UPDATE orders SET crypto_invoice_id = ? WHERE id = ?", (invoice_id, order_id))
        conn.commit()

        crypto_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💸 ПЕРЕЙТИ К ОПЛАТЕ", url=invoice_url)],
            [InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ ОПЛАТУ", callback_data=f"check_crypto_{order_id}")],
            [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="buy_menu")]
        ])

        await callback.message.edit_text(
            f"🪙 <b>ОПЛАТА CRYPTO (USDT)</b>\n\n"
            f"📦 Заказ: #{order_id}\n"
            f"💰 Сумма: 1 USDT\n\n"
            f"1️⃣ Нажми «ПЕРЕЙТИ К ОПЛАТЕ»\n"
            f"2️⃣ Оплати в @CryptoBot\n"
            f"3️⃣ Нажми «ПРОВЕРИТЬ ОПЛАТУ»\n\n"
            f"⚠️ Конфиг придёт автоматически!",
            parse_mode="HTML",
            reply_markup=crypto_btn
        )
    else:
        await callback.message.edit_text(
            f"❌ <b>ОШИБКА СОЗДАНИЯ СЧЁТА</b>\n\n"
            f"Проверь:\n"
            f"1. CRYPTOBOT_TOKEN в переменных\n"
            f"2. BOT_USERNAME (без @)\n"
            f"3. @CryptoBot дал права боту\n\n"
            f"📞 Напиши админу: {ADMIN_CONTACT}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="buy_menu")]
            ])
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("check_crypto_"))
async def check_crypto_payment_handler(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[2])

    cursor.execute("SELECT order_status, crypto_invoice_id, user_id FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()

    if not row:
        await callback.answer("Заказ не найден")
        return

    status, invoice_id, user_id = row

    if status == "completed":
        await callback.answer("✅ Конфиг уже выдан!", show_alert=True)
        return

    inv_status = await check_crypto_payment(invoice_id)

    if inv_status == "paid":
        cursor.execute("UPDATE orders SET order_status = ?, completed_at = ? WHERE id = ?", ("completed", datetime.now().isoformat(), order_id))
        conn.commit()
        await send_config(user_id, order_id)
        await callback.message.edit_text("✅ <b>ОПЛАТА ПОДТВЕРЖДЕНА!</b>\nКонфиг отправлен выше.", parse_mode="HTML")
        await callback.answer("Конфиг отправлен!")
    elif inv_status == "expired":
        await callback.answer("❌ Счёт просрочен. Создай новый заказ", show_alert=True)
    else:
        await callback.answer("⏳ Ещё не оплачено. Оплати и нажми снова.", show_alert=True)

@dp.callback_query(lambda c: c.data == "noop")
async def noop_handler(callback: types.CallbackQuery):
    await callback.answer("ℹ️ Информация", show_alert=False)

# ========== АДМИН-ПАНЕЛЬ ==========
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ <b>НЕТ ДОСТУПА</b>", parse_mode="HTML")
        return
    await message.answer("🔧 <b>АДМИН-ПАНЕЛЬ SHADOWVPN</b>\n\nВыбери действие:", parse_mode="HTML", reply_markup=Keyboards.admin_main())

@dp.callback_query(lambda c: c.data == "admin_orders")
async def admin_orders(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return

    cursor.execute("SELECT id, username, payment_method, amount, order_status FROM orders ORDER BY id DESC LIMIT 30")
    rows = cursor.fetchall()

    if not rows:
        await callback.message.edit_text("📭 <b>ЗАКАЗОВ НЕТ</b>", parse_mode="HTML")
        return

    text = "📋 <b>СПИСОК ЗАКАЗОВ</b>\n\n"
    for row in rows:
        emoji = "✅" if row[4] == "completed" else "⏳" if row[4] == "waiting" else "❌"
        text += f"{emoji} #{row[0]} | @{row[1]} | {row[2]} | {row[3]}\n"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]
    ]))

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

    await callback.message.edit_text(
        f"📊 <b>СТАТИСТИКА SHADOWVPN</b>\n\n"
        f"👥 Пользователей: {users_total}\n"
        f"📦 Всего заказов: {total}\n"
        f"✅ Выполнено: {completed}\n"
        f"⏳ Ожидают: {total - completed}\n\n"
        f"⭐ Stars продажи: {stars_sales}\n"
        f"💳 Карта продажи: {card_sales}\n"
        f"🪙 Crypto продажи: {crypto_sales}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]])
    )

@dp.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    cursor.execute("SELECT user_id, username, first_name, joined_at, is_banned FROM users ORDER BY joined_at DESC LIMIT 20")
    rows = cursor.fetchall()

    if not rows:
        await callback.message.edit_text("📭 Нет пользователей")
        return

    text = "👥 <b>ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ</b>\n\n"
    for row in rows:
        ban_status = "🔴 БАН" if row[4] == 1 else "🟢 АКТИВЕН"
        text += f"{ban_status} | {row[0]} | @{row[1] or 'нет'} | {row[2]} | {row[3][:10]}\n"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]
    ]))

@dp.callback_query(lambda c: c.data == "admin_new_order")
async def admin_new_order_prompt(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("📝 <b>СОЗДАНИЕ ЗАКАЗА</b>\n\nВведи команду:\n<code>/neworder 123456789</code>", parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing_prompt(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("📢 <b>РАССЫЛКА</b>\n\nОтправь любое сообщение — бот разошлёт ВСЕМ пользователям.\n\nДля отмены: /cancel_mailing", parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_settings")
async def admin_settings(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    text = f"⚙️ <b>НАСТРОЙКИ</b>\n\n⭐ Stars: {STARS_PRICE}\n📢 Канал: {REQUIRED_CHANNEL or 'НЕ ЗАДАН'}\n🪙 CryptoBot: {'✅' if CRYPTOBOT_TOKEN else '❌'}\n👤 Админ: {ADMIN_CONTACT}"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_back")]]))

@dp.callback_query(lambda c: c.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("🔧 <b>АДМИН-ПАНЕЛЬ SHADOWVPN</b>\n\nВыбери действие:", parse_mode="HTML", reply_markup=Keyboards.admin_main())

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

    order_id = int(parts[1])
    cursor.execute("SELECT user_id, order_status FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Заказ не найден")
        return

    user_id, status = row

    if status == "completed":
        await message.answer("✅ Конфиг уже был отправлен")
        return

    cursor.execute("UPDATE orders SET order_status = ?, completed_at = ? WHERE id = ?", ("completed", datetime.now().isoformat(), order_id))
    conn.commit()
    await send_config(user_id, order_id)
    await message.answer(f"✅ Конфиг для заказа #{order_id} отправлен!")

@dp.message(Command("neworder"))
async def new_order_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Использование: /neworder 123456789")
        return

    user_id = int(parts[1])

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?,?,?,?,?,?)",
                   (user_id, "admin_created", "manual", "100₽", "waiting", datetime.now().isoformat()))
    conn.commit()
    order_id = cursor.lastrowid

    await message.answer(f"✅ Создан заказ #{order_id} для {user_id}\n\n/send_config {order_id}")

@dp.message(Command("orders"))
async def list_orders_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    cursor.execute("SELECT id, username, payment_method, amount, order_status FROM orders ORDER BY id DESC LIMIT 30")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("📭 Нет заказов")
        return

    text = "📋 ЗАКАЗЫ:\n\n"
    for row in rows:
        emoji = "✅" if row[4] == "completed" else "⏳"
        text += f"{emoji} #{row[0]} | @{row[1]} | {row[2]} | {row[3]}\n"
    await message.answer(text)

@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'completed'")
    completed = cursor.fetchone()[0]

    await message.answer(f"📊 Статистика:\nЗаказов: {total}\nВыполнено: {completed}\nОжидают: {total - completed}")

# ========== РАССЫЛКА ==========
mailing_active = False

@dp.message(lambda msg: msg.from_user.id in ADMIN_IDS)
async def process_mailing(message: types.Message):
    global mailing_active
    if message.text and message.text.startswith("/"):
        return

    if not mailing_active and message.text and not message.text.startswith("/"):
        mailing_active = True
        cursor.execute("SELECT user_id FROM users WHERE is_banned = 0")
        users = cursor.fetchall()

        sent = 0
        failed = 0
        status_msg = await message.answer("📢 РАССЫЛКА НАЧАТА...")

        for user in users:
            try:
                await bot.copy_message(user[0], message.chat.id, message.message_id)
                sent += 1
            except:
                failed += 1
            await asyncio.sleep(0.05)

        await status_msg.edit_text(f"✅ Рассылка завершена!\nОтправлено: {sent}\nНе доставлено: {failed}")
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
    print("🚀 SHADOWVPN БОТ ЗАПУЩЕН")
    print(f"👥 Админы: {ADMIN_IDS}")
    print(f"⭐ Цена Stars: {STARS_PRICE}")
    print(f"📢 Канал: {REQUIRED_CHANNEL or 'НЕ ЗАДАН'}")
    print(f"📞 Админ контакт: {ADMIN_CONTACT}")
    if CRYPTOBOT_TOKEN:
        print(f"🪙 CryptoBot: ВКЛЮЧЁН")
    else:
        print(f"🪙 CryptoBot: ВЫКЛЮЧЕН")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
