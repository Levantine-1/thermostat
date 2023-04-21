import logging
import threading

import config
import state_manager
import thermostat_controller

# Setup logging
l = logging.getLogger(__name__)

# Alias setup
l.info("Configuring Aliases")
get_info = thermostat_controller.get_info
thermostat_control = thermostat_controller.thermostat_control

lock = threading.Lock()
current_thread_stop_event = threading.Event()
preserve_state = False
thread_running = False


def stop_ac():
    global current_thread_stop_event
    current_thread_stop_event.set()
    state_manager.clear_state_change_status()  # Because we grab the last value


def ac_threads(cycle_time, temperature):
    t1 = threading.Thread(target=ac_timer_thread, args=(cycle_time, temperature))
    t1.start()


def ac_timer_thread(cycle_time, temperature):
    global thread_running
    thread_running = True
    global preserve_state

    lock_acquired = lock.acquire(blocking=False)  # We don't block here, so we can run a bit of logic first.
    if not lock_acquired:
        l.warning("Could not acquire lock. Skipping AC timer thread.")
        return

    if preserve_state is False:
        state_manager.save_current_state()
    elif preserve_state is True:
        l.info("State is preserved for this iteration. Resetting for next iteration")
        preserve_state = False

    l.info("Setting Thermostat to " + str(temperature) + "F for " + str(cycle_time) + " minutes")
    thermostat_control(mode='2', heat_temp='60', cool_temp=temperature)
    remaining_time = int(cycle_time) * int(config.timescale)

    while not current_thread_stop_event.is_set():  # Instead of a time.sleep, we check for stop event signal on interval
        current_thread_stop_event.wait(1)
        if current_thread_stop_event.is_set():
            l.info("Kill signal received")
            break

        l.debug("Remaining Time: " + str(remaining_time))
        if remaining_time < 1:
            if state_manager.state_is_changed() is False:
                l.info("Resetting thermostat to previous settings")
                previous_mode = state_manager.last_saved_state['mode']
                previous_heat_temp = state_manager.last_saved_state['heattemp']
                previous_cool_temp = state_manager.last_saved_state['cooltemp']
                thermostat_control(mode=previous_mode, heat_temp=previous_heat_temp, cool_temp=previous_cool_temp)
            elif state_manager.state_is_changed() is True:
                l.warning("Thermostat Settings have been changed, not going to reset it.")
            break
        remaining_time = remaining_time - 1

    if current_thread_stop_event.is_set():
        preserve_state = True
        l.warning("We probably received multiple update requests, going to preserve the original settings")
    current_thread_stop_event.clear()
    thread_running = False
    lock.release()
