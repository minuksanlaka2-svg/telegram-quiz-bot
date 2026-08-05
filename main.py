import os
import time
import telebot
from telebot import types

# Bot Token & Admin Setup
TOKEN = "8657556886:AAE4eT2cznyCEOOXXwvIArAbOTOCqjUahcY"
ADMIN_IDS = [8207531738, 1732059165]

bot = telebot.TeleBot(TOKEN)

# Quiz State Storage
quiz_data = {
    "active": False,
    "current_question": 0,
    "scores": {},
    "users": {}
}

# Quiz Questions List
questions = [
    {
        "question": "1. චලිතයක් පිළිබඳ v-t ප්‍රස්ථාරයක වර්ගඵලයෙන් නිරූපණය වන්නේ කුමක්ද?",
        "options": ["ත්වරණය", "විස්ථාපනය", "ප්‍රවේගය", "බලය"],
        "correct": 1,
        "explanation": "💡 **Explanation:** v-t ප්‍රස්ථාරයක් යටතේ වර්ගඵලයෙන් ලබා දෙන්නේ චලනය වූ මුළු විස්ථාපනයයි."
    },
    {
        "question": "2. ජලයේ අණුක සූත්‍රය කුමක්ද?",
        "options": ["CO2", "H2O", "NaCl", "O2"],
        "correct": 1,
        "explanation": "💡 **Explanation:** ජල අණුවක් හයිඩ්‍රජන් පරමාණු 2 කින් සහ ඔක්සිජන් පරමාණු 1 කින් සෑදී ඇත (H2O)."
    },
    {
        "question": "3. ත්වරණය මනින SI ඒකකය කුමක්ද?",
        "options": ["m/s", "N", "ms⁻²", "J"],
        "correct": 2,
        "explanation": "💡 **Explanation:** ත්වරණයේ SI ඒකකය ms⁻² වේ."
    }
]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 ආයුබෝවන්! Quiz Master Science Stream Bot වෙත සාදරයෙන් පිළිගනිමු.\n\nQuiz එක ආරම්භ කිරීමට Admin කෙනෙකු /startquiz ලබාදිය යුතුය.")

@bot.message_handler(commands=['startquiz'])
def start_quiz(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⚠️ මෙම Quiz එක ආරම්භ කිරීමට ඔබට අවසර නැත!")
        return

    if quiz_data["active"]:
        bot.reply_to(message, "⚠️ දැනටමත් Quiz එකක් ක්‍රියාත්මක වේ!")
        return

    quiz_data["active"] = True
    quiz_data["current_question"] = 0
    quiz_data["scores"] = {}
    quiz_data["users"] = {}

    bot.send_message(message.chat.id, "🚀 **Quiz එක තව තත්පර 5කින් ආරම්භ වේ!**", parse_mode="Markdown")
    time.sleep(5)
    send_next_question(message.chat.id)

def send_next_question(chat_id):
    q_index = quiz_data["current_question"]

    if q_index >= len(questions):
        finish_quiz(chat_id)
        return

    q = questions[q_index]
    markup = types.InlineKeyboardMarkup()

    for idx, opt in enumerate(q["options"]):
        btn = types.InlineKeyboardButton(text=opt, callback_data=f"ans_{q_index}_{idx}")
        markup.add(btn)

    bot.send_message(chat_id, f"❓ **ප්‍රශ්නය {q_index + 1}/{len(questions)}:**\n\n{q['question']}", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("ans_"))
def handle_answer(call):
    if not quiz_data["active"]:
        bot.answer_callback_query(call.id, "Quiz එක අවසන් වී ඇත!", show_alert=True)
        return

    _, q_idx, opt_idx = call.data.split("_")
    q_idx, opt_idx = int(q_idx), int(opt_idx)

    if q_idx != quiz_data["current_question"]:
        bot.answer_callback_query(call.id, "මෙම ප්‍රශ්නය සඳහා වේලාව අවසන්!", show_alert=True)
        return

    user_id = call.from_user.id
    user_name = call.from_user.first_name

    quiz_data["users"][user_id] = user_name

    if user_id not in quiz_data["scores"]:
        quiz_data["scores"][user_id] = 0

    correct_opt = questions[q_idx]["correct"]

    if opt_idx == correct_opt:
        quiz_data["scores"][user_id] += 1
        bot.answer_callback_query(call.id, "✅ නිවැරදියි!", show_alert=False)
    else:
        bot.answer_callback_query(call.id, "❌ වැරදියි!", show_alert=False)

    time.sleep(1)
    explanation = questions[q_idx]["explanation"]
    bot.send_message(call.message.chat.id, explanation, parse_mode="Markdown")

    quiz_data["current_question"] += 1
    time.sleep(3)
    send_next_question(call.message.chat.id)

def finish_quiz(chat_id):
    quiz_data["active"] = False
    bot.send_message(chat_id, "🏁 **Quiz එක අවසන්! මෙන්න ප්‍රතිඵල ලැයිස්තුව (Leaderboard):**\n", parse_mode="Markdown")

    sorted_scores = sorted(quiz_data["scores"].items(), key=lambda x: x[1], reverse=True)

    leaderboard_text = ""
    for rank, (u_id, score) in enumerate(sorted_scores, 1):
        name = quiz_data["users"].get(u_id, "User")
        leaderboard_text += f"{rank}. **{name}** - ලකුණු: {score}/{len(questions)}\n"

    if not leaderboard_text:
        leaderboard_text = "කිසිවෙකු පිළිතුරු ලබාදුන්නේ නැත."

    bot.send_message(chat_id, leaderboard_text, parse_mode="Markdown")

print("🤖 Quiz Bot is running...")
bot.infinity_polling()
