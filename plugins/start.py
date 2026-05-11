#(©)CodeXBotz

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL_2
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    text = message.text
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        track_msgs = []
        for msg in messages:
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                try:
                    copied_msg_for_deletion = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    if copied_msg_for_deletion:
                        track_msgs.append(copied_msg_for_deletion)
                except Exception as e:
                    print(f"Error copying message: {e}")
            else:
                try:
                    await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                except:
                    pass

        if track_msgs:
            delete_data = await client.send_message(chat_id=message.from_user.id, text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME))
            asyncio.create_task(delete_file(track_msgs, client, delete_data))
        return
    else:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("😊 About Me", callback_data = "about"), InlineKeyboardButton("🔒 Close", callback_data = "close")]])
        if START_PIC:
            await message.reply_photo(photo=START_PIC, caption=START_MSG.format(first=message.from_user.first_name, last=message.from_user.last_name, username=None if not message.from_user.username else '@' + message.from_user.username, mention=message.from_user.mention, id=message.from_user.id), reply_markup=reply_markup, quote=True)
        else:
            await message.reply_text(text=START_MSG.format(first=message.from_user.first_name, last=message.from_user.last_name, username=None if not message.from_user.username else '@' + message.from_user.username, mention=message.from_user.mention, id=message.from_user.id), reply_markup=reply_markup, disable_web_page_preview=True, quote=True)
        return

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    invite_1 = await client.create_chat_invite_link(chat_id=FORCE_SUB_CHANNEL)
    invite_3 = await client.create_chat_invite_link(chat_id=FORCE_SUB_CHANNEL_2)

    buttons = [
        [InlineKeyboardButton("Join Channel 1 ✅", url=invite_1.invite_link)],
        [InlineKeyboardButton("Join Channel 2 (Main) 🚀", url="https://t.me/+bGRwATxBAHEzOTI9")], 
        [InlineKeyboardButton("Join Channel 3 ✅", url=invite_3.invite_link)]
    ]

    try:
        buttons.append([InlineKeyboardButton(text = '🔄 Try Again', url = f"https://t.me/{client.username}?start={message.command[1]}")])
    except:
        pass

    await message.reply(
        text = "⚠️ **අවධානයට:** මෙම වීඩියෝව ලබා ගැනීමට පහත චැනල් **3ටම** අනිවාර්යයෙන්ම සම්බන්ධ වන්න.\n\nඑකක් හෝ මඟහැරුණහොත් වීඩියෝව ලැබෙන්නේ නැත!",
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    users = await full_userbase()
    await message.reply_text(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
            except:
                pass
        await message.reply("Broadcast Completed!")
