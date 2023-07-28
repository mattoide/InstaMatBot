import os
from dotenv import load_dotenv
import json
import requests
import datetime as dt
from bs4 import BeautifulSoup
import sqlite3
import logging
from uploadFromApi import post_from_api
from common import post_on_insta, log_level, sad_image_foler, sad_img_url, happy_image_foler, happy_img_url, caption_base, caption_hashtags, url_raw_contents

logging.basicConfig(level=log_level)


def what_post():
    with open('lastStyleUsed.json') as f:
        json_file = json.load(f)
        f.close()
        return json_file['lastStyleUsed']


def is_time_to_post():
    hour = dt.datetime.now().hour
    logging.debug("Sono le: " + str(hour))

    with open('lastStyleUsed.json') as f:
        json_file = json.load(f)

        time_to_post = False

        if json_file['lastTimePublish'] == 0 and 14 <= hour <= 16:
            time_to_post = True

        if json_file['lastTimePublish'] == 1 and 20 <= hour <= 22:
            time_to_post = True

        if json_file['lastTimePublish'] == 2 and 9 <= hour <= 11:
            time_to_post = True

        f.close()
        return time_to_post


def create_caption(name):
    caption = name
    caption = name.replace("_", " #")
    caption = caption.replace("/mattoide/mattoide.github.io/master/images/sad/", "")
    caption = caption.replace("/mattoide/mattoide.github.io/master/images/happy/", "")
    caption = caption.replace(".png", "")
    caption = caption_base + caption_hashtags + caption
    return caption


def image_to_post(url, p_table, p_folder):
    response = requests.get(url)

    img_url = ""

    if response.status_code == 200:

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        links = soup.find_all('a')

        for link in links:
            href = link.get('href')
            if ".png" in href:
                href = href.replace("blob/", "")

                href = href.split("/")
                href = href[len(href) - 1]

                cursor = conn.cursor()

                cursor.execute("SELECT * FROM " + p_table + " WHERE name = ?", (href,))
                row = cursor.fetchone()

                if row:
                    name = row[1]
                    logging.info("Immagine gia presente:\n " + name)
                else:
                    cursor.execute("INSERT INTO " + p_table + " (name, posted) VALUES (?, ?)", (href, False))
                    conn.commit()

        cursor.execute("SELECT * FROM " + p_table + " WHERE posted = ?", (False,))
        row = cursor.fetchone()

        if row:
            name = row[1]
            img_url = url_raw_contents + p_folder + name
            caption = create_caption(name)
            logging.debug("Url immagine: " + img_url)
            logging.debug("Caption immagine: " + caption)
            logging.info("Image url:")
            logging.info(img_url)
            posted = post_on_insta(img_url, caption)
            if posted == 1:
                cursor.execute("UPDATE " + p_table + " SET posted = ? WHERE name = ?", (True, name))
                conn.commit()
        else:
            logging.info("Nessuna immagine che non sia stata gia postata\nNe creo una da API")
            post_from_api()

        cursor.close()

    else:
        logging.warning("Errore nella richiesta:", response.status_code)

    cursor = conn.cursor()
    logging.debug("Tabella: " + p_table)
    cursor.execute("SELECT * FROM " + p_table)
    rows = cursor.fetchall()
    for row in rows:
        logging.debug(row)


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS sad_images
                  (id INTEGER PRIMARY KEY, name TEXT, posted BOOLEAN)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS happy_images
                  (id INTEGER PRIMARY KEY, name TEXT, posted BOOLEAN)''')


# conn.close()

def post_from_local():
    if what_post() == 1:
        table = "sad_images"
        url = sad_img_url
        folder = sad_image_foler
    elif what_post() == 0:
        table = "happy_images"
        url = happy_img_url
        folder = happy_image_foler

    if is_time_to_post():
        logging.info("Orario per postare")
        image_to_post(url, table, folder)
    else:
        logging.info("Fuori orario per postare")
