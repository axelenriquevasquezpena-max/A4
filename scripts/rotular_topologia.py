"""Apply readable IP labels to the real A4 topology through GNS3's API."""
from pathlib import Path
import json
from gns3_local import GNS3

gns3 = GNS3()
project = gns3.project()
prefix = "/projects/" + project["project_id"]
labels = {
    "R1-AXEL": "R1-AXEL / IOS 12.4\nFa0/0: 10.24.23.1/24\nFa0/1: 10.24.88.1/24",
    "KALI-ADMIN": "KALI-ADMIN\n10.24.23.10/24",
    "PC-CLIENTE": "PC-CLIENTE\n10.24.88.20/24",
    "SW-ADMIN": "SW-ADMIN",
    "SW-CLIENTES": "SW-CLIENTES",
}
for node in gns3.nodes():
    label = {"text": labels[node["name"]], "x": -40, "y": -80, "rotation": 0,
             "style": "font-family: Arial;font-size: 12.0;font-weight: bold;fill: #c9e8ff;fill-opacity: 1.0;"}
    gns3.api(prefix + "/nodes/" + node["node_id"], "PUT", {"label": label})
if not gns3.api(prefix + "/drawings"):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="110">'
           '<rect width="1060" height="110" fill="#15344d"/>'
           '<text x="20" y="35" font-family="Arial" font-size="22" fill="#ffffff">'
           'A4 - CIS IOS 12 - Axel Enrique Vasquez Pena - 2024-2388</text>'
           '<text x="20" y="70" font-family="Arial" font-size="18" fill="#ffffff">'
           'Administracion SSHv2 / Telnet desactivado / Sesiones limitadas / AUX y CDP desactivados</text>'
           '<text x="20" y="95" font-family="Arial" font-size="16" fill="#ffffff">'
           'ADMIN 10.24.23.0/24  --  R1  --  CLIENTES 10.24.88.0/24</text></svg>')
    gns3.api(prefix + "/drawings", "POST", {"x": -500, "y": -260, "z": 0, "svg": svg})
print("Topology labels updated through GNS3 API")
