import time, logging, json, schedule, threading
import thermostat_database, thermostat_controller, config

# Setup logging
l = logging.getLogger(__name__)

query_db = thermostat_database.query_db
get_info = thermostat_controller.get_info
thermostat_control = thermostat_controller.thermostat_control


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
    cycle_time = int(cycle_time) * config.timescale
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