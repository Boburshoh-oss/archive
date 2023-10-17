import pickle
import numpy as np
import json
import io
# import stt
from playsound import playsound
from pydub import AudioSegment

import requests
from tensorflow import keras

with open("combined_intents.json") as file:
    data = json.load(file)


def chat():
    # load trained model
    model = keras.models.load_model('content/chat_model')

    # load tokenizer object
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open('label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)

    # parameters
    max_len = 20
    fallback_responses = ["Kechirasiz, savolingizni tushunaolmadim.", "Kechirasiz, Savolingizni qaytara olasizmi?"]
    while True:
        print("User: ", end="")
        inp = input()
        # inp = stt.listen()
        # print(inp)
        if inp.lower() == "quit":
            break

        result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]),
                                                                          truncating='post', maxlen=max_len))

        confidence = np.max(result)
        print(confidence)
        if confidence < 0.6:  # Threshold ustanish
            random_response = np.random.choice(fallback_responses)
            print("ChatBot:", random_response)
            speak(random_response)
            continue

        tag = lbl_encoder.inverse_transform([np.argmax(result)])

        print("tag", tag)

        for i in data['intents']:
            if i['tag'] == tag:
                print("ChatBot:", i['responses'])
                speak(i['responses'])


print("Start messaging with the Chatbot (type quit to stop)!")

url = "https://api.muxlisa.uz/v1/api/services/tts/"


def speak(text):
    url = "https://api.muxlisa.uz/v1/api/services/tts/"

    payload = {"text": text, "token": "vhRe6NFj9CJwpkW_U07dEQ"}
    files = []
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    if response.status_code == 200:
        with open("./../response_audio.ogg", "wb") as audio_file:
            audio_file.write(response.content)

    playsound("./../response_audio.ogg")


# call the function to start chat
chat()
