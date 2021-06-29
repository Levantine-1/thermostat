#!flask/bin/python
from flask import Flask, jsonify, render_template, request, Response, \
    redirect, url_for, session, flash, send_from_directory, abort
from logging.handlers import RotatingFileHandler
from os import path
import time, logging,configparser, sys, uuid
import thermostat_database, thermostat_controller, fan_logic, ac_logic

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

l.info("Initializing Levantine's thermostat API backend...")

# Flask app setup
l.info("Configuring FLASK...")
app = Flask(__name__)
apath_status = config['api_path']['apath_get_status']
apath_cmd = config['api_path']['apath_send_cmd']

# Alias setup
l.info("Configuring Aliases")
query_db = thermostat_database.query_db
get_info = thermostat_controller.get_info
thermostat_control = thermostat_controller.thermostat_control
fan_controller = fan_logic.fan_controller
ac_threads = ac_logic.ac_threads


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
    while 1:
        try:
            thermostat_database.configure_SQLite()
            l.info("Initialization complete, starting front end api flask application.")
            app.run(debug=True)

        except Exception:
            l.exception("Unable to continue the API server. Restarting in 3 seconds")
            time.sleep(3)


#Thermostat modes
# 0: Off
# 1: Heat
# 2: Cool
# 3: Auto