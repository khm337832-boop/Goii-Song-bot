import os
import asyncio
import yt_dlp
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIG ---
TOKEN = "8750923349:AAHsRNgP_f-o1p5-fXnTjkY0s2w8-6wh41U"

app = Flask('')
@app.route('/')
def home(): return "Bot Online"

# HIGH-END DOWNLOADER SETTINGS
YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192', # RAM သက်သာအောင် 192 ထားတာ အကောင်းဆုံးပဲ
    }],
    'quiet': True,
    'nocheckcertificate': True,
    'proxy': '', # လိုအပ်ရင်သုံးဖို့
}

async def download_task(url):
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        return ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3'), info.get('title')

async def handle_yt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtu" not in url: return
    
    msg = await update.message.reply_text("⏳ **Converting to Audio... Please wait.**")
    try:
        path, title = await download_task(url)
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(path, 'rb'), title=title)
        os.remove(path) # RAM နေရာလွတ်အောင် ချက်ချင်းပြန်ဖျက်မယ်
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

def main():
    if not os.path.exists("downloads"): os.makedirs("downloads")
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_yt))
    bot.run_polling()

if __name__ == '__main__':
    main()
