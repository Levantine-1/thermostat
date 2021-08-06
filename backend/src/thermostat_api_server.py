#!flask/bin/python
from flask import Flask, jsonify, render_template, request, Response, \
    redirect, url_for, session, flash, send_from_directory, abort
from logging.handlers import RotatingFileHandler
from os import path
import time, logging, configparser, sys, uuid
import config, thermostat_database, thermostat_controller, fan_logic, ac_logic, console_window

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
apath_status = config.get['api_path']['apath_get_status']
apath_cmd = config.get['api_path']['apath_send_cmd']
console_data = config.get['api_path']['console_data']
port = config.get['default']['port']
if port != 5000:
    l.warning("Port is not the default 5000, this may break in prod!")

# Alias setup
l.info("Configuring Aliases")
query_db = thermostat_database.query_db
get_info = thermostat_controller.get_info
thermostat_control = thermostat_controller.thermostat_control
fan_controller = fan_logic.fan_controller
ac_threads = ac_logic.ac_threads


@app.route(console_data, methods=['GET'])
def get_console_data():
    l.info(request)
    return console_window.generate_status_console_html()


@app.route(apath_status, methods=['GET'])
def get_thermostat_data():
    l.info(request)
    data_requested = request.args.get('status_page')
    return get_info(info=data_requested)


@app.route(apath_cmd, methods=['POST'])
def set_thermostat():
    l.info(request)
    action = request.args.get('action')

    if action == "set_fan_state":
        action_type = request.args.get('action_type')
        action_state = request.args.get('action_state')
        new_uuid = str(uuid.uuid4())
        query_db(task='update', table='fan', data=new_uuid)  # Update with new uuid
        if query_db(task='fetch', table='fan', data='') == new_uuid:  # Check to make sure uuid is updated
            response = fan_controller(my_uuid=new_uuid, action_type=action_type, action_state=action_state)
            return response

    elif action == "set_ac_timer":
        cycle_time = request.args.get('cycle_time')
        response = ac_threads(threadname='ac_timer', myuuid='', action_state=cycle_time)
        return response

    elif action == "acOFF":
        l.info("Turning off AC")
        response = thermostat_control(mode='0', fan='0', heat_temp='60', cool_temp='85')  # turn off AC
        l.info(response)
        return response

    return "No valid action specified", 400


# API Routes
if __name__ == '__main__':
    # l.info(console_window.generate_status_console_html())
    # exit(0)
    while 1:
        try:
            thermostat_database.configure_SQLite()
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
