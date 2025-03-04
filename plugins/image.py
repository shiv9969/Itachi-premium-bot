from telegraph import Telegraph
import os
from pyrogram import Client, filters
from plugins.image import telegraph_handler

# Initialize Telegraph API
telegraph = Telegraph()
telegraph.create_account(short_name="autofilter_bot")

# Function to upload image to Telegraph
def upload_to_telegraph(image_path):
    try:
        with open(image_path, "rb") as f:
            response = telegraph.upload_file(f)
        return "https://telegra.ph" + response[0]["src"]
    except Exception as e:
        return f"Error uploading to Telegraph: {str(e)}"

# Handler for /telegraph command (photo upload)
@Client.on_message(filters.command("telegraph") & filters.photo)
async def telegraph_handler(client, message):
    await message.reply_text("Received your image, processing...")

    file = message.photo[-1]
    file_path = f"./downloads/{file.file_id}.jpg"

    # Ensure 'downloads' directory exists
    os.makedirs("downloads", exist_ok=True)

    # Download the image
    await client.download_media(file, file_path)

    # Upload to Telegraph
    telegraph_url = upload_to_telegraph(file_path)

    # Delete local file after uploading
    os.remove(file_path)

    # Send the Telegraph link
    await message.reply_text(f"Your image has been uploaded: {telegraph_url}")
