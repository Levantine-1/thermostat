server {
        location /thermostat/cmd/ {
                proxy_pass http://localhost:5000/thermostat/cmd/;
        }

        location /thermostat/status/ {
                proxy_pass http://localhost:5000/thermostat/status/;
        }
}