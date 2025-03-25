from load import bot, storage
from main import dp
import aioschedule
import asyncio
from database import Database
import datetime as dt
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from keyboard  import*


db = Database()
btn = Button()

async def send_message(chat_id, message):
    try:
        await bot.send_message(chat_id, message, reply_markup=btn.again())
        return True
    except Exception as e:
        print(f"Failed to send message to {chat_id}: {e}")
        return False

async def send_daily_message(chunk_size: int = 30, delay: float = 1.0):
    users = db.gatherClients()
    #current_date = dt.datetime.now().date()
    #target_date = dt.datetime(2024, 8, 25).date()
    #t_money = dt.datetime(2024, 8, 20).date()
    #days_left = (target_date - current_date).days
    #days_left2 = (t_money - current_date).days    
    
    for i in range(0, len(users), chunk_size):
                chunk = users[i:i + chunk_size]
                tasks = []
                for user_id in chunk:
                    tickets = db.fetch_tickets(user_id)
                    
                    # Handle the list of id_loto carefully
                    if tickets:
                        ticket_numbers = "\n".join([str(ticket) for ticket in tickets])
                    else:
                        ticket_numbers = "No tickets available"

                    message = (
                        f"31-шы тамыз күні Mercedez GL авто көлігін сыйға береміз\n\n"
                        f"Сіздің билет номерлері: \n{ticket_numbers}\n\n"
                        f"Сізде көлікті ұтып алу мүмкіндігі жоғары\n\n"
                        f"Көлікті беруге  санаулы сағаттар қалды.\n🎬 Қайтадан киноны сатып алу сатып алу түймесін басып көлікті ұтып алуға мүмкіндігіңізді арттырыңыз"
                    )

                    tasks.append(send_message(user_id, message))

                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        print(f"Error in sending message: {result}")

                await asyncio.sleep(delay)


async def scheduler():
    #aioschedule.every().day.at("03:00").do(send_daily_message)
    #aioschedule.every().day.at("05:00").do(send_daily_message)
    #aioschedule.every().day.at("08:00").do(send_daily_message)
    #aioschedule.every().day.at("07:27").do(send_daily_message)
    #aioschedule.every().day.at("10:10").do(send_daily_message)
    #aioschedule.every().day.at("13:00").do(send_daily_message)
    #aioschedule.every().day.at("17:00").do(send_daily_message)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


#async def on_startup(dp):
#    asyncio.create_task(scheduler())

async def on_stop(dp):
    await bot.close()
    await storage.close()

def main():

    #dp.middleware.setup(LoggingMiddleware())
    
    #loop = asyncio.get_event_loop()
    #loop.create_task(scheduler())

    from aiogram import executor
    #executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_stop)
    executor.start_polling(dp,  on_shutdown=on_stop)


if __name__ == "__main__":
    main()