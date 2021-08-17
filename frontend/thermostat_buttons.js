function submitRunAC_Timer() {
    const cycle_time = document.querySelector('#ttr').value;
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
    if(this.readyState === 4) {
        console.log(this.responseText);
        }
    });

    xhr.open("POST", "/thermostat/cmd?action=set_ac_timer&cycle_time=" + cycle_time );
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
}


function submit_AC_off() {
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
    if(this.readyState === 4) {
        console.log(this.responseText);
        }
    });

    xhr.open("POST", "/thermostat/cmd?action=acOFF");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
}


function set_fan_cycle() {
    const cycle_time = document.querySelector('#fan_cycle_time').value;
    const interval = document.querySelector('#fan_cycle_interval').value;
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
    if(this.readyState === 4) {
        console.log(this.responseText);
        }
    });

    xhr.open("POST", "/thermostat/cmd?action=set_fan_state&action_type=scheduled&action_state=" + cycle_time + "," + interval);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
}


function turn_fanON() {
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
    if(this.readyState === 4) {
        console.log(this.responseText);
        }
    });

    xhr.open("POST", "/thermostat/cmd?action=set_fan_state&action_type=simple&action_state=1");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
}


function turn_fanOFF() {
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.addEventListener("readystatechange", function() {
    if(this.readyState === 4) {
        console.log(this.responseText);
        }
    });

    xhr.open("POST", "/thermostat/cmd?action=set_fan_state&action_type=simple&action_state=0");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
}

function get_console_data(){
    var xhr = typeof XMLHttpRequest != 'undefined' ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
    xhr.open('GET', '/thermostat/console_data', true);
    xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
        document.getElementById("console_window").innerHTML = xhr.responseText;
        }
    }
    xhr.send();
}