import asyncio
import json
import os
import random
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError, RetryAfter, TimedOut, NetworkError
import logging
from typing import Dict, Optional, Set, List
import traceback

# ===================== CONFIGURATION =====================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8007925386:AAFrVLoIaOL0yTvBp1pwXXgEAJA6ClluKXE')
OWNER_ID = [8672896246, 8882297263, 8538439635]

# ===================== ULTRA FAST SETTINGS =====================
MESSAGE_DELAY = 0.001
MAX_RAID_COUNT = 999999
MAX_SPAM_COUNT = 999999
FLOOD_WAIT_TIME = 0.5
MAX_RETRIES = 999999
BATCH_SIZE = 50
PARALLEL_TASKS = 10

# Files
SUDO_FILE = 'sudo_users.json'
ADMIN_FILE = 'admin_users.json'
MUTED_USERS_FILE = 'muted_users.json'
RAID_HISTORY_FILE = 'raid_history.json'

# ===================== 100+ GAALI MESSAGES =====================
RAID_MESSAGES = [
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗟𝗘𝗧𝗜 𝗠𝗘𝗥𝗜 𝗟𝗨𝗡𝗗 𝗕𝗔𝗗𝗘 𝗠𝗔𝗦𝗧𝗜 𝗦𝗘",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗡𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗕𝗢𝗛𝗢𝗧 𝗦𝗔𝗦𝗧𝗘 𝗦𝗘",
    "𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗",
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗟𝗘𝗞𝗘 𝗕𝗛𝗔𝗚 𝗝𝗔𝗔𝗨𝗡𝗚𝗔",
    "𝗞𝗜𝗗𝗭 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘",
    "𝗝𝗨𝗡𝗚𝗟𝗘 𝗠𝗘 𝗡𝗔𝗖𝗛𝗧𝗔 𝗛𝗘 𝗠𝗢𝗥𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔",
    "𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗠𝗨𝗝𝗛𝗞𝗢 𝗣𝗔𝗣𝗔 𝗞𝗬𝗢𝗨𝗡𝗞𝗜 𝗠𝗘𝗡𝗘 𝗕𝗔𝗡𝗔𝗗𝗜𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢𝗧𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗣𝗨𝗥𝗔 𝗙𝗔𝗔𝗗 𝗗𝗜𝗔 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗔𝗕𝗕 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗕𝗛𝗘𝗝 😆💦🤤",
    "𝗧𝗘𝗥𝗜 𝗚𝗙 𝗞𝗢 𝗘𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗧𝗢 𝗠𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗕𝗔𝗡𝗚𝗔𝗬𝗜 𝗔𝗕𝗕 𝗖𝗛𝗔𝗟 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗𝗧𝗔 𝗙𝗜𝗥𝗦𝗘 ♥️💦😆😆😆😆",
    "𝗛𝗔𝗥𝗜 𝗛𝗔𝗥𝗜 𝗚𝗛𝗔𝗔𝗦 𝗠𝗘 𝗝𝗛𝗢𝗣𝗗𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 🤣🤣💋💦",
    "𝗖𝗛𝗔𝗟 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗕𝗛𝗘𝗝 𝗧𝗘𝗥𝗔 𝗕𝗔𝗦𝗞𝗔 𝗡𝗛𝗜 𝗛𝗘 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗟𝗔𝗗𝗘𝗚𝗔 𝗧𝗨",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗕𝗢𝗠𝗕 𝗗𝗔𝗟𝗞𝗘 𝗨𝗗𝗔 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗞𝗘 𝗟𝗔𝗪𝗗𝗘",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗧𝗥𝗔𝗜𝗡 𝗠𝗘 𝗟𝗘𝗝𝗔𝗞𝗘 𝗧𝗢𝗣 𝗕𝗘𝗗 𝗣𝗘 𝗟𝗜𝗧𝗔𝗞𝗘 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 🤣🤣💋💋",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗘 𝗡𝗨𝗗𝗘𝗦 𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗘𝗪𝗗𝗘 👻🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗩𝗜𝗗𝗘𝗢 𝗕𝗔𝗡𝗔𝗞𝗘 𝗫𝗡𝗫𝗫.𝗖𝗢𝗠 𝗣𝗘 𝗡𝗘𝗘𝗟𝗔𝗠 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗞𝗨𝗧𝗧𝗘 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💦💋",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗞𝗢 𝗣𝗢𝗥𝗡𝗛𝗨𝗕.𝗖𝗢𝗠 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗗𝗨𝗡𝗚𝗔 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 🤣💋💦",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗘𝗞𝗢 𝗖𝗛𝗔𝗞𝗞𝗢 𝗦𝗘 𝗣𝗜𝗟𝗪𝗔𝗩𝗨𝗡𝗚𝗔 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 🤣🤣",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗙𝗔𝗔𝗗𝗞𝗘 𝗥𝗔𝗞𝗗𝗜𝗔 𝗠𝗔‌𝗔‌𝗞𝗘 𝗟𝗢𝗗𝗘 𝗝𝗔𝗔 𝗔𝗕𝗕 𝗦𝗜𝗟𝗪𝗔𝗟𝗘 👄👄",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗘𝗥𝗔 𝗟𝗨𝗡𝗗 𝗞𝗔𝗔𝗟𝗔",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗟𝗘𝗧𝗜 𝗠𝗘𝗥𝗜 𝗟𝗨𝗡𝗗 𝗕𝗔𝗗𝗘 𝗠𝗔𝗦𝗧𝗜 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗠𝗘𝗡𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗕𝗢𝗛𝗢𝗧 𝗦𝗔𝗦𝗧𝗘 𝗦𝗘",
    "𝗕𝗘𝗧𝗘 𝗧𝗨 𝗕𝗔𝗔𝗣 𝗦𝗘 𝗟𝗘𝗚𝗔 𝗣𝗔𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔 𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗘 𝗡𝗔𝗡𝗚𝗔 💦💋",
    "𝗛𝗔𝗛𝗔𝗛𝗔𝗛 𝗠𝗘𝗥𝗘 𝗕𝗘𝗧𝗘 𝗔𝗚𝗟𝗜 𝗕𝗔𝗔𝗥 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗟𝗘𝗞𝗘 𝗔𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗧 𝗢𝗥 𝗠𝗘𝗥𝗘 𝗠𝗢𝗧𝗘 𝗟𝗨𝗡𝗗 𝗦𝗘 𝗖𝗛𝗨𝗗𝗪𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗥",
    "𝗖𝗛𝗔𝗟 𝗕𝗘𝗧𝗔 𝗧𝗨𝗝𝗛𝗘 𝗠𝗔‌𝗔‌𝗙 𝗞𝗜𝗔 🤣 𝗔𝗕𝗕 𝗔𝗣𝗡𝗜 𝗚𝗙 𝗞𝗢 𝗕𝗛𝗘𝗝",
    "𝗦𝗛𝗔𝗥𝗔𝗠 𝗞𝗔𝗥 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗞𝗜𝗧𝗡𝗔 𝗚𝗔𝗔𝗟𝗜𝗔 𝗦𝗨𝗡𝗪𝗔𝗬𝗘𝗚𝗔 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗔 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗨𝗣𝗘𝗥",
    "𝗔𝗕𝗘 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗔𝗨𝗞𝗔𝗧 𝗡𝗛𝗜 𝗛𝗘𝗧𝗢 𝗔𝗣𝗡𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗟𝗘𝗞𝗘 𝗔𝗔𝗬𝗔 𝗠𝗔𝗧𝗛 𝗞𝗔𝗥 𝗛𝗔𝗛𝗔𝗛𝗔𝗛𝗔",
    "𝗞𝗜𝗗𝗭 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗 𝗖𝗛𝗢𝗗𝗞𝗘 𝗧𝗘𝗥𝗥 𝗟𝗜𝗬𝗘 𝗕𝗛𝗔𝗜 𝗗𝗘𝗗𝗜𝗬𝗔",
    "𝗝𝗨𝗡𝗚𝗟𝗘 𝗠𝗘 𝗡𝗔𝗖𝗛𝗧𝗔 𝗛𝗘 𝗠𝗢𝗥𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗗𝗘𝗞𝗞𝗘 𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗢𝗡𝗖𝗘 𝗠𝗢𝗥𝗘 𝗢𝗡𝗖𝗘 𝗠𝗢𝗥𝗘 🤣🤣💦💋",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗢𝗥 𝗕𝗔𝗡𝗔 𝗗𝗜𝗔 𝗥𝗔𝗡𝗗 🤤🤣",
    "𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗠𝗨𝗝𝗛𝗞𝗢 𝗣𝗔𝗣𝗔 𝗞𝗬𝗢𝗨𝗡𝗞𝗜 𝗠𝗘𝗡𝗘 𝗕𝗔𝗡𝗔𝗗𝗜𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧 🤣🤣",
    "𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗦𝗨𝗔𝗥 𝗞𝗔 𝗟𝗢𝗨𝗗𝗔 𝗢𝗥 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗘𝗥𝗔 𝗟𝗢𝗗𝗔",
    "𝗖𝗛𝗔𝗟 𝗖𝗛𝗔𝗟 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗖𝗛𝗜𝗬𝗔 𝗗𝗜𝗞𝗔",
    "𝗛𝗔𝗛𝗔𝗛𝗔𝗛𝗔 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗜𝗔 𝗡𝗔𝗡𝗚𝗔 𝗞𝗔𝗥𝗞𝗘",
    "𝗧𝗘𝗥𝗜 𝗚𝗙 𝗛𝗘 𝗕𝗔𝗗𝗜 𝗦𝗘𝗫𝗬 𝗨𝗦𝗞𝗢 𝗣𝗜𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗢𝗗𝗘𝗡𝗚𝗘 𝗣𝗘𝗣𝗦𝗜",
    "2 𝗥𝗨𝗣𝗔𝗬 𝗞𝗜 𝗣𝗘𝗣𝗦𝗜 𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗦𝗔𝗕𝗦𝗘 𝗦𝗘𝗫𝗬 💋💦",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗘𝗘𝗠𝗦 𝗦𝗘 𝗖𝗛𝗨𝗗𝗪𝗔𝗩𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗘𝗥𝗖𝗛𝗢𝗢𝗗 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💦🤣",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗠𝗘 𝗠𝗨𝗧𝗛𝗞𝗘 𝗙𝗔𝗥𝗔𝗥 𝗛𝗢𝗝𝗔𝗩𝗨𝗡𝗚𝗔 𝗛𝗨𝗜 𝗛𝗨𝗜 𝗛𝗨𝗜",
    "𝗦𝗣𝗘𝗘𝗗 𝗟𝗔𝗔𝗔 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 💋💦🤣",
    "𝗧𝗨𝗝𝗛𝗘 𝗔𝗕 𝗧𝗔𝗞 𝗡𝗔𝗛𝗜 𝗦𝗠𝗝𝗛 𝗔𝗬𝗔 𝗞𝗜 𝗠𝗔𝗜 𝗛𝗜 𝗛𝗨 𝗧𝗨𝗝𝗛𝗘 𝗣𝗔𝗜𝗗𝗔 𝗞𝗔𝗥𝗡𝗘 𝗪𝗔𝗟𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘𝗘 𝗔𝗣𝗡𝗜 𝗠𝗔‌𝗔‌ 𝗦𝗘 𝗣𝗨𝗖𝗛 𝗥Æ𝗡𝗗𝗜 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘𝗘𝗘𝗘 🤩👊👤😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗗𝗔𝗟 𝗞𝗘 𝗟𝗢𝗙𝗜 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔 𝗗𝗜𝗡 𝗕𝗛𝗔𝗥 😍🎶🎶💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗡𝗔𝗬𝗔 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗔 𝗞𝗛𝗢𝗟𝗨𝗡𝗚𝗔 𝗖𝗛𝗜𝗡𝗧𝗔 𝗠𝗔𝗧 𝗞𝗔𝗥 👊🤣🤣😳",
    "𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗘 𝗣𝗘 𝗖𝗛𝗨𝗗𝗪𝗔 𝗞𝗘 𝗨𝗦 𝗣𝗔𝗜𝗦𝗘 𝗞𝗜 𝗗𝗔𝗔𝗥𝗨 𝗣𝗘𝗘𝗧𝗔 𝗛𝗨 🍷🤩🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗔𝗣𝗡𝗔 𝗕𝗔𝗗𝗔 𝗦𝗔 𝗟𝗢𝗗𝗔 𝗚𝗛𝗨𝗦𝗦𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗞𝗔𝗟𝗟𝗔𝗔𝗣 𝗞𝗘 𝗠𝗔𝗥 𝗝𝗔𝗬𝗘𝗚𝗜 🤩😳😳🔥",
    "𝗧𝗢𝗛𝗔𝗥 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜𝗡𝗚𝗙𝗜𝗦𝗛𝗘𝗥 𝗞𝗜 𝗕𝗢𝗧𝗧𝗟𝗘 𝗗𝗔𝗟 𝗞𝗘 𝗧𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗛𝗜 😱😂🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗠𝗘𝗥𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗬𝗔𝗔𝗗 𝗞𝗔𝗥𝗘𝗚𝗜 𝗥Æ𝗡𝗗𝗜 🥳😍👊💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗔𝗨𝗥 𝗕𝗔𝗛𝗘𝗡 𝗞𝗢 𝗗𝗔𝗨𝗗𝗔 𝗗𝗔𝗨𝗗𝗔 𝗡𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗨𝗡𝗞𝗘 𝗡𝗢 𝗕𝗢𝗟𝗡𝗘 𝗣𝗘 𝗕𝗛𝗜 𝗟𝗔𝗡𝗗 𝗚𝗛𝗨𝗦𝗔 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗧𝗔𝗞 😎😎🤣🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗢 𝗢𝗡𝗟𝗜𝗡𝗘 𝗢𝗟𝗫 𝗣𝗘 𝗕𝗘𝗖𝗛𝗨𝗡𝗚𝗔 𝗔𝗨𝗥 𝗣𝗔𝗜𝗦𝗘 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗞𝗢𝗧𝗛𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔 😎🤩😝😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗔 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗧𝗨 𝗖𝗔𝗛 𝗞𝗘 𝗕𝗛𝗜 𝗪𝗢 𝗠𝗔𝗦𝗧 𝗖𝗛𝗨𝗗𝗔𝗜 𝗦𝗘 𝗗𝗨𝗥 𝗡𝗛𝗜 𝗝𝗔 𝗣𝗔𝗬𝗘𝗚𝗔𝗔 😏😏🤩😍",
    "𝗦𝗨𝗡 𝗕𝗘 𝗥Æ𝗡𝗗𝗜 𝗞𝗜 𝗔𝗨𝗟𝗔𝗔𝗗 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗔𝗛𝗘𝗡 𝗦𝗘 𝗦𝗘𝗘𝗞𝗛 𝗞𝗨𝗖𝗛 𝗞𝗔𝗜𝗦𝗘 𝗚𝗔𝗔𝗡𝗗 𝗠𝗔𝗥𝗪𝗔𝗧𝗘 𝗛𝗔𝗜😏🤬🔥💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗬𝗔𝗔𝗥 𝗛𝗨 𝗠𝗘𝗜 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗣𝗬𝗔𝗔𝗥 𝗛𝗨 𝗠𝗘𝗜 𝗔𝗝𝗔 𝗠𝗘𝗥𝗔 𝗟𝗔𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 𝗟𝗘 🤩🤣💥",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗨𝗦𝗘𝗥𝗕𝗢𝗧 𝗟𝗔𝗚𝗔𝗔𝗨𝗡𝗚𝗔 𝗦𝗔𝗦𝗧𝗘 𝗦𝗣𝗔𝗠 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗦𝗔𝗥𝗜𝗬𝗔 𝗗𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗨𝗦𝗜 𝗦𝗔𝗥𝗜𝗬𝗘 𝗣𝗥 𝗧𝗔𝗡𝗚 𝗞𝗘 𝗕𝗔𝗖𝗛𝗘 𝗣𝗔𝗜𝗗𝗔 𝗛𝗢𝗡𝗚𝗘 😱😱",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 ✋ 𝗛𝗔𝗧𝗧𝗛 𝗗𝗔𝗟𝗞𝗘 👶 𝗕??𝗖𝗖𝗛𝗘 𝗡𝗜𝗞𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘 🤤🤤",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣💋",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗘𝗘𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😚",
    "𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😆🤤💋",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗔𝗣𝗡𝗘 𝗟𝗨𝗡𝗗 𝗣𝗥 𝗜𝗧𝗡𝗔 𝗝𝗛𝗨𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗝𝗛𝗨𝗟𝗧𝗘 𝗝𝗛𝗨𝗟𝗧𝗘 𝗛𝗜 𝗕𝗔𝗖𝗛𝗔 𝗣𝗔𝗜𝗗𝗔 𝗞𝗥 𝗗𝗘𝗚𝗜 💦💋",
    "𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗦𝗔𝗗𝗔𝗞 𝗣𝗥 𝗟𝗜𝗧𝗔𝗞𝗘 𝗖𝗛𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 😂😆🤤",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗠𝗔𝗗𝗘𝗥𝗖𝗛𝗢𝗢𝗗 𝗞𝗥 𝗣𝗜𝗟𝗟𝗘 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗟𝗔𝗗𝗘𝗚𝗔 𝗧𝗨 😼😂🤤",
    "𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗡𝗘 𝗦𝗛𝗢𝗥 𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗥Æ𝗡𝗗𝗜 𝗖𝗛𝗢𝗥 𝗛𝗘 💋💋💦",
    "𝗔𝗕𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗞𝗨𝗧𝗧𝗘 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘 😂👻🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗔𝗜𝗦𝗘 𝗖𝗛𝗢𝗗𝗔 𝗔𝗜𝗦𝗘 𝗖𝗛𝗢𝗗𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗔 𝗕𝗘𝗗 𝗣𝗘𝗛𝗜 𝗠𝗨𝗧𝗛 𝗗𝗜𝗔 💦💦💦💦",
    "𝗧𝗘𝗥𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗔𝗔𝗚 𝗟𝗔𝗚𝗔𝗗𝗜𝗔 𝗠𝗘𝗥𝗔 𝗠𝗢𝗧𝗔 𝗟𝗨𝗡𝗗 𝗗𝗔𝗟𝗞𝗘 🔥🔥💦😆😆",
    "𝗥Æ𝗡𝗗𝗜𝗞𝗘 𝗕𝗔𝗖𝗛𝗛𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗖𝗛𝗢𝗗𝗨 𝗖𝗛𝗔𝗟 𝗡𝗜𝗞𝗔𝗟",
    "𝗞𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧𝗛 𝗔𝗕𝗕 𝗔𝗣𝗡𝗜 𝗕𝗘‌𝗛𝗘𝗡 𝗞𝗢 𝗕𝗛𝗘𝗝 😆👻🤤",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗛𝗢𝗗 𝗞𝗘 𝗨𝗦𝗠𝗘 𝗖𝗬𝗟𝗜𝗡𝗗𝗘𝗥 ⛽️ 𝗙𝗜𝗧 𝗞𝗔𝗥𝗞𝗘 𝗨𝗦𝗠𝗘𝗘 𝗗𝗔𝗟 𝗠𝗔𝗞𝗛𝗔𝗡𝗜 𝗕𝗔𝗡𝗔𝗨𝗡𝗚𝗔𝗔𝗔🤩👊🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗛𝗘𝗘𝗦𝗛𝗔 𝗗𝗔𝗟 𝗗𝗨𝗡𝗚𝗔𝗔𝗔 𝗔𝗨𝗥 𝗖𝗛𝗔𝗨𝗥𝗔𝗛𝗘 𝗣𝗘 𝗧𝗔𝗔𝗡𝗚 𝗗𝗨𝗡𝗚𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘😈😱🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗚𝗘 𝗦𝗘 500 𝗞𝗘 𝗞𝗔𝗔𝗥𝗘 𝗞𝗔𝗔𝗥𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘💰💰🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗦𝗔𝗧𝗛 𝗦𝗨𝗔𝗥 𝗞𝗔 𝗦𝗘𝗫 𝗞𝗔𝗥𝗪𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗘𝗞 𝗦𝗔𝗧𝗛 6-6 𝗕𝗔𝗖𝗛𝗘 𝗗𝗘𝗚𝗜💰🔥😱",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗔𝗣𝗣𝗟𝗘 𝗞𝗔 18𝗪 𝗪𝗔𝗟𝗔 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 🔥🤩",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝗞𝗔 𝗪𝗥𝗔𝗣 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 30𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 💥😂😎",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗢 𝗔𝗠𝗔𝗭𝗢𝗡 𝗦𝗘 𝗢𝗥𝗗𝗘𝗥 𝗞𝗔𝗥𝗨𝗡𝗚𝗔 10 𝗿𝘀 𝗠𝗘𝗜 𝗔𝗨𝗥 𝗙𝗟𝗜𝗣𝗞𝗔𝗥𝗧 𝗣𝗘 20 𝗥𝗦 𝗠𝗘𝗜 𝗕𝗘𝗖𝗛 𝗗𝗨𝗡𝗚𝗔🤮👿😈🤖",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗕𝗔𝗗𝗜 𝗕𝗛𝗨𝗡𝗗 𝗠𝗘 𝗭𝗢𝗠𝗔𝗧𝗢 𝗗𝗔𝗟 𝗞𝗘 𝗦𝗨𝗕𝗪𝗔𝗬 𝗞𝗔 𝗕𝗙𝗙 𝗩𝗘𝗚 𝗦𝗨𝗕 𝗖𝗢𝗠𝗕𝗢 [15𝗰𝗺 , 16 𝗶𝗻𝗰𝗵𝗲𝘀 ] 𝗢𝗥𝗗𝗘𝗥 𝗖𝗢𝗗 𝗞𝗥𝗩𝗔𝗨𝗡𝗚𝗔 𝗢𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗝𝗔𝗕 𝗗𝗜𝗟𝗜𝗩𝗘𝗥𝗬 𝗗𝗘𝗡𝗘 𝗔𝗬𝗘𝗚𝗜 𝗧𝗔𝗕 𝗨𝗦𝗣𝗘 𝗝𝗔𝗔𝗗𝗨 𝗞𝗥𝗨𝗡𝗚𝗔 𝗢𝗥 𝗙𝗜𝗥 9 𝗠𝗢𝗡𝗧𝗛 𝗕𝗔𝗔𝗗 𝗩𝗢 𝗘𝗞 𝗢𝗥 𝗙𝗥𝗘𝗘 𝗗𝗜𝗟𝗜𝗩𝗘𝗥𝗬 𝗗𝗘𝗚𝗜🙀👍🥳🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔𝗔𝗟𝗜🙁🤣💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜🤖🙏🤔",
    "𝗧𝗘𝗥𝗜 𝗠𝗔𝗨𝗦𝗜 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗜𝗡𝗗𝗜𝗔𝗡 𝗥𝗔𝗜𝗟𝗪𝗔𝗬 🚂💥😂",
    "𝗧𝗨 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗧𝗘𝗥𝗔 𝗞𝗛𝗔𝗡𝗗𝗔𝗡 𝗦𝗔𝗕 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗪𝗗𝗘 𝗥Æ𝗡𝗗𝗜 𝗛𝗔𝗜 𝗥Æ𝗡𝗗𝗜 🤢✅🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗜𝗢𝗡𝗜𝗖 𝗕𝗢𝗡𝗗 𝗕𝗔𝗡𝗔 𝗞𝗘 𝗩𝗜𝗥𝗚𝗜𝗡𝗜𝗧𝗬 𝗟𝗢𝗢𝗦𝗘 𝗞𝗔𝗥𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗨𝗦𝗞𝗜 📚 😎🤩",
    "𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗠𝗔‌𝗔‌ 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗕𝗔𝗔𝗣 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘𝗘 🤩🥳😳",
    "𝗧𝗨 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗗𝗢𝗡𝗢 𝗞𝗜 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗠𝗘𝗧𝗥𝗢 𝗖𝗛𝗔𝗟𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔𝗗𝗔𝗥𝗫𝗛𝗢𝗗 🚇🤩😱🥶",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣 𝗕𝗛𝗜 𝗨𝗦𝗞𝗢 𝗣𝗔𝗛𝗖𝗛𝗔𝗡𝗔𝗡𝗘 𝗦𝗘 𝗠𝗔𝗡𝗔 𝗞𝗔𝗥 𝗗𝗘𝗚𝗔😂👿🤩",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗛𝗔𝗜𝗥 𝗗𝗥𝗬𝗘𝗥 𝗖𝗛𝗔𝗟𝗔 𝗗𝗨𝗡𝗚𝗔𝗔💥🔥🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗞𝗜 𝗦𝗔𝗥𝗜 𝗥Æ𝗡𝗗𝗜𝗬𝗢𝗡 𝗞𝗔 𝗥Æ𝗡𝗗𝗜 𝗞𝗛𝗔𝗡𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔𝗔👿🤮😎",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗟𝗘𝗫𝗔 𝗗𝗔𝗟 𝗞𝗘𝗘 𝗗𝗝 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔𝗔𝗔 🎶 ⬆️🤩💥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗚𝗜𝗧𝗛𝗨𝗕 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗣𝗡𝗔 𝗕𝗢𝗧 𝗛𝗢𝗦𝗧 𝗞𝗔𝗥𝗨𝗡𝗚𝗔𝗔 🤩👊👤😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗩𝗣𝗦 𝗕𝗔𝗡𝗔 𝗞𝗘 24*7 𝗕𝗔𝗦𝗛 𝗖𝗛𝗨𝗗𝗔𝗜 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔𝗔 🤩💥🔥🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗧𝗘𝗥𝗘 𝗟𝗔𝗡𝗗 𝗞𝗢 𝗗𝗔𝗟 𝗞𝗘 𝗞𝗔𝗔𝗧 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 🔪😂🔥",
    "𝗦𝗨𝗡 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗕𝗛𝗢𝗦𝗗𝗔 𝗔𝗨𝗥 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗕𝗛𝗜 𝗕𝗛𝗢𝗦𝗗𝗔 👿😎👊",
    "𝗧𝗨𝗝𝗛𝗘 𝗗𝗘𝗞𝗛 𝗞𝗘 𝗧𝗘𝗥𝗜 𝗥Æ𝗡𝗗𝗜 𝗕𝗔𝗛𝗘𝗡 𝗣𝗘 𝗧𝗔𝗥𝗔𝗦 𝗔𝗧𝗔 𝗛𝗔𝗜 𝗠𝗨𝗝𝗛𝗘 𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗢𝗗𝗘𝗘𝗘𝗘 👿💥🤩🔥",
    "𝗦𝗨𝗡 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗝𝗬𝗔𝗗𝗔 𝗡𝗔 𝗨𝗖𝗛𝗔𝗟 𝗠𝗔‌𝗔‌ 𝗖𝗛𝗢𝗗 𝗗𝗘𝗡𝗚𝗘 𝗘𝗞 𝗠𝗜𝗡 𝗠𝗘𝗜 ✅🤣🔥🤩",
    "𝗔𝗣𝗡𝗜 𝗔𝗠𝗠𝗔 𝗦𝗘 𝗣𝗨𝗖𝗛𝗡𝗔 𝗨𝗦𝗞𝗢 𝗨𝗦 𝗞𝗔𝗔𝗟𝗜 𝗥𝗔𝗔𝗧 𝗠𝗘𝗜 𝗞𝗔𝗨𝗡 𝗖𝗛𝗢𝗗𝗡𝗘𝗘 𝗔𝗬𝗔 𝗧𝗛𝗔𝗔𝗔! 𝗧𝗘𝗥𝗘 𝗜𝗦 𝗣𝗔𝗣𝗔 𝗞𝗔 𝗡𝗔𝗔𝗠 𝗟𝗘𝗚𝗜 😂👿😳",
    "𝗧𝗢𝗛𝗔𝗥 𝗕𝗔𝗛𝗜𝗡 𝗖𝗛𝗢𝗗𝗨 𝗕𝗕𝗔𝗛𝗘𝗡 𝗞𝗘 𝗟𝗔𝗪𝗗𝗘 𝗨𝗦𝗠𝗘 𝗠𝗜𝗧𝗧𝗜 𝗗𝗔𝗟 𝗞𝗘 𝗖𝗘𝗠𝗘𝗡𝗧 𝗦𝗘 𝗕𝗛𝗔𝗥 𝗗𝗨 🏠🤢🤩💥",
    "𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗚𝗛𝗨𝗧𝗞𝗔 𝗞𝗛𝗔𝗔𝗞𝗘 𝗧𝗛𝗢𝗢𝗞 𝗗𝗨𝗡𝗚𝗔 🤣🤣",
    "𝗧𝗘𝗥𝗘 𝗕𝗘‌𝗛𝗘𝗡 𝗞 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗚𝗔",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗡𝗛𝗜 𝗛𝗔𝗜 𝗞𝗬𝗔? 9 𝗠𝗔𝗛𝗜𝗡𝗘 𝗥𝗨𝗞 𝗦𝗔𝗚𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗘𝗧𝗔 𝗛𝗨 🤣🤣🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗘𝗥𝗢𝗣𝗟𝗔𝗡𝗘𝗣𝗔𝗥𝗞 𝗞𝗔𝗥𝗞𝗘 𝗨𝗗𝗔𝗔𝗡 𝗕𝗛𝗔𝗥 𝗗𝗨𝗚𝗔 ✈️🛫",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗖𝗢𝗢𝗧𝗘𝗥 𝗗𝗔𝗔𝗟 𝗗𝗨𝗚𝗔👅",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗔𝗞𝗧𝗘 🤱 𝗚𝗔𝗟𝗜 𝗞𝗘 𝗞𝗨𝗧𝗧𝗢 🦮 𝗠𝗘 𝗕𝗔𝗔𝗧 𝗗𝗨𝗡𝗚𝗔 𝗣𝗛𝗜𝗥 🍞 𝗕𝗥𝗘𝗔𝗗 𝗞𝗜 𝗧𝗔𝗥𝗛 𝗞𝗛𝗔𝗬𝗘𝗡𝗚𝗘 𝗪𝗢 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧",
    "𝗗𝗨𝗗𝗛 𝗛𝗜𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗘 𝗨𝗣𝗥 𝗡𝗜𝗖𝗛𝗘 🆙🆒😙",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 @ll_ALPHA_BABY_lll 𝗞𝗔 𝗟𝗨𝗡𝗗 𝗗𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗙𝗜𝗥 𝗢 𝗣𝗥𝗘𝗚𝗡𝗘𝗡𝗧 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜 🍌🍌😍",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗛𝗔𝗡𝗗𝗛𝗘 𝗩𝗔𝗔𝗟𝗜 😋😛",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗖 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗦𝗔𝗔𝗥𝗜 𝗚𝗔𝗥𝗠𝗜 𝗡𝗜𝗞𝗔𝗟 𝗝𝗔𝗔𝗬𝗘𝗚𝗜",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗘𝗘𝗟𝗔𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗😚",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗞𝗢𝗟𝗞𝗔𝗧𝗔 𝗩𝗔𝗔𝗟𝗘 𝗝𝗜𝗧𝗨 𝗕𝗛𝗔𝗜𝗬𝗔 𝗞𝗔 𝗟𝗨𝗡𝗗 𝗠𝗨𝗕𝗔𝗥𝗔𝗞 🤩🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗙𝗔𝗡𝗧𝗔𝗦𝗬 𝗛𝗨 𝗟𝗔𝗪𝗗𝗘, 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗛𝗘𝗡 𝗞𝗢 𝗦𝗠𝗕𝗛𝗔𝗔𝗟 😈😈",
    "𝗧𝗘𝗥𝗔 𝗣𝗘𝗛𝗟𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗 ",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗫𝗩𝗜𝗗𝗘𝗢𝗦.𝗖𝗢𝗠 𝗖𝗛𝗔𝗟𝗔 𝗞𝗘 𝗠𝗨𝗧𝗛 𝗠𝗔‌𝗔‌𝗥𝗨𝗡𝗚𝗔 🤡😹",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗔 𝗚𝗥𝗢𝗨𝗣 𝗩𝗔𝗔𝗟𝗢𝗡 𝗦𝗔𝗔𝗧𝗛 𝗠𝗜𝗟𝗞𝗘 𝗚𝗔𝗡𝗚 𝗕𝗔𝗡𝗚 𝗞𝗥𝗨𝗡𝗚𝗔🙌🏻☠️ ",
    "𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗🤘🏻🙌🏻☠️ ",
    "𝗔𝗨𝗞𝗔𝗔𝗧 𝗠𝗘 𝗥𝗘𝗛 𝗩𝗥𝗡𝗔 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗗𝗔𝗡𝗗𝗔 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗠𝗨𝗛 𝗦𝗘 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗦𝗛𝗔𝗥𝗜𝗥 𝗕𝗛𝗜 𝗗𝗔𝗡𝗗𝗘 𝗝𝗘𝗦𝗔 𝗗𝗜𝗞𝗛𝗘𝗚𝗔 🙄🤭🤭",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗟𝗨𝗗𝗢 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗨𝗦𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘 𝗔𝗣𝗡𝗔 𝗟𝗢𝗗𝗔 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔☝🏻☝🏻😬",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗔𝗣𝗡𝗘 𝗟𝗨𝗡𝗗 𝗣𝗥 𝗜𝗧𝗡𝗔 𝗝𝗛𝗨𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗝𝗛𝗨𝗟𝗧𝗘 𝗝𝗛𝗨𝗟𝗧𝗘 𝗛𝗜 𝗕𝗔𝗖𝗛𝗔 𝗣𝗔𝗜𝗗𝗔 𝗞𝗥 𝗗𝗘𝗚𝗜👀👯 ",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗕𝗔𝗧𝗧𝗘𝗥𝗬 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗣𝗢𝗪𝗘??𝗕𝗔𝗡𝗞 𝗕??𝗡𝗔 𝗗𝗨??𝗔 🔋 🔥🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖++ 𝗦𝗧𝗥𝗜𝗡𝗚 𝗘𝗡𝗖𝗥𝗬𝗣𝗧𝗜𝗢𝗡 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗛𝗧𝗜 𝗛𝗨𝗬𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗥𝗨𝗞 𝗝𝗔𝗬𝗘𝗚𝗜𝗜𝗜𝗜😈🔥😍",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗘 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗝𝗛𝗔𝗔𝗗𝗨 𝗗𝗔𝗟 𝗞𝗘 𝗠𝗢𝗥 🦚 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 🤩🥵😱",
    "𝗧𝗘𝗥𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗛𝗢𝗨𝗟𝗗𝗘𝗥𝗜𝗡𝗚 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔𝗔 𝗛𝗜𝗟𝗔𝗧𝗘 𝗛𝗨𝗬𝗘 𝗕𝗛𝗜 𝗗𝗔𝗥𝗗 𝗛𝗢𝗚𝗔𝗔𝗔😱🤮👺",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗥𝗘𝗗𝗜 𝗣𝗘 𝗕𝗔𝗜𝗧𝗛𝗔𝗟 𝗞𝗘 𝗨𝗦𝗦𝗘 𝗨𝗦𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗕𝗜𝗟𝗪𝗔𝗨𝗡𝗚𝗔𝗔 💰 😵🤩",
    "𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 4 𝗛𝗢𝗟𝗘 𝗛𝗔𝗜 𝗨𝗡𝗠𝗘 𝗠𝗦𝗘𝗔𝗟 𝗟𝗔𝗚𝗔 𝗕𝗔𝗛𝗨𝗧 𝗕𝗔𝗛𝗘𝗧𝗜 𝗛𝗔𝗜 𝗕𝗛𝗢𝗙𝗗𝗜𝗞𝗘👊🤮🤢🤢",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗕𝗔𝗥𝗚𝗔𝗗 𝗞𝗔 𝗣𝗘𝗗 𝗨𝗚𝗔 𝗗𝗨𝗡𝗚𝗔𝗔 𝗖𝗢𝗥𝗢𝗡𝗔 𝗠𝗘𝗜 𝗦𝗔𝗕 𝗢𝗫𝗬𝗚𝗘𝗡 𝗟𝗘𝗞𝗔𝗥 𝗝𝗔𝗬𝗘𝗡𝗚𝗘🤢🤩🥳",
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗨𝗗𝗢 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗕𝗜𝗚𝗦𝗣𝗔𝗠 𝗟𝗔𝗚𝗔 𝗞𝗘 9999 𝗙𝗨𝗖𝗞 𝗟𝗔𝗚𝗔𝗔 𝗗𝗨 🤩🥳🔥",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗡 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 𝗠𝗘𝗜 𝗕𝗘𝗦𝗔𝗡 𝗞𝗘 𝗟𝗔𝗗𝗗𝗨 𝗕𝗛𝗔𝗥 𝗗𝗨𝗡𝗚𝗔🤩🥳🔥😈",
]

# ===================== GLOBALS =====================
sudo_users = {}
admin_users = {}
muted_users = {}
active_operations = {}
raid_history = {}

# ===================== FILE HANDLING =====================
def load_data():
    global sudo_users, admin_users, muted_users, raid_history
    
    try:
        if os.path.exists(SUDO_FILE):
            with open(SUDO_FILE, 'r') as f:
                sudo_users = json.load(f)
                for owner_id in OWNER_ID:
                    if str(owner_id) not in sudo_users:
                        sudo_users[str(owner_id)] = {
                            'sudo': True,
                            'username': 'Owner',
                            'first_name': 'Owner',
                            'is_owner': True
                        }
        
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r') as f:
                admin_users = json.load(f)
        
        if os.path.exists(MUTED_USERS_FILE):
            with open(MUTED_USERS_FILE, 'r') as f:
                muted_users = json.load(f)
        
        if os.path.exists(RAID_HISTORY_FILE):
            with open(RAID_HISTORY_FILE, 'r') as f:
                raid_history = json.load(f)
            
    except Exception as e:
        print(f"Load error: {e}")
        sudo_users = {}
        admin_users = {}
        muted_users = {}
        raid_history = {}

def save_data():
    try:
        with open(SUDO_FILE, 'w') as f:
            json.dump(sudo_users, f, indent=2)
        
        with open(ADMIN_FILE, 'w') as f:
            json.dump(admin_users, f, indent=2)
        
        with open(MUTED_USERS_FILE, 'w') as f:
            json.dump(muted_users, f, indent=2)
        
        with open(RAID_HISTORY_FILE, 'w') as f:
            json.dump(raid_history, f, indent=2)
            
    except Exception as e:
        print(f"Save error: {e}")

load_data()

# ===================== CHECK FUNCTIONS =====================
def is_sudo(user_id: int) -> bool:
    user_id_str = str(user_id)
    return user_id_str in sudo_users and sudo_users[user_id_str].get('sudo', False)

def is_admin(user_id: int) -> bool:
    user_id_str = str(user_id)
    return user_id_str in admin_users and admin_users[user_id_str].get('admin', False)

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_ID

def is_sudo_or_admin(user_id: int) -> bool:
    return is_sudo(user_id) or is_admin(user_id) or is_owner(user_id)

def is_muted(chat_id: int, user_id: int) -> bool:
    chat_str = str(chat_id)
    user_str = str(user_id)
    return chat_str in muted_users and user_str in muted_users[chat_str]

def mute_user(chat_id: int, user_id: int) -> bool:
    try:
        chat_str = str(chat_id)
        user_str = str(user_id)
        
        if chat_str not in muted_users:
            muted_users[chat_str] = []
        
        if user_str not in muted_users[chat_str]:
            muted_users[chat_str].append(user_str)
            save_data()
        return True
    except Exception as e:
        return False

def unmute_user(chat_id: int, user_id: int) -> bool:
    try:
        chat_str = str(chat_id)
        user_str = str(user_id)
        
        if chat_str in muted_users and user_str in muted_users[chat_str]:
            muted_users[chat_str].remove(user_str)
            save_data()
        return True
    except Exception as e:
        return False

# ===================== ULTRA FAST SEND FUNCTIONS =====================
async def send_message_ultra_fast(context, chat_id: int, message: str, reply_to: int = None, retry_count: int = 0) -> bool:
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_to_message_id=reply_to,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30,
            pool_timeout=30
        )
        await asyncio.sleep(MESSAGE_DELAY)
        return True
        
    except RetryAfter as e:
        wait_time = e.retry_after + 0.1
        await asyncio.sleep(wait_time)
        return await send_message_ultra_fast(context, chat_id, message, reply_to, retry_count + 1)
        
    except (TimedOut, NetworkError) as e:
        await asyncio.sleep(0.5)
        if retry_count < MAX_RETRIES:
            return await send_message_ultra_fast(context, chat_id, message, reply_to, retry_count + 1)
        return False
        
    except Exception as e:
        if "Flood" in str(e):
            await asyncio.sleep(1)
            return await send_message_ultra_fast(context, chat_id, message, reply_to, retry_count + 1)
        return False

async def send_message_batch(context, chat_id: int, messages: list, reply_to: int = None) -> tuple:
    tasks = []
    for msg in messages:
        tasks.append(send_message_ultra_fast(context, chat_id, msg, reply_to))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False or isinstance(r, Exception))
    return success, failed

# ===================== RAID WORKER =====================
async def raid_worker_ultra(chat_id: int, target_name: str, target_user_id: int, count: int, context, attacker_msg_id: int):
    if target_user_id in OWNER_ID:
        await send_message_ultra_fast(context, chat_id, 
            "𝗧𝗨 𝗔𝗣𝗡𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗕𝗔𝗔𝗣 𝗣𝗘 𝗥𝗔𝗜𝗗 𝗞𝗔𝗥𝗪𝗚𝗔? 𝗜𝗧𝗡𝗔 𝗕𝗔𝗗𝗔 𝗞𝗕 𝗦𝗘 𝗛𝗢 𝗚𝗔𝗬𝗔 𝗧𝗨 𝗕𝗔𝗧𝗔𝗡𝗔 𝗭𝗔𝗥𝗔")
        return
    
    sent = 0
    failed = 0
    start_time = time.time()
    last_update = time.time()
    
    chat_id_str = str(chat_id)
    active_operations[chat_id_str] = {'type': 'raid', 'stop': False, 'target': target_name}
    
    try:
        await send_message_ultra_fast(context, chat_id, 
            f"⚡⚡ 𝗨𝗟𝗧𝗥𝗔 𝗥𝗔𝗜𝗗 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 𝗢𝗡 {target_name} ⚡⚡")
        
        batch_messages = []
        
        for i in range(count):
            if active_operations.get(chat_id_str, {}).get('stop', False):
                await send_message_ultra_fast(context, chat_id,
                    f"𝗝𝗔𝗔 𝗧𝗔𝗧𝗧𝗪 𝗗𝗜𝗞𝗛𝗔 𝗗𝗜 𝗧𝗨𝗡𝗘 𝗔𝗣𝗡𝗜 𝗔𝗨𝗞𝗔𝗧 😒😒")
                break
            
            msg = random.choice(RAID_MESSAGES)
            text = f"[{target_name}](tg://user?id={target_user_id}) {msg}"
            batch_messages.append(text)
            
            if len(batch_messages) >= BATCH_SIZE:
                batch_sent, batch_failed = await send_message_batch(context, chat_id, batch_messages)
                sent += batch_sent
                failed += batch_failed
                batch_messages = []
                
                current_time = time.time()
                if current_time - last_update >= 2:
                    elapsed = current_time - start_time
                    speed = sent / elapsed if elapsed > 0 else 0
                    last_update = current_time
        
        if batch_messages:
            batch_sent, batch_failed = await send_message_batch(context, chat_id, batch_messages)
            sent += batch_sent
            failed += batch_failed
        
        await send_message_ultra_fast(context, chat_id,
            f"𝗧𝗔𝗥𝗚𝗘𝗧 [](tg://user?id={target_user_id}) 𝗞𝗢 𝗠𝗘𝗡𝗦𝗧𝗜𝗢𝗡 𝗞𝗔𝗥 𝗞𝗘 𝗕𝗢𝗟𝗪𝗚𝗔 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗 𝗗𝗜 𝗦𝗔𝗟𝗘 𝗞𝗜")
        
    except Exception as e:
        pass
        
    finally:
        if chat_id_str in active_operations:
            del active_operations[chat_id_str]

