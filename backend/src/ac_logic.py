from logging.handlers import RotatingFileHandler
from os import path
import time, logging, configparser, sys, threading
import thermostat_database, thermostat_controller

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

# Alias setup
l.info("Configuring Aliases")
query_db = thermostat_database.query_db
get_info = thermostat_controller.get_info
thermostat_control = thermostat_controller.thermostat_control

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
