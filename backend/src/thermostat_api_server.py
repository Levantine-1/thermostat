#!flask/bin/python
from flask import Flask, jsonify, render_template, request, Response, \
    redirect, url_for, session, flash, send_from_directory, abort
from logging.handlers import RotatingFileHandler
from os import path
import requests, time, logging,configparser, sys, json, sqlite3, os, uuid, schedule, threading

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
thermostat_host = config['default']['thermostat_host']

def configure_SQLite():
    try:
        l.info("Configuring SQLite3...")
        db_file = config['database']['db_file']
        if os.path.exists(db_file):
            l.info("DB exists, resetting all values")
            db = sqlite3.connect("thermostat.db")
            cur = db.cursor()
            cur.execute("UPDATE fan SET pk = '1', uuid = '' WHERE pk = '1'")
            cur.execute("UPDATE ac_scheduler SET pk = '1', uuid = '' WHERE pk = '1'")
            cur.execute("UPDATE ac_timer SET pk = '1', uuid = '' WHERE pk = '1'")
            db.commit()
            db.close()
        else:
            l.info("DB doesn't exist, creating tables...")
            db = sqlite3.connect("thermostat.db")
            cur = db.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS fan(pk, uuid)")
            cur.execute("CREATE TABLE IF NOT EXISTS ac_scheduler(pk, uuid)")
            cur.execute("CREATE TABLE IF NOT EXISTS ac_timer(pk, uuid)")
            cur.execute("INSERT INTO fan(pk, uuid) VALUES('1', '')")
            cur.execute("INSERT INTO ac_scheduler(pk, uuid) VALUES('1', '')")
            cur.execute("INSERT INTO ac_timer(pk, uuid) VALUES('1', '')")
            db.commit()
            db.close()
    except Exception:
        l.exception("Unable to setup database")
        raise


def query_db(task, table, data): # data could be empty string
    db = sqlite3.connect("thermostat.db")
    cur = db.cursor()
    if task == 'fetch':
        l.debug("Fetching data about table: " + table)
        query = cur.execute("SELECT uuid FROM " + table + " WHERE pk = '1'").fetchone()
        cur.close()
        db.close()
        l.debug("Result: " + str(query[0]))
        return query[0]
    elif task == 'update':
        l.info("Updating table: " + table + " with new uuid: " + str(data))
        cur.execute("UPDATE " + table + " SET uuid = '" + data + "' WHERE pk = '1'")
        updated_value = query_db(task='fetch', table=table, data='')
        db.commit()
        cur.close()
        db.close()
        l.info("Updated value: " + updated_value)
        return updated_value


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


def set_fan_state(state): # Turn fan on or off, state value 1 or 0
    valid_states = ['0', '1']
    if state not in valid_states:
        return "Fan state value not valid, use 1 or 0", 400
    l.info("Getting current state")
    current_state = json.loads(get_info(info='info'))

    mode = current_state['mode']
    fan = current_state['fan']
    heattemp = current_state['heattemp']
    cooltemp = current_state['cooltemp']

    l.info("Current mode: " + str(mode) + " fan: " + str(fan) +  " heat: " + str(heattemp) + " cool: " + str(cooltemp))
    l.info("Setting mode: " + str(mode) + " fan: " + state +  " heat: " + str(heattemp) + " cool: " + str(cooltemp))
    return thermostat_control(mode=mode, fan=state, heat_temp=heattemp, cool_temp=cooltemp)


def fan_timer_thread(cycle_time): # Runs fan for $x amount of time
    l.info("Turning fan on for " + str(cycle_time) + " minutes.")
    cycle_time = int(cycle_time) * 60 # Convert minutes to seconds
    set_fan_state('1')
    time.sleep(cycle_time)
    l.info("Time's up, turning fan off")
    set_fan_state('0')
    return "Timer done", 200


