import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
print("TOKEN:", BOT_TOKEN)  # Bu qatorni vaqtincha qo‘shamiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Savollar va ballar
questions = [
    {"question": "1 + 1 = ?", "options": ["A) 1", "B) 2", "C) 3", "D) 4"], "answer": "B"},
    {"question": "5 × 2 = ?", "options": ["A) 10", "B) 7", "C) 3", "D) 12"], "answer": "A"},
    {"question": "9 − 3 = ?", "options": ["A) 6", "B) 5", "C) 8", "D) 9"], "answer": "A"},
    {"question": "12 ÷ 4 = ?", "options": ["A) 2", "B) 3", "C) 4", "D) 5"], "answer": "B"},
    {"question": "7 + 6 = ?", "options": ["A) 11", "B) 12", "C) 13", "D) 14"], "answer": "C"},
    {"question": "√25 = ?", "options": ["A) 4", "B) 5", "C) 6", "D) 7"], "answer": "B"},
    {"question": "3^2 = ?", "options": ["A) 6", "B) 9", "C) 8", "D) 7"], "answer": "B"},
    {"question": "10 + 15 = ?", "options": ["A) 25", "B) 20", "C) 24", "D) 30"], "answer": "A"},
    {"question": "18 ÷ 3 = ?", "options": ["A) 5", "B) 7", "C) 6", "D) 8"], "answer": "C"},
    {"question": "6 × 6 = ?", "options": ["A) 36", "B) 42", "C) 30", "D) 48"], "answer": "A"},
    {"question": "8^2 = ?", "options": ["A) 56", "B) 64", "C) 72", "D) 60"], "answer": "B"},
    {"question": "√81 = ?", "options": ["A) 8", "B) 10", "C) 9", "D) 11"], "answer": "C"},
    {"question": "11 × 11 = ?", "options": ["A) 121", "B) 111", "C) 131", "D) 141"], "answer": "A"},
    {"question": "100 − 45 = ?", "options": ["A) 65", "B) 55", "C) 50", "D) 45"], "answer": "B"},
    {"question": "20 + 30 = ?", "options": ["A) 40", "B) 45", "C) 50", "D) 55"], "answer": "C"}
]
points_per_question = [1.3]*5 + [2.6]*5 + [5.2]*5
user_sessions = {}

game_questions = [
    {"question": "Qaysi so'z boshqalariga o‘xshamaydi?", "options": ["A) Olma", "B) Banan", "C) Sabzi", "D) Anor"], "answer": "C"},
    {"question": "3, 6, 9, 12, ?", "options": ["A) 13", "B) 15", "C) 14", "D) 18"], "answer": "B"},
    {"question": "Qaysi so‘z ortiqcha: Qor, Yomg‘ir, Quyosh, Buzoq", "options": ["A) Qor", "B) Yomg‘ir", "C) Quyosh", "D) Buzoq"], "answer": "D"},
    {"question": "5, 10, 20, ?", "options": ["A) 30", "B) 40", "C) 25", "D) 50"], "answer": "B"},
    {"question": "Qaysi biri hayvon emas?", "options": ["A) Mushuk", "B) It", "C) Kitob", "D) Ot"], "answer": "C"},
    {"question": "2, 4, 8, 16, ?", "options": ["A) 18", "B) 24", "C) 32", "D) 30"], "answer": "C"},
    {"question": "Katta:kichik, uzun:?", "options": ["A) qisqa", "B) keng", "C) katta", "D) yupqa"], "answer": "A"},
    {"question": "Qaysi so‘z ortiqcha?", "options": ["A) Qalam", "B) Kitob", "C) Ruchka", "D) Olma"], "answer": "D"},
    {"question": "Bahor:yoz, kuz:?", "options": ["A) qish", "B) tong", "C) bahor", "D) oqshom"], "answer": "A"},
    {"question": "Kvadrat:4, Uchburchak:?", "options": ["A) 2", "B) 3", "C) 5", "D) 6"], "answer": "B"},
]
game_active = {}

# Callback: Menyu
@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    await menu_command(callback.message)

# Start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    name = message.from_user.full_name
    await message.answer(
        f"Salom, <b>{name}</b>!\n\n"
        "Botdan foydalanish uchun:\n"
        "👉 /menu - asosiy menyu\n"
        "ℹ️ /help - yordam"
    )

