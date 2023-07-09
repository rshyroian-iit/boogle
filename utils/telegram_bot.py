def send_telegram_message(message, filename=None):
    
    import asyncio
    from telegram import Bot

    TOKEN = "6290394082:AAHcFkRsGM-XPalCCyHTzWPc07S4GKHhSnM"
    CHAT_ID = "-1001919002420"
    print(message)
    async def main(message, filename):
        bot = Bot(token=TOKEN)
        if filename:
            with open(filename, 'rb') as f:
                await bot.send_document(chat_id=CHAT_ID, document=f, caption=message[:1000])
        else:
            print('here')
            await bot.send_message(chat_id=CHAT_ID, text=message[:1000])
    asyncio.run(main(message, filename))