import requests
import numpy as np
import pickle
import json
from tensorflow import keras
from playsound import playsound

with open("intents_converted_original.json") as file:
    data = json.load(file)


def chat():
    # load trained model
    model = keras.models.load_model("content/chat_model")

    # load tokenizer object
    with open("tokenizer.pickle", "rb") as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open("label_encoder.pickle", "rb") as enc:
        lbl_encoder = pickle.load(enc)

    # parameters
    max_len = 20

    while True:
        print("User: ", end="")
        inp = input()
        if inp.lower() == "quit":
            break

        result = model.predict(
            keras.preprocessing.sequence.pad_sequences(
                tokenizer.texts_to_sequences([inp]), truncating="post", maxlen=max_len
            )
        )
        tag = lbl_encoder.inverse_transform([np.argmax(result)])

        for i in data["intents"]:
            if i["tag"] == tag:
                text = np.random.choice(i["responses"])
                print("ChatBot:", text)
                speak(text)


print("Start messaging with the Chatbot (type quit to stop)!")


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