# Help
@dp.message(F.text == "/help")
async def help_command(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam:</b>\n\n"
        "📊 <b>Quiz</b> — 15 ta matematika savoliga javob berasiz, har bir savolga 30 soniya vaqt bor.\n"
        "🧠 <b>Aqil charxlovchi o‘yin</b> — mantiqiy savollar, javobni tanlang.\n\n"
        "Boshlash uchun:\n👉 /menu"
    )

# Menu
@dp.message(F.text == "/menu")
async def menu_command(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Quizni boshlash", callback_data="start_quiz")],
        [InlineKeyboardButton(text="🧠 Aqil charxlovchi o‘yin", callback_data="start_game")]
    ])
    await message.answer("📋 Asosiy menyu:", reply_markup=kb)

# /game bilan boshlash
@dp.message(F.text == "/game")
async def start_game_command(message: Message):
    user_id = message.from_user.id
    game_active[user_id] = 0
    await send_game_question(message, user_id)

# Callback bilan game boshlash
@dp.callback_query(F.data == "start_game")
async def start_game(callback: CallbackQuery):
    user_id = callback.from_user.id
    game_active[user_id] = 0
    await send_game_question(callback.message, user_id)

# Game savollari
async def send_game_question(message: Message, user_id: int):
    index = game_active[user_id]
    if index >= len(game_questions):
        await message.answer("🎉 O‘yin tugadi!\n👉 /menu ni bosing", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Menyuga qaytish", callback_data="menu")]
        ]))
        return
    q = game_questions[index]
    builder = InlineKeyboardBuilder()
    for opt in q["options"]:
        code = opt[0]
        builder.button(text=opt, callback_data=f"game_answer:{code}")
    await message.answer(f"🧠 <b>{q['question']}</b>", reply_markup=builder.as_markup())

# Game javoblar
@dp.callback_query(F.data.startswith("game_answer:"))
async def handle_game_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = game_active.get(user_id, 0)
    selected = callback.data.split(":")[1]
    correct = game_questions[index]["answer"]

    is_correct = selected == correct
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ To‘g‘ri!" if is_correct else f"❌ Noto‘g‘ri! To‘g‘ri javob: {correct}")
    game_active[user_id] += 1
    await send_game_question(callback.message, user_id)

# Quiz boshlash
@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_sessions[user_id] = {
        "index": 0,
        "score": 0,
        "answers": []
    }
    await callback.message.answer("🧠 Test boshlandi! Har bir savolga 30 soniya vaqtingiz bor.")
    await send_question(callback.message, user_id)

# Quiz savol
async def send_question(message: Message, user_id: int):
    session = user_sessions[user_id]
    index = session["index"]
    if index >= len(questions):
        await finish_quiz(message, user_id)
        return

    q = questions[index]
    builder = InlineKeyboardBuilder()
    for option in q["options"]:
        code = option[0]
        builder.button(text=option, callback_data=f"answer:{code}")
    sent = await message.answer(f"<b>{index+1}-savol:</b> {q['question']}\n⏳ 30 sekund qoldi", reply_markup=builder.as_markup())
    for t in range(29, -1, -1):
        await asyncio.sleep(1)
        try:
            await sent.edit_text(f"<b>{index+1}-savol:</b> {q['question']}\n⏳ {t} sekund qoldi", reply_markup=builder.as_markup())
        except:
            return
    if user_sessions[user_id]["index"] == index:
        session["answers"].append(False)
        session["index"] += 1
        await message.answer("❌ Vaqt tugadi. Keyingi savolga o'tamiz.")
        await send_question(message, user_id)

# Quiz javob
@dp.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    session = user_sessions[user_id]
    index = session["index"]
    if index >= len(questions):
        return
    selected = callback.data.split(":")[1]
    correct = questions[index]["answer"]
    is_correct = selected == correct
    session["answers"].append(is_correct)
    if is_correct:
        session["score"] += points_per_question[index]
    session["index"] += 1
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ To‘g‘ri!" if is_correct else "❌ Noto‘g‘ri!")
    await send_question(callback.message, user_id)

# Quiz tugash
async def finish_quiz(message: Message, user_id: int):
    session = user_sessions[user_id]
    total = session["score"]
    results = session["answers"]
    msg = "<b>🧾 Test tugadi!</b>\n\n"
    for i, r in enumerate(results, start=1):
        icon = "✅" if r else "❌"
        msg += f"{i}-savol: {icon}\n"
    msg += f"\n<b>Jami ball: {round(total, 2)} / 45.5</b>"
    await message.answer(msg, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Menyuga qaytish", callback_data="menu")]
    ]))

# Polling

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

