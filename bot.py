import os
from pyunpack import Archive
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Ambil TOKEN dari environment variable
TOKEN = os.getenv("TOKEN")

# Buat folder penyimpanan
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Halo! Kirim file ZIP atau RAR, saya akan mengekstraknya!")

async def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document
    if not file:
        return

    file_name = file.file_name
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    # Pastikan hanya menerima ZIP atau RAR
    if not (file_name.endswith(".zip") or file_name.endswith(".rar")):
        await update.message.reply_text("Saya hanya bisa ekstrak file ZIP atau RAR.")
        return

    # Download file dari Telegram
    file_obj = await file.get_file()
    await file_obj.download_to_drive(file_path)
    
    # Folder hasil ekstraksi
    extract_folder = os.path.join(DOWNLOAD_FOLDER, file_name + "_extracted")
    os.makedirs(extract_folder, exist_ok=True)

    try:
        # Ekstrak file ZIP atau RAR
        Archive(file_path).extractall(extract_folder)
        await update.message.reply_text("File berhasil diekstrak! Mengirim file...")

        # Kirim semua file hasil ekstraksi ke Telegram
        for extracted_file in os.listdir(extract_folder):
            extracted_path = os.path.join(extract_folder, extracted_file)
            await update.message.reply_document(document=open(extracted_path, "rb"))

    except Exception as e:
        await update.message.reply_text(f"Terjadi kesalahan saat ekstraksi: {e}")

async def error_handler(update: object, context: CallbackContext) -> None:
    print(f"Terjadi kesalahan: {context.error}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_error_handler(error_handler)
    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
