import os
from dotenv import load_dotenv
import random
import openai
import time
import json
import requests
import datetime as dt
from bs4 import BeautifulSoup
import sqlite3
import logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
graph_fb_insta_api_token = os.getenv('graph_fb_insta_api_token')
insta_account_id = os.getenv('insta_account_id')

graph_insta_base_url = "https://graph.facebook.com/v16.0/"
graph_insta_media_container_url = graph_insta_base_url + insta_account_id + "/media"
graph_insta_media_publish_container_url = graph_insta_base_url + insta_account_id + "/media_publish"

caption_base = "\nImmagine generata automaticamente da intelligenza artificiale.\nImage automatically generated by " \
               "artificial intelligence. \n\n\n"

caption_hashtags = "#openai #chatgpt #dalle2 #intelligenzaartificiale #ia #ai"

url_raw_contents = "https://raw.githubusercontent.com/"
sad_image_foler = "/mattoide/mattoide.github.io/master/images/sad/"
happy_image_foler = "/mattoide/mattoide.github.io/master/images/happy/"
sad_img_url = "https://github.com/mattoide/mattoide.github.io/tree/master/images/sad/"
happy_img_url = "https://github.com/mattoide/mattoide.github.io/tree/master/images/happy/"


def post_on_insta(image_url, caption):
    # body = {'image_url': image_url, 'caption': caption, 'access_token': graph_fb_insta_api_token}
    # resp = requests.post(graph_insta_media_container_url, json=body)
    #
    # container_id = resp.json()['id']
    #
    # body = {'creation_id': container_id, 'access_token': graph_fb_insta_api_token}
    # resp = requests.post(graph_insta_media_publish_container_url, json=body)
    #
    # logging.info(resp.json())

    logging.debug("Caption immagine: \n" + caption)
    logging.debug("Url immagine: \n" + image_url)
    hour = dt.datetime.now().hour

    with open('lastStyleUsed.json') as f:
        json_file = json.load(f)
        json_file['lastStyleUsed'] = 1 if json_file['lastStyleUsed'] == 0 else 0

        if json_file['lastTimePublish'] == 0 and 14 <= hour <= 16:
            json_file['lastTimePublish'] = 1

        if json_file['lastTimePublish'] == 1 and 20 <= hour <= 22:
            json_file['lastTimePublish'] = 2

        if json_file['lastTimePublish'] == 2 and 9 <= hour <= 11:
            json_file['lastTimePublish'] = 0

        f = open("lastStyleUsed.json", "w")
        f.write(json.dumps(json_file))
        f.close()

    return 1


def what_post():
    with open('lastStyleUsed.json') as f:
        json_file = json.load(f)
        f.close()
        return json_file['lastStyleUsed']


def is_time_to_post():
    hour = dt.datetime.now().hour
    hour = 21
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
                caption = href.replace("_", " #")
                caption = caption.replace("/mattoide/mattoide.github.io/master/images/sad/", "")
                caption = caption.replace("/mattoide/mattoide.github.io/master/images/happy/", "")
                caption = caption.replace(".png", "")
                caption = caption_base + caption_hashtags + caption

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
            posted = post_on_insta(img_url, caption)
            if posted == 1:
                cursor.execute("UPDATE " + p_table + " SET posted = ? WHERE name = ?", (True, name))
                conn.commit()
        else:
            logging.info("Nessuna immagine che non sia stata gia postata")

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

while True:

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

    time.sleep(10)
