#!/usr/bin/python3
__author__ = 'guarente'

import json
import logging
# Echo server program
import socket
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
from ping3 import ping
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# DEFINIZIONE DELLA CLASSE HOST
class Host:
    def __init__(self, name, address, open_ports):
        self.name = name
        self.address = address
        self.status = "non raggiungibile"
        self.last_seen = ""
        self.last_delay = 0
        self.open_ports = open_ports

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_last_seen(self):
        return self.last_seen

    def set_last_seen(self, last_seen):
        self.last_seen = last_seen

    def get_last_delay(self):
        return self.last_delay

    def set_last_delay(self, last_delay):
        self.last_delay = last_delay

    def get_open_ports(self):
        return self.open_ports

    def set_open_ports(self, open_ports):
        self.open_ports = open_ports


# FUNZIONE DI APERTURA DEL JSON HOST E CREAZIONE DELLA LISTA

def read_hosts(file_path):

    with open(file_path, 'r') as file:
        hosts_data = json.load(file)
        file_hosts = []

    for host in hosts_data['hosts']:
        try:
            if "NAME" in host and "ADDRESS" in host and "PORT" in host:
                new_host = Host(host["NAME"], host["ADDRESS"], host["PORT"])
                file_hosts.append(new_host)
        except Exception as e:
            logging.info(f"Error processing host: {e}")

    return file_hosts

def ping(host):
      try:
          start_time = time.time()
          ping_result = ping(host.address, unit="ms", timeout=2)
          end_time = time.time()
          delay = end_time - start_time

          if ping_result is not None:

              host.set_status("raggiungibile")
              host.set_last_seen(time.time().strftime("%Y-%m-%d %H:%M:%S"))
              host.set_last_delay(delay)
              logging.info("SERVER: Host: "+host.name+", RAGGIUNGIBILE!")

          else:
              host.set_status("non raggiungibile")
              logging.info("SERVER: Host: "+host.name+", NON RAGGIUNGIBILE!")

      except Exception as e:
            host.set_status("non raggiungibile")
            logging.error(f"processing host {host.name}")


def monitor(hosts, stop, broker_address, publisher_name):
    client = mqtt.Client()

    client.connect(broker_address)

    try:
        while True:
            pings = []

            for host in hosts:
                pong = threading.Thread(target=ping, args=(host,))
                pong.start()
                pings.append(pong)

            for pong in pings:
                pong.join()

            logging.info("SERVER: Completato ping su tutti gli HOST!")

            threads = []
            for host in hosts:
                topic = f"{publisher_name}/{host.name}"
                message = f"Stato: {host.status}, Ultimo delay: {host.last_delay:.4f}"

                thread_publish_mqtt = threading.Thread(target=mqtt_client_message, args=(client, topic, message))
                thread_publish_mqtt.start()
                threads.append(thread_publish_mqtt)

            for thread_mqtt in threads:
                thread_mqtt.join()

            logging.info("SERVER: Completato publisher su tutti gli HOST! Attendo...")
            time.sleep(stop)

        client.disconnect()

    except KeyboardInterrupt:
        logging.info("SERVER: Rilevata interruzzione dall'utente, interrompo e spengo")



def mqtt_client_message(client, topic, message):
    client.publish(topic, message)
    logging.info("SERVER: nuovo messaggio pubblicato dal Client: "+topic)


def main():

    logging.info("SERVER: avvio in corso inizio lettura file")

    hosts = read_hosts("host.json")
    mqtt_broker_address = "mqtt.ssh.edu.it"
    publisher_name = "Guarente"
    interval = 30
    monitor(hosts, interval, mqtt_broker_address, publisher_name)


if __name__ == "__main__":
    main()
