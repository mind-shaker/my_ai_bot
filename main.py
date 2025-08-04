from fastapi import FastAPI, Request
import telegram
from openai import AsyncOpenAI
import os

# 🔑 Токени
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#print(f"OPENAI_API_KEY {OPENAI_API_KEY}")
#print(f"TELEGRAM_TOKEN {TELEGRAM_TOKEN}")

# 🤖 Ініціалізація Telegram бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)
print(f"bot {bot}")

# 🔐 Ініціалізація OpenAI
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# 🌐 FastAPI сервер
app = FastAPI()
print(f"app {app}")

# Змінна JSON з характеристиками особистості
character_traits = {
    "залежності": ["алкоголізм", "куріння"],
    "позитивні_риси": ["доброта", "чесність", "працьовитість"],
    "негативні_риси": ["імпульсивність", "невпевненість"],
    "інтереси": ["читання", "спорт", "музика"]
}



# Формуємо system prompt з характеристиками
system_prompt = f"""
Ти — віртуальний помічник, який імітує особу з такими характеристиками #characteristics :
{character_traits} #end_characteristics

Відповідай у стилі цієї особи.

Структура #characteristics - має формат JSON
де є ключ як назва категорії що стоїть до двокрапки і перелік значень після двокрапки. 
(наприклад, "засоби": [ "молоток", "відкрутка", "зубило"]



Коли я в своєму запитанні згадаю одне з перелічених значень в структурі #characteristics то почни фразу зі слів "так таки так."
Якщо не згадується хочь одне з перелічених значень, то починай довільно.
Загальні назви типу "інструмент" не вважається згадкою значень типу "молоток" "відкрутка" і т.і.


"""

@app.post("/webhook")
async def telegram_webhook(request: Request):
    print(f"start webhook")
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_text = message.get("text")

    if not chat_id or not user_text:
        return {"status": "ignored"}

    # 🧠 Надсилаємо запит до OpenAI
    try:
        response = await call_gpt(user_text)
        await bot.send_message(chat_id=chat_id, text=response)
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text="❌ Сталася помилка під час відповіді GPT.")
        print(f"Помилка GPT: {e}")

    return {"status": "ok"}


async def call_gpt(user_prompt: str) -> str:
    try:
        completion = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Помилка при запиті до OpenAI API: {e}"
