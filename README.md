# Graphite Sender - Metrics script
This repo contains my solution for the challenge described during the FA interview process.

I have written a wrapper around the provided script `cpu_latency.bt` using **Python 3**. It extracts the script's output and sends a rounded average(mean) of the accumulated metric values to Graphite.

## How to deploy it through CM tools
There are two suggested approaches to deploy the script using Change Management tools. Regardless what option has been chosen, the configuration process, described below, is common.

### Using Git (Provided approach)
The solution is currently stored on one of my public git repositories. I would recommend uploading it to your preferred Git solution. The instructions below need to be amended if so.

The preferred Change Management tool needs to execute the following commands:

```bash
git clone https://github.com/xposix/cpu-latency-to-graphite.git
cd cpu-latency-to-graphite
make install
```

That process will deploy the following files:

* The provided script at `/opt/gsender/cpu_latency.bt`
* My wrapper at `/opt/gsender/gsender.py`
* The SystemD service file at `/etc/systemd/system/gsender.service`
* The configuration of the service at `/etc/gsender.conf`. See 'Configuration' section below for more details.

#### Pros
* Deploying new changes is easy, no need for additional steps.

#### Cons
* Versioning could be confusing.

### Using .deb/.rpm package (Not provided, but recommended)
Most of the software deployed on an instance is done through the OS packaging system, that is why I think that the most professional solution is to use the same format.

I recommend using the same file locations described above for the .deb/.rpm package installation targets.

#### Pros
* Using packages allows better control over the version it's being deployed.
* The deployment of the solution is streamlined with the deployment/updates of the OS.

#### Cons
* More complex: a new .deb / .rpm package needs to be created for every change. For this step, CI pipelines are recommended.

### Configuration
The solution relies on a configuration file to set few required parameters.
The example below is provided on the repository. It is configured to send the metrics to Graphite every 15 seconds. This Graphite service should be installed in the localhost and serving through the default port 2003.

```ini
[default]
frequency       = 15
script_path     = /opt/gsender/cpu_latency.bt
# One of the following: DEBUG, INFO, WARNING, ERROR or CRITICAL
logging_level   = INFO


[graphite]
server_address  = localhost
port            = 2003
```

The script/service needs to be **restarted every time this file changes.** 

## How to run the script
Alternatively, the script can be manually run directly from the same directory where the repository has been cloned by typing:

```bash
python3 gsender.py
```
To stop the script, we just need to press Control+C.
