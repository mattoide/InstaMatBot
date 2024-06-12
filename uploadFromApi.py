import logging
import random
from openai import OpenAI
import json
from common import post_on_insta, log_level, caption_base, caption_hashtags

logging.basicConfig(level=log_level)

client = OpenAI()

def generate_words(prompt):
    temp = random.uniform(0.5, 2.0)

    logging.debug("Temperature:")
    logging.debug(str(temp))

    completions = client.completions.create(model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=2020,
    n=1,
    stop=None,
    temperature=temp)

    return completions.choices[0].text


def translate_words(prompt):
    completions = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="traduci solo in inglese le seguenti parole massimo 10 parole" + prompt,
        max_tokens=2020,
        n=1,
        stop=None
    )

    return completions.choices[0].text


def reduce_hashtags_to_25(hashtags):
    completions = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=hashtags + " riduci questi tag a 2",
        max_tokens=2020,
        n=1,
        stop=None
    )
    logging.debug("DIOCANE")
    logging.debug(hashtags)
    logging.debug(completions.choices[0].text)
    return completions.choices[0].text


def generate_image(words):

    response = client.images.generate(
        model="dall-e-3",
        prompt=words,
        n=1,
        size="1024x1024",
        quality="standard"
    )

    logging.debug(response)

    return response.data[0].url


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



        caption = translate_words(words)

        caption = caption + " " + words
        caption = caption.replace(".", ",")
        caption = caption.replace(",", " ")
        caption = caption.split()
        caption = " #".join(caption)

        logging.debug('CAPITON LE PRIMA:')
        logging.debug(len(caption.split(' ')))
        logging.debug(caption)

        # if len(caption.split(' ')) > 4:
        #     caption = reduce_hashtags_to_25(caption)


        logging.debug('CAPITON LE DOPO:')
        logging.debug(len(caption.split(' ')))
        logging.debug(caption)


        caption = caption_base + caption_hashtags + caption

        logging.debug("caption")
        logging.debug(caption)
        logging.debug('caption lengh')
        logging.debug(len(caption))

        logging.debug("words")
        logging.debug(words)

        logging.debug("prompt[prompt_image_extras]")
        logging.debug(prompt["prompt_image_extras"])
        return


        image_url = generate_image(words + " " + prompt["prompt_image_extras"])
        print("Image url")
        print(image_url)
        logging.debug(image_url)

    except Exception as error:
        logging.warning("Errore: \n" + str(error))

    else:
        post_on_insta(image_url, caption)