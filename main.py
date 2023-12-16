import telebot
import speech_recognition as sr
import os
import subprocess
from dotenv import load_dotenv
import shutil

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет. Я бот, который может превратить голосовое сообщение в текст. Отправь мне голосовое сообщение до двух минут и я расшифрую его.")

@bot.message_handler(content_types=['voice'])
def voice_nadler(message):
    file_id = message.voice.file_id
    file = bot.get_file(file_id)
    
    if int(file.file_size) >= 10000000:
        bot.send_message(message.from_user.id, f'Твое голосовое слишком огромное и оно весит {int(file.file_size)} байт.')
    else:
        download_file = bot.download_file(file.file_path)
        with open('audio.ogg', 'wb') as file:
            file.write(download_file)
            
        voice_recognizer(message)

def voice_recognizer(message,chunk_size=60):
    subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])
    text = 'Я не смог распознать слова.'
    recognizer = sr.Recognizer()
    audio_file = 'audio.wav'
    with sr.AudioFile(audio_file) as source:
        for start_time in range(0, int(source.DURATION), chunk_size):
            end_time = min(start_time + chunk_size, int(source.DURATION))
            print(f"Обработка сегмента {start_time} - {end_time}.")
            
            audio = recognizer.record(source, offset=start_time, duration=end_time)

            try:
                text = recognizer.recognize_google(audio, language='ru_RU')
                bot.send_message(message.chat.id, text)
            except Exception as e:
                print('in voice message is not found words')
                bot.send_message(message.chat.id, text)

bot.infinity_polling()