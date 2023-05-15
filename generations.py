import os
from dotenv import load_dotenv
import random
import openai
import time
import json
import requests
import datetime as dt

load_dotenv()
openai.api_key = os.getenv('openai_api_token')
graph_fb_insta_api_token = os.getenv('graph_fb_insta_api_token')
insta_account_id = os.getenv('insta_account_id')

graph_insta_base_url = "https://graph.facebook.com/v16.0/"
graph_insta_media_container_url = graph_insta_base_url + insta_account_id + "/media"
graph_insta_media_publish_container_url = graph_insta_base_url + insta_account_id + "/media_publish"

caption = "#openai chatgpt dalle2 intelligenzaartificiale ia ai "


def generate_words(prompt):
    temp = random.uniform(0.0, 2.0)
    # print("Temp: " + str(temp))
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2020,
        n=1,
        stop=None,
        temperature=temp
    )

    return completions.choices[0].text


def translate_words(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt="traduci in inglese " + prompt,
        max_tokens=2020,
        n=1,
        stop=None
    )

    return completions.choices[0].text


def generate_image(words):
    response = openai.Image.create(
        prompt=words,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']


def post_on_insta(image_url, caption):
    body = {'image_url': image_url, 'caption': caption, 'access_token': graph_fb_insta_api_token}
    resp = requests.post(graph_insta_media_container_url, json=body)

    container_id = resp.json()['id']

    body = {'creation_id': container_id, 'access_token': graph_fb_insta_api_token}
    resp = requests.post(graph_insta_media_publish_container_url, json=body)

    print(resp.json())
    print(caption)


# a = "Gruesome, macabra, dark, paurosa, spaventosa, desolante. photorealistic dark senza testo sull immagine"

while True:

    time = dt.datetime.now().hour
    # time = 15

    with open('lastStyleUsed.json') as f:
        jsonFile = json.load(f)
        lastStyleUsed = 1 if jsonFile['lastStyleUsed'] == 0 else 0

        prompt = jsonFile['styles']['style' + str(lastStyleUsed)]
        print('prompt')
        print(prompt)

    try:
        words = generate_words(prompt["prompt_what_i_want"] + " " + prompt["prompt_image_object"])
        print('words')
        print(words)

        caption = caption + translate_words(words)

        caption = caption + " " + words
        caption = caption.replace(".", ",")
        caption = caption.replace(",", " ")
        caption = caption.split()
        caption = " #".join(caption)
        caption = "Immagine generata automaticamente da intelligenza artificiale.\nImage automatically generated by " \
                  "artificial intelligence. \n\n\n" + caption
        # print('caption')
        # print(caption)
        imageUrl = generate_image(words + " " + prompt["prompt_image_extras"])

    except Exception as error:
        print("Errore:\n" + str(error))

    else:
        jsonFile['lastStyleUsed'] = 1 if jsonFile['lastStyleUsed'] == 0 else 0

        print("Ultima pubblicazione: ")
        print(jsonFile['lastTimePublish'])
        print("ora attuale")
        print(time)

        if jsonFile['lastTimePublish'] == 0 and 14 <= time <= 16:
            jsonFile['lastTimePublish'] = 1
            post_on_insta(imageUrl, caption)

        if jsonFile['lastTimePublish'] == 1 and 20 <= time <= 22:
            jsonFile['lastTimePublish'] = 2
            post_on_insta(imageUrl, caption)

        if jsonFile['lastTimePublish'] == 2 and 9 <= time <= 11:
            jsonFile['lastTimePublish'] = 0
            post_on_insta(imageUrl, caption)

        f = open("lastStyleUsed.json", "w")
        f.write(json.dumps(jsonFile))
        f.close()
        # post_on_insta(imageUrl, caption)

time.sleep(10800)
