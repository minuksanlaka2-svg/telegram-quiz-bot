import os
import telebot
import google.generativeai as genai

# Railway Variables වල නම හරියටම මෙතැනට දෙන්න (Token එක මෙතැන ලියන්න එපා!)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ටෝකන් හෝ කී එක නැත්නම් පැහැදිලි Error එකක් පෙන්වීම
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in Environment Variables!")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in Environment Variables!")

# Gemini AI සෙට්අප් කිරීම
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: message.text is not None)
def handle_message(message):
    text = message.text.lower().strip()
    
    # 1. විශේෂ පිළිගැනීමේ වචන (Greeting trigger)
    if "science guys" in text or "hii science guys" in text:
        bot.reply_to(
            message, 
            "👋 Hello! Welcome to Science Guys.\n"
            "I'm the Science Guys AI Bot. Ask me any science question!"
        )
        return

    # 2. ගෘප් එකක ස්පෑම් වීම වැළැක්වීමට (Trigger conditions check කිරීම)
    # පුද්ගලික චැට් එකක (Private chat) නම් ඕනෑම මැසේජ් එකකට උත්තර දෙයි.
    # ගෘප් එකක (Group) නම් /ask කමාන්ඩ් එකෙන්, බෝට්ව Mention කර (@) හෝ Reply කර ඇසුවොත් පමණක් AI උත්තර දෙයි.
    is_group = message.chat.type in ['group', 'supergroup']
    
    bot_username = bot.get_me().username.lower()
    is_mentioned = f"@{bot_username}" in text
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id
    has_ask_command = text.startswith('/ask')

    if is_group and not (is_mentioned or is_reply_to_bot or has_ask_command):
        return  # අනෙකුත් සාමාන්‍ය මැසේජ් වලදී බෝට් නිහඬව සිටියි (Spam වීම වැළකේ)

    # /ask කමාන්ඩ් එක භාවිත කර ඇත්නම්, එම වචනය අයින් කර ප්‍රශ්නය පමණක් AI වෙත යැවීම
    if has_ask_command:
        query = message.text[4:].strip()
        if not query:
            bot.reply_to(message, "⚠️ කරුණාකර `/ask` සමඟ ඔබ අසන්නට අවශ්‍ය ප්‍රශ්නයත් ලියන්න.")
            return
    else:
        query = message.text

    # AI හරහා පිළිතුරු ලබා ගැනීම
    try:
        response = model.generate_content(query)
        bot.reply_to(message, response.text)
    except Exception:
        bot.reply_to(message, "❌ සමාවන්න, පිළිතුරක් ජනනය කිරීමේදී දෝෂයක් සිදු විය.")

print("Optimized AI Bot is running...")
bot.infinity_polling()
