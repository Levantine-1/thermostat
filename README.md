# thermostat

Main entry point (Basically run this to start the app)
thermostat_api_server.py

Features Completed:
- Run AC on a timer
- Run fan on intervals (Turn on fan for x minutes every x minutes)
    - Difficulty encountered here were concurrency issues. Issue solved with threading and database
- Manually Control Fan (On/Off)
- Auto deployment with Jenkins
- Web browser based logging
- Daemonize services with systemd
- Inject build information into site and link dev tools (jenkins, log, git links)
- Implement logging inheritance to submodules
- Implement configuration inheritance
- Implement test mode with sample data and time scaler
- Console window:
    - Display system status
        - Show current system status  (what it's doing now)
        - Show current temp


Features In Progress:
- Not working on anything at the moment.

Features Desired:
- AC scheduler: Allow schedule based on: 
    - Specify temperature for certain time of day over a week
    - Specify temperature response based on internal thermostat sensor temp
    - Specify temperature based on local weather from weather.gov api
    - Specify with temperature range
    
- Console window:
    - Display system status
        - Show current AC schedule
        - Show fan interval settings
    - Display system statistics
        - Show how long system has been running for given day
        - Number of times AC/Fan cycled on and off
    - While page is open, continuously update the console
        
- Expose RPI to world wide web by port forwarding:
    - SSL encryption
    - Reverse proxy for jenkins
    - Login required to change thermostat settings
    - User management