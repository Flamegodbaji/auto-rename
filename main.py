from pyrogram import Client, filters
import os

# Initialize the Pyrogram Client
api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'

app = Client("rename_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Dictionary to store user file information
user_data = {}

# Function to handle file download and rename
async def handle_rename(chat_id):
    try:
        file_data = user_data.get(chat_id)
        if file_data and 'file_id' in file_data and 'new_name' in file_data:
            # Download the file
            file_path = await app.download_media(file_data['file_id'])
            # Rename the file
            os.rename(file_path, f"{os.path.dirname(file_path)}/{file_data['new_name']}")
            # Send the renamed file
            await app.send_document(
                chat_id,
                document=f"{os.path.dirname(file_path)}/{file_data['new_name']}",
                caption=file_data['new_name'],
                thumb=file_data.get('thumbnail')
            )
            # Clear the stored data after renaming
            del user_data[chat_id]
    except Exception as e:
        print(f"Error handling rename: {e}")

# Handler for incoming messages
@app.on_message(filters.private)
async def handle_message(bot, message):
    try:
        chat_id = message.chat.id
        # Check if an image is received
        if message.photo:
            # Save the image as a thumbnail for the user
            user_data[chat_id] = {'thumbnail': message.photo.file_id}
        elif message.document:
            # Ask user for a new name
            await message.reply_text("Please provide a new name for the file using the /rename command.")
            # Store file information for later renaming
            user_data[chat_id] = {'file_id': message.document.file_id}
    except Exception as e:
        print(f"Error handling message: {e}")

# Handler for /rename command
@app.on_message(filters.command("rename") & filters.private)
async def handle_rename_command(bot, message):
    try:
        chat_id = message.chat.id
        # Check if a new name is provided
        if len(message.command) > 1:
            new_name = message.command[1]
            # Store the new name with the file information
            if chat_id in user_data:
                user_data[chat_id]['new_name'] = new_name
                # Perform file download and rename
                await handle_rename(chat_id)
            else:
                await message.reply_text("No file to rename. Please send a file first.")
        else:
            await message.reply_text("Please provide a new name for the file using the /rename command.")
    except Exception as e:
        print(f"Error handling rename command: {e}")

# Run the bot
app.run()
