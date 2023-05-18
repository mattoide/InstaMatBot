import logging
import os
from dotenv import load_dotenv
import random
import openai
import time
import json
import requests
import datetime as dt
from common import post_on_insta, log_level, caption_base, caption_hashtags

logging.basicConfig(level=log_level)


def generate_words(prompt):
    temp = random.uniform(0.5, 2.0)

    logging.debug("Temperature:")
    logging.debug(str(temp))

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


def post_from_api():
    with open('lastStyleUsed.json') as f:
        json_file = json.load(f)
        last_style_used = 1 if json_file['lastStyleUsed'] == 0 else 0

        prompt = json_file['styles']['style' + str(last_style_used)]
        logging.debug('Prompt:')
        logging.debug(prompt)

    try:
        words = generate_words(prompt["prompt_what_i_want"] + " " + prompt["prompt_image_object"])
        logging.debug('Parole generate: ')
        logging.debug(words)

        caption = caption_base + translate_words(words)

        caption = caption + " " + words
        caption = caption.replace(".", ",")
        caption = caption.replace(",", " ")
        caption = caption.split()
        caption = " #".join(caption)
        caption = caption_base + caption_hashtags + caption

        image_url = generate_image(words + " " + prompt["prompt_image_extras"])
        logging.debug(image_url)

    except Exception as error:
        logging.warning("Errore: \n" + str(error))

    else:
        post_on_insta(image_url, caption)
