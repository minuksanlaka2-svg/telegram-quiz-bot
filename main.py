import sqlite3
import telebot
from telebot import types
import google.generativeai as genai

# --- Configurations ---
TELEGRAM_BOT_TOKEN = "8657556886:AAHd2tU-MLqCLSdwM5w4qIIoAu4qvzUcJiQ"
GEMINI_API_KEY = "AQ.Ab8RN6LpsyLKot_Z6bQI-Qy_4UQqWoA7hBXkgxQRTf4H4KlvKg"

# ඇඩ්මින්වරුන්ගේ Telegram Numeric ID ලැයිස්තුව
ADMIN_USER_IDS = [8207531738, 1732059165]

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel("gemini-1.5-flash")

# අත්සන (Signature)
FOOTER_SIGNATURE = "\n\n_⁠∫(Science_Guys)dx_Administration"

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        fullname TEXT)''')
                        
    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        quiz_name TEXT,
                        score REAL,
                        total_questions INTEGER,
                        percentage REAL,
                        time_taken TEXT)''')
                        
    cursor.execute('''CREATE TABLE IF NOT EXISTS essay_submissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        quiz_name TEXT,
                        question_text TEXT,
                        user_answer TEXT,
                        status TEXT DEFAULT 'pending')''')
    conn.commit()
    conn.close()

init_db()

admin_creation_state = {}
active_quizzes = {}

# --- Commands: Start, Help & AI Ask ---
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user = message.from_user
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, username, fullname) VALUES (?, ?, ?)",
                   (user.id, user.username, user.full_name))
    conn.commit()
    conn.close()
    
    welcome_text = (
        f"👋 සාදරයෙන් පිළිගනිමු, {user.first_name}!\n\n"
        f"මෙය Science Guys Group හි නිල Quiz සහ AI Assistant Bot වේ.\n\n"
        f"🔹 **පාවිච්චි කළ හැකි කමාන්ඩ්ස්:**\n"
        f"• `/ask [ඔබේ ප්‍රශ්නය]` - ඕනෑම දෙයක් AI එකෙන් දැනගැනීමට\n"
        f"• `/myhistory` - ඔබගේ පෙර ලකුණු බැලීමට\n"
        f"• `/help` - උදව් මෙනුව බැලීමට\n"
        f"{FOOTER_SIGNATURE}"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def cmd_help(message):
    help_text = (
        "🤖 **Science_Guys Bot Help Menu:**\n\n"
        "🔹 **සාමාන්‍ය විධාන (Members):**\n"
        "• `/ask [question]` - ඕනෑම විෂයයක් හෝ සාමාන්‍ය දෙයක් AI එකෙන් අසා දැනගැනීමට\n"
        "• `/myhistory` - ඔබගේ ලකුණු වාර්තා බැලීමට\n\n"
        "🔹 **ඇඩ්මින් විධාන (Admins Only):**\n"
        "• `/intro` - AI ක්‍රියාකරු හඳුන්වා දීමේ පණිවිඩය සියලුම දෙනාට යැවීමට\n"
        "• `/morning` - සුභ උදෑසනක් සහ හෑල්ල සියලුම දෙනාට යැවීමට\n"
        "• `/night` - සුභ රාත්‍රියක් පණිවිඩය සියලුම දෙනාට යැවීමට\n"
        "• `/createquiz` - AI ආධාරයෙන් Quiz එකක් සකස් කිරීමට\n"
        "• `/broadcast [message]` - සැමට පණිවිඩයක් යැවීමට\n"
        "• `/stats` - බෝට් සංඛ්‍යාලේඛන බැලීමට\n"
        "• `/stop` - ක්‍රියාත්මක වෙමින් පවතින වැඩ නවත්වීමට\n"
        f"{FOOTER_SIGNATURE}"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

# --- Admin Command: Intro / AI Operator Message (/intro) ---
@bot.message_handler(commands=['intro'])
def cmd_intro(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.reply_to(message, f"❌ ඔබට මෙම විධානය භාවිතා කළ නොහැක.{FOOTER_SIGNATURE}")
        return
        
    intro_text = (
        f"Hii මම _⁠∫(Science_Guys)dx_ හි Ai ක්‍රියාකරු ඔබට පවතින ඕනෑම ගැටලු `/ask` ලෙස සඳහන් කර ලබා දෙන්න!\n"
        f"{FOOTER_SIGNATURE}"
    )
    
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    for user in users:
        try:
            bot.send_message(user[0], intro_text)
            success_count += 1
        except Exception:
            pass
            
    bot.reply_to(message, f"✅ AI ක්‍රියාකරුගේ හැඳින්වීම් පණිවිඩය සාර්ථකව මෙම්බර්ලා **{success_count}** දෙනෙකු වෙත යවන ලදී.{FOOTER_SIGNATURE}")

# --- Admin Command: Morning Wish (/morning) ---
@bot.message_handler(commands=['morning'])
def cmd_morning(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.reply_to(message, f"❌ ඔබට මෙම විධානය භාවිතා කළ නොහැක.{FOOTER_SIGNATURE}")
        return
        
    morning_text = (
        "🌅 **සුභ උදෑසනක් වේවා!** ☀️✨\n\n"
        "අලුත් දවසක් කියන්නේ අලුත් බලාපොරොත්තු, අලුත් උත්සාහයන් සහ ජයග්‍රහණ රැසක් අරන් එන සුන්දර අවස්ථාවක්. 🚀 "
        "පහුගිය දවස්වල තිබුණු බාධක, අභියෝග පැත්තකට දාලා, අද දවස ඔයාගේ ජීවිතයේ වැඩදායීත්ම සහ සතුටින්ම පිරුණු දවසක් කරගන්න! 💪🔥\n\n"
        "විද්‍යාවෙන් සහ දැනුමෙන් ඔළුව පුරවන්, අද දවසේ ඉලක්ක එකින් එක ජයගන්න ඔබට ශක්තිය හා ධෛර්යය ලැබේවා! කම්මැලිකම දුරු කරලා උපරිමෙන් වැඩ කරමු! 🧠💡\n\n"
        "ඔබට අවශ්‍ය ඕනෑම ගැටලුවක් විසඳා ගැනීමට මම (AI ක්‍රියාකරු) සූදානම්. `/ask` මඟින් මගෙන් අසන්න!\n"
        f"{FOOTER_SIGNATURE}"
    )
    
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    for user in users:
        try:
            bot.send_message(user[0], morning_text)
            success_count += 1
        except Exception:
            pass
            
    bot.reply_to(message, f"✅ සුභ උදෑසනක් පණිවිඩය සාර්ථකව මෙම්බර්ලා **{success_count}** දෙනෙකු වෙත යවන ලදී.{FOOTER_SIGNATURE}")

# --- Admin Command: Night Wish (/night) ---
@bot.message_handler(commands=['night'])
def cmd_night(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.reply_to(message, f"❌ ඔබට මෙම විධානය භාවිතා කළ නොහැක.{FOOTER_SIGNATURE}")
        return
        
    night_text = (
        "🌙 **සුභ රාත්‍රියක් වේවා!** ✨💤\n\n"
        "අද දවස පුරාම මහන්සි වෙලා අධ්‍යාපන කටයුතු කරපු, වැඩ කටයුතු කරපු ඔය හැමෝටම ගොඩක් ස්තුතියී. දැන් හොඳින් විවේක ගන්න කාලයයි! 🌌\n\n"
        "හෙට දවස මීටත් වඩා සාර්ථක, ප්‍රශ්න ගැටලු පහසුවෙන් විසඳගන්න පුළුවන් සුන්දර දවසක් වෙන්න කියලා මම ප්‍රාර්ථනා කරනවා. හෙට අලුත් ශක්තියකින් යුතුව ආයෙත් වැඩ පටන් ගමු! 🚀🧠\n\n"
        "නැවත හෙට උදෑසනින් හමුවෙමු. සුභ නින්දක්! 😴✨\n"
        f"{FOOTER_SIGNATURE}"
    )
    
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    for user in users:
        try:
            bot.send_message(user[0], night_text)
            success_count += 1
        except Exception:
            pass
            
    bot.reply_to(message, f"✅ සුභ රාත්‍රියක් පණිවිඩය සාර්ථකව මෙම්බර්ලා **{success_count}** දෙනෙකු වෙත යවන ලදී.{FOOTER_SIGNATURE}")

# --- AI General Chat Command (/ask) ---
@bot.message_handler(commands=['ask'])
def cmd_ask_ai(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        bot.reply_to(message, f"⚠️ කරුණාකර අසන්න අවශ්‍ය ප්‍රශ්නය සමඟ `/ask` විධානය යොදන්න.\nඋදා: `/ask ප්‍රභාසංශ්ලේෂණය කියන්නේ මොකක්ද?`{FOOTER_SIGNATURE}", parse_mode="Markdown")
        return
        
    user_query = command_parts[1]
    wait_msg = bot.reply_to(message, f"⏳ AI එකෙන් පිළිතුරක් සූදානම් කරමින් පවතී...")
    
    try:
        response = ai_model.generate_content(user_query)
        ai_reply = response.text + FOOTER_SIGNATURE
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=wait_msg.message_id,
            text=ai_reply
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=wait_msg.message_id,
            text=f"❌ කණගාටුයි, AI එකෙන් පිළිතුර ලබාගැනීමේදී දෝෂයක් සිදු විය.{FOOTER_SIGNATURE}"
        )

@bot.message_handler(commands=['myhistory', 'myranks'])
def cmd_my_history(message):
    user_id = message.from_user.id
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT quiz_name, score, total_questions, percentage FROM results WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        bot.send_message(user_id, f"📊 ඔබ මෙතෙක් කිසිදු Quiz එකකට සහභාගී වී නැත.{FOOTER_SIGNATURE}")
        return
        
    text = "📊 **ඔබේ මෙතෙක් ඉතිහාසය සහ ලකුණු (Analysis):**\n\n"
    for r in rows:
        text += f"🔹 **Quiz:** {r[0]}\n   ස්කෝර්: {r[1]}/{r[2]} ({r[3]}%)\n\n"
        
    bot.send_message(user_id, text + FOOTER_SIGNATURE)

# --- Admin: Create Quiz & Stop ---
@bot.message_handler(commands=['createquiz'])
def cmd_create_quiz(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.reply_to(message, f"❌ ඔබට මෙම විධානය භාවිතා කළ නොහැක.{FOOTER_SIGNATURE}")
        return
    
    admin_creation_state[message.from_user.id] = {"step": "waiting_name"}
    bot.reply_to(message, f"📝 නව Quiz එකක් සකස් කිරීමට කරුණාකර **Quiz නම (Title)** ලබා දෙන්න:{FOOTER_SIGNATURE}")

@bot.message_handler(commands=['stop'])
def cmd_stop_quiz(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        return
    active_quizzes.clear()
    bot.reply_to(message, f"🛑 ක්‍රියාත්මක වෙමින් පැවති සියලුම Quiz නවත්වන ලදී.{FOOTER_SIGNATURE}")

# --- Admin Extra: Bot Statistics ---
@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.reply_to(message, f"❌ ඔබට මෙම විධානය භාවිතා කළ නොහැක.{FOOTER_SIGNATURE}")
        return
        
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM results")
    quiz_attempts = cursor.fetchone()[0]
    conn.close()
    
    stats_text = (
        f"📈 **ბෝට් සංඛ්‍යාලේඛන (Bot Statistics):**\n\n"
        f"👥 ලියාපදිංචි මුළු යූසර්ස්ලා: **{user_count}** දෙනෙක්\n"
        f"📝 සම්පූර්ණ කළ Quiz වාර ගණන: **{quiz_attempts}** ක්\n"
        f"{FOOTER_SIGNATURE}"
    )
    bot.reply_to(message, stats_text, parse_mode="Markdown")

# --- Admin Command: Broadcast ---
@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.reply_to(message, f"❌ ඔබට මෙම විධානය භාවිතා කළ නොහැක.{FOOTER_SIGNATURE}")
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        bot.reply_to(message, f"⚠️ කරුණාකර යැවිය යුතු පණිවිඩය එකතු කරන්න.\nඋදා: `/broadcast හෙට Quiz එකක් තියෙනවා!`{FOOTER_SIGNATURE}", parse_mode="Markdown")
        return
        
    broadcast_msg = command_parts[1] + FOOTER_SIGNATURE
    
    conn = sqlite3.connect("quiz_bot_pro.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    for user in users:
        try:
            bot.send_message(user[0], broadcast_msg)
            success_count += 1
        except Exception:
            pass
            
    bot.reply_to(message, f"✅ සාර්ථකව මෙම්බර්ලා **{success_count}** දෙනෙකුගේ Direct Messages වෙත පණිවිඩය යවන ලදී.{FOOTER_SIGNATURE}")

# --- AI Integration for Content Parsing ---
def process_quiz_content_with_ai(raw_text):
    prompt = (
        "ඔයා විද්‍යා සහ ගණිතමය දත්ත ප්‍රොසෙස් කරන AI කෙනෙක්. පහත දී ඇති ප්‍රශ්න කෝඩ් එක/ටෙක්ස්ට් එක "
        "ප්‍රමිතිගත කර, Unicode සංකේත (α, √, θ වැනි) නිවැරදිව යොදා, MCQ සහ Essay ලෙස වර්ග කර Structured format එකකට සකස් කර දෙන්න. "
        f"ප්‍රශ්න දත්ත මෙන්න:\n{raw_text}"
    )
    response = ai_model.generate_content(prompt)
    return response.text

# --- Message Handler for Admin Creation & Essay Submissions ---
@bot.message_handler(func=lambda msg: True)
def handle_general_messages(message):
    user_id = message.from_user.id
    
    if user_id in ADMIN_USER_IDS and user_id in admin_creation_state:
        state = admin_creation_state[user_id]
        if state["step"] == "waiting_name":
            state["quiz_name"] = message.text
            state["step"] = "waiting_questions"
            bot.reply_to(message, f"✅ නම සටහන් කරගැනිණි. දැන් **Code එකක්, Text එකක් හෝ Poll එකක්** ලෙස ප්‍රශ්න ටික එවන්න (EX සහ Time ranges සමඟ):{FOOTER_SIGNATURE}")
        elif state["step"] == "waiting_questions":
            processed_data = process_quiz_content_with_ai(message.text)
            admin_creation_state.pop(user_id, None)
            bot.reply_to(message, f"🎉 **Quiz එක සාර්ථකව සකස් විය!**\n\nProcessed Data:\n{processed_data[:600]}...\n\nඇඩ්මින්ට /broadcast මඟින් මෙය පාලනය කළ හැක.{FOOTER_SIGNATURE}")
        return

    if message.chat.type == "private" and user_id not in ADMIN_USER_IDS:
        bot.send_message(user_id, f"📥 Your answers are being checked...{FOOTER_SIGNATURE}")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Give Full Marks", callback_data=f"grade_{user_id}_pass"),
            types.InlineKeyboardButton("❌ Give Zero", callback_data=f"grade_{user_id}_fail")
        )
        bot.send_message(ADMIN_USER_IDS[0], f"📝 **New Essay Submission from User `{user_id}`:**\n\n{message.text}", reply_markup=markup, parse_mode="Markdown")

# --- Admin Grading Callbacks for Essays ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("grade_"))
def handle_grading(call):
    if call.from_user.id not in ADMIN_USER_IDS:
        return
        
    data = call.data.split("_")
    target_user_id = int(data[1])
    status = data[2]
    
    bot.answer_callback_query(call.id, "Graded successfully!")
    
    if status == "pass":
        bot.send_message(target_user_id, f"🎉 සුභ පැතුම්! ඔබේ Essay පිළිතුර නිවැරදියි, ඔබට ලකුණු ලැබී ඇත.{FOOTER_SIGNATURE}")
    else:
        bot.send_message(target_user_id, f"❌ ඔබේ Essay පිළිතුර වැරදියි. වැඩිදුර අධ්‍යයනය කරන්න.{FOOTER_SIGNATURE}")
        
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"{call.message.text}\n\n**Status: Graded ({status.upper()})**",
        parse_mode="Markdown"
    )

print("Science Guys Final Pro Bot with Revoked Token is running successfully...")
bot.infinity_polling()
