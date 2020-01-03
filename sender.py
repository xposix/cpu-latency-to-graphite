# import graphyte
import socket
import time
from subprocess import Popen, PIPE, CalledProcessError

# Preparing necessary variables
hostname = socket.gethostname()
sending_frequency = 15 # in seconds
# Executing the process
#graphyte.init('localhost', prefix=hostname + ".cpu-lat.", interval=10)
popen = Popen(['./cpu_latency'], stdout=PIPE, universal_newlines=True)
timer = 0
bucket_values = {}
for stdout_line in iter(popen.stdout.readline, ""):
    try:
        if stdout_line.startswith('@usecs:'):
            timer = timer + 1
        elif stdout_line.startswith('['):
            line_components = stdout_line.split()
            bucket = line_components[0].strip('[,')

            if line_components.endswith[0](']'):
                value = line_components.endswith[1]
            else:
                value = line_components.endswith[2]
            
            if bucket in bucket_values:
                bucket_values[bucket].add(value)
            else:
                bucket_values[bucket] = [ value ]

            print("bucket: {} value: {}".format(bucket,value))
        else:
            # <key>\s<value>\s<timestamp>\n
            # "​<hostname>.cpu-lat.<bucket>​"
            # timestamp = int(time.time())
            if timer >= sending_frequency:
                for bucket in bucket_values:
                    # graphyte.send(bucket, value)
                    print("Max => bucket: {} value: {}".format(bucket,value))
                timer = 0
    except Exception as e:
        print("Exception raised: {} on line {}".format(e, stdout_line))
    
## Wrapping up after the process ends
popen.stdout.close()
return_code = popen.wait()
if return_code:
    raise CalledProcessError(return_code, './cpu_latency')


# ========
# >>> print('We are the {} who say "{}!"'.format('knights', 'Ni'))
# We are the knights who say "Ni!"

# @usecs:
# [1]                    2 |@@@@@@@@@@                                          |
# [2, 4)                 4 |@@@@@@@@@@@@@@@@@@@@                                |
# [4, 8)                 2 |@@@@@@@@@@                                          |
# [8, 16)                4 |@@@@@@@@@@@@@@@@@@@@                                |
# [16, 32)              10 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
# [32, 64)               9 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      |
# [64, 128)              2 |@@@@@@@@@@                                          |

# @usecs:
# [16, 32)               6 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                     |
# [32, 64)              10 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
# [64, 128)              2 |@@@@@@@@@@                                          |

# @usecs:
# [16, 32)               5 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@                        |
# [32, 64)               9 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
# [64, 128)              4 |@@@@@@@@@@@@@@@@@@@@@@@                             |

# @usecs:
# [0]                    1 |@@@@                                                |
# [1]                    1 |@@@@                                                |
# [2, 4)                 4 |@@@@@@@@@@@@@@@@@@                                  |
# [4, 8)                 4 |@@@@@@@@@@@@@@@@@@                                  |
# [8, 16)               11 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
# [16, 32)               9 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@          |
# [32, 64)               6 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@                        |
# [64, 128)              1 |@@@@                                                |
# [128, 256)             0 |                                                    |
# [256, 512)             1 |@@@@                                                |