import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

import asyncio

# --- ASYNCIO EVENT LOOP FIX FOR PYTHON 3.14+ (NO MORE RUNTIME ERROR) ---
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# -----------------------------------------------------------------------

import random
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode, UserStatus, ChatMembersFilter, ChatMemberStatus
from pyrogram.errors import FloodWait, MessageNotModified, UserNotParticipant
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- FLASK KEEP ALIVE SECTION ---
from flask import Flask
from threading import Thread

web_app = Flask('')

@web_app.route('/')
def home():
    return "King Manager Bot is Running!"

def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
# --------------------------------------

# ==================== CONFIGURATION ====================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ✅ FORCE SUBSCRIBE CONFIG
FORCE_CHANNEL_ID = int(os.getenv("FORCE_CHANNEL_ID"))
FORCE_CHANNEL_LINK = os.getenv("FORCE_CHANNEL_LINK")
FORCE_GROUP = os.getenv("FORCE_GROUP")

# Owner ID for special formatting in .info
OWNER_ID = int(os.getenv("OWNER_ID", 8081343902))

# Main Manager Bot
bot = Client("KingManager", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Storage for running clients
running_users = {} 

# ==================== GLOBAL STORAGE ====================
active_spams = {} 
auto_reply_users = {}
backup_profile = {} 
tagall_running = {}
active_bans = {} # Ban tasks ko track karne ke liye

# --- SHORT SPAM LIST (AS REQUESTED) ---
SPAM_MESSAGES = [
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜 🤖🙏🤔",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗞𝗢 𝗢𝗡𝗟𝗜𝗡𝗘 𝗢𝗟𝗫 𝗣𝗘 𝗕𝗘𝗖𝗛𝗨𝗡𝗚𝗔 𝗔𝗨𝗥 𝗣𝗔𝗜𝗦𝗘 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗞𝗢𝗧𝗛𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔 😎🤩😝😍",
    "{target} 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗛𝗘 𝗕𝗔𝗗𝗜 𝗦𝗘𝗫𝗬 𝗨𝗦𝗞𝗢 𝗣𝗜𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗢𝗗𝗘𝗡𝗚𝗘 𝗣𝗘𝗣𝗦𝗜",
    "{target} 𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗢𝗥 𝗕𝗔𝗡𝗔 𝗗𝗜𝗔 𝗥𝗔𝗡𝗗 🤤🤣",
    "{target} 𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗥𝗔𝗡𝗗𝗜𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗞𝗨𝗧𝗧𝗘 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 😂👻🔥",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗔𝗞𝗘 𝗡𝗨𝗗𝗘𝗦 𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗕𝗘𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗘𝗪𝗗𝗘 👻🔥",
    "{target} 𝗬𝗘 𝗟𝗗𝗡𝗚𝗘 𝗕𝗔𝗣𝗣 𝗦𝗘",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨𝗧 𝗠𝗘𝗜 𝗔𝗣𝗣𝗟𝗘 𝗞𝗔 𝟭𝟴𝗪 𝗪𝗔𝗟𝗔 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 🔥🤩",
    "{target} 𝗥𝗔𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗘 𝗞𝗜 𝗨𝗟𝗔𝗗𝗗𝗗",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗔 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗧𝗨 𝗖𝗔𝗛 𝗞𝗘 𝗕𝗛𝗜 𝗪𝗢 𝗠𝗔𝗦𝗧 𝗖𝗛𝗨𝗗𝗔𝗜 𝗦𝗘 𝗗𝗨𝗥 𝗡𝗛𝗜 𝗝𝗔 𝗣𝗔𝗬𝗘𝗚𝗘𝗔 😏😏🤩😍",
    "{target} 𝗞𝗬𝗔 𝗠𝗔𝗧𝗟𝗔𝗕 𝗟𝗢𝗚 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗝𝗔𝗔𝗧𝗘 𝗛𝗘𝗡 𝗣𝗔𝗥 𝗣𝗔𝗜𝗦𝗘 𝗡𝗛𝗜 𝗗𝗘𝗞𝗘 𝗝𝗔𝗔𝗧𝗘 🥲 🤣 😂😂",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗞𝗔𝗔𝗧 𝗞𝗘 🤱 𝗚𝗔𝗟𝗜 𝗞𝗘 𝗞𝗨𝗧𝗧𝗢 🦮 𝗠𝗘 𝗕𝗔𝗔𝗧 𝗗𝗨𝗡𝗚𝗔 𝗣𝗛𝗜𝗥 🍞 𝗕𝗥𝗘𝗔𝗗 𝗞𝗜 𝗧𝗔𝗥𝗛 𝗞𝗛𝗔𝗬𝗘𝗡𝗚𝗘 𝗪𝗢 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 😂",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗗𝗔𝗟 𝗞𝗘 𝗟𝗢𝗙𝗜 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔 𝗗𝗜𝗡 𝗕𝗛𝗔𝗥 😍🎶🎶💥",
    "{target} 𝗧𝗘𝗥Ａ 𝗠𝗔𝗔 𝗠𝗘𝗥𝗜 𝗙𝗔𝗡",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢𝗧𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗣𝗨𝗥𝗔 𝗙𝗔𝗔𝗗 𝗗𝗜𝗔 𝗖𝗛𝗨𝗧𝗛 𝗔𝗕𝗕 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗕𝗛𝗘𝗝 😆💦🤤",
    "{target} 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗚𝗛𝗨𝗧𝗞𝗔 𝗞𝗛𝗔𝗔𝗞𝗞𝗘 𝗧𝗛𝗢𝗢𝗞 𝗗𝗨𝗡𝗚𝗔 🤣🤣",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔 𝗞𝗜 𝗖𝗛𝗨𝗤 𝗠 𝗗𝗨 𝗧𝗔𝗣𝗔 𝗧𝗔𝗣?",
    "{target} 𝗠𝗘𝗥𝗘 𝗟𝗨𝗡𝗗 𝗞𝗘 𝗕𝗔𝗔𝗔𝗔𝗔𝗟𝗟𝗟𝗟𝗟",
    "{target} 𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗠𝗔𝗗𝗘𝗥𝗖𝗛𝗢𝗢𝗗 𝗞𝗥 𝗣𝗜𝗟𝗟𝗘 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗟𝗔𝗗𝗘𝗚𝗔 𝗧𝗨 😼😂🤤",
    "{target} 𝗦𝗨𝗡 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗝𝗬𝗔𝗗𝗔 𝗡𝗔 𝗨𝗖𝗛𝗔𝗟 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗 𝗗𝗘𝗡𝗚𝗘 𝗘𝗞 𝗠𝗜𝗡 𝗠𝗘𝗜 ✅🤣🔥🤩",
    "{target} 𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗡𝗛𝗜 𝗛𝗔𝗜 𝗞𝗬𝗔? 𝟵 𝗠𝗔𝗛𝗜𝗡𝗘 𝗥𝗨𝗞 𝗦𝗔𝗚𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗘𝗧𝗔 𝗛𝗨 🤣🤣🤩",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗤 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘 🍌🍌😍",
    "{target} 𝗧𝗨 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗧𝗘𝗥𝗔 𝗞𝗛𝗔𝗡𝗗𝗔𝗡 𝗦𝗔𝗕 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗪𝗗𝗘 𝗥𝗔𝗡𝗗𝗜 𝗛𝗔𝗜 𝗥𝗔𝗡𝗗𝗜 🤢✅🔥",
    "{target} 𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗠𝗨𝗝𝗛𝗞𝗢 𝗣𝗔𝗣𝗔 𝗞𝗬𝗢𝗨𝗡𝗞𝗜 𝗠𝗘𝗡𝗘 𝗕𝗔𝗡𝗔𝗗𝗜𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀𝗞𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧 🤣🤣",
    "{target} 𝗛𝗔𝗥𝗜 𝗛𝗔𝗥𝗜 𝗚𝗛𝗔𝗔𝗦 𝗠𝗘 𝗝𝗛𝗢𝗣𝗗𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 🤣🤣💋💦",
    "{target} 𝗥𝗔𝗡𝗗𝗜 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘",
    "{target} 𝗔𝗔𝗝 𝗧𝗘𝗥𝗔 𝗞𝗛𝗔𝗡𝗗𝗔𝗡 𝗫𝗛𝗨𝗗𝗘𝗚𝗔 💦🍆🍑",
    "{target} 𝗔𝗥𝗘 𝗥𝗘 𝗠𝗘𝗥𝗘 𝗕𝗘𝗧𝗘 𝗞𝗬𝗢𝗨𝗡 𝗦𝗣𝗘𝗘𝗗 𝗣𝗔𝗞𝗔𝗗 𝗡𝗔 𝗣𝗔𝗔𝗔 𝗥𝗔𝗛𝗔 𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗛𝗔𝗛𝗔𝗛 🤣",
    "{target} 𝗦𝗛𝗔𝗥𝗔𝗠 𝗞𝗔𝗥 𝗧𝗘𝗥𝗜 𝗕𝗘́𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗞𝗜𝗧𝗡𝗔 𝗚𝗔𝗔𝗟𝗜𝗔 𝗦𝗨𝗡𝗪𝗔𝗬𝗘𝗚𝗔 𝗔𝗣𝗡𝗜 𝗠𝗔́𝗔̀𝗔 𝗕𝗘́𝗛𝗘𝗡 𝗞𝗘 𝗨𝗣𝗘𝗥",
    "{target} 𝗔𝗨𝗞𝗔𝗔𝗧 𝗠𝗘 𝗥𝗘𝗛 𝗩𝗥𝗡𝗔 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗗𝗔𝗡𝗗𝗔 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗠𝗨𝗛 𝗦𝗘 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗦𝗛𝗔𝗥𝗜𝗥 𝗕𝗛𝗜 𝗗𝗔𝗡𝗗𝗘 𝗝𝗘𝗦𝗔 𝗗𝗜𝗞𝗛𝗘𝗚𝗔 🙄🤭🤭",
    "{target} 𝗧𝗘𝗥𝗜 𝗦𝗘𝗫𝗬 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗤 𝗢𝗣",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗔𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗞𝗢 𝗣𝗢𝗥𝗡𝗛𝗨𝗕.𝗖𝗢𝗠 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 🤣💋💦",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗙𝗔𝗡𝗧𝗔𝗦𝗬 𝗛𝗨 𝗟𝗔𝗪𝗗𝗘, 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗛𝗘𝗡 𝗞𝗢 𝗦𝗠𝗕𝗛𝗔𝗔𝗹 😈😈",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗨𝗧 𝗠𝗘𝗜 𝗖++ 𝗦𝗧𝗥𝗜𝗡𝗚 𝗘𝗡𝗖𝗥𝗬𝗣𝗧𝗜𝗢𝗡 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗛𝗧𝗜 𝗛𝗨𝗬𝗜 𝗖𝗛𝗨𝗨𝗧 𝗥𝗨𝗞 𝗝𝗔𝗬𝗘𝗚𝗜𝗜𝗜𝗜 😈🔥😍",
    "{target} 𝗧𝗨𝗝𝗛𝗘 𝗔𝗕 𝗧𝗔𝗞 𝗡𝗔𝗛𝗜 𝗦𝗠𝗝𝗛 𝗔𝗬𝗔 𝗞𝗜 𝗠𝗔𝗜 𝗛𝗜 𝗛𝗨 𝗧𝗨𝗝𝗛𝗘 𝗣𝗔𝗜𝗗𝗔 𝗞𝗔𝗥𝗡𝗘 𝗪𝗔𝗟𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘𝗘 𝗔𝗣𝗡𝗜 𝗠𝗔𝗔 𝗦𝗘 𝗣𝗨𝗖𝗛 𝗥𝗔𝗡𝗗𝗜 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘𝗘𝗘𝗘 🤩👊👤😍",
    "{target} 𝗞𝗬𝗔 𝗠𝗔𝗧𝗟𝗔𝗕 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗠𝗘𝗥𝗘 𝗟𝗢𝗗𝗘 𝗞𝗜 𝗗𝗜𝗘 𝗛𝗔𝗥𝗗 𝗙𝗔𝗡 𝗛𝗔𝗜 🔥😂💋",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗕𝗔𝗧𝗧𝗘𝗥𝗬 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗣𝗢𝗪𝗘𝗥𝗕𝗔𝗡𝗞 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔 🔋 🔥🤩",
    "{target} 𝗧𝗨𝗝𝗛𝗘 𝗗𝗘𝗞𝗛 𝗞𝗘 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗕𝗔𝗛𝗘𝗡 𝗣𝗘 𝗧𝗔𝗥𝗔𝗦 𝗔𝗧𝗔 𝗛𝗔𝗜 𝗠𝗨𝗝𝗛𝗘 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘 👿💥🤩🔥",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗛𝗔𝗜𝗥 𝗗𝗥𝗬𝗘𝗥 𝗖𝗛𝗔𝗟𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 💥🔥🔥",
    "{target} 𝗠𝗜𝗚𝗛𝗧𝗬 𝗨𝗦𝗘𝗥 𝗛𝗘𝗡 𝗛𝗨𝗠, 𝗛𝗨𝗠𝗞𝗢 𝗞𝗘𝗛𝗧𝗘 𝗛𝗘𝗡 𝗢𝗣 𝗔𝗨𝗥 𝗕𝗘𝗧𝗘 𝗧𝗨𝗠 𝗛𝗔𝗠𝗔𝗥𝗘 𝗟𝗨𝗡𝗗 𝗞𝗜 𝗧𝗢𝗣𝗜 😂",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗞𝗔𝗔𝗟𝗜 𝗠𝗜𝗧𝗖𝗛",
    "{target} 𝗧𝗘𝗥𝗜𝗜𝗜𝗜𝗜𝗜𝗜 𝗠𝗔𝗔𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧𝗧𝗧 𝗠𝗘 𝗔𝗕𝗖𝗗 𝗟𝗜𝗞𝗛 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔𝗔 𝗞𝗘 𝗟𝗢𝗗𝗘",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝗞𝗔 𝗪𝗥𝗔𝗣 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 𝟯𝟬𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 💥😂😎",
    "{target} 𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘, 𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 😆🤤💋",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 ✋ 𝗛𝗔𝗧𝗧𝗛 𝗗𝗔𝗟𝗞𝗘 👶 𝗕𝗔𝗖𝗖𝗛𝗘 𝗡𝗜𝗞𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 😍",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗦𝗨𝗗𝗢 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗕𝗜𝗚𝗦𝗣𝗔𝗠 𝗟𝗔𝗚𝗔 𝗞𝗘 𝟵𝟵𝟵𝟵 𝗙𝗨𝗖𝗞 𝗟𝗔𝗚𝗔𝗔 𝗗𝗨 🤩🥳🔥",
    "{target} 𝗥𝗔𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗖𝗛𝗔𝗟 𝗡𝗜𝗞𝗔𝗟",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗔 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗜𝗟𝗔𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗",
    "{target} 𝗦𝗨𝗡 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗜 𝗕𝗛𝗢𝗦𝗗𝗔 👿😎👊",
    "{target} 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔́𝗔̀ 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘𝗘 🤩🥳😳",
    "{target} 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗘𝗧𝗡𝗛𝗔 𝗖𝗛𝗢𝗗𝗔 𝗕𝗘𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗧𝗢 𝗠𝗘𝗥𝗜 𝗥𝗔𝗡𝗗𝗜 𝗕𝗔𝗡𝗚𝗔𝗬𝗜 𝗔𝗕𝗕 𝗖𝗛𝗔𝗟 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗢 𝗖𝗛𝗢𝗗𝗧𝗔 𝗙𝗜𝗥𝗦𝗘 ♥️💦😆",
    "{target} 𝗧𝗘𝗥𝗘 𝗕𝗘𝗛𝗘𝗡 𝗞 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗚𝗔",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗛𝗔𝗔𝗧 𝗗𝗔𝗔𝗟𝗟𝗞𝗞𝗘 𝗕𝗛𝗔𝗔𝗚 𝗝𝗔𝗔𝗡𝗨𝗡𝗚𝗔",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗠𝗘𝗥𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗬𝗔𝗔𝗗𝗘 𝗞𝗔𝗥𝗘𝗚𝗜 𝗥Æ𝗡𝗗𝗜 🥳😍👊💥",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗜 𝗖𝗛𝗨𝗨𝗧 𝗠𝗘 𝗦𝗖𝗢𝗢𝗧𝗘𝗥 𝗗𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 👅",
    "{target} 𝗧𝗘𝗥Ａ 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗥𝗔𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗘 𝗣𝗘 𝗖𝗛𝗨𝗗𝗪𝗔 𝗞𝗘 𝗨𝗦 𝗣𝗔𝗜𝗦𝗘 𝗞𝗜 𝗗𝗔𝗔𝗥𝗨 𝗣𝗘𝗘𝗧𝗔 𝗛𝗨 🍷🤩🔥",
    "{target} 𝗧𝗨 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗗𝗢𝗡𝗢 𝗞𝗜 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗠𝗘𝗧𝗥𝗢 𝗖𝗛𝗔𝗟𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗔𝗥𝗫𝗛𝗢𝗗 🚇🤩😱🥶",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗕𝗔𝗥𝗚𝗔𝗗 𝗞𝗔 𝗣𝗘𝗗 𝗨𝗚𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗖𝗢𝗥𝗢𝗡𝗔 𝗠𝗘𝗜 𝗦𝗔𝗕 𝗢𝗫𝗬𝗚𝗘𝗡 𝗟𝗘𝗞𝗮𝗿 𝗝𝗔𝗬𝗘𝗡𝗚𝗘 🤢🤩🥳",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗸 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜 💣",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗢 𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗝𝗔𝗥 𝗠𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 🤣🤣💋",
    "{target} 𝗛𝗔𝗛𝗔𝗛𝗔𝗛𝗔 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗔𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗜𝗔 𝗡𝗔𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗞𝗘",
    "{target} 𝗔𝗣𝗡𝗜 𝗔𝗠𝗠𝗔 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗨𝗦𝗞𝗢 𝗨𝗦 𝗞𝗔𝗔𝗟𝗜 𝗥𝗔𝗔𝗧 𝗠𝗘𝗜 𝗞𝗔𝗨𝗡 𝗖𝗛𝗢𝗗𝗡𝗘𝗘 𝗔𝗬𝗔 𝗧𝗛𝗔𝗔𝗔! 𝗧𝗘𝗥𝗘 𝗜𝗦 𝗣𝗔𝗣𝗔 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗟𝗘𝗚𝗜 😂👿😳",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗛𝗡 𝗦𝗕𝗦𝗘 𝗕𝗗𝗜 𝗥𝗔𝗡𝗗𝗜.",

    # 3. PURE DESI LIST (BINA MACHINE WALI)
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗕𝗜𝗦𝗧𝗔𝗥 𝗣𝗘 𝗕𝗔𝗔𝗡𝗗𝗛 𝗞𝗘 𝗣𝗘𝗟𝗨𝗡𝗚𝗔 𝗥𝗔𝗔𝗧 𝗕𝗛𝗔𝗥 🔥",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗧𝗔𝗡𝗗𝗔𝗩 𝗞𝗔𝗥𝗨𝗡𝗚𝗔 😈",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗙𝗔𝗔𝗗 𝗞𝗘 𝗛𝗔𝗪𝗔𝗜 𝗔𝗗𝗗𝗔 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔 ✈️",
    "{target} 𝗧𝗘𝗥𝗜 𝗥𝗔𝗡𝗗𝗜 𝗚𝗙 𝗞𝗢 𝗡𝗔𝗡𝗚𝗔 𝗡𝗔𝗖𝗛𝗔𝗨𝗡𝗚𝗔 𝗦𝗔𝗗𝗔𝗞 𝗣𝗘 💃",
    "{target} 𝗦𝗔𝗔𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗚𝗛𝗢𝗗𝗜 𝗕𝗔𝗡𝗔 𝗞𝗘 𝗧𝗔𝗕𝗘𝗟𝗘 𝗠𝗘𝗜 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 🐎",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗦𝗘𝗔𝗟 𝗧𝗢𝗗 𝗞𝗘 𝗨𝗦𝗞𝗢 𝗥𝗔𝗡𝗗𝗜 𝗚𝗛𝗢𝗦𝗜𝗧 𝗞𝗔𝗥𝗨𝗡𝗚𝗔 🩸",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗜𝗧𝗡𝗔 𝗩𝗜𝗥𝗬𝗔 𝗕𝗛𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗕𝗔𝗛𝗔𝗥 𝗔𝗔 𝗝𝗔𝗬𝗘 💦",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗥𝗘 𝗟𝗨𝗡𝗗 𝗞𝗜 𝗔𝗔𝗗𝗔𝗧 𝗟𝗔𝗚 𝗚𝗔𝗬𝗜 𝗛𝗔𝗜 🍆",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗 𝗞𝗘 𝗨𝗦𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗟𝗔𝗔𝗟 𝗞𝗔𝗥 𝗗𝗨𝗡𝗗𝗔 🔴",
    "{target} 𝗔𝗕𝗘 𝗥𝗔𝗡𝗗𝗜 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗞𝗢𝗧𝗛𝗘 𝗣𝗘 𝗕𝗜𝗧𝗛𝗔 𝗔𝗔𝗬𝗔 𝗛𝗨 🏚️",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗔𝗔𝗥 𝗞𝗘 𝗨𝗦𝗞𝗢 𝗖𝗛𝗔𝗟𝗡𝗘 𝗟𝗔𝗬𝗔𝗞 𝗡𝗔𝗛𝗜 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 ♿",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘𝗜 𝗟𝗨𝗡𝗗 𝗗𝗘𝗞𝗘 𝗨𝗦𝗞𝗜 𝗔𝗪𝗔𝗔𝗭 𝗕𝗔𝗡𝗗 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 🙊",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗣𝗔𝗧𝗔𝗞 𝗣𝗔𝗧𝗔𝗸 𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 🤼‍♂️",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗠𝗘𝗥𝗔 𝗟𝗔𝗪𝗗𝗔 𝗝𝗔𝗬𝗘𝗚𝗔 𝗧𝗢 𝗖𝗛𝗜𝗟𝗟𝗔𝗬𝗘𝗚𝗜 😱",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗗𝗔𝗡𝗗𝗔 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗠𝗢𝗥 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔 🦚",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝟭𝟬 𝗟𝗢𝗚𝗢𝗡 𝗦𝗘 𝗘𝗞 𝗦𝗔𝗔𝗧𝗛 𝗖𝗛𝗨𝗗𝗪𝗔𝗨𝗡𝗚𝗔 🔟",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗚𝗔𝗔𝗗𝗜 𝗠𝗘𝗜 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗦𝗨𝗡𝗦𝗔𝗔𝗡 𝗝𝗔𝗚𝗔𝗛 𝗟𝗘 𝗝𝗔𝗞𝗘 𝗣𝗘𝗟𝗨𝗡𝗚𝗔 🚗",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗔 𝗛𝗔𝗜 𝗞𝗜 𝗚𝗨𝗙𝗔 𝗟𝗔𝗚𝗧𝗔 𝗛𝗔𝗜 🕳️",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗘 𝗦𝗧𝗔𝗡 𝗞𝗔𝗔𝗧 𝗞𝗘 𝗞𝗨𝗧𝗧𝗢𝗡 𝗞𝗢 𝗞𝗛𝗜𝗟𝗔 𝗗𝗨𝗡𝗚𝗔 🐕",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗡𝗔𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗞𝗘 𝗣𝗢𝗢𝗥𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜 𝗚𝗛𝗨𝗠𝗔𝗨𝗡𝗚𝗔 🛍️",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗠𝗜𝗥𝗖𝗛𝗜 𝗕𝗛𝗔𝗥 𝗞𝗘 𝗡𝗔𝗖𝗛𝗔𝗨𝗡𝗚𝗔 🌶️",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗦𝗨𝗛𝗔𝗔𝗚𝗥𝗔𝗔𝗧 𝗠𝗔𝗡𝗔𝗨𝗡𝗚𝗔 🛌",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗥𝗘 𝗟𝗨𝗡𝗗 𝗣𝗘 𝗝𝗛𝗨𝗟𝗔 𝗝𝗛𝗨𝗟𝗔𝗔𝗨𝗡𝗚𝗔 🎢",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗛𝗔𝗧𝗛𝗢𝗗𝗔 𝗠𝗔𝗔𝗥 𝗞𝗘 𝗣𝗔𝗔𝗡𝗜 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 🔨",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗕𝗔𝗔𝗟𝗢𝗡 𝗦𝗘 𝗣𝗔𝗞𝗔𝗗 𝗞𝗘 𝗚𝗛𝗔𝗦𝗘𝗘𝗧 𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 💇‍♀️",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗞𝗔 𝗕𝗛𝗔𝗥𝗧𝗔 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔 🍆",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗝𝗔𝗡𝗚𝗔𝗟 𝗠𝗘𝗜 𝗟𝗘 𝗝𝗔𝗞𝗘 𝗝𝗔𝗔𝗡𝗪𝗔𝗥𝗢𝗡 𝗦𝗘 𝗖𝗛𝗨𝗗𝗪𝗔𝗨𝗡𝗚𝗔 🐅",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗦𝗜𝗟 𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗜 𝗗𝗛𝗔𝗔𝗚𝗘 𝗦𝗘 🧵",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗘𝗘𝗡𝗧 𝗗𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 🧱",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗞𝗛𝗔𝗗𝗔 𝗞𝗔𝗥𝗞𝗞𝗘 𝗣𝗘𝗟𝗨𝗡𝗚𝗔 𝗗𝗜𝗪𝗔𝗔𝗥 𝗞𝗘 𝗦𝗔𝗛𝗔𝗥𝗘 🧱",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗕𝗔𝗟𝗟𝗔 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗦𝗜𝗫 𝗠𝗔𝗔𝗥𝗨𝗡𝗚𝗔 🏏",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗔𝗟𝗧𝗜 𝗧𝗥𝗔𝗜𝗡 𝗠𝗘𝗜 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 🚂",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗨𝗟𝗧𝗔 𝗞𝗔𝗥𝗞𝗞𝗞𝗘 𝗨𝗦𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗠𝗨𝗛 𝗗𝗔𝗔𝗟𝗨𝗡𝗚𝗔 👅",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗕𝗔𝗔𝗡𝗦 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗠𝗢𝗥 𝗕𝗔𝗡𝗔𝗨𝗡𝗚𝗔 🎍",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗣𝗔𝗜𝗦𝗘 𝗗𝗘𝗞𝗞𝗞𝗘 𝗥𝗔𝗡𝗗𝗜 𝗕𝗔𝗡𝗔 𝗗𝗜𝗬𝗔 💵",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗞𝗜𝗖𝗛𝗔𝗗 𝗠𝗘𝗜 𝗣𝗔𝗧𝗔𝗞 𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 💩",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗦𝗔𝗔𝗠𝗣 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 🐍",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗥𝗘𝗣 𝗞𝗔𝗥𝗨𝗡𝗚𝗔 𝗣𝗢𝗟𝗜𝗖𝗘 𝗦𝗧𝗔𝗧𝗜𝗢𝗡 𝗞𝗘 𝗦𝗔𝗔𝗠𝗡𝗘 👮",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗦𝗛𝗔𝗥𝗔𝗔𝗕 𝗣𝗜𝗟𝗔 𝗞𝗘 𝗕𝗘𝗛𝗢𝗦𝗦 𝗞𝗔𝗥𝗞𝗞𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 🍷",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗚𝗢𝗟𝗜 𝗠𝗔𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 🔫",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗡𝗔𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗞𝗞𝗘 𝗩𝗜𝗗𝗘𝗢 𝗕𝗔𝗡𝗔𝗨𝗡𝗚𝗔 📹",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗖𝗛𝗘𝗘𝗥 𝗗𝗨𝗡𝗚𝗔 𝗕𝗟𝗔𝗗𝗘 𝗦𝗘 🔪",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗞𝗛𝗘𝗧 𝗠𝗘𝗜 𝗟𝗘 𝗝𝗔𝗞𝗘 𝗚𝗛𝗔𝗔𝗦 𝗣𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 🌾",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗠𝗨𝗞𝗞𝗞𝗞𝗔 𝗠𝗔𝗔𝗥 𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗗𝗔𝗔𝗡𝗜 𝗕𝗔𝗛𝗔𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗟𝗨𝗡𝗚𝗔 👊",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗠𝗢𝗠𝗕𝗔𝗧𝗧𝗜 𝗝𝗔𝗟𝗔 𝗗𝗨𝗡𝗚𝗔 🕯️",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗣𝗔𝗔𝗡𝗜 𝗞𝗜 𝗧𝗔𝗡𝗞𝗜 𝗠𝗘𝗜 𝗗𝗨𝗕𝗢 𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 💧",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗦𝗜𝗟 𝗗𝗨𝗡𝗚𝗔 𝗙𝗘𝗩𝗜𝗤𝗨𝗜𝗖𝗞 𝗦𝗘 🧪",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗞𝗢 𝗞𝗨𝗧𝗧𝗢𝗡 𝗦𝗘 𝗡𝗢𝗖𝗛𝗪𝗔𝗨𝗡𝗚𝗔 🐕",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗕𝗛𝗔𝗥𝗜 𝗦𝗔𝗕𝗛𝗔 𝗠𝗘𝗜 𝗕𝗘𝗜𝗭𝗭𝗔𝗧 𝗞𝗔𝗥𝗞𝗞𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 🤬",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗞𝗔𝗔𝗟𝗔 𝗣𝗔𝗗 𝗚𝗔𝗬𝗔 𝗛𝗔𝗜 𝗖𝗛𝗨𝗗 𝗖𝗛𝗨𝗗 𝗞𝗘 ⚫",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗝𝗛𝗔𝗔𝗗𝗨 𝗗𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 🧹",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗔𝗧 𝗦𝗘 𝗡𝗘𝗘𝗖𝗛𝗘 𝗣𝗛𝗘𝗞 𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 🏢",
    "{target} 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘𝗜 𝗣𝗔𝗧𝗧𝗛𝗔𝗥 𝗕𝗛𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 🪨",
]

# ==================== HELPER FUNCTIONS ====================

async def check_force_subscribe(client, message):
    user_id = message.from_user.id
    try:
        await client.get_chat_member(FORCE_CHANNEL_ID, user_id)
        await client.get_chat_member(FORCE_GROUP, user_id)
        return True
    except UserNotParticipant:
        buttons = [
            [InlineKeyboardButton("📢 Join Channel", url=FORCE_CHANNEL_LINK)],
            [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{FORCE_GROUP}")],
        ]
        await message.reply(
            "**⛔ ACCESS DENIED!**\n\n"
            "You must join our Channel and Group to use this bot.\n"
            "Join then try again!",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return False
    except Exception as e:
        print(f"FS Error: {e}")
        return True 

async def smart_edit(message, text, sleep_time=0.5):
    try:
        await message.edit(text, parse_mode=ParseMode.HTML)
        await asyncio.sleep(sleep_time)
    except FloodWait as e:
        if e.value < 6:
            await asyncio.sleep(e.value)
            try:
                await message.edit(text, parse_mode=ParseMode.HTML)
                await asyncio.sleep(sleep_time)
            except: pass
        else:
            pass 
    except: pass

async def draw_art(message, art_var, header="", footer="", chunk_size=4):
    lines = art_var.strip().split("\n")
    current_art = ""
    for i, line in enumerate(lines):
        current_art += line + "\n"
        if (i + 1) % chunk_size == 0 or i == len(lines) - 1:
            if header:
                display_text = f"<b>{header}</b>\n<code>{current_art}</code>"
            else:
                display_text = f"<code>{current_art}</code>"
            if i == len(lines) - 1 and footer:
                display_text += f"\n\n<b>{footer}</b>"
            await smart_edit(message, display_text, 0.5)

async def delete_res(message):
    await asyncio.sleep(5)
    try: await message.delete()
    except: pass

async def run_spam(client, chat_id, mention, count):
    global active_spams
    for i in range(count):
        if chat_id not in active_spams or not active_spams[chat_id]: break
        try:
            msg = random.choice(SPAM_MESSAGES).format(target=mention)
            await client.send_message(chat_id, msg, parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.7)
        except: break
    active_spams[chat_id] = False

# ==================== ART ASSETS ====================
CAT_ANIMATION = ["🐈",
    "🐈\nWalking...",
    "🐈\nWalking...",
    "╱|、\n( .. )\n |、˜〵\nじしˍ,)ノ", 
    "╱|、\n( > < )\n |、˜〵\nじしˍ,)ノ", 
    "╱|、\n(˚ˎ 。7\n |、˜〵\nじしˍ,)ノ", 
    "╱|、\n(˚ˎ 。7  < Meow! 🎵\n |、˜〵\nじしˍ,)ノ" ]
FLOWER_BLOOM = ["🌱", "🌿\n🌿\n🌿", "🌷\n🌷\n🌷", "🌹\n🌹\n🌹"]
ROSE_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⢔⣒⠂⣀⣀⣤⣄⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⣿⠋⢠⣟⡼⣷⠼⣆⣼⢇⣿⣄⠱⣄
⠀⠀⠀⠀⠀⠀⠀⠹⣿⡀⣆⠙⠢⠐⠉⠉⣴⣾⣽⢟⡰⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣦⠀⠤⢴⣿⠿⢋⣴⡏⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡙⠻⣿⣶⣦⣭⣉⠁⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⠀⠈⠉⠉⠉⠉⠇⡟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⣘⣦⣀⠀⠀⣀⡴⠊⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⢻⣿⣿⣿⣿⠻⣧⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠫⣿⠉⠻⣇⠘⠓⠂⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢶⣾⣿⣿⣿⣿⣿⣶⣄⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣧⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠙⠻⢿⣿⣿⠿⠛⣄⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣷⠂⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠀⠀⠀
"""
HACKER_ART = r"""
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠈⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⢀⣠⣤⣤⣤⣤⣄⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠾⣿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⣤⣶⣤⣉⣿⣿⡯⣀⣴⣿⡗⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⡈⠀⠀⠉⣿⣿⣶⡉⠀⠀⣀⡀⠀⠀⠀⢻⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⢸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠉⢉⣽⣿⠿⣿⡿⢻⣯⡍⢁⠄⠀⠀⠀⣸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠐⡀⢉⠉⠀⠠⠀⢉⣉⠀⡜⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠿⠁⠀⠀⠀⠘⣤⣭⣟⠛⠛⣉⣁⡜⠀⠀⠀⠀⠀⠛⠿⣿⣿⣿
⡿⠟⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⡀⠀⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
ERROR_ART = r"""
▒▒▒▒▒▒▒▒▄▄▄▄▄▄▄▄▒▒▒▒▒▒
▒▒█▒▒▒▄██████████▄▒▒▒▒
▒█▐▒▒▒████████████▒▒▒▒
▒▌▐▒▒██▄▀██████▀▄██▒▒▒
▐┼▐▒▒██▄▄▄▄██▄▄▄▄██▒▒▒
▐┼▐▒▒██████████████▒▒▒
▐▄▐████─▀▐▐▀█─█─▌▐██▄▒
▒▒█████──────────▐███▌
▒▒█▀▀██▄█─▄───▐─▄███▀▒
▒▒█▒▒███████▄██████▒▒▒
▒▒▒▒▒██████████████▒▒▒
▒▒▒▒▒█████████▐▌██▌▒▒▒
▒▒▒▒▒▐▀▐▒▌▀█▀▒▐▒█▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▐▒▒▒▒▌▒▒▒▒▒
"""
FUCK_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⢀⡤⠤⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣾⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⠋⠻⡇⠀⠀⢸⣧⣀⡀⠀⠀⠀⠀
⠀⠀⢀⣾⠁⠀⠀⡇⠀⠀⢸⠁⠀⢹⣀⠀⠀⠀
⢀⡴⠋⡟⠀⠀⢠⡇⠀⠀⢸⠀⠀⠀⡇⠉⢆⠀
⡎⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⠈⣆
⢷⡀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⠀⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾
⠀⠀⠈⠻⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠁
⠀⠀⠀⠀⠈⣷⠀⠀⠀⠀⠀⠀⠀⠀⢰⠋⠀⠀
⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⠀
⠀⠀⠀⠀⠀⠛⠒⠒⠒⠒⠒⠒⠒⠚⠃⠀⠀⠀
"""
BUTTERFLY_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢔⣶⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⠀⡼⠗⡿⣾⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⣀⠀⠀⠀⡇⢀⡼⠓⡞⢩⣯⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⠀⠀⠀⠀⠉⠳⢜⠰⡹⠁⢰⠃⣩⣿⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣿⠿⣉⣩⠛⠲⢶⡠⢄⢙⣣⠃⣰⠗⠋⢀⣯⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣯⣠⠬⠦⢤⣀⠈⠓⢽⣿⢔⣡⡴⠞⠻⠙⢳⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣵⣳⠖⠉⠉⢉⣩⣵⣿⣿⣒⢤⣴⠤⠽⣬⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢻⣟⠟⠋⢡⡎⢿⢿⠳⡕⢤⡉⡷⡽⠁
⣧⢮⢭⠛⢲⣦⣀⠀⠀⠀⠀⡀⠀⠀⠀⡾⣥⣏⣖⡟⠸⢺⠀⠀⠈⠙⠋⠁⠀⠀
⠈⠻⣶⡛⠲⣄⠀⠙⠢⣀⠀⢇⠀⠀⠀⠘⠿⣯⣮⢦⠶⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢻⣿⣥⡬⠽⠶⠤⣌⣣⣼⡔⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢠⣿⣧⣤⡴⢤⡴⣶⣿⣟⢯⡙⠒⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⣗⣞⣢⡟⢋⢜⣿⠛⡿⡄⢻⡮⣄⠈⠳⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠻⠮⠴⠵⢋⣇⡇⣷⢳⡀⢱⡈⢋⠛⣄⣹⣲⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣱⡇⣦⢾⣾⠿⠟⠿⠷⠷⣻⠧⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⠽⠞⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
YOURMOM_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣾⣶⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡿⠟⣡⣴⣦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀
⠀⣠⣤⣴⣶⣿⡀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠈⠻⢿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀
⢸⣿⣿⣿⣿⣿⡅⠀⠀⠀⠀⠀⢸⣿⣿⣿⣀⣀⣀⡙⢿⣿⣿⣿⣿⡄⠀⠀⠀⠀
⠸⣿⣿⣿⣿⠟⣠⣤⣴⣶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⡄⢹⣿⣿⣿⠀⠀⠀⠀⠀
⠀⠈⠉⠉⠁⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⢸⣿⣿⣿⠄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⣿⡿⠛⠛⠛⠛⠛⠛⠛⠛⣿⣿⣿⣯⢸⣿⣿⣿⠂⠀⠀⠀⠀
⢀⣤⣤⣤⣤⣤⣿⣿⣗⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣾⣿⣿⣿⣷⣶⣶⣶⣄
⠸⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟
"""
MYSON_ART = r"""
  ⠀     (\__/)
      (•ㅅ•)      Don’t talk to
   ＿ノヽ ノ＼＿      me or my son
/　/ ⌒Ｙ⌒ Ｙ  ヽ     ever again.
( 　(三ヽ人　 /　  |
|　ﾉ⌒＼ ￣￣ヽ   ノ
ヽ＿＿＿＞､＿_／
      ｜( 王 ﾉ〈  (\__/)
      /ﾐ`ー―彡\  (•ㅅ•)
     / ╰    ╯ \ /    \>
"""

# ==================== USERBOT HANDLERS ====================

async def help_handler(client, message):
    text = """
🔥 **KING USERBOT COMMANDS** 🔥

🐱 `.cat` - Cute Cat Animation
🌹 `.rose` - Rose Animation
💻 `.hacker` - Hacking Animation
⚠️ `.error` - System Crash Animation
🖕 `.fuck` - Middle Finger Animation
🦋 `.butterfly` - Draw Butterfly
🤱 `.yourmom` - Mom Roast Animation
🐰 `.myson` - Me & My Son
❤️ `.love` - Magic Heart Animation
ℹ️ `.info <reply>` - Get User Info
🚀 `.anysnap <count>` - Spam
🎯 `.aanysnap` - Global Auto-Reply
👥 `.clone` - Copy ID
🔄 `.back` - Restore ID
📍 `.tagall <msg>` - Tag Everyone
🔨 `.allban <id>` - Ban members (0.5s delay)
⚡ `.fastallban <id>` - Fast ban (0.2s - 0.3s delay)
☠️ `.end <id>` - Nuke GC (Ban -> Title -> Tag & Pin)
🛑 `.stop` - Stop Tasks
"""
    try: await message.edit(text)
    except:
        try: await client.send_message(message.chat.id, text)
        except: pass

async def cat_handler(client, message):
    for frame in CAT_ANIMATION:
        await smart_edit(message, f"<code>{frame}</code>")

async def rose_handler(client, message):
    for frame in FLOWER_BLOOM:
        await smart_edit(message, f"<code>{frame}</code>", 0.6)
    await draw_art(message, ROSE_ART, footer="🌹 **FOR YOU!**")

async def hacker_handler(client, message):
    await smart_edit(message, "💻 **Hacking System...**")
    await draw_art(message, HACKER_ART, footer="💻 **SYSTEM HACKED!**")

async def error_handler(client, message):
    await smart_edit(message, "⚠️ **SYSTEM CRASHING...**")
    await draw_art(message, ERROR_ART, footer="⚠️ **FATAL ERROR DETECTED!**")

async def fuck_handler(client, message):
    await smart_edit(message, "🖕 **Loading...**")
    await draw_art(message, FUCK_ART, footer="🖕 **FUCK YOU!**")

async def butterfly_handler(client, message):
    await smart_edit(message, "🦋 **Drawing...**")
    await draw_art(message, BUTTERFLY_ART, footer="🦋 **Fly High!**")

async def love_handler(client, message):
    frames = [
        "❤️🧡💛💚💙💜🖤🤍🤎\n❤️🧡💛💚💙💜🖤🤍🤎\n❤️🧡💛💚💙💜🖤🤍🤎",
        "🧡💛💚💙💜🖤🤍🤎❤️\n🧡💛💚💙💜🖤🤍🤎❤️\n🧡💛💚💙💜🖤🤍🤎❤️",
        "💛💚💙💜🖤🤍🤎❤️🧡\n💛💚💙💜🖤🤍🤎❤️🧡\n💛💚💙💜🖤🤍🤎❤️🧡",
        "💚💙💜🖤🤍🤎❤️🧡💛\n💚💙💜🖤🤍🤎❤️🧡💛\n💚💙💜🖤🤍🤎❤️🧡💛",
        "💙💜🖤🤍🤎❤️🧡💛💚\n💙💜🖤🤍🤎❤️🧡💛💚\n💙💜🖤🤍🤎❤️🧡💛💚",
        "💜🖤🤍🤎❤️🧡💛💚💙\n💜🖤🤍🤎❤️🧡💛💚💙\n💜🖤🤍🤎❤️🧡💛💚💙",
        "🖤🤍🤎❤️🧡💛💚💙💜\n🖤🤍🤎❤️🧡💛💚💙💜\n🖤🤍🤎❤️🧡💛💚💙💜",
        "🤍🤎❤️🧡💛💚💙💜🖤\n🤍🤎❤️🧡💛💚💙💜🖤\n🤍🤎❤️🧡💛💚💙💜🖤",
        "🤎❤️🧡💛💚💙💜🖤🤍\n🤎❤️🧡💛💚💙💜🖤🤍\n🤎❤️🧡💛💚💙💜🖤🤍",
        "❤️❤️❤️❤️❤️❤️❤️❤️❤️\n❤️❤️❤️❤️❤️❤️❤️❤️❤️\n❤️❤️❤️❤️❤️❤️❤️❤️❤️",
        "<b>I LOVE YOU ❤️</b>"
    ]
    for frame in frames:
        await smart_edit(message, frame, 0.6)

async def yourmom_handler(client, message):
    await smart_edit(message, "🤱 **Searching for Mom...**")
    await smart_edit(message, "🫦 **Target Locked!**")
    header = "🤱 ANYSNAP USER'S VS YOUR MOM 💋"
    footer = "TERI MAA MERI LUND PE 🥵💋"
    await draw_art(message, YOURMOM_ART, header=header, footer=footer)

async def myson_handler(client, message):
    await smart_edit(message, "🐰 **Summoning Son...**")
    await draw_art(message, MYSON_ART)

async def info_cmd(client, message):
    target_id = message.command[1] if len(message.command) > 1 else (message.reply_to_message.from_user.id if message.reply_to_message else "me")
    status_msg = await message.edit("Processing . . .")
    try:
        user = await client.get_users(target_id)
        chat = await client.get_chat(target_id)
        try: common = len(await client.get_common_chats(user.id))
        except: common = 0
        status_map = {UserStatus.ONLINE:"Online 🟢", UserStatus.OFFLINE:"Offline ⚫", UserStatus.RECENTLY:"Recently 🟡"}
        status = status_map.get(user.status, "Unknown")
        
        # Dynamically verify the owner using the configured .env variable
        if user.id == OWNER_ID:
            link = f"<a href='tg://user?id={user.id}'>ㅤ❛ .𝁘ໍ⸼ ‌‌ 𝐌 𝐀 𝐆 𝐌 𝐀 𐏓𝟑 🪙</a>" 
        else:
            link = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        caption = f"""USER INFORMATION:

🆔 User ID: <code>{user.id}</code>
👤 First Name: {user.first_name}
🗣️ Last Name: {user.last_name or "-"}
🌐 Username: @{user.username or "-"}
🏛️ DC ID: {user.dc_id or "-"}
🤖 Is Bot: {user.is_bot}
🚷 Is Scam: {user.is_scam}
🚫 Restricted: {user.is_restricted}
✅ Verified: {user.is_verified}
⭐ Premium: {user.is_premium or False}
📝 User Bio: {chat.bio or "-"}

👀 Same groups seen: {common}
👁️ Last Seen: {status}
🔗 User permanent link: {link}
"""
        photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
        if photos:
            await status_msg.delete()
            await client.send_photo(message.chat.id, photo=photos[0].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: await status_msg.edit(caption, parse_mode=ParseMode.HTML)
    except Exception as e: 
        await status_msg.edit(f"❌ Error: {e}")
        asyncio.create_task(delete_res(status_msg))

async def clone_cmd(client, message):
    global backup_profile
    if not message.reply_to_message:
        res = await message.edit("❌ Reply to clone!")
        return asyncio.create_task(delete_res(res))
    target = message.reply_to_message.from_user
    await message.edit(f"👤 Cloning {target.first_name}...")
    try:
        me = await client.get_me()
        backup_profile[me.id] = {
            "fn": me.first_name, 
            "ln": me.last_name or "", 
            "bio": (await client.get_chat("me")).bio or ""
        }
        async for p in client.get_chat_photos("me", limit=1):
            backup_profile[me.id]["photo"] = await client.download_media(p.file_id)

        full_t = await client.get_chat(target.id)
        await client.update_profile(first_name=target.first_name or "", last_name=target.last_name or "", bio=full_t.bio or "")
        async for p in client.get_chat_photos(target.id, limit=1):
            path = await client.download_media(p.file_id)
            await client.set_profile_photo(photo=path)
            if os.path.exists(path): os.remove(path)
        res = await message.edit(f"✅ Cloned: {target.first_name}")
    except Exception as e: res = await message.edit(f"❌ Error: {e}")
    asyncio.create_task(delete_res(res))

async def back_cmd(client, message):
    global backup_profile
    me_id = client.me.id
    if me_id not in backup_profile:
        res = await message.edit("❌ No backup found!")
        return asyncio.create_task(delete_res(res))
    await message.edit("🔄 Restoring...")
    try:
        data = backup_profile[me_id]
        await client.update_profile(first_name=data["fn"], last_name=data["ln"], bio=data["bio"])
        if "photo" in data:
            await client.set_profile_photo(photo=data["photo"])
        res = await message.edit("✅ Profile Restored!")
    except Exception as e: res = await message.edit(f"❌ Error: {e}")
    asyncio.create_task(delete_res(res))

async def anysnap_cmd(client, message):
    global active_spams
    args = message.command
    if len(args) < 2:
        res = await message.edit("❌ `.anysnap <count>`")
        return asyncio.create_task(delete_res(res))
    count = int(args[1])
    target = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(args[2] if len(args) > 2 else "me")
    mention = f"<a href='tg://user?id={target.id}'>{target.first_name}</a>"
    active_spams[message.chat.id] = True
    res = await message.edit(f"🔥 Spamming {count} on {mention}...")
    asyncio.create_task(run_spam(client, message.chat.id, mention, count))
    asyncio.create_task(delete_res(res))

async def aanysnap_cmd(client, message):
    global auto_reply_users
    if not message.reply_to_message:
        res = await message.edit("❌ Reply to target!")
        return asyncio.create_task(delete_res(res))
    target = message.reply_to_message.from_user
    mention = f"<a href='tg://user?id={target.id}'>{target.first_name}</a>"
    auto_reply_users[target.id] = mention
    res = await message.edit(f"🎯 Global Auto-Reply: {mention}")
    asyncio.create_task(delete_res(res))

async def tagall_cmd(client, message):
    global tagall_running
    chat_id = message.chat.id
    tagall_running[chat_id] = True
    msg = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    await message.delete()
    async for m in client.get_chat_members(chat_id):
        if not tagall_running.get(chat_id): break
        if m.user.is_bot: continue
        try:
            await client.send_message(chat_id, f"<a href='tg://user?id={m.user.id}'>{m.user.first_name}</a>\n{msg}", parse_mode=ParseMode.HTML)
            await asyncio.sleep(1.5)
        except: continue
    tagall_running[chat_id] = False

async def allban_cmd(client, message):
    global active_bans
    if len(message.command) < 2:
        res = await message.edit("❌ Usage: `.allban <chat_id or username>`")
        return asyncio.create_task(delete_res(res))

    chat_id = message.command[1]
    try:
        if chat_id.lstrip('-').isdigit():
            chat_id = int(chat_id)
    except: pass

    active_bans[message.chat.id] = True
    status_msg = await message.edit(f"🔨 **Mass ban started in {chat_id}...**\n(0.5s safe delay)")
    me = await client.get_me()
    banned_count = 0
    try:
        async for member in client.get_chat_members(chat_id):
            if not active_bans.get(message.chat.id, True):
                await status_msg.edit(f"🛑 **Mass ban stopped!** Banned {banned_count} members.")
                return
            if member.user.id == me.id: continue
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
            except Exception: continue

        if active_bans.get(message.chat.id, True):
            await status_msg.edit(f"✅ **Mass ban complete!** Successfully banned {banned_count} members.")
    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {e}")
        asyncio.create_task(delete_res(status_msg))

async def fastallban_cmd(client, message):
    global active_bans
    if len(message.command) < 2:
        res = await message.edit("❌ Usage: `.fastallban <chat_id or username>`")
        return asyncio.create_task(delete_res(res))

    chat_id = message.command[1]
    try:
        if chat_id.lstrip('-').isdigit():
            chat_id = int(chat_id)
    except: pass

    active_bans[message.chat.id] = True
    status_msg = await message.edit(f"⚡ **FAST Mass ban started in {chat_id}...**\n(Random delay 0.2s - 0.3s)")
    me = await client.get_me()
    banned_count = 0
    try:
        async for member in client.get_chat_members(chat_id):
            if not active_bans.get(message.chat.id, True):
                await status_msg.edit(f"🛑 **Fast Mass ban stopped!** Banned {banned_count} members.")
                return
            if member.user.id == me.id: continue
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
                await asyncio.sleep(random.uniform(0.2, 0.3)) 
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
            except Exception: continue

        if active_bans.get(message.chat.id, True):
            await status_msg.edit(f"✅ **Fast Mass ban complete!** Successfully banned {banned_count} members.")
    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {e}")
        asyncio.create_task(delete_res(status_msg))

async def end_cmd(client, message):
    global active_bans
    if len(message.command) < 2:
        res = await message.edit("❌ Usage: `.end <chat_id or username>`")
        return asyncio.create_task(delete_res(res))

    chat_id = message.command[1]
    try:
        if chat_id.lstrip('-').isdigit():
            chat_id = int(chat_id)
    except: pass

    active_bans[message.chat.id] = True
    status_msg = await message.edit(f"☠️ **NUKE GC started in {chat_id}...**\n(1. Mass Ban -> 2. Change Title -> 3. Tag & Pin)")
    me = await client.get_me()
    banned_count = 0

    # 1. FAST MASS BAN
    try:
        async for member in client.get_chat_members(chat_id):
            if not active_bans.get(message.chat.id, True):
                await status_msg.edit(f"🛑 **Nuke stopped!** Banned {banned_count} members.")
                return
            if member.user.id == me.id: continue
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
                await asyncio.sleep(random.uniform(0.2, 0.3)) 
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
            except Exception: continue
    except Exception:
        pass # Ignore errors if we can't fetch some members

    if not active_bans.get(message.chat.id, True):
        return

    # 2. CHANGE TITLE
    try:
        await client.set_chat_title(chat_id, "FUCK BY ANYSNAP USER")
    except Exception:
        pass

    # 3. FIND OWNER
    owner_mention = "Owner"
    try:
        async for admin in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if admin.status == ChatMemberStatus.OWNER:
                owner_mention = f"<a href='tg://user?id={admin.user.id}'>{admin.user.first_name}</a>"
                break
    except Exception:
        pass

    # 4. SEND MESSAGE AND PIN IT
    try:
        final_text = f"{owner_mention}\nME KYA LADLE MEAOOOUUUUUU\nGOP GOP GOP GOP GOP 🥳"
        sent_msg = await client.send_message(chat_id, final_text, parse_mode=ParseMode.HTML)
        try:
            await sent_msg.pin(both_sides=True)
        except Exception:
            try:
                await sent_msg.pin() # Fallback pin attempt
            except:
                pass
    except Exception:
        pass

    await status_msg.edit(f"✅ **Nuke complete!** Banned {banned_count} members, changed title, tagged owner and pinned message.")


async def stop_cmd(client, message):
    global active_spams, tagall_running, auto_reply_users, active_bans
    active_spams[message.chat.id] = False
    tagall_running[message.chat.id] = False
    active_bans[message.chat.id] = False 
    auto_reply_users.clear()
    res = await message.edit("🛑 **All Stopped!** (Spam, Ban, Nuke, Tagall & Auto-Reply Cleared)")
    asyncio.create_task(delete_res(res))

async def auto_reply_listener(client, message):
    global auto_reply_users
    if not message.from_user: return
    if message.from_user.id in auto_reply_users:
        mention = auto_reply_users[message.from_user.id]
        msg = random.choice(SPAM_MESSAGES).format(target=mention)
        try: await message.reply(msg, parse_mode=ParseMode.HTML)
        except: pass

# ==================== MAIN BOT LOGIC ====================

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if not await check_force_subscribe(client, message):
        return

    text = """
🔥 **WELCOME TO KING USERBOT MANAGER** 🔥

**I can help you run the powerful king Userbot on your Telegram account.**

✨ **HOW TO START:**

1️⃣ **Get Session:**
   Go to @sungofsenssion_bot and generate a **Pyrogram** String Session.

2️⃣ **Connect:**
   Send the session here using the add command:
   `/add <your_string_session>`

3️⃣ **Enjoy:**
   Once connected, type `.help` in your Saved Messages to see commands!

⚠️ **Note:** Keep your session safe!
"""
    await message.reply(text, parse_mode=ParseMode.HTML)

@bot.on_message(filters.command("add") & filters.private)
async def add_session_handler(client, message):
    if not await check_force_subscribe(client, message):
        return

    if len(message.command) < 2:
        await message.reply("❌ Usage: `/add <StringSession>`")
        return

    session_string = message.text.split(None, 1)[1]
    msg = await message.reply("🔄 Connecting...")

    try:
        new_user = Client(
            name=f"user_{random.randint(1000, 9999)}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            in_memory=True
        )

        await new_user.start()
        me = await new_user.get_me()

        new_user.add_handler(MessageHandler(help_handler, filters.command("help", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(cat_handler, filters.command("cat", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(rose_handler, filters.command("rose", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(hacker_handler, filters.command("hacker", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(error_handler, filters.command("error", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(fuck_handler, filters.command("fuck", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(butterfly_handler, filters.command("butterfly", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(love_handler, filters.command("love", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(yourmom_handler, filters.command("yourmom", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(myson_handler, filters.command("myson", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(info_cmd, filters.command("info", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(clone_cmd, filters.command("clone", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(back_cmd, filters.command("back", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(anysnap_cmd, filters.command("anysnap", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(aanysnap_cmd, filters.command("aanysnap", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(tagall_cmd, filters.command("tagall", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(allban_cmd, filters.command("allban", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(fastallban_cmd, filters.command("fastallban", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(end_cmd, filters.command("end", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(stop_cmd, filters.command("stop", prefixes=".") & filters.me))

        new_user.add_handler(MessageHandler(auto_reply_listener, filters.incoming & ~filters.me))

        running_users[me.id] = new_user

        await msg.edit(f"✅ **Connected Successfully!**\nUser: {me.first_name}\nID: `{me.id}`\n\nKing Bot is now active on your account.")
        print(f"User {me.first_name} started.")

    except Exception as e:
        await msg.edit(f"❌ **Connection Failed!**\nError: {e}")

print("✅ King Manager Bot Online - Force Subscribe Active!")

keep_alive()
bot.run()