# ===================== SPAM WORKER =====================
async def spam_worker_ultra(chat_id: int, text: str, count: int, context, update_id: int):
    sent = 0
    failed = 0
    start_time = time.time()
    last_update = time.time()
    
    chat_id_str = str(chat_id)
    active_operations[chat_id_str] = {'type': 'spam', 'stop': False}
    
    try:
        await send_message_ultra_fast(context, chat_id,
            f"⚡⚡ 𝗨𝗟𝗧𝗥𝗔 𝗦𝗣𝗔𝗠 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 ⚡⚡")
        
        batch_messages = []
        
        for i in range(count):
            if active_operations.get(chat_id_str, {}).get('stop', False):
                await send_message_ultra_fast(context, chat_id,
                    f"𝗝𝗔𝗔 𝗧𝗔𝗧𝗧𝗪 𝗗𝗜𝗞𝗛𝗔 𝗗𝗜 𝗧𝗨𝗡𝗘 𝗔𝗣𝗡𝗜 𝗔𝗨𝗞𝗔𝗧 😒😒")
                break
            
            batch_messages.append(text)
            
            if len(batch_messages) >= BATCH_SIZE:
                batch_sent, batch_failed = await send_message_batch(context, chat_id, batch_messages)
                sent += batch_sent
                failed += batch_failed
                batch_messages = []
                
                current_time = time.time()
                if current_time - last_update >= 2:
                    elapsed = current_time - start_time
                    speed = sent / elapsed if elapsed > 0 else 0
                    last_update = current_time
        
        if batch_messages:
            batch_sent, batch_failed = await send_message_batch(context, chat_id, batch_messages)
            sent += batch_sent
            failed += batch_failed
        
    except Exception as e:
        pass
        
    finally:
        if chat_id_str in active_operations:
            del active_operations[chat_id_str]

# ===================== COMMAND HANDLERS =====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Add owner to sudo automatically
    if is_owner(user_id) and str(user_id) not in sudo_users:
        sudo_users[str(user_id)] = {
            'sudo': True,
            'username': update.effective_user.username or "",
            'first_name': update.effective_user.first_name or "Owner",
            'is_owner': True
        }
        save_data()
    
    keyboard = [
        [
            InlineKeyboardButton("ʜᴇʟᴘ ᴄᴍᴅ", callback_data="help_cmd"),
            InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url="https://t.me/Rinnegan_anime_group")
        ],
        [
            InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_NAGUMO_ll")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = """**🔥 ᴀꜱʜɪꜱʜ ᴘᴀᴘᴀ ʀᴀɪᴅ ʙᴏᴛ 🔥**

**⚡ ᴜʟᴛʀᴀ ꜰᴀꜱᴛ ʀᴀɪᴅɪɴɢ ʙᴏᴛ**

**👑 ᴏᴡɴᴇʀ:** ᴀꜱʜɪꜱʜ ᴘᴀᴘᴀ

**🚀 ꜰᴇᴀᴛᴜʀᴇꜱ:**
• ⚡ 1000+ ᴍꜱɢꜱ/ꜱᴇᴄ ꜱᴘᴇᴇᴅ
• 🛡 ɴᴇᴠᴇʀ ꜱᴛᴏᴘꜱ ᴏɴ ꜰʟᴏᴏᴅ
• ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ ʀᴀɪᴅ ᴄᴏᴜɴᴛ
• 🔄 ᴀᴜᴛᴏ-ʀᴇᴛʀʏ ᴏɴ ᴇʀʀᴏʀꜱ

**📌 ᴄʟɪᴄᴋ ʜᴇʟᴘ ᴄᴍᴅ ꜰᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ**"""
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "help_cmd":
        help_msg = """**ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ:**

**ʀᴀɪᴅ ᴄᴏᴍᴍᴀɴᴅꜱ:**
• `.ʀᴀɪᴅ [ᴄᴏᴜɴᴛ]` - ᴜʟᴛʀᴀ ʀᴀɪᴅ ᴏɴ ᴀ ᴜꜱᴇʀ (ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇᴍ)
  ᴇx: `.ʀᴀɪᴅ 100` ᴏʀ `.ʀᴀɪᴅ` (ᴜɴʟɪᴍɪᴛᴇᴅ)

• `.ꜱᴘᴀᴍ [ᴄᴏᴜɴᴛ] [ᴛᴇxᴛ]` - ᴜʟᴛʀᴀ ꜱᴘᴀᴍ ᴛᴇxᴛ
  ᴇx: `.ꜱᴘᴀᴍ 50 ʜᴇʟʟᴏ`

• `.ᴘɪɴɢ` - ᴄʜᴇᴄᴋ ʙᴏᴛ ꜱᴛᴀᴛᴜꜱ ᴀɴᴅ ʀᴇꜱᴘᴏɴꜱᴇ ᴛɪᴍᴇ

• `.ꜱᴛᴏᴘ` - ꜱᴛᴏᴘ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ᴏᴘᴇʀᴀᴛɪᴏɴꜱ

**ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴄᴏᴍᴍᴀɴᴅꜱ:**
• `.ᴄʜᴜᴘ` - ᴍᴜᴛᴇ ᴀ ᴜꜱᴇʀ (ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇᴍ) [𝗦𝗨𝗗𝗢/𝗔𝗗𝗠𝗜𝗡]
• `.ʙᴏʟ` - ᴜɴᴍᴜᴛᴇ ᴀ ᴜꜱᴇʀ (ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇᴍ) [𝗦𝗨𝗗𝗢/𝗔𝗗𝗠𝗜𝗡]

**ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ:**
• `/ᴀᴅᴅꜱᴜᴅᴏ [ɪᴅ]` - ᴀᴅᴅ ꜱᴜᴅᴏ ᴜꜱᴇʀ
• `/ᴅɪꜱꜱᴜᴅᴏ [ɪᴅ]` - ʀᴇᴍᴏᴠᴇ ꜱᴜᴅᴏ ᴜꜱᴇʀ
• `/ᴀᴅᴅᴀᴅᴍɪɴ [ɪᴅ]` - ᴀᴅᴅ ᴀᴅᴍɪɴ ᴜꜱᴇʀ
• `/ᴅɪꜱᴀᴅᴍɪɴ [ɪᴅ]` - ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ ᴜꜱᴇʀ

**ᴜʟᴛʀᴀ ꜰᴇᴀᴛᴜʀᴇꜱ:**
• ⚡ 1000+ ᴍꜱɢꜱ/ꜱᴇᴄ ꜱᴘᴇᴇᴅ
• 🛡 ɴᴇᴠᴇʀ ꜱᴛᴏᴘꜱ ᴏɴ ꜰʟᴏᴏᴅ
• ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ ʀᴀɪᴅ ᴄᴏᴜɴᴛ
• 🔄 ᴀᴜᴛᴏ-ʀᴇᴛʀʏ ᴏɴ ᴇʀʀᴏʀꜱ"""
        
        await query.edit_message_text(help_msg, parse_mode=ParseMode.MARKDOWN)
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_menu")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    elif query.data == "back_menu":
        keyboard = [
            [
                InlineKeyboardButton("ʜᴇʟᴘ ᴄᴍᴅ", callback_data="help_cmd"),
                InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url="https://t.me/Rinnegan_anime_group")
            ],
            [
                InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_NAGUMO_ll")
            ]
        ]
        
        welcome_msg = """**🔥 ᴀꜱʜɪꜱʜ ᴘᴀᴘᴀ ʀᴀɪᴅ ʙᴏᴛ 🔥**

**⚡ ᴜʟᴛʀᴀ ꜰᴀꜱᴛ ʀᴀɪᴅɪɴɢ ʙᴏᴛ**

**👑 ᴏᴡɴᴇʀ:** ᴀꜱʜɪꜱʜ ᴘᴀᴘᴀ

**🚀 ꜰᴇᴀᴛᴜʀᴇꜱ:**
• ⚡ 1000+ ᴍꜱɢꜱ/ꜱᴇᴄ ꜱᴘᴇᴇᴅ
• 🛡 ɴᴇᴠᴇʀ ꜱᴛᴏᴘꜱ ᴏɴ ꜰʟᴏᴏᴅ
• ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ ʀᴀɪᴅ ᴄᴏᴜɴᴛ
• 🔄 ᴀᴜᴛᴏ-ʀᴇᴛʀʏ ᴏɴ ᴇʀʀᴏʀꜱ

**📌 ᴄʟɪᴄᴋ ʜᴇʟᴘ ᴄᴍᴅ ꜰᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ**"""
        
        await query.edit_message_text(welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_sudo_or_admin(user_id):
        await update.message.reply_text("𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗙𝗜𝗥 𝗪𝗢 𝗦𝗨𝗗𝗢 𝗗𝗘𝗚𝗔 𝗧𝗔𝗧𝗧𝗘")
        return
    
    start_time = time.time()
    await update.message.reply_text("𝗕𝗢𝗟 𝗕𝗘𝗧𝗨 𝗞𝗜𝗦 𝗞𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗𝗡𝗜 𝗛 𝗧𝗨 𝗕𝗔𝗦𝗦 𝗡𝗔𝗔𝗠 𝗕𝗔𝗧𝗔")
    end_time = time.time()
    ping = round((end_time - start_time) * 1000, 2)
    
    await update.message.reply_text(f"ᴘɪɴɢ: `{ping}ᴍꜱ`", parse_mode=ParseMode.MARKDOWN)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_str = str(chat_id)
    
    if not is_sudo_or_admin(user_id):
        await update.message.reply_text("𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗙𝗜𝗥 𝗪𝗢 𝗦𝗨𝗗𝗢 𝗗𝗘𝗚𝗔 𝗧𝗔𝗧𝗧𝗘")
        return
    
    if chat_str in active_operations:
        active_operations[chat_str]['stop'] = True
        await update.message.reply_text("𝗝𝗔𝗔 𝗧𝗔𝗧𝗧𝗪 𝗗𝗜𝗞𝗛𝗔 𝗗𝗜 𝗧𝗨𝗡𝗘 𝗔𝗣𝗡𝗜 𝗔𝗨𝗞𝗔𝗧 😒😒")
    else:
        await update.message.reply_text("✅ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴏᴘᴇʀᴀᴛɪᴏɴꜱ")

async def addsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("📝 ᴜꜱᴀɢᴇ: /addsudo [ᴜꜱᴇʀ_ɪᴅ]")
        return
    
    try:
        target_id = int(context.args[0])
        
        if str(target_id) in sudo_users:
            await update.message.reply_text("⚠️ ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ꜱᴜᴅᴏ!")
            return
        
        try:
            user = await context.bot.get_chat(target_id)
            username = user.username or ""
            first_name = user.first_name or f"User_{target_id}"
        except:
            username = ""
            first_name = f"User_{target_id}"
        
        sudo_users[str(target_id)] = {
            'sudo': True,
            'username': username,
            'first_name': first_name,
            'is_owner': False,
            'added_by': user_id,
            'added_date': datetime.now().isoformat()
        }
        save_data()
        
        await update.message.reply_text(
            f"𝗔𝗔𝗝 𝗦𝗘 𝗧𝗨 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗔 𝗕𝗘𝗧𝗨 𝗝𝗔𝗔 𝗠𝗢𝗝 𝗠𝗔𝗔𝗥\n\n"
            f"✅ {first_name} ɪꜱ ɴᴏᴡ ꜱᴜᴅᴏ!"
        )
        
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="𝗔𝗔𝗝 𝗦𝗘 𝗧𝗨 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗔 𝗕𝗘𝗧𝗨 𝗝𝗔𝗔 𝗠𝗢𝗝 𝗠𝗔𝗔𝗥\n\n✅ ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ꜱᴜᴅᴏ!"
            )
        except:
            pass
            
    except ValueError:
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!")

async def dissudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("📝 ᴜꜱᴀɢᴇ: /dissudo [ᴜꜱᴇʀ_ɪᴅ]")
        return
    
    try:
        target_id = int(context.args[0])
        
        if target_id in OWNER_ID:
            await update.message.reply_text("❌ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ ꜱᴜᴅᴏ!")
            return
        
        if str(target_id) not in sudo_users:
            await update.message.reply_text("❌ ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ɴᴏᴛ ꜱᴜᴅᴏ!")
            return
        
        user_info = sudo_users[str(target_id)]
        first_name = user_info.get('first_name', f'User_{target_id}')
        
        del sudo_users[str(target_id)]
        save_data()
        
        await update.message.reply_text(
            f"𝗝𝗔𝗔 𝗧𝗔𝗧𝗧𝗪 𝗧𝗨𝗡𝗘 𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗔𝗦𝗛𝗜𝗦𝗛 𝗦𝗪 𝗚𝗔𝗗𝗗𝗔𝗥𝗜 𝗞𝗜 𝗔𝗕 𝗔𝗦𝗛𝗜𝗦𝗛 𝗕𝗔𝗔𝗣 𝗧𝗨𝗝𝗛𝗘 𝗔𝗣𝗡𝗢 𝗝𝗔𝗬𝗘𝗗𝗔𝗧 𝗦𝗘 𝗟𝗔𝗔𝗧 𝗞𝗜 𝗠𝗔𝗔𝗥 𝗞𝗘 𝗡𝗜𝗞𝗔𝗟𝗧𝗘 𝗛\n\n"
            f"❌ {first_name} ʟᴏꜱᴛ ꜱᴜᴅᴏ ᴀᴄᴄᴇꜱꜱ!"
        )
        
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="𝗝𝗔𝗔 𝗧𝗔𝗧𝗧𝗪 𝗧𝗨𝗡𝗘 𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗔𝗦𝗛𝗜𝗦𝗛 𝗦𝗪 𝗚𝗔𝗗𝗗𝗔𝗥𝗜 𝗞𝗜 𝗔𝗕 𝗔𝗦𝗛𝗜𝗦𝗛 𝗕𝗔𝗔𝗣 𝗧𝗨𝗝𝗛𝗘 𝗔𝗣𝗡𝗢 𝗝𝗔𝗬𝗘𝗗𝗔𝗧 𝗦𝗘 𝗟𝗔𝗔𝗧 𝗞𝗜 𝗠𝗔𝗔𝗥 𝗞𝗘 𝗡𝗜𝗞𝗔𝗟𝗧𝗘 𝗛\n\n❌ ʏᴏᴜ ʜᴀᴠᴇ ʟᴏꜱᴛ ꜱᴜᴅᴏ ᴀᴄᴄᴇꜱꜱ!"
            )
        except:
            pass
            
    except ValueError:
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!")

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("📝 ᴜꜱᴀɢᴇ: /addadmin [ᴜꜱᴇʀ_ɪᴅ]")
        return
    
    try:
        target_id = int(context.args[0])
        
        if str(target_id) in admin_users:
            await update.message.reply_text("⚠️ ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ!")
            return
        
        if str(target_id) in sudo_users:
            await update.message.reply_text("⚠️ ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ꜱᴜᴅᴏ!")
            return
        
        try:
            user = await context.bot.get_chat(target_id)
            username = user.username or ""
            first_name = user.first_name or f"User_{target_id}"
        except:
            username = ""
            first_name = f"User_{target_id}"
        
        admin_users[str(target_id)] = {
            'admin': True,
            'username': username,
            'first_name': first_name,
            'added_by': user_id,
            'added_date': datetime.now().isoformat()
        }
        save_data()
        
        await update.message.reply_text(
            f"𝗝𝗔𝗔 𝗕𝗘𝗧𝗨 𝗧𝗨 𝗠𝗢𝗝 𝗠𝗔𝗔𝗥 𝗧𝗨 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗔 𝗙𝗔𝗩𝗢𝗨𝗥𝗜𝗧𝗘 𝗖𝗛𝗜𝗟𝗗 𝗛\n\n"
            f"✅ {first_name} ɪꜱ ɴᴏᴡ ᴀᴅᴍɪɴ!"
        )
        
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="𝗝𝗔𝗔 𝗕𝗘𝗧𝗨 𝗧𝗨 𝗠𝗢𝗝 𝗠𝗔𝗔𝗥 𝗧𝗨 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗔 𝗙𝗔𝗩𝗢𝗨𝗥𝗜𝗧𝗘 𝗖𝗛𝗜𝗟𝗗 𝗛\n\n✅ ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴀᴅᴍɪɴ!"
            )
        except:
            pass
            
    except ValueError:
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!")

async def disadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("📝 ᴜꜱᴀɢᴇ: /disadmin [ᴜꜱᴇʀ_ɪᴅ]")
        return
    
    try:
        target_id = int(context.args[0])
        
        if target_id in OWNER_ID:
            await update.message.reply_text("❌ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ!")
            return
        
        if str(target_id) not in admin_users:
            await update.message.reply_text("❌ ᴛʜɪꜱ ᴜꜱᴇʀ ɪꜱ ɴᴏᴛ ᴀᴅᴍɪɴ!")
            return
        
        user_info = admin_users[str(target_id)]
        first_name = user_info.get('first_name', f'User_{target_id}')
        
        del admin_users[str(target_id)]
        save_data()
        
        await update.message.reply_text(
            f"❌ {first_name} ʟᴏꜱᴛ ᴀᴅᴍɪɴ ᴀᴄᴄᴇꜱꜱ!"
        )
        
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="❌ ʏᴏᴜ ʜᴀᴠᴇ ʟᴏꜱᴛ ᴀᴅᴍɪɴ ᴀᴄᴄᴇꜱꜱ!"
            )
        except:
            pass
            
    except ValueError:
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!")

async def chup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_sudo_or_admin(user_id):
        await update.message.reply_text("𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗙𝗜𝗥 𝗪𝗢 𝗦𝗨𝗗𝗢 𝗗𝗘𝗚𝗔 𝗧𝗔𝗧𝗧𝗘")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("📌 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴍᴜᴛᴇ ᴛʜᴇᴍ")
        return
    
    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    
    if target_user.id in OWNER_ID:
        await update.message.reply_text("❌ ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ᴏᴡɴᴇʀ!")
        return
    
    if target_user.id == context.bot.id:
        await update.message.reply_text("❌ ᴍᴀɪɴ ᴋʜᴜᴅ ᴋᴏ ᴍᴜᴛᴇ ɴᴀʜɪ ᴋʀ ꜱᴀᴋᴛᴀ!")
        return
    
    if is_sudo_or_admin(target_user.id):
        await update.message.reply_text("❌ ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ꜱᴜᴅᴏ/ᴀᴅᴍɪɴ!")
        return
    
    if mute_user(chat_id, target_user.id):
        try:
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=target_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False
                    )
                )
        except Exception as e:
            pass
        
        await update.message.reply_text(f"🔇 ᴍᴜᴛᴇᴅ {target_user.first_name} - ᴀʙ ᴄʜᴜᴘ ʜᴏᴊᴀ")
    else:
        await update.message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴍᴜᴛᴇ ᴜꜱᴇʀ")

async def bol_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_sudo_or_admin(user_id):
        await update.message.reply_text("𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗙𝗜𝗥 𝗪𝗢 𝗦𝗨𝗗𝗢 𝗗𝗘𝗚𝗔 𝗧𝗔𝗧𝗧𝗘")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("📌 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴜɴᴍᴜᴛᴇ ᴛʜᴇᴍ")
        return
    
    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    
    if unmute_user(chat_id, target_user.id):
        try:
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=target_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
        except Exception as e:
            pass
        
        await update.message.reply_text(f"🔊 ᴜɴᴍᴜᴛᴇᴅ {target_user.first_name} - ᴀʙ ʙᴏʟ ꜱᴀᴋᴛᴀ ʜᴀɪ")
    else:
        await update.message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜɴᴍᴜᴛᴇ ᴜꜱᴇʀ")

# ===================== MAIN MESSAGE HANDLER =====================
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    
    # Handle .ping
    if text.lower() == '.ping':
        await ping_command(update, context)
        return
    
    # Handle .stop
    if text.lower() == '.stop':
        await stop_command(update, context)
        return
    
    # Handle .chup
    if text.lower() == '.chup':
        await chup_command(update, context)
        return
    
    # Handle .bol
    if text.lower() == '.bol':
        await bol_command(update, context)
        return
    
    # Split the message into parts
    parts = text.lower().split()
    if not parts:
        return
    
    command = parts[0].lower()
    if command.startswith('.'):
        command = command[1:]
    
    # ========== RAID COMMAND ==========
    if command == 'raid':
        if not is_sudo_or_admin(user_id):
            await update.message.reply_text("𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗙𝗜𝗥 𝗪𝗢 𝗦𝗨𝗗𝗢 𝗗𝗘𝗚𝗔 𝗧𝗔𝗧𝗧𝗘")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("📌 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ꜰɪʀꜱᴛ!")
            return
        
        count = 999999
        if len(parts) >= 2:
            try:
                count = int(parts[1])
                if count <= 0:
                    count = 999999
            except ValueError:
                count = 999999
        
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
        target_name = target_user.first_name or "User"
        
        if target_id in OWNER_ID:
            await update.message.reply_text("𝗧𝗨 𝗔𝗣𝗡𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗕𝗔𝗔𝗣 𝗣𝗘 𝗥𝗔𝗜𝗗 𝗞𝗔𝗥𝗪𝗚𝗔? 𝗜𝗧𝗡𝗔 𝗕𝗔𝗗𝗔 𝗞𝗕 𝗦𝗘 𝗛𝗢 𝗚𝗔𝗬𝗔 𝗧𝗨 𝗕𝗔𝗧𝗔𝗡𝗔 𝗭𝗔𝗥𝗔")
            return
        
        await update.message.reply_text(f"⚡⚡ 𝗨𝗟𝗧𝗥𝗔 𝗥𝗔𝗜𝗗 𝗦𝗧𝗔𝗥𝗧𝗜𝗡𝗚 𝗢𝗡 {target_name} ⚡⚡")
        
        asyncio.create_task(
            raid_worker_ultra(
                chat_id,
                target_name,
                target_id,
                count,
                context,
                update.message.message_id
            )
        )
        return
    
    # ========== SPAM COMMAND ==========
    elif command == 'spam':
        if not is_sudo_or_admin(user_id):
            await update.message.reply_text("𝗣𝗘𝗟𝗘 𝗔𝗦𝗛𝗜𝗦𝗛 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗢𝗟 𝗞𝗘 𝗔𝗔 𝗙𝗜𝗥 𝗪𝗢 𝗦𝗨𝗗𝗢 𝗗𝗘𝗚𝗔 𝗧𝗔𝗧𝗧𝗘")
            return
        
        if len(parts) < 3:
            await update.message.reply_text("ᴜꜱᴀɢᴇ: .spam 50 ᴛᴇxᴛ")
            return
        
        try:
            count = int(parts[1])
            if count <= 0:
                count = 999999
        except ValueError:
            count = 999999
        
        original_parts = text.split()
        spam_text = " ".join(original_parts[2:])
        
        await update.message.reply_text(f"⚡⚡ 𝗨𝗟𝗧𝗥𝗔 𝗦𝗣𝗔𝗠 𝗦𝗧𝗔𝗥𝗧𝗜𝗡𝗚 ⚡⚡")
        
        asyncio.create_task(
            spam_worker_ultra(
                chat_id,
                spam_text,
                count,
                context,
                update.message.message_id
            )
        )
        return

# ===================== ERROR HANDLER =====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print(f"Error: {context.error}")
    except:
        pass

# ===================== MAIN FUNCTION =====================
def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         ULTIMATE ULTRA RAID BOT - 20X SPEED              ║
    ║         NEVER STOPS - INFINITE FLOOD PROTECTION          ║
    ║         1000+ MESSAGES PER SECOND                        ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    application = Application.builder()\
        .token(BOT_TOKEN)\
        .connect_timeout(30)\
        .read_timeout(30)\
        .write_timeout(30)\
        .pool_timeout(30)\
        .build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("addsudo", addsudo_command))
    application.add_handler(CommandHandler("dissudo", dissudo_command))
    application.add_handler(CommandHandler("addadmin", addadmin_command))
    application.add_handler(CommandHandler("disadmin", disadmin_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Main message handler
    application.add_handler(MessageHandler(filters.TEXT, handle_messages))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    print(f"\n⚡⚡ ULTRA BOT ACTIVATED ⚡⚡")
    print(f"👑 Owner IDs: {OWNER_ID}")
    print(f"👥 Sudo Users: {len(sudo_users)}")
    print(f"👥 Admin Users: {len(admin_users)}")
    print(f"\n✅ ULTRA FEATURES ENABLED:")
    print(f"  • Speed: 1000+ msgs/sec")
    print(f"  • Flood Protection: INFINITE")
    print(f"  • Raid Count: UNLIMITED")
    
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            poll_interval=0.0,
            timeout=30
        )
    except KeyboardInterrupt:
        print("\n👋 ULTRA BOT stopped!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        time.sleep(5)
        main()

if __name__ == '__main__':
    main()
