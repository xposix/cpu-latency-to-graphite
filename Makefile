all: install

install-requirements:
	pip3 install -r requirements.txt

install-files:
	mkdir -p /opt/gsender
	cp -v cpu_latency.bt gsender.py /opt/gsender
	cp -v gsender.service /etc/systemd/system/
	cp -v gsender.conf	/etc/

install: install-requirements install-files
	systemctl daemon-reload
	systemctl start gsender.service
	systemctl enable gsender.service
