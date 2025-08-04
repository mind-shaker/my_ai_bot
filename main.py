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
#openai_client = OpenAI(api_key=OPENAI_API_KEY)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
#openai.api_key = OPENAI_API_KEY

# 🌐 FastAPI сервер
app = FastAPI()
print(f"app {app}")

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
                {"role": "system", "content": "Ти корисний Telegram-помічник."},
                {"role": "user", "content": user_prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Помилка при запиті до OpenAI API: {e}"

