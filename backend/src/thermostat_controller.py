from logging.handlers import RotatingFileHandler
from os import path
import requests, logging, configparser, sys

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
l = logging.getLogger(__name__)


# Global Vars
thermostat_host = config['default']['thermostat_host']

def thermostat_control(mode, fan, heat_temp, cool_temp):
    url = "http://" + thermostat_host + "/control"
    parameters = {'mode': int(mode),
                  'fan': int(fan),
                  'heattemp': int(heat_temp),
                  'cooltemp': int(cool_temp),
                  }
    payload = {}
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    if config['default']['test_mode'].upper() == 'TRUE':
        response = requests.Request("POST", url, headers=headers, data=payload, params=parameters)
        prepared = response.prepare()
        method = str(prepared.method)
        url = str(prepared.url)
        headers = str(prepared.headers)
        string = "Method: " + method + " Headers: " + headers + " URL: " + url
        l.info(str(string))
        return string, 200
    else:
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
    # No need to set test mode for getting info because it's read only and other processes need this to work.
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text
