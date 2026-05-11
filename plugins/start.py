import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL_2, START_MSG, START_PIC
from helper_func import subscribed, decode, get_messages
from database.database import add_user, present_user

# 1. චැනල් වලට ජොයින් වී නැති විට පෙන්වන මැසේජ් එක (බටන් 3 සහිතව)
@Client.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # ජොයින් වී ඇත්දැයි පරීක්ෂා කිරීම (බොට් ඇඩ්මින් චැනල් 2 පමණක් චෙක් කරයි)
    if not await subscribed(client, message):
        buttons = [
            [
                InlineKeyboardButton("Join Channel 1 ✅", url="https://t.me/+QoKuBOJd_CZmMjU1")
            ],
            [
                # මෙය බොට් චෙක් නොකරන, වෙනත් අයෙකුගේ චැනල් එකයි
                InlineKeyboardButton("Join Channel 2 (Main) 🚀", url="https://t.me/+bGRwATxBAHEzOTI9")
            ],
            [
                InlineKeyboardButton("Join Channel 3 ✅", url="https://t.me/+z3y1IwnZYJhjYWU1")
            ]
        ]

        try:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text = '🔄 Try Again',
                        url = f"https://t.me/{client.username}?start={message.command[1]}"
                    )
                ]
            )
        except IndexError:
            pass

        return await message.reply(
            text = "⚠️ **අවධානයට:** මෙම වීඩියෝව ලබා ගැනීමට පහත චැනල් **3ටම** අනිවාර්යයෙන්ම සම්බන්ධ වන්න.\n\nඑකක් හෝ මඟහැරුණහොත් වීඩියෝව ලැබෙන්නේ නැත!",
            reply_markup = InlineKeyboardMarkup(buttons)
        )
    
    # 2. චැනල් වලට ජොයින් වී ඇත්නම් වීඩියෝව ලබා දීම හෝ Start පණිවිඩය පෙන්වීම
    # (මෙහිදී බොට් චෙක් කරන්නේ Force Sub 1 සහ 2 පමණි)
    
    # ඔබේ පරණ start_command එකේ කේතය මෙතැනට එයි...
    # (පහතින් ඇති කේතය දිගටම ඇතුළත් කරන්න)
