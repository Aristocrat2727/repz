import asyncio
import sqlite3
import os
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    BufferedInputFile, LabeledPrice, PreCheckoutQuery
)
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# ===== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
STARS_PRICE = int(os.getenv("STARS_PRICE", 75))
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/shadowvpn_news")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
# =================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# База данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    username TEXT,
    payment_method TEXT,
    amount TEXT,
    order_status TEXT,
    created_at TEXT,
    invoice_id TEXT,
    crypto_check_id TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    joined_at TEXT
)
''')
conn.commit()

# ТВОЙ КОНФИГ
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

START_TEXT = """🔮 **ShadowVPN** — путь в свободный интернет

🌐 **Обходим любые блокировки**
🚀 **Максимальная скорость**
🛡️ **Полная анонимность**
♾️ **Бессрочный доступ**

✅ **Разблокирует:**
YouTube, Instagram*, TikTok, Discord, Spotify, Netflix, Twitch, Brawl Stars, Clash

📊 **Характеристики:**
• Выделенные серверы
• Нет ограничений скорости
• Нет логирования
• Аптайм 99.9%

*Meta признана нежелательной в РФ

💰 **Цена:**
⭐ {stars_price} Telegram Stars
💎 100₽ (карта РФ)
🪙 1 USDT (крипта)

📌 **Перед покупкой подпишись на наш канал:**
{channel_url}

После подписки нажми ✅ Я подписался"""

# ========== ФУНКЦИИ ==========
async def check_subscription(user_id: int) -> bool:
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def create_crypto_invoice(amount_usd: float, order_id: int) -> tuple:
    async with aiohttp.ClientSession() as session:
        payload = {
            "asset": "USDT",
            "amount": str(amount_usd),
            "description": f"ShadowVPN заказ #{order_id}",
            "hidden_message": f"Оплата заказа #{order_id}",
            "paid_btn_name": "openBot",
            "paid_btn_url": f"https://t.me/{BOT_USERNAME}?start=check_{order_id}"
        }
        headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN, "Content-Type": "application/json"}
        async with session.post("https://pay.crypt.bot/api/createInvoice", json=payload, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok"):
                return data["result"]["bot_url"], data["result"]["invoice_id"]
            return None, None

async def check_crypto_invoice(invoice_id: str) -> str:
    async with aiohttp.ClientSession() as session:
        payload = {"invoice_ids": invoice_id}
        headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
        async with session.post("https://pay.crypt.bot/api/getInvoices", json=payload, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok") and data["result"]["items"]:
                return data["result"]["items"][0]["status"]
    return "unknown"

async def send_config_to_user(user_id: int, order_id: int):
    config_bytes = CONFIG_TEXT.encode('utf-8')
    file = BufferedInputFile(config_bytes, filename="shadow.conf")
    await bot.send_document(user_id, document=file, caption="✅ Твой конфиг ShadowVPN. Импортируй в AmneziaWG и подключайся.")
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"✅ Конфиг отправлен заказ #{order_id} пользователю")

# ========== ХЕНДЛЕРЫ ПОЛЬЗОВАТЕЛЯ ==========
@dp.message(Command("start"))
async def start_cmd(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без юзернейма"
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, joined_at) VALUES (?, ?, ?)",
                   (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    if REQUIRED_CHANNEL and not await check_subscription(user_id):
        sub_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
        ])
        await message.answer(START_TEXT.format(channel_url=CHANNEL_URL, stars_price=STARS_PRICE), parse_mode="Markdown", reply_markup=sub_keyboard)
        return

    main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Купить ShadowVPN", callback_data="buy_menu")],
        [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")]
    ])
    await message.answer("🔮 **ShadowVPN** — твой ключ к свободному интернету\n\nВыбери действие:", parse_mode="Markdown", reply_markup=main_keyboard)

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    if await check_subscription(callback.from_user.id):
        main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Купить ShadowVPN", callback_data="buy_menu")],
            [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")]
        ])
        await callback.message.edit_text("🔮 **ShadowVPN** — твой ключ к свободному интернету\n\nВыбери действие:", parse_mode="Markdown", reply_markup=main_keyboard)
    else:
        await callback.answer("❌ Ты не подписан на канал!", show_alert=True)

@dp.callback_query(lambda c: c.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⭐ {STARS_PRICE} Stars", callback_data="pay_stars")],
        [InlineKeyboardButton(text="💰 1 USDT (крипта)", callback_data="pay_crypto")],
        [InlineKeyboardButton(text="💳 100₽ (карта РФ)", callback_data="pay_card")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    await callback.message.edit_text("💎 **Выбери способ оплаты:**\n\n⭐ Stars — моментально\n💰 USDT — через CryptoBot\n💳 Карта РФ — напишешь админу", parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "pay_stars")
async def pay_stars(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "без юзернейма"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, username, "stars", str(STARS_PRICE), "waiting_payment", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    order_id = cursor.lastrowid

    prices = [LabeledPrice(label="ShadowVPN — доступ навсегда", amount=STARS_PRICE)]

    await bot.send_invoice(
        chat_id=user_id,
        title="ShadowVPN",
        description=f"Конфиг для AmneziaWG. Цена: {STARS_PRICE} Stars",
        payload=f"order_{order_id}",
        currency="XTR",
        prices=prices
    )
    await callback.answer("⭐ Счёт отправлен! Проверь диалог с ботом.")

@dp.callback_query(lambda c: c.data == "pay_crypto")
async def pay_crypto(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "без юзернейма"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, username, "crypto", "1 USDT", "waiting_payment", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    order_id = cursor.lastrowid

    invoice_url, invoice_id = await create_crypto_invoice(1.0, order_id)

    if invoice_url:
        cursor.execute("UPDATE orders SET crypto_check_id = ? WHERE id = ?", (str(invoice_id), order_id))
        conn.commit()

        crypto_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💸 Перейти к оплате", url=invoice_url)],
            [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check_crypto_{order_id}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="buy_menu")]
        ])
        await callback.message.edit_text(
            f"💰 Оплата криптой (USDT)\n\nЗаказ #{order_id}\nСумма: 1 USDT\n\n1. Нажми «Перейти к оплате»\n2. Оплати через CryptoBot\n3. Нажми «Проверить оплату»\n\nПосле подтверждения конфиг придет автоматически.",
            reply_markup=crypto_keyboard
        )
    else:
        await callback.message.edit_text("❌ Ошибка создания счета. Попробуй позже.")
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("check_crypto_"))
async def check_crypto_payment(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    cursor.execute("SELECT order_status, crypto_check_id, user_id FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        await callback.answer("Заказ не найден")
        return

    status, invoice_id, user_id = row
    if status == "completed":
        await callback.answer("✅ Ты уже получил конфиг!")
        return

    inv_status = await check_crypto_invoice(invoice_id)
    if inv_status == "paid":
        cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", ("completed", order_id))
        conn.commit()
        await callback.message.edit_text("✅ Оплата подтверждена! Отправляю конфиг...")
        await send_config_to_user(user_id, order_id)
        await callback.answer("Конфиг отправлен!")
    elif inv_status == "expired":
        await callback.answer("❌ Счет просрочен. Создай новый заказ через /start")
    else:
        await callback.answer("⏳ Еще не оплачено. Оплати и нажми снова.", show_alert=True)

@dp.callback_query(lambda c: c.data == "pay_card")
async def pay_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "без юзернейма"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, username, "card", "100₽", "waiting", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    order_id = cursor.lastrowid

    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"🆕 ЗАЯВКА #{order_id}\n👤 @{username}\n💳 Карта\nСтатус: ожидает")

    await callback.message.edit_text(
        f"💳 Оплата картой РФ\n\nЗаказ #{order_id}\nСумма: 100₽\n\n👉 Напиши админу: @admin_username\nУкажи номер заказа #{order_id}\n\nПосле оплаты конфиг придет сюда."
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text("📞 **Поддержка:**\n\nПо всем вопросам пиши сюда: @admin_username\n\nОтветим в течение 24 часов.", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Купить ShadowVPN", callback_data="buy_menu")],
        [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")]
    ])
    await callback.message.edit_text("🔮 **ShadowVPN** — твой ключ к свободному интернету\n\nВыбери действие:", parse_mode="Markdown", reply_markup=main_keyboard)
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    order_id = int(payload.split("_")[1])
    cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", ("completed", order_id))
    conn.commit()
    await send_config_to_user(message.chat.id, order_id)

# ========== АДМИН-ПАНЕЛЬ ==========
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет прав.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список заказов", callback_data="admin_orders")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")]
    ])
    await message.answer("🔧 **Админ-панель ShadowVPN**\n\nВыбери действие:", parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return

    cursor.execute("SELECT id, username, payment_method, amount, order_status FROM orders ORDER BY id DESC LIMIT 30")
    rows = cursor.fetchall()
    if not rows:
        await callback.message.edit_text("📭 Нет заказов.")
        return

    text = "📋 **Список заказов:**\n\n"
    for row in rows:
        status_emoji = "✅" if row[4] == "completed" else "⏳"
        text += f"{status_emoji} #{row[0]} | @{row[1]} | {row[2]} | {row[3]}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Посмотреть заказ", callback_data="view_order")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "view_order")
async def view_order_prompt(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return
    await callback.message.edit_text("📝 Введите номер заказа командой:\n`/order 123`", parse_mode="Markdown")
    await callback.answer()

@dp.message(Command("order"))
async def view_order(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет прав.")
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: `/order 123`", parse_mode="Markdown")
        return

    order_id = int(parts[1])
    cursor.execute("SELECT id, user_id, username, payment_method, amount, order_status FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        await message.answer("❌ Заказ не найден.")
        return

    _, user_id, username, method, amount, status = row
    status_text = "✅ Выполнен" if status == "completed" else "⏳ Ожидает оплаты"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Отправить конфиг", callback_data=f"send_conf_{order_id}")],
        [InlineKeyboardButton(text="❌ Отменить заказ", callback_data=f"cancel_order_{order_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin_orders")]
    ])

    await message.answer(
        f"📦 **Заказ #{order_id}**\n\n"
        f"👤 Пользователь: @{username}\n"
        f"🆔 User ID: `{user_id}`\n"
        f"💳 Способ: {method}\n"
        f"💰 Сумма: {amount}\n"
        f"📌 Статус: {status_text}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data and c.data.startswith("send_conf_"))
async def send_config_by_admin(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return

    order_id = int(callback.data.split("_")[2])
    cursor.execute("SELECT user_id, order_status FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        await callback.answer("Заказ не найден")
        return

    user_id, status = row
    if status == "completed":
        await callback.answer("Конфиг уже был отправлен")
        return

    cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", ("completed", order_id))
    conn.commit()
    await send_config_to_user(user_id, order_id)
    await callback.message.edit_text(f"✅ Конфиг для заказа #{order_id} отправлен!")
    await callback.answer("Конфиг отправлен")

@dp.callback_query(lambda c: c.data and c.data.startswith("cancel_order_"))
async def cancel_order(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return

    order_id = int(callback.data.split("_")[2])
    cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", ("cancelled", order_id))
    conn.commit()
    await callback.message.edit_text(f"❌ Заказ #{order_id} отменен.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'completed'")
    completed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    await callback.message.edit_text(
        f"📊 **Статистика ShadowVPN**\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"📦 Всего заказов: {total_orders}\n"
        f"✅ Выполнено: {completed}\n"
        f"⏳ Ожидают: {total_orders - completed}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")]])
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return

    cursor.execute("SELECT user_id, username, joined_at FROM users ORDER BY joined_at DESC LIMIT 20")
    rows = cursor.fetchall()
    if not rows:
        await callback.message.edit_text("📭 Нет пользователей.")
        return

    text = "👥 **Последние пользователи:**\n\n"
    for row in rows:
        text += f"🆔 `{row[0]}` | @{row[1]} | {row[2]}\n"

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")]]))
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список заказов", callback_data="admin_orders")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")]
    ])
    await callback.message.edit_text("🔧 **Админ-панель ShadowVPN**\n\nВыбери действие:", parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_admin_orders")
async def back_to_admin_orders(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав")
        return
    await admin_orders(callback)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
