from tabulate import tabulate
import logging, json
import config, thermostat_controller

# Setup logging
l = logging.getLogger(__name__)

def generate_status_console_html():
    status_data = get_current_status()
    html = '''\
<html>
<body>
<table>
  <tr>
    <td>Current Mode</td>
    <td>{current_mode}</td>
    <td>Cool Target</td>
    <td>{cool_target}</td>
  </tr>
  <tr>
    <td>Current Mode State</td>
    <td>{current_mode_state}</td>
    <td>Heat Target</td>
    <td>{heat_target}</td>
  </tr>
  <tr>
    <td>Current Temperature</td>
    <td>{sensor_temp}</td>
    <td>Temperature Delta</td>
    <td>{temperature_delta}</td>
  </tr>
  <tr>
    <td>Fan Setting</td>
    <td>{fan_setting}</td>
  </tr>
    <tr>
    <td>Current Fan State</td>
    <td>{current_fan_state}</td>
  </tr>
    <tr>
    <td>Away Mode</td>
    <td>{away_mode}</td>
  </tr>
</table>
</body>
</html>
    '''.format(current_mode=status_data["current_mode"],
               current_mode_state=status_data["current_mode_state"],
               fan_setting=status_data["fan_setting"],
               current_fan_state=status_data["current_fan_state"],
               away_mode=status_data["away_mode"],
               cool_target=status_data["cool_target"],
               heat_target=status_data["heat_target"],
               temperature_delta=status_data["temperature_delta"],
               sensor_temp=status_data["sensor_temp"])

    return html

def get_current_status():
    valid_modes = {
        0: "OFF",
        1: "HEAT",
        2: "COOL",
        3: "AUTO"
    }

    valid_mode_state = {
        0: "OFF",
        1: "HEATING",
        2: "COOLING",
        3: "AUTO"
    }

    valid_bools = {
        0: "OFF",
        1: "ON"
    }

    data = json.loads(thermostat_controller.get_info(info="info"))
    sensor_data = json.loads(thermostat_controller.get_info(info="sensors"))
    primary_sensor = config.get["thermostat_info"]["primary_sensor"]
    sensor_temp = "INVALID PRIMARY SENSOR"
    for sensor in sensor_data["sensors"]:
        if sensor['name'] == primary_sensor:
            sensor_temp = str(sensor["temp"]) + "°F"

    info_dict = {
        "current_mode": valid_modes[data['mode']],
        "current_mode_state": valid_mode_state[data['state']],
        "fan_setting": valid_bools[data['fan']],
        "current_fan_state": valid_bools[data['fanstate']],
        "away_mode": valid_bools[data['away']],
        "cool_target": str(data['cooltemp']) + "°F",
        "heat_target": str(data['heattemp']) + "°F",
        "temperature_delta": str(data['setpointdelta']) + "°F",
        "sensor_temp": sensor_temp
    }

    return info_dict
