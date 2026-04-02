import os
import asyncio
import logging
import yt_dlp
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8750923349:AAHsRNgP_f-o1p5-fXnTjkY0s2w8-6wh41U"
CHANNEL_LINK = "https://t.me/music002234"
CHANNEL_USERNAME = "@music002234"

# Logging setup
logging.basicConfig(level=logging.INFO)

# Render Health Check
app = Flask('')
@app.route('/')
def home(): return "Bot is Running"
def run_web(): app.run(host='0.0.0.0', port=8080)

# --- HIGH-SPEED DOWNLOAD OPTIONS ---
YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320', # High Quality Audio
    }],
    'keepvideo': False,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'buffer_size': '16K', # RAM buffer မြှင့်ထားတယ်
    'retries': 10,
}

async def download_audio(url):
    """YouTube Video ကို MP3 အဖြစ် အမြန်ဆုံး ပြောင်းပေးမယ်"""
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        file_path = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        return file_path, info.get('title', 'Unknown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Channel Join မ Join စစ်ဆေးချက် (ရိုးရှင်းအောင် လုပ်ထားတယ်)
    btn = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]]
    await update.message.reply_text(
        "👋 မင်္ဂလာပါ! YouTube Link ပို့ပေးလိုက်ပါ၊ ကျွန်တော် MP3 အဖြစ် ချက်ချင်းပြောင်းပေးပါ့မယ်။",
        reply_markup=InlineKeyboardMarkup(btn)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        return # YouTube Link မဟုတ်ရင် ဘာမှမလုပ်ဘူး

    status = await update.message.reply_text("⚡ **Processing...**")
    
    try:
        # Download & Convert
        file_path, title = await download_audio(url)
        
        # Send Audio
        await status.edit_text("📤 **Uploading High Quality Audio...**")
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio,
                title=title,
                caption=f"🎵 {title}\n🚀 Powered by High-Speed Server"
            )
        
        # Cleanup
        os.remove(file_path)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")

def main():
    # Start Web Server for Render
    Thread(target=run_web).start()
    
    # Start Telegram Bot
    if not os.path.exists("downloads"): os.makedirs("downloads")
    
    app_tg = Application.builder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Bot is Flying...")
    app_tg.run_polling()

if __name__ == '__main__':
    main()
