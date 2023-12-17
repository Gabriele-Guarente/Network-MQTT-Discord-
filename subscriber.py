#!/usr/bin/python3
__author__ = 'guarente'


# Librerie di programma

import threading
import time
from discord_webhook import DiscordWebhook
import paho.mqtt.client as mqtt
from main import read_hosts
import logging


# LINK WEBHOOK GLOBALE FISSO

id_webhook = "https://discord.com/api/webhooks/1185989276828180520/HGwoI5_lUEccJR_0sebt5If_DCqCCt2HduR0iSVLIOCwg_EoROX1cYhnhWV7tagz3D-a" # -------> Inserisci il tuo link webhook discord
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def on_message(client, userdata, msg):
    try:
        payload = str(msg.payload.decode())
        if "non raggiungibile" in payload:
            logging.info("SUBSCRIBER: "+msg.topic +" non raggiungibile")
        else:
            logging.info("SUBSCRIBER: Ricevuto messaggio dal topic: "+msg.topic)
            logging.info("SUBSCRIBER: Webhook collegato: " +id_webhook)

        webhook = DiscordWebhook(url=id_webhook, content="**Host**: "+msg.topic+", "+payload)
        webhook.execute()

    except Exception as e:
      print(e)

def connect(address, publisher_name):
    logging.info("SUBSCRIBER: Connessione al broker:"+address)
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(address)

    hosts = read_hosts('host.json')
    for host in hosts:
        topic = f"{publisher_name}/{host.name}"
        client.subscribe(topic)

    client.loop_forever()


def main():
    address = "mqtt.ssh.edu.it"
    publisher_name = "Guarente"

    logging.info("SUBSCRIBER: Avvio server...")

    thread = threading.Thread(target=connect, args=(address, publisher_name))
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Uscita dal programma...")

if __name__ == "__main__":
    main()