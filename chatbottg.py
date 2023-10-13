import json

import telebot
import pickle
import numpy as np
from telebot import types
import requests
from tensorflow import keras

bot = telebot.TeleBot("6133521715:AAHy9pq179oFYuPg2izr-ky2ig5xDu30pbM")

model = keras.models.load_model('content/chat_model')
with open("intents_v2.json") as file:
    datasss = json.load(file)
# load tokenizer object
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# load label encoder object
with open('label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)


class MuxlisaApi:
    def __init__(self, text=None, audio=None):
        self.base_url = "https://api.muxlisa.uz/"
        if text:
            self.text = text
        if audio:
            self.audio = audio

    def tts(self, speaker_id=0):
        endpoint = "v1/tts/tts-ogg/"
        res = requests.get(
            self.base_url + endpoint,
            params={
                "text": self.text,
                "speaker_id": int(speaker_id)
            })
        return res.content if res.ok else None

    def stt(self):
        endpoint = "v2/recognize/"
        file = open(self.audio, "rb")
        files = [("file", (self.audio.split("/")[-1], file, "audio/ogg"))]
        res = requests.post(self.base_url + endpoint, headers={}, files=files)
        file.close()
        if res.status_code == 413:
            return {
                'success': False,
                'content': 'Yuborilgan fayl juda katta',
            }
        if res.ok:
            result = res.json().get('result', {})
            text = result.get('text', '')
            created_time = res.json().get('created_time', '')
            recognize_time = res.json().get('recognize_time', '')

            return {
                'success': True,
                'content': text,
                'created_time': created_time,
                'recognize_time': recognize_time,
            }
        else:
            return {
                'success': False,
                'content': 'Xatolik yuz berdi, botni boshqatdan ishga tushiring',
            }


@bot.message_handler(content_types=["voice"])
def chat(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = "stt.ogg"
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    api = MuxlisaApi(audio=file_name)
    data = api.stt()
    max_len = 20
    fallback_responses = ["Kechirasiz, savolingizni tushunaolmadim.", "Kechirasiz, Savolingizni qaytara olasizmi?"]
    res = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([data["content"]]),
                                                                   truncating='post', maxlen=max_len))

    confidence = np.max(res)
    random_response = np.random.choice(fallback_responses)
    print("o'xshashlik: ", confidence)
    if confidence < 0.6:  # Threshold ustanish
        api = MuxlisaApi(text=random_response)
        response = random_response
    else:
        tag = lbl_encoder.inverse_transform([np.argmax(res)])
        for i in datasss['intents']:
            if i['tag'] == tag:
                api = MuxlisaApi(text=i['responses'])
                response = i['responses']
    res = api.tts(speaker_id=0)
    audio = res
    file_name = "tts_audio.ogg"
    with open(file_name, "wb") as f:
        f.write(audio)
    with open(file_name, "rb") as f:
        bot.send_voice(
            chat_id=message.chat.id,
            voice=f,
            caption=f"Savol: {data['content']}\n\nJavob: {response}"
        )


@bot.message_handler(content_types=["text"])
def chat_text(message):
    max_len = 20
    fallback_responses = ["Kechirasiz, savolingizni tushunaolmadim.", "Kechirasiz, Savolingizni qaytara olasizmi?"]
    res = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([message.text]),
                                                                   truncating='post', maxlen=max_len))

    confidence = np.max(res)
    random_response = np.random.choice(fallback_responses)
    print("o'xshashlik: ", confidence)
    if confidence < 0.6:  # Threshold ustanish
        api = MuxlisaApi(text=random_response)
        response = random_response
    else:
        tag = lbl_encoder.inverse_transform([np.argmax(res)])
        for i in datasss['intents']:
            if i['tag'] == tag:
                print(i["responses"])
                api = MuxlisaApi(text=i['responses'])
                response = i['responses']
                print(f"response>> {response}\n"
                      f"response type>> {type(response)}")
    res = api.tts(speaker_id=0)
    audio = res
    file_name = "tts_audio.ogg"
    with open(file_name, "wb") as f:
        f.write(audio)
    with open(file_name, "rb") as f:
        bot.send_voice(
            chat_id=message.chat.id,
            voice=f,
            caption=f"Savol: {message.text}\n\nJavob: {response}"
        )
        # print(bot.message_handler())


if __name__ == '__main__':
    bot.polling()
