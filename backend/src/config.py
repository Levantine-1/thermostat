from os import path
import configparser, sys

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