import re
import logging
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageTextIsEmpty
from load import dp, bot
from keyboard import Button
from database import Database
from config import *

btn = Button()
db = Database()

class FormaAdmin(StatesGroup):
    s1 = State()  # type of message?
    s2 = State()  # message to send
    s3 = State()  # type of users

def sanitize_markdown(text):
    # Escape markdown special characters for MarkdownV2
    escape_chars = r'()[]{}_*~`>#+-=|.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def ForwardMessage(file_id: str, chat_ids: list, file_type: str, caption: str = None, chunk_size: int = 30, delay: float = 1.5):
    successful = 0
    failed = 0

    for i in range(0, len(chat_ids), chunk_size):
        chunk = chat_ids[i:i + chunk_size]
        tasks = []
        for chat_id in chunk:
            tasks.append(send_message(chat_id, file_id, file_type, caption))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            elif result is False:
                failed += 1
            else:
                successful += 1
        await asyncio.sleep(delay)

    return successful, failed

async def send_message(chat_id, file_id, file_type, caption):
    try:
        if caption:
            sanitized_caption = sanitize_markdown(caption)
        else:
            sanitized_caption = caption

        if file_type == 'photo':
            await bot.send_photo(chat_id, file_id, caption=sanitized_caption, protect_content=True, parse_mode="MarkdownV2", reply_markup=btn.buy_cinema())
        elif file_type == 'video':
            await bot.send_video(chat_id, file_id, caption=sanitized_caption, protect_content=True, parse_mode="MarkdownV2", reply_markup=btn.buy_cinema())
        elif file_type == 'document':
            await bot.send_document(chat_id, file_id, caption=sanitized_caption, protect_content=True, parse_mode="MarkdownV2", reply_markup=btn.buy_cinema())
        elif file_type == 'video_note':
            await bot.send_video_note(chat_id, file_id, protect_content=True, reply_markup=btn.buy_cinema())
        elif file_type == 'voice':
            await bot.send_voice(chat_id, file_id, caption=sanitized_caption, protect_content=True, parse_mode="MarkdownV2")
        elif file_type == 'text':
            if sanitized_caption:  # Ensure the text is not empty
                await bot.send_message(chat_id, sanitized_caption, protect_content=True, parse_mode="MarkdownV2")
            else:
                logging.error(f"Message text is empty for chat {chat_id}")
                return False
        return True
    except MessageTextIsEmpty:
        # If the caption is empty or incorrectly formatted, send without parse_mode
        try:
            if file_type == 'photo':
                await bot.send_photo(chat_id, file_id, protect_content=True, caption=caption, reply_markup=btn.buy_cinema())
            elif file_type == 'video':
                await bot.send_video(chat_id, file_id, protect_content=True, caption=caption, parse_mode="Markdown", reply_markup=btn.buy_cinema())
            elif file_type == 'document':
                await bot.send_document(chat_id, file_id,  protect_content=True, caption=caption, reply_markup=btn.buy_cinema())
            elif file_type == 'video_note':
                await bot.send_video_note(chat_id, file_id, protect_content=True, reply_markup=btn.buy_cinema())
            elif file_type == 'voice':
                await bot.send_voice(chat_id, file_id, caption=caption)
            elif file_type == 'text':
                if caption:  # Ensure the text is not empty
                    await bot.send_message(chat_id, caption, protect_content=True)
                else:
                    logging.error(f"Message text is empty for chat {chat_id}")
                    return False
            return True
        except Exception as e:
            logging.error(f"Failed to forward message to chat {chat_id}: {str(e)}")
            return False
    except Exception as e:
        logging.error(f"Failed to forward message to chat {chat_id}: {str(e)}")
        return False

@dp.message_handler(state='*', commands='🔕 Бас тарту')
@dp.message_handler(Text(equals='🔕 Бас тарту', ignore_case=True), state='*')
async def cancell_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Бас тарту!')
    await state.finish()
    if message.from_user.id == admin or message.from_user.id == admin2:
        await message.reply('Сіз тапсырыстан бас тарттыңыз.', reply_markup=btn.admin())
    
    await message.reply('Сіз тапсырыстан бас тарттыңыз.', reply_markup=btn.menu_not_paid())

@dp.message_handler(state=FormaAdmin.s1)
async def handler(message: types.Message, state: FSMContext):
    await FormaAdmin.next()
    async with state.proxy() as data:
        data['msg'] = message.text

    await bot.send_message(
        message.from_user.id,
        text="Жіберетін материялды жазыңыз",
        reply_markup=btn.cancel()
    )

@dp.message_handler(state=FormaAdmin.s2, content_types=types.ContentTypes.ANY)
async def handler(message: types.Message, state: FSMContext):
    file_id = None
    caption = message.caption if message.caption else ''
    logging.info(f"Received message with caption: {caption}")

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    elif message.video:
        file_id = message.video.file_id
        file_type = 'video'
    elif message.document:
        file_id = message.document.file_id
        file_type = 'document'
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = 'video_note'
    elif message.voice:
        file_id = message.voice.file_id
        file_type = 'voice'
    elif message.text:
        file_id = message.text
        file_type = 'text'
    else:
        await message.reply("Unsupported file type")
        logging.error(f"Unsupported file type for message: {message}")
        return

    async with state.proxy() as data:
        data['file_id'] = file_id
        data['file_type'] = file_type
        data['caption'] = caption
        logging.info(f"Stored data in state: file_id={file_id}, file_type={file_type}, caption={caption}")

    await FormaAdmin.next()

    await bot.send_message(
        message.from_user.id,
        text="Қандай типтегі қолданушыларға жазамыз?",
        reply_markup=btn.typeUsers()
    )

@dp.message_handler(state=FormaAdmin.s3)
async def send_to_users(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file_id = data.get('file_id')
        file_type = data.get('file_type')
        caption = data.get('caption', '')
        data['typeOfUsers'] = message.text

        logging.info(f"Sending to users: file_id={file_id}, file_type={file_type}, caption={caption}, typeOfUsers={data['typeOfUsers']}")

    if data['typeOfUsers'] == "📑 Жалпы қолданушыларға":
        user_ids = db.gatherJustID()
        successful, failed = await ForwardMessage(file_id, user_ids, file_type, caption)
    elif data['typeOfUsers'] == "💳 Төлем 🟢 жасаған 📊 қолданушаларға":
        user_ids = db.gatherPaid()
        successful, failed = await ForwardMessage(file_id, user_ids, file_type, caption)

    # Send summary message to admins
    await bot.send_message(admin, text=f"Сәтті жіберілді: {successful} қолданушыға\nҚателік болды: {failed} қолданушыға", reply_markup=btn.admin())
    await bot.send_message(admin2, text=f"Сәтті жіберілді: {successful} қолданушыға\nҚателік болды: {failed} қолданушыға", reply_markup=btn.admin())
    await state.finish()
