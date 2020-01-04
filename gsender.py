#!/usr/bin/python3
import graphyte
import socket, configparser, time, logging
from subprocess import Popen, PIPE, CalledProcessError
from statistics import mean

# Initialising logging
logger = logging.getLogger('gs')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Loading configuration from file
config = configparser.ConfigParser()
config_file_path = "/etc/gsender.conf"
config.read(config_file_path)
try:
    sending_frequency = int(config['default']['frequency'])
    script_path = config['default']['script_path']
    selected_log_level = config['default']['logging_level']
    log_level = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    server_address = config['graphite']['server_address']
    port = config['graphite']['port']
except Exception as e:
    logger.critical("Problem reading config file on {}. Exception: {} ".format(config_file_path, e))

# Setting up logging
logger.setLevel(log_level[selected_log_level])
ch.setLevel(log_level[selected_log_level])

# Preparing necessary variables
hostname = socket.gethostname()

# Executing the process
logger.debug("Initialising {} as the remote graphite endpoint".format(server_address + ":" + port))
graphyte.init(server_address, port=port, prefix=hostname + ".cpu-lat", interval=sending_frequency)
popen = Popen([script_path], stdout=PIPE, universal_newlines=True)
timer = 0
bucket_values = {}
for stdout_line in iter(popen.stdout.readline, ""):
    try:
        if stdout_line.startswith('@usecs:'):
            timer = timer + 1
        elif stdout_line.startswith('['):
            line_components = stdout_line.split()
            bucket = line_components[0].strip('[],')

            if line_components[0].endswith(']'):
                value = int(line_components[1])
            else:
                value = int(line_components[2])
            
            if bucket in bucket_values:
                bucket_values[bucket].append(value)
            else:
                bucket_values[bucket] = [ value ]

            logger.debug("bucket: {} value: {}".format(bucket,value))
        else:
            if timer >= sending_frequency:
                for bucket, values in bucket_values.items():
                    graphyte.send(bucket, int(mean(values)))
                    logger.info("Sent! => bucket: {} value: {}".format(bucket,int(mean(values))))
                timer = 0
                bucket_values = {}
    except Exception as e:
        logger.error("Exception raised: {} while processing line {}".format(e, stdout_line))
    
## Wrapping up after the process ends
popen.stdout.close()
return_code = popen.wait()
if return_code:
    raise CalledProcessError(return_code, script_path)
logger.error("Process finished")
