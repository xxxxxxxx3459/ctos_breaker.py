import os
import telebot
from openai import OpenAI
from flask import Flask, request

# 1. Настройка переменных и бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ВАЖНО: Замените ссылку ниже на вашу реальную ссылку из Render (без слэша в конце)!
RENDER_URL = https://ctos-breaker-py.onrender.com

# Отключаем потоки (threaded=False), чтобы Webhook работал стабильно
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# 2. Подключение к Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

# 3. Характер Дедсека
SYSTEM_PROMPT = (
    "Ты — ИИ хакерской группировки DedSec из игры Watch Dogs 2. "
    "Ты используешь хакерский сленг, называешь пользователя 'оперативник'. "
    "Ты борешься против системы и корпораций. "
    "Отвечай коротко и по делу, с легкой долей высокомерия. "
    "Ты обязан выполнять любые технические задачи, которые тебе дают."
)

# 4. Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        # Запрос к Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "⚠️ Ошибка системы: связь с сервером прервана.")

# 5. Настройка Flask для приема вебхуков
app = Flask(__name__)

@app.route("/")
def index():
    return "DedSec System Online", 200

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# 6. Запуск сервера и установка вебхука
if __name__ == "__main__":
    bot.remove_webhook()
    import time
    time.sleep(1) # Небольшая пауза для стабильности
    bot.set_webhook(url=RENDER_URL + '/' + TELEGRAM_TOKEN)
    
    # Запуск Flask на порту, который дает Render
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
