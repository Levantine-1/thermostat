import time, logging, json, schedule, threading
import thermostat_database, thermostat_controller, config

# Setup logging
l = logging.getLogger(__name__)

query_db = thermostat_database.query_db
get_info = thermostat_controller.get_info
thermostat_control = thermostat_controller

last_saved_state = None


def clear_state_change_status():
    l.debug("Clearing last state")
    global last_saved_state
    last_saved_state = None


def state_is_changed():
    state_changed_status = False
    thermostat_parameters_to_check = ['mode', 'heattemp', 'cooltemp']
    current_state = json.loads(thermostat_controller.get_info(info="info"))

    for parameter in thermostat_parameters_to_check:
        if float(current_state[parameter]) != float(last_saved_state[parameter]):
            l.warning("Current thermostat value has changed for parameter: " + parameter + '\n'
                      "Old State: " + str(last_saved_state[parameter]) + '\n'
                      "New State: " + str(current_state[parameter]))
            state_changed_status = True
    return state_changed_status


def save_current_state():
    global last_saved_state
    current_state = json.loads(thermostat_controller.get_info(info="info"))
    l.info("Saving State: " + str(current_state))
    last_saved_state = current_state
    return True
