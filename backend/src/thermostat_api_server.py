#!flask/bin/python
import json
import logging
import time
from logging.handlers import RotatingFileHandler

from flask import Flask, request, send_from_directory

import ac_logic
import config
import console_window
import fan_logic
import thermostat_controller

# Setup logging

logfile = config.get['logging']['logfile']
log_lvl = config.get['logging']['loglevel']
log_out = config.get['logging']['log_stream_to_console']
max_bytes = int(config.get['logging']['maxBytes'])
backup_count = int(config.get['logging']['backupCount'])

my_handler = RotatingFileHandler(logfile, mode='a', maxBytes=max_bytes,
                                 backupCount=backup_count, encoding=None,
                                 delay=False)
my_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d: %(message)s'))
l = logging.getLogger()
l.setLevel(log_lvl.upper())
l.addHandler(my_handler)
if log_out.upper() == 'TRUE':
    l.addHandler(logging.StreamHandler())

l.info("Initializing Levantine's thermostat API backend...")

# Flask app setup
l.info("Configuring FLASK...")
app = Flask(__name__)
port = config.get['default']['port']

# Alias setup
l.info("Configuring Aliases")
get_info = thermostat_controller.get_info
thermostat_control = thermostat_controller.thermostat_control
fan_controller = fan_logic.fan_controller
ac_threads = ac_logic.ac_threads


@app.route('/')
def index():
    return send_from_directory('static/html', 'thermostat_buttons.html')


@app.route('/thermostat_buttons.css')
def send_css():
    return send_from_directory('static/css', 'thermostat_buttons.css')


@app.route('/thermostat_buttons.js')
def send_js():
    return send_from_directory('static/js', 'thermostat_buttons.js')


@app.route('/thermostat/console_data', methods=['GET'])
def get_console_data():
    l.debug(request)
    return console_window.generate_status_console_html()


@app.route('/thermostat/status', methods=['GET'])
def get_thermostat_data():
    l.info(request)
    data_requested = request.args.get('status_page')
    return get_info(info=data_requested)


@app.route('/thermostat/cmd', methods=['POST'])
def set_thermostat():
    l.info(request)
    data = json.loads(request.data)
    cycle_time = data["time"]
    temperature = data["temperature"]
    if ac_logic.thread_running is True:
        l.warning("There is another AC logic thread running. Killing it")
        ac_logic.current_thread_stop_event.set()
        # Short delay to help alleviate a race condition where it tries to start a thread before the previous one exits
        time.sleep(.2)  # 200 ms
    ac_threads(cycle_time, temperature)
    return "Request Sent", 200


# API Routes
if __name__ == '__main__':
    # l.info(console_window.generate_status_console_html())
    # exit(0)
    while 1:
        try:
            l.info("Initialization complete, starting front end api flask application.")
            app.run(debug=True, port=port)

        except Exception:
            l.exception("Unable to continue the API server. Restarting in 3 seconds")
            time.sleep(3)


# Thermostat modes
# 0: Off
# 1: Heat
# 2: Cool
# 3: Auto
