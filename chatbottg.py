import json
import time

import telebot
import pickle
import numpy as np
from fuzzywuzzy import process, fuzz
import requests

bot = telebot.TeleBot("6266290171:AAEFG6zA2vflDd961bc-YEFFpclUf9gUHQI")

with open("intents_v3_converted_new.json") as file:
    datasss = json.load(file)
# load tokenizer object
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# load label encoder object
with open('label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)


def replace_apostrophes(input_text):
    text_rep = []
    for i in input_text:
        if i == "'":
            text_rep.extend(i.replace("'", "‘"))
        else:
            text_rep.extend(i)
    text_rep = "".join(text_rep)
    return text_rep


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
    ict_week_replacer = [
        "aysichivik", "aysitivik", "aysittivik", "asicivik", "ayshitchivik", "sitivik", "aysisivik", "aysitvik",
        "asitivik", "asisivik", "aysichivik"
    ]
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = "stt.ogg"
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    api = MuxlisaApi(audio=file_name)
    data = api.stt()
    user_voice_text = data['content']
    questions = [items for items in datasss]
    fallback_responses = ["Kechirasiz, savolingizni tushunaolmadim.", "Kechirasiz, Savolingizni qaytara olasizmi?"]
    random_response = np.random.choice(fallback_responses)
    res = process.extractOne(query=user_voice_text.lower(), choices=questions, scorer=fuzz.token_sort_ratio)
    print(res)
    temp_list = []
    if res[1] > 60:
        res = res[0]
        for each_word in user_voice_text.lower().split(" "):
            if each_word in ict_week_replacer:
                new_var = each_word.replace(each_word, "ICT WEEK")
                temp_list.append(new_var)
            else:
                temp_list.append(each_word)
        random_answer = np.random.choice(datasss[res]['responses'])
        api = MuxlisaApi(text=random_answer)
        answer = random_answer
    else:
        for each_word in user_voice_text.lower().split(" "):
            temp_list.append(each_word)
        api = MuxlisaApi(text=random_response)
        answer = random_response

    res = api.tts(speaker_id=0)
    audio = res
    file_name = "tts_audio.ogg"
    data_content = " ".join(temp_list)
    print(f"user message: {data_content}")
    with open(file_name, "wb") as f:
        f.write(audio)
    with open(file_name, "rb") as f:
        bot.send_voice(
            chat_id=message.chat.id,
            voice=f,
            caption=f"Savol: {data_content}\n\nJavob: {answer}"
        )


@bot.message_handler(content_types=["text"])
def chat_text(message):
    ict_week_replacer = [
        "aysichivik", "aysitivik", "aysittivik", "asicivik", "ayshitchivik", "sitivik", "aysisivik", "aysitvik",
        "asitivik", "asisivik", "aysichivik"
    ]
    input_message = replace_apostrophes(message.text)
    fallback_responses = ["Kechirasiz, savolingizni tushunaolmadim.", "Kechirasiz, Savolingizni qaytara olasizmi?"]
    questions = [items for items in datasss]
    res = process.extractOne(query=input_message.lower(), choices=questions, scorer=fuzz.token_sort_ratio)
    print(res)
    random_response = np.random.choice(fallback_responses)
    temp_list = []
    if res[1] > 60:  # Threshold ustanish
        res = res[0]
        for each_word in input_message.lower().split(" "):
            if each_word in ict_week_replacer:
                new_var = each_word.replace(each_word, "ICT WEEK")
                temp_list.append(new_var)
            else:
                temp_list.append(each_word)
        random_answer = np.random.choice(datasss[res]['responses'])
        api = MuxlisaApi(text=random_answer)
        response = random_answer
    else:
        for each_word in input_message.lower().split(" "):
                temp_list.append(each_word)
        api = MuxlisaApi(text=random_response)
        response = random_response
    res = api.tts(speaker_id=0)
    audio = res
    file_name = "tts_audio.ogg"
    data_content = " ".join(temp_list)
    print(f"user message: {data_content}")
    with open(file_name, "wb") as f:
        f.write(audio)
    with open(file_name, "rb") as f:
        bot.send_voice(
            chat_id=message.chat.id,
            voice=f,
            caption=f"Savol: {data_content}\n\nJavob: {response}"
        )
        # print(bot.message_handler())


if __name__ == "__main__":
    count = 0
    while True:
        count += 1
        print(count)
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
