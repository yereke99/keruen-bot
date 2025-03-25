#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from load import bot, dp
from aiogram import types
from FormaAdmin import *
from keyboard import*
from database import*
from config import*
from Forma import*
import asyncio
from traits import*
import time
from FormaAdmin import*
from aiogram.types import InputMediaPhoto, InputMediaVideo
from tests import*

generator = Generator()
btn = Button()
db = Database()

################
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def pdf_received_handler(message: types.Message, state: FSMContext):
    # Проверяем, что отправленный файл — это PDF
    if message.document.mime_type == 'application/pdf':
        document = message.document

        # Generate a unique filename
        user_id = message.from_user.id
        timestamp = int(time.time())
        random_int = Generator.generate_random_int()
        file_name = f"{user_id}_{timestamp}_{random_int}.pdf"
        file_path = os.path.join('./pdf/', file_name)

        # Download the PDF file
        file_info = await bot.get_file(document.file_id)
        await bot.download_file(file_info.file_path, file_path)

        # Process the PDF file
        pdf_reader = PDFReader(file_path)
        pdf_reader.open_pdf()
        result = pdf_reader.extract_specific_info()
        pdf_reader.close_pdf()

        
        print(result)
        print(len(result))

        async with state.proxy() as data:
            data['data'] = message.text
            data['pdf_result'] = result
            data['fileName'] = file_name


            data['count'] = int(convert_currency_to_int(data['pdf_result'][1])/500)
            sum = 500 * data['count']
            data['sum'] = sum
            print(data['sum'])

        
        print(f"Expected sum: {data['sum']}, Actual sum: {convert_currency_to_int(data['pdf_result'][1])}")

        if convert_currency_to_int(data['pdf_result'][1]) != data['sum']: 
            await bot.send_message(
                message.from_user.id,
                text="*Төленетін сумма қате!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu()
            ) 
            return
        
        if data['pdf_result'][3] == "Сатушының ЖСН/БСН 811212302853" or data['pdf_result'][3] == "ИИН/БИН продавца 811212302853":
            print(db.CheckLoto(data['pdf_result'][2]))
            if db.CheckLoto(data['pdf_result'][2]) == True:
                await bot.send_message(
                        message.from_user.id,
                        text="*ЧЕК ТӨЛЕНІП ҚОЙЫЛҒАН!\nҚайталап көріңіз*",
                        parse_mode="Markdown",
                        reply_markup=btn.menu()
                )   
                return

            await Forma.s3.set()
            await bot.send_message(
                message.from_user.id,
                text="*Аты жөніңізді жазыңыз*",
                parse_mode="Markdown",
            )
        else:
            await bot.send_message(
                message.from_user.id,
                text="*Дұрыс емес счетқа төледіңіз!\nҚайталап көріңіз*",
                parse_mode="Markdown",
                reply_markup=btn.menu_not_paid()
            )  
    else:
        # Если отправлен не PDF-файл, можно уведомить пользователя
        await message.reply("Тек, PDF файл жіберу керек!")



@dp.callback_query_handler(lambda c: c.data == "buy_cinema")
async def process_buy_cinema(callback_query: types.CallbackQuery):
    # Удаляем предыдущее сообщение
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

    await bot.answer_callback_query(callback_query.id)
    
    await Forma.s1.set()

    await bot.send_message(
        callback_query.from_user.id,
        text="*Қанша шұлық алғыңыз келеді? Шұлық саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
        parse_mode="Markdown",
        reply_markup=btn.digits_and_cancel()
    ) 
  

@dp.message_handler(commands=['get_last_message'])
async def get_last_message_handler(message: types.Message):
    try:
        # Use the current chat ID from the message
        chat_id = message.chat.id

        # Fetch the chat details
        chat_info = await bot.get_chat(chat_id)

        # Fetch the most recent messages using bot.get_updates workaround
        updates = await bot.get_updates(limit=1000)

        # Extract message from the update
        if updates and updates[0].message:
            last_msg = updates[0].message
            last_message_id = last_msg.message_id
            last_message_text = last_msg.text or "<No text content>"

            # Send the message ID and text to the user
            await message.answer(
                f"Chat Title: {chat_info.title}\n"
                f"Message ID: {last_message_id}\n"
                f"Text: {last_message_text}"
            )
        else:
            await message.answer("No recent messages found in this chat.")

    except Exception as e:
        await message.answer(f"An error occurred: {e}")

@dp.message_handler(commands=['admin'])
async def handler(message: types.Message):
    print(message.from_user.id)

    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        await bot.send_message(
        message.from_user.id,
        text="😊 *Сәлеметсіз бе %s !\nСіздің статусыңыз 👤 Админ(-ка-)*"%message.from_user.first_name,
        parse_mode="Markdown",
        reply_markup=btn.admin()
    )
 

@dp.message_handler(Text(equals="📈 Статистика"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id in {admin, admin2, admin3}:
        # Получаем статистику из базы данных
        tik_tok_count = db.get_tiktok_count()
        instagram_count = db.get_instagram_count()
        
        # Форматируем сообщение
        stats_message = (
            f"📊 <b>Статистика:</b>\n\n"
            f"🔹 TikTok: {tik_tok_count} заходов\n"
            f"🔹 Instagram: {instagram_count} заходов\n"
        )
        
        # Отправляем сообщение
        await message.reply(stats_message, parse_mode="HTML")
    
        
@dp.message_handler(commands=['start', 'go'])
async def start_handler(message: types.Message):
    
    args = message.get_args()

    if args == "TikTok":
        # Логика для TikTok
        db.tiktok_counter()
        await Forma.s1.set()
        await bot.send_message(
            message.from_user.id,
            text="*Қанша шұлық алғыңыз келеді? Шұлық саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        ) 
        return
    elif args == "Instagram":
        # Логика для Instagram
        db.instagram_counter()
        await Forma.s1.set()
        await bot.send_message(
            message.from_user.id,
            text="*Қанша шұлық алғыңыз келеді? Шұлық саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        )
        return 

    
    print(message.from_user.id)
      
    from datetime import datetime
    fileId = "BAACAgIAAxkBAAIBRGfikw74saJw7kYZS6QasxskT4XoAAJ7aQAC9EoRS4kQw0L6RQFWNgQ"

    user_id = message.from_user.id
    user_name = f"@{message.from_user.username}"
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db.JustInsert(user_id, user_name, time_now)  
    
    if db.CheckUserPaid(message.from_user.id) == True:
        await bot.send_video(
            message.from_user.id,
            fileId,
            caption="""*KN KERUEN экологиялық таза, сапалы шұлықтар брендтіне қош келдіңіз!

Біздың шұлықтар - 100 % табиғи бамбуктан жасалған, жоғары сапа мен жайлылықты ұсынады!
100% Евро стандартқа сай шұлықтар! 🌱🧦

Акция! Акция!
Біздің шұлықтарды сатып ала отырып!
Керемет сыйлықтарға ие болыңыз!
Сыйлықтар тізімі!
. Авто көлік
. Пәтер
. пылесос 
. Ас үй комбайны!
. Бу үтігі
. Планшет

Тіркеліп, ұтыс ойынына қатысыңыз!
KN KERUEN — сіздің жайлылығыңыз біз үшін маңызды!*""",
            parse_mode="Markdown",
            protect_content=True,
            reply_markup=btn.menu(),
        )
        return

    await bot.send_video(
        message.from_user.id,
        fileId,
        caption="""*KN KERUEN экологиялық таза, сапалы шұлықтар брендтіне қош келдіңіз!

Біздың шұлықтар - 100 % табиғи бамбуктан жасалған, жоғары сапа мен жайлылықты ұсынады!
100% Евро стандартқа сай шұлықтар! 🌱🧦

Акция! Акция!
Біздің шұлықтарды сатып ала отырып!
Керемет сыйлықтарға ие болыңыз!
Сыйлықтар тізімі!
. Авто көлік
. Пәтер
. пылесос 
. Ас үй комбайны!
. Бу үтігі
. Планшет


Тіркеліп, ұтыс ойынына қатысыңыз!
KN KERUEN — сіздің жайлылығыңыз біз үшін маңызды!*""",        
        parse_mode="Markdown",
        protect_content=True,
        reply_markup=btn.buy_cinema(),
    )

    
@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO])
async def media_handler(message: types.Message, state: FSMContext):
    file_id = None

    # Проверяем тип контента
    if message.content_type == 'photo':
        # Получаем file_id самого большого размера фото
        file_id = message.photo[-1].file_id
    elif message.content_type == 'video':
        # Получаем file_id видео
        file_id = message.video.file_id

    if file_id:
        # Сохраняем file_id в состоянии
        async with state.proxy() as data:
            data['file_id'] = file_id

        # Отправляем file_id пользователю
        await bot.send_message(
            message.from_user.id,
            text=f"*FileID: {data['file_id']}*",
            parse_mode="Markdown",
        )
    else:
        await bot.send_message(
            message.from_user.id,
            text="Ошибка: неизвестный тип медиафайла.",
        )  

@dp.message_handler(Text(equals="🎥 Бейне курстар"), content_types=['text'])
async def handler(message: types.Message):

    file_id = "BAACAgIAAxkBAAIMsGYOfL6V-0jAR11JZUN9v2NrKV-8AALORQAC_NNxSKAE1UMhWlFeNAQ"     

    await bot.send_video(message.from_user.id, file_id, protect_content=True)

    await bot.send_message(
        message.from_user.id,
        text="""*Видео материялдағы сұрақтарға жауап беріңіз!\n Сұрақтар саны 5\nСұрақтар 1 ...*""",
        parse_mode="Markdown",
        reply_markup=btn.cancel()
    ) 

@dp.message_handler(commands=['help'])
@dp.message_handler(Text(equals="📲 Байланыс номері"), content_types=['text'])
async def handler(message: types.Message):

    await bot.send_message(
        message.from_user.id,
        text="""*https://wa.me/77710000144*""",
        parse_mode="Markdown",
    ) 




@dp.message_handler(Text(equals="💸 Money"), content_types=['text'])
async def handler(message: types.Message):
    
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        sum = db.get_money_sum()
        await bot.send_message(
                message.from_user.id,
                text="""*💳 Жалпы қаражат: %d*"""%sum,
                parse_mode="Markdown",
                reply_markup=btn.admin()
            )    

@dp.message_handler(Text(equals="📨 Хабарлама жіберу"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        await FormaAdmin.s1.set()
        await bot.send_message(
                message.from_user.id,
                text="""*✏️ Хабарлама типін таңдаңыз*""",
                parse_mode="Markdown",
                reply_markup=btn.typeMsg()
            )     


@dp.message_handler(Text(equals="📨 Әкімшіге хабарлама"), content_types=['text'])
async def handler(message: types.Message):

    await bot.send_message(
        message.from_user.id,
        text="""*@senior_coffee_drinker*\n\nhttps://wa.me/+77710000144""",
        parse_mode="Markdown",
    ) 


@dp.message_handler(Text(equals="💳 Қайтадан керуен өнімін сатып алу"), content_types=['text'])
async def handler(message: types.Message):
    
    await Forma.s1.set()
    await bot.send_message(
            message.from_user.id,
            text="*Қанша шұлық алғыңыз келеді 😉?*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
    )

"""
# Новый хендлер для обработки отправки PDF-файла
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state='*')
async def pdf_received_handler(message: types.Message, state: FSMContext):
    # Проверяем, что отправленный файл — это PDF
    if message.document.mime_type == 'application/pdf':
        # Устанавливаем состояние Forma.s1
        await Forma.s1.set()
        # Отправляем сообщения, как при нажатии на кнопку "Қайтадан киноны сатып алу"
        await bot.send_message(
            message.from_user.id,
            text="*Билет саны көп болған сайын жүлдені ұту 📈 ықтималдығы соғырлым жоғары 😉👌*",
            parse_mode="Markdown",
        )
        await bot.send_message(
            message.from_user.id,
            text="*Қанша билет алғыңыз келеді? Билет саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
        )
    else:
        # Если отправлен не PDF-файл, можно уведомить пользователя
        await message.reply("Тек, PDF файл жіберу керек!")
    

"""
@dp.message_handler(Text(equals="🎬 Киноны сатып алу"), content_types=['text'])
async def handler(message: types.Message):
    
    await Forma.s1.set()
    await bot.send_message(
            message.from_user.id,
            text="*Қанша билет алғыңыз келеді? Билет саны көп болған сайын ұтыста жеңу ықтималдығы жоғары 😉*",
            parse_mode="Markdown",
            reply_markup=btn.digits_and_cancel()
    ) 
    

@dp.message_handler(Text(equals="📑 Лото"), content_types=['text'])
async def send_just_excel(message: types.Message):
    if message.from_user.id == admin:
        db.create_loto_excel('./excell/loto.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/loto.xlsx', 'rb'))

@dp.message_handler(Text(equals="👥 Қолданушылар саны"), content_types=['text'])
async def send_client_excel(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        db.create_client_excel('./excell/clients.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/clients.xlsx', 'rb'))

@dp.message_handler(Text(equals="👇 Just Clicked"), content_types=['text'])
async def send_loto_excel(message: types.Message):
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        db.create_just_excel('./excell/just_users.xlsx')
        await bot.send_document(message.from_user.id, open('./excell/just_users.xlsx', 'rb'))
    


@dp.message_handler(Text(equals="📨 Хабарлама жіберу"), content_types=['text'])
async def handler(message: types.Message):

    await bot.send_message(
        message.from_user.id,
        text="""*@senior_coffee_drinker*""",
        parse_mode="Markdown",
        reply_markup=btn.admin()
    ) 

@dp.message_handler(Text(equals="🧧 Ұтыс билеттерім"), content_types=['text'])
async def handler(message: types.Message):

    id_user = message.from_user.id            # Get the user ID from the message
    loto_ids = db.FetchIdLotoByUser(id_user)  # Fetch the list of id_loto for this user
    
    if loto_ids:
        ids_formatted = ", ".join(map(str, loto_ids))  # Format the list as a comma-separated string
        response_text = f"Сіздің ұтыс билеттеріңіздің ID-лары: {ids_formatted}"
    else:
        response_text = "Сіздің ұтыс билетіңіз жоқ."

    await bot.send_message(
        message.from_user.id,
        text=response_text,
        parse_mode="Markdown",
        reply_markup=btn.menu()
    )


    
@dp.message_handler(Text(equals="🎁 Сыйлықтар"), content_types=['text'])
async def handler(message: types.Message):
    print(message.from_user.id)
    if message.from_user.id == admin or message.from_user.id == admin2 or message.from_user.id == admin3:
        await bot.send_message(
        message.from_user.id,
        text="😊 *🎁 Сыйлықтар*",
        parse_mode="Markdown",
        reply_markup=btn.gift()
    )

@dp.message_handler(Text(equals="🎁 1-ші сыйлық"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5) 


@dp.message_handler(Text(equals="🎁 2-ші сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5) 

@dp.message_handler(Text(equals="🎁 3-ші сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5)  

@dp.message_handler(Text(equals="🎁 4-ші сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5) 

@dp.message_handler(Text(equals="🎁 5-ші сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5)  

@dp.message_handler(Text(equals="🎁 6-шы сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5)  

@dp.message_handler(Text(equals="🎁 7-ші сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5)  



@dp.message_handler(Text(equals="🎁 8-ші сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5)  


@dp.message_handler(Text(equals="🎁 9-шы сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5)  

@dp.message_handler(Text(equals="🎁 10-шы сыйлық"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 100 000 теңге\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5) 

@dp.message_handler(Text(equals="◀️ Кері"), content_types=['text'])
async def handler(message: types.Message):

    if message.from_user.id == admin or message.from_user.id == admin2:
        await bot.send_message(
        message.from_user.id,
        text="😊 *Сәлеметсіз бе %s !\nСіздің статусыңыз 👤 Админ(-ка-)*"%message.from_user.first_name,
        parse_mode="Markdown",
        reply_markup=btn.admin()
    )

async def send_pdf_with_caption(user_id, id_loto, caption):
    loto_info = db.fetch_loto_by_id(id_loto)
    if not loto_info:
        await bot.send_message(user_id, text="PDF not found.")
        return

    receipt = loto_info[3]  # Adjusted index for receipt column
    pdf_path = f"/home/cinema/pdf/{receipt}"
    
    if os.path.exists(pdf_path):
        await bot.send_document(
            user_id,
            document=open(pdf_path, 'rb'),
            caption=caption,
            reply_markup=btn.gift()
        )
    else:
        await bot.send_message(user_id, text="PDF file not found.")



#
@dp.message_handler(Text(equals="🎁 🚗 Көлік"), content_types=['text'])
async def handler(message: types.Message):
    if message.from_user.id in [admin, admin2, admin3]:
        steps = [50, 25, 10, 1]
        
        # Fetch 100 entries initially
        entries = db.fetch_random_loto_car(100)
        if not entries:
            await bot.send_message(
                message.from_user.id,
                text="No data available.",
                reply_markup=btn.gift()
            )
            return
        
        # Send the first 100 entries as one message
        first_batch = entries[:100]
        text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in first_batch])
        for chunk in split_message(text):
            sent_message = await bot.send_message(
                message.from_user.id,
                text=chunk,
                reply_markup=btn.gift()
            )
            await asyncio.sleep(2)
            await bot.delete_message(message.from_user.id, sent_message.message_id)
        
        # Process subsequent steps by selecting random subsets
        current_entries = entries
        for step in steps:
            current_entries = random.sample(current_entries, step)
            if step == 1:
                row = current_entries[0]
                text = f"🎁 🚗 Көлік\n\nID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}"
                await send_pdf_with_caption(message.from_user.id, row[0], text)
            else:
                text = "\n\n".join([f"ID Loto: {row[0]}\nContact: {row[1]}\nData Pay: {row[2]}" for row in current_entries])
                for chunk in split_message(text):
                    sent_message = await bot.send_message(
                        message.from_user.id,
                        text=chunk,
                        reply_markup=btn.gift()
                    )
                    await asyncio.sleep(5)
                    await bot.delete_message(message.from_user.id, sent_message.message_id)
            
            await asyncio.sleep(0.5)





