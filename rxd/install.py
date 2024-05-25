
"""
[Unit]
Description=rxd
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m rxd.daemon
TimeoutStopSec=5

[Install]
WantedBy=default.target
"""