def fan_scheduler(my_uuid, action_state): # Runs fan on a scheduled interval
    try:
        cycle_time = action_state.split(',')[0]
        interval = action_state.split(',')[1]
        l.info("Scheduling fan to turn on for " + str(cycle_time) + " every " + str(interval) + " minutes for UUID: " + str(my_uuid))
        schedule.every(int(interval)).minutes.do(lambda: fan_threads(threadname='fan_timer_thread',
                                                                     my_uuid=my_uuid,
                                                                     action_state=action_state))
        l.info("Starting first run of fans since the scheduler doesn't start it first")
        fan_threads(threadname='fan_timer_thread', my_uuid=my_uuid, action_state=action_state)
        while query_db(task='fetch', table='fan', data='') == my_uuid:
            l.debug("fan scheduler looping: " + my_uuid)
            schedule.run_pending()
            time.sleep(.5)
        l.info("UUID No longer valid. Old: " + str(my_uuid) + " Stopping job")
    except Exception:
        l.exception("Something went wrong with the fan scheduler")
        raise


def fan_threads(threadname, my_uuid, action_state): # Spawns threads to control fans
    if threadname == 'fan_timer_thread':
        l.info("Starting fan_timer_thread")
        cycle_time = str(action_state.split(',')[0])
        l.info("CYCLETIME: " + cycle_time)
        t1 = threading.Thread(target=fan_timer_thread, args=(cycle_time,))
        t1.start()
        return "Thread started", 200
    elif threadname == 'fan_scheduler':
        l.info("Starting fan_scheduler thread")
        t1 = threading.Thread(target=fan_scheduler, args=(my_uuid, action_state))
        t1.start()
        return "Thread started", 200
    else:
        return "Invalid threadname", 400


def fan_controller(my_uuid, action_type, action_state): # fan command router
    try:
        l.info("Setting up fan controller")
        if action_type == 'simple':
            if action_state == '0':
                l.info("Turning fan off")
                response = set_fan_state(state=action_state)
                l.info(response)
                return response
            elif action_state == '1':
                l.info("Turning fan on")
                response = set_fan_state(state=action_state)
                return response
            else:
                return "Invalid aciton state for simple fan setting. Needs to be 1 or 0", 400

        elif action_type == 'scheduled':
            response = fan_threads(threadname="fan_scheduler", my_uuid=my_uuid, action_state=action_state)
            return response

        else:
            l.exception("")
            return "Something went wrong with fan_controller"
    except Exception:
        l.exception("")
        raise


def ac_threads(threadname, myuuid, action_state):
    if threadname == 'ac_timer':
        l.info("Starting AC timer thread")
        cycle_time = action_state
        l.info(cycle_time)
        t1 = threading.Thread(target=ac_timer_thread, args=(cycle_time,))
        t1.start()
        return "AC timer thread started", 200
    else:
        return "Invalid AC thread name", 400


def ac_timer_thread(cycle_time):
    l.info("Turning on AC for " + str(cycle_time) + " minutes.")
    cycle_time = int(cycle_time) * 60 # convert minutes to seconds
    thermostat_control(mode='2', fan='0', heat_temp='60', cool_temp='68')
    time.sleep(cycle_time)
    l.info("Time's up, turning off AC")
    thermostat_control(mode='0', fan='0', heat_temp='60', cool_temp='85')
    return "Timer done", 200


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
        query_db(task='update', table='fan', data=new_uuid) # Update with new uuid
        if query_db(task='fetch', table='fan', data='') == new_uuid: # Check to make sure uuid is updated
            response = fan_controller(my_uuid=new_uuid, action_type=action_type, action_state=action_state)
            return response

    elif action == "set_ac_timer":
        cycle_time = request.args.get('cycle_time')
        response = ac_threads(threadname='ac_timer', myuuid='', action_state=cycle_time)
        return response

    elif action == "acOFF":
        l.info("Turning off AC")
        response = thermostat_control(mode='0', fan='0', heat_temp='60', cool_temp='85') # turn off AC
        l.info(response)
        return response

    return "No valid action specified", 400

# API Routes
if __name__ == '__main__':
    while 1:
        try:
            configure_SQLite()
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