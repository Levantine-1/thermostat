import requests, logging, random
import config

# Setup logging
l = logging.getLogger(__name__)

# Global Vars
thermostat_host = config.get['thermostat_info']['thermostat_host']

def thermostat_control(mode, fan, heat_temp, cool_temp):
    url = "http://" + thermostat_host + "/control"
    parameters = {'mode': int(mode),
                  'fan': int(fan),
                  'heattemp': int(heat_temp),
                  'cooltemp': int(cool_temp),
                  }
    payload = {}
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    if config.get['test_mode']['test_mode'].upper() == 'TRUE':
        response = requests.Request("POST", url, headers=headers, data=payload, params=parameters)
        prepared = response.prepare()
        method = str(prepared.method)
        url = str(prepared.url)
        headers = str(prepared.headers)
        string = "Method: " + method + " Headers: " + headers + " URL: " + url
        l.info(str(string))
        return string, 200
    else:
        response = requests.request("POST", url, headers=headers, data=payload, params=parameters)
        l.info("Setting Thermostat with: " + response.request.url)
        l.info("Thermostat request sent")
        return response.text
        # return "Request sent", 200


def get_info(info): # info could be 'sensors', 'runtimes', 'info'
    valid_info_pages = ['sensors', 'runtimes', 'info']
    if info not in valid_info_pages:
        return "Invalid status_page: '" + info + "' - Valid status_page values are 'sensors', 'runtimes', 'info'", 400

    if config.get['test_mode']['test_mode'].upper() == 'TRUE':
        if config.get['test_mode']['test_mode_use_sample_data'].upper() == 'TRUE':
            return return_sample_info(info=info)

    l.info("Querying thermostat for live data")
    url = "http://" + thermostat_host + "/query/" + info
    payload = {}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # No need to set test mode for getting info because it's read only and other processes need this to work.
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


def return_sample_info(info):
    l.info("Querying sample thermostat data")
    sample_sensors_data = ['{"sensors":[{"name":"Thermostat","temp":68.0},{"name":"Outdoor","temp":0.0}]}',
                           '{"sensors":[{"name":"Thermostat","temp":72.0},{"name":"Outdoor","temp":68.0}]}',
                           '{"sensors":[{"name":"Thermostat","temp":78.0},{"name":"Outdoor","temp":80.0}]}',
                           '{"sensors":[{"name":"Thermostat","temp":80.0},{"name":"Outdoor","temp":95.0}]}',
                           '{"sensors":[{"name":"Thermostat","temp":85.0},{"name":"Outdoor","temp":105.0}]}'
                           ]
    sample_runtimes_data = ['{"runtimes":[{"ts":1627689600,"heat1":0,"heat2":0,"cool1":144,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627776000,"heat1":0,"heat2":0,"cool1":131,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627862400,"heat1":0,"heat2":0,"cool1":159,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627948800,"heat1":0,"heat2":0,"cool1":36,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628035200,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628121600,"heat1":0,"heat2":0,"cool1":1,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628202278,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0}]}',
                            '{"runtimes":[{"ts":1627689600,"heat1":0,"heat2":0,"cool1":144,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627776000,"heat1":0,"heat2":0,"cool1":131,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627862400,"heat1":0,"heat2":0,"cool1":159,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627948800,"heat1":0,"heat2":0,"cool1":36,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628035200,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628121600,"heat1":0,"heat2":0,"cool1":1,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628202278,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0}]}',
                            '{"runtimes":[{"ts":1627689600,"heat1":0,"heat2":0,"cool1":144,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627776000,"heat1":0,"heat2":0,"cool1":131,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627862400,"heat1":0,"heat2":0,"cool1":159,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627948800,"heat1":0,"heat2":0,"cool1":36,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628035200,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628121600,"heat1":0,"heat2":0,"cool1":1,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628202278,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0}]}',
                            '{"runtimes":[{"ts":1627689600,"heat1":0,"heat2":0,"cool1":144,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627776000,"heat1":0,"heat2":0,"cool1":131,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627862400,"heat1":0,"heat2":0,"cool1":159,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627948800,"heat1":0,"heat2":0,"cool1":36,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628035200,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628121600,"heat1":0,"heat2":0,"cool1":1,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628202278,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0}]}',
                            '{"runtimes":[{"ts":1627689600,"heat1":0,"heat2":0,"cool1":144,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627776000,"heat1":0,"heat2":0,"cool1":131,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627862400,"heat1":0,"heat2":0,"cool1":159,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1627948800,"heat1":0,"heat2":0,"cool1":36,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628035200,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628121600,"heat1":0,"heat2":0,"cool1":1,"cool2":0,"aux1":0,"aux2":0,"fc":0},{"ts":1628202278,"heat1":0,"heat2":0,"cool1":35,"cool2":0,"aux1":0,"aux2":0,"fc":0}]}'
                            ]
    sample_info_data = ['{"name":"LIVING%20ROOM","mode":0,"state":0,"fan":0,"fanstate":0,"tempunits":0,"schedule":0,"schedulepart":255,"away":0,"spacetemp":81.0,"heattemp":60.0,"cooltemp":85.0,"cooltempmin":35.0,"cooltempmax":99.0,"heattempmin":35.00,"heattempmax":99.0,"setpointdelta":1.0,"availablemodes":0}',
                        '{"name":"LIVING%20ROOM","mode":0,"state":0,"fan":1,"fanstate":1,"tempunits":0,"schedule":0,"schedulepart":255,"away":0,"spacetemp":81.0,"heattemp":60.0,"cooltemp":85.0,"cooltempmin":35.0,"cooltempmax":99.0,"heattempmin":35.00,"heattempmax":99.0,"setpointdelta":1.0,"availablemodes":0}',
                        '{"name":"LIVING%20ROOM","mode":3,"state":0,"fan":0,"fanstate":1,"tempunits":0,"schedule":0,"schedulepart":255,"away":0,"spacetemp":81.0,"heattemp":60.0,"cooltemp":68.0,"cooltempmin":35.0,"cooltempmax":99.0,"heattempmin":35.00,"heattempmax":99.0,"setpointdelta":1.0,"availablemodes":0}',
                        '{"name":"LIVING%20ROOM","mode":2,"state":0,"fan":0,"fanstate":1,"tempunits":0,"schedule":0,"schedulepart":255,"away":0,"spacetemp":81.0,"heattemp":74.0,"cooltemp":85.0,"cooltempmin":35.0,"cooltempmax":99.0,"heattempmin":35.00,"heattempmax":99.0,"setpointdelta":1.0,"availablemodes":0}',
                        '{"name":"LIVING%20ROOM","mode":1,"state":0,"fan":0,"fanstate":0,"tempunits":0,"schedule":0,"schedulepart":255,"away":0,"spacetemp":81.0,"heattemp":72.0,"cooltemp":78.0,"cooltempmin":35.0,"cooltempmax":99.0,"heattempmin":35.00,"heattempmax":99.0,"setpointdelta":1.0,"availablemodes":0}']

    if config.get['test_mode']['test_mode_sample_data_custom_index'].upper() == 'FALSE':
        index = random.randint(0, 4)
    else:
        index = int(config.get['test_mode']['test_mode_sample_data_custom_index'])

    if info == 'sensors':
        return sample_sensors_data[index]
    elif info == 'runtimes':
        return sample_runtimes_data[index]
    elif info == 'info':
        return sample_info_data[index]
    else:
        l.exception("Index Error")
        return IndexError
