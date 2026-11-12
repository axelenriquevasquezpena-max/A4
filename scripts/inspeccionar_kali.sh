#!/bin/bash
# Read-only guest inventory, saved locally for provisioning diagnostics.
exec > /tmp/a4-inspeccion.txt 2>&1
date -Is
id
ip -br address
ip route
nmcli -t -f NAME,UUID,DEVICE connection show
command -v nmap python3 pip3
python3 -c 'import netmiko; print("Netmiko", netmiko.__version__)'
python3 -m venv --help >/dev/null && echo VENV_DISPONIBLE
