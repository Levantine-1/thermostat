import time, logging, threading
import thermostat_database, thermostat_controller

# Setup logging
l = logging.getLogger(__name__)

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
