import configparser
import sys
from os import path

# Reading config file
get = configparser.ConfigParser()
get.sections()
try:
    if path.exists(sys.argv[1]):
        get.read(sys.argv[1])
except IndexError:
    if path.exists('config.ini'):
        get.read('config.ini')
    else:
        print("No config file found")

# Global Variables
timescale_option = get['default']['timescale']
if timescale_option.upper() == 'SECOND':
    timescale = 1
elif timescale_option.upper() == 'MINUTE':
    timescale = 60
