import sys

systemd_service = \
f"""
# save this into /etc/systemd/system/rxd.service
[Unit]
Description=rxd
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/screen -dmS rxd {sys.executable} -m rxd.daemon
TimeoutStopSec=5

[Install]
WantedBy=default.target
"""

if __name__ == "__main__":
    print(systemd_service)
