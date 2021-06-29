#!flask/bin/python
from flask import Flask, jsonify, render_template, request, Response, \
    redirect, url_for, session, flash, send_from_directory, abort
from logging.handlers import RotatingFileHandler
from os import path
import requests, time, logging,configparser, sys, json, sqlite3, os, uuid, schedule, threading
import thermostat_database

# Reading config file
config = configparser.ConfigParser()
config.sections()
try:
    if path.exists(sys.argv[1]):
        config.read(sys.argv[1])
except IndexError:
    if path.exists('config.ini'):
        config.read('config.ini')
    else:
        print("No config file found")

# Setup logging
logfile = config['logging']['logdir'] + "/thermostat_api.log"
log_lvl = config['logging']['loglevel']
log_out = config['logging']['log_stream_to_console']

my_handler = RotatingFileHandler(logfile,
                                 mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(funcName)s (%(lineno)d) %(message)s'))
l = logging.getLogger(__name__)
l.setLevel(log_lvl.upper())
l.addHandler(my_handler)
if log_out.upper() == 'TRUE':
    l.addHandler(logging.StreamHandler())

# Global Vars
thermostat_host = config['default']['thermostat_host']

def thermostat_control(mode, fan, heat_temp, cool_temp):
    url = "http://" + thermostat_host + "/control"
    parameters = {'mode': int(mode),
                  'fan': int(fan),
                  'heattemp': int(heat_temp),
                  'cooltemp': int(cool_temp),
                  }
    payload={}
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload, params=parameters)
    l.info("Setting Thermostat with: " + response.request.url)

    l.info("Thermostat request sent")
    return response.text
    # return "Request sent", 200


def get_info(info): # info could be 'sensors', 'runtimes', 'info'
    valid_info_pages = ['sensors', 'runtimes', 'info']
    if info not in valid_info_pages:
        return "Invalid status_page: '" + info + "' - Valid status_page values are 'sensors', 'runtimes', 'info'", 400
    url = "http://" + thermostat_host + "/query/" + info
    payload = {}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text
