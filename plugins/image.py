from telegraph import upload_file
import os
from pyrogram import Client, filters

bot = Client("AutoFilterBot")  # Ensure this matches your bot's session

@bot.on_message(filters.command("telegraph") & filters.reply)
async def upload_to_telegraph(client, message):
    """Handles /telegraph command on a replied image"""
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("❌ Please reply to an image!")

    try:
        # Download the replied photo
        file_path = await message.reply_to_message.download()
        
        # Upload to Telegraph
        telegraph_url = upload_file(file_path)[0]
        full_url = f"https://telegra.ph{telegraph_url}"

        # Send the link
        await message.reply_text(f"✅ Telegraph Link: {full_url}")

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

bot.run()
