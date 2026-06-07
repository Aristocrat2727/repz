import asyncio
import sqlite3
import os
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, LabeledPrice
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# ===== КОНФИГ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")  # Токен от @CryptoBot
STARS_PRICE = int(os.getenv("STARS_PRICE", 75))
# =========================================

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
conn.commit()

# ТВОЙ КОНФИГ (полный, рабочий)
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

# ТЕКСТ СООБЩЕНИЯ
MESSAGE_TEXT = """🎉 ShadowVPN — полный доступ активирован

♾️ Бессрочная подписка

✅ Открывает:
📺 YouTube без рекламы и буфера
📸 Instagram*, TikTok, Twitch
🎮 Brawl Stars, Clash — низкий пинг
🌍 Все заблокированные сервисы РФ
📱 Discord, Spotify, Netflix
🔒 Полное шифрование трафика

📊 Характеристики:
• Выделенные серверы
• Отсутствие ограничений скорости
• Нет логирования
• Аптайм 99.9%

* Meta признана нежелательной в РФ

📲 Установка:
1️⃣ Скачай AmneziaWG: [Android](https://play.google.com/store/apps/details?id=org.amnezia.vpn) | [iPhone](https://apps.apple.com/app/amneziawg/id6446746462)
2️⃣ Открой shadow.conf → импорт
3️⃣ Включи туннель

❓ Не работает? Попробуй WireGuard: [Android](https://play.google.com/store/apps/details?id=com.wireguard.android) | [iPhone](https://apps.apple.com/app/wireguard/id1441195209)"""

# Функция создания счета в CryptoBot
async def create_crypto_invoice(amount_usd: float, order_id: int) -> tuple:
    async with aiohttp.ClientSession() as session:
        payload = {
            "asset": "USDT",
            "amount": str(amount_usd),
            "description": f"ShadowVPN заказ #{order_id}",
            "hidden_message": f"Оплата заказа #{order_id}",
            "paid_btn_name": "openBot",
            "paid_btn_url": f"https://t.me/{os.getenv('BOT_USERNAME')}?start=check_{order_id}"
        }
        headers = {
            "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
            "Content-Type": "application/json"
        }
        async with session.post("https://pay.crypt.bot/api/createInvoice", json=payload, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok"):
                return data["result"]["bot_url"], data["result"]["invoice_id"]
            return None, None

# Функция проверки статуса счета в CryptoBot
async def check_crypto_invoice(invoice_id: str) -> str:
    async with aiohttp.ClientSession() as session:
        payload = {"invoice_ids": invoice_id}
        headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
        async with session.post("https://pay.crypt.bot/api/getInvoices", json=payload, headers=headers) as resp:
            data = await resp.json()
            if data.get("ok") and data["result"]["items"]:
                return data["result"]["items"][0]["status"]
    return "unknown"

# Отправка конфига пользователю
async def send_config_to_user(user_id: int, order_id: int):
    config_bytes = CONFIG_TEXT.encode('utf-8')
    file = BufferedInputFile(config_bytes, filename="shadow.conf")
    await bot.send_document(user_id, document=file, caption=MESSAGE_TEXT, parse_mode="Markdown")
    await bot.send_message(ADMIN_ID, f"✅ Конфиг отправлен заказ #{order_id} пользователю")

@dp.message(Command("start"))
async def start(message: types.Message):
    # Обработка callback из CryptoBot
    if message.text and "start=check_" in message.text:
        order_id = int(message.text.split("_")[1])
        await check_payment_command(message, order_id)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Оплатить Stars (75⭐)", callback_data="pay_stars")],
        [InlineKeyboardButton(text="💰 Оплатить криптой (USDT)", callback_data="pay_crypto")],
        [InlineKeyboardButton(text="💳 Оплатить картой РФ (100₽)", callback_data="pay_card")],
        [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")]
    ])
    await message.answer("💸 ShadowVPN — оплата\n\nВыбери способ:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "pay_stars")
async def pay_stars(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "без юзернейма"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, username, "stars", str(STARS_PRICE), "waiting_payment", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    order_id = cursor.lastrowid

    await bot.send_invoice(
        chat_id=user_id,
        title="ShadowVPN — доступ навсегда",
        description=f"Конфиг для AmneziaWG / WireGuard. Цена: {STARS_PRICE} Stars",
        payload=f"order_{order_id}",
        currency="XTR",
        prices=[LabeledPrice(label="ShadowVPN", amount=STARS_PRICE)]
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "pay_crypto")
async def pay_crypto(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "без юзернейма"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, username, "crypto", "100₽ (≈1 USDT)", "waiting_payment", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    order_id = cursor.lastrowid

    invoice_url, invoice_id = await create_crypto_invoice(1.0, order_id)

    if invoice_url:
        cursor.execute("UPDATE orders SET crypto_check_id = ? WHERE id = ?", (str(invoice_id), order_id))
        conn.commit()

        crypto_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💸 Перейти к оплате", url=invoice_url)],
            [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check_crypto_{order_id}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
        ])
        await callback.message.edit_text(
            f"💰 Оплата криптой (USDT)\n\nЗаказ #{order_id}\nСумма: ~1 USDT\n\n1. Нажми «Перейти к оплате»\n2. Оплати через CryptoBot\n3. Нажми «Проверить оплату»\n\nПосле подтверждения конфиг придет автоматически.",
            reply_markup=crypto_keyboard
        )
    else:
        await callback.message.edit_text("❌ Ошибка создания счета. Попробуй позже или выбери другой способ оплаты.")
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("check_crypto_"))
async def check_crypto_payment(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[2])

    cursor.execute("SELECT order_status, crypto_check_id, user_id FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        await callback.answer("Заказ не найден")
        return

    status, invoice_id, user_id = row

    if status == "completed":
        await callback.answer("✅ Ты уже получил конфиг! Проверь чат.")
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
async def pay_card(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "без юзернейма"

    cursor.execute("INSERT INTO orders (user_id, username, payment_method, amount, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, username, "card", "100₽", "waiting", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    order_id = cursor.lastrowid

    await callback.message.edit_text(
        f"💳 Оплата картой РФ\n\nЗаказ #{order_id}\nСумма: 100₽\n\n👉 Напиши админу: @admin_username\nУкажи номер заказа #{order_id}\n\nПосле оплаты конфиг придет в этот чат."
    )
    await callback.answer()
    await bot.send_message(ADMIN_ID, f"🆕 ЗАЯВКА #{order_id}\n👤 @{username}\n💳 Карта\nСтатус: ожидает")

@dp.callback_query(lambda c: c.data == "support")
async def support(callback: types.CallbackQuery):
    await callback.message.edit_text("📞 Поддержка: @admin_username\n\nПо всем вопросам пиши сюда.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Оплатить Stars (75⭐)", callback_data="pay_stars")],
        [InlineKeyboardButton(text="💰 Оплатить криптой (USDT)", callback_data="pay_crypto")],
        [InlineKeyboardButton(text="💳 Оплатить картой РФ (100₽)", callback_data="pay_card")],
        [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")]
    ])
    await callback.message.edit_text("💸 ShadowVPN — оплата\n\nВыбери способ:", reply_markup=keyboard)
    await callback.answer()

@dp.message(Command("send_config"))
async def send_config_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет прав.")
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /send_config <order_id>")
        return
    order_id = int(parts[1])
    cursor.execute("SELECT user_id, order_status FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        await message.answer("Заказ не найден.")
        return
    user_id, status = row
    if status == "completed":
        await message.answer("Конфиг уже был отправлен.")
        return
    cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", ("completed", order_id))
    conn.commit()
    await send_config_to_user(user_id, order_id)
    await message.answer(f"📁 shadow.conf отправлен по заказу #{order_id}")

@dp.message(Command("orders"))
async def list_orders_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет прав.")
        return
    cursor.execute("SELECT id, username, payment_method, amount, order_status FROM orders ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    if not rows:
        await message.answer("Нет заказов.")
        return
    text = "📋 Заказы:\n\n"
    for row in rows:
        text += f"#{row[0]} | @{row[1]} | {row[2]} | {row[3]} | {row[4]}\n"
    await message.answer(text)

@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload
    order_id = int(payload.split("_")[1])
    cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", ("completed", order_id))
    conn.commit()
    await send_config_to_user(message.chat.id, order_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
