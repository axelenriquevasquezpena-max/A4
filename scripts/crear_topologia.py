"""Create the A4 topology through a local GNS3 2.2 controller (Windows).

Uses existing local controller credentials without printing or exporting them.
Does not configure guests or start virtual machines.
"""
import base64
import configparser
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NAME = "A4-CIS-2024-2388"


def main():
    config = configparser.ConfigParser(interpolation=None)
    config.read(Path.home() / "AppData/Roaming/GNS3/2.2/gns3_server.ini")
    server = config["Server"]
    base = f"http://localhost:{server.get('port', '3080')}/v2"
    headers = {"Content-Type": "application/json"}
    if server.getboolean("auth", fallback=False):
        token = base64.b64encode(f"{server['user']}:{server['password']}".encode()).decode()
        headers["Authorization"] = "Basic " + token

    def api(path, method="GET", body=None):
        request = urllib.request.Request(base + path, method=method, headers=headers,
                                         data=json.dumps(body).encode() if body is not None else None)
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
            return json.loads(data) if data else None

    templates = {t["name"]: t for t in api("/templates")}
    for name in ("c2691", "Kali Linux"):
        if name not in templates:
            raise RuntimeError(f"Falta plantilla {name}")
    existing = [p for p in api("/projects") if p["name"] == NAME]
    if len(existing) > 1:
        raise RuntimeError("Hay varios proyectos con ese nombre; revisar en GNS3")
    project = existing[0] if existing else api("/projects", "POST", {"name": NAME})
    prefix = "/projects/" + project["project_id"]
    if project.get("status") != "opened":
        api(prefix + "/open", "POST")
    nodes = {n["name"]: n for n in api(prefix + "/nodes")}

    def template_node(name, template, x, y):
        if name not in nodes:
            nodes[name] = api(prefix + "/templates/" + templates[template]["template_id"], "POST",
                              {"x": x, "y": y, "name": name})
        return nodes[name]

    def basic_node(name, node_type, x, y):
        if name not in nodes:
            nodes[name] = api(prefix + "/nodes", "POST", {
                "name": name, "node_type": node_type, "compute_id": "local", "x": x, "y": y,
                "symbol": ":/symbols/ethernet_switch.svg" if node_type == "ethernet_switch" else ":/symbols/vpcs_guest.svg"})
        return nodes[name]

    template_node("R1-AXEL", "c2691", 0, 0)
    kali = template_node("KALI-ADMIN", "Kali Linux", -450, 0)
    # Isolate the new project's disk state from the existing Kali VM.
    if kali["status"] == "stopped" and not kali["properties"].get("linked_clone"):
        nodes["KALI-ADMIN"] = api(prefix + "/nodes/" + kali["node_id"], "PUT",
                                  {"properties": {"linked_clone": True}})
    basic_node("SW-ADMIN", "ethernet_switch", -225, 0)
    basic_node("SW-CLIENTES", "ethernet_switch", 225, 0)
    basic_node("PC-CLIENTE", "vpcs", 450, 0)
    links = api(prefix + "/links")
    occupied = {frozenset((e["node_id"], e["adapter_number"], e["port_number"]) for e in link["nodes"])
                for link in links}
    connections = [
        (("KALI-ADMIN", 0, 0), ("SW-ADMIN", 0, 0)),
        (("SW-ADMIN", 0, 1), ("R1-AXEL", 0, 0)),
        (("R1-AXEL", 0, 1), ("SW-CLIENTES", 0, 0)),
        (("SW-CLIENTES", 0, 1), ("PC-CLIENTE", 0, 0)),
    ]
    for endpoints in connections:
        ends = [{"node_id": nodes[name]["node_id"], "adapter_number": adapter, "port_number": port}
                for name, adapter, port in endpoints]
        key = frozenset((e["node_id"], e["adapter_number"], e["port_number"]) for e in ends)
        if key not in occupied:
            api(prefix + "/links", "POST", {"nodes": ends})

    if not api(prefix + "/drawings"):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="145">'
               '<rect width="1100" height="145" rx="12" fill="#152a43"/>'
               '<g fill="white" font-family="Arial" font-size="20">'
               '<text x="20" y="35">A4 · CIS IOS 12 · Axel Enrique Vasquez Pena · 2024-2388</text>'
               '<text x="20" y="70">ADMIN: Kali 10.24.23.10/24 — R1 Fa0/0 10.24.23.1/24</text>'
               '<text x="20" y="100">CLIENTES: R1 Fa0/1 10.24.88.1/24 — VPCS 10.24.88.20/24</text>'
               '<text x="20" y="130">Objetivo: SSHv2, sin Telnet, timeout, AUX/CDP desactivados</text>'
               '</g></svg>')
        api(prefix + "/drawings", "POST", {"x": -500, "y": -225, "z": 0, "svg": svg})

    details = api(prefix)
    source = Path(details["path"]) / f"{NAME}.gns3"
    target = ROOT / "gns3" / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    topology = json.loads(source.read_text(encoding="utf-8"))
    # Export only topology; no images, disks, controller credentials or lab secrets.
    target.write_text(json.dumps(topology, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    final_nodes = api(prefix + "/nodes")
    final_links = api(prefix + "/links")
    print(json.dumps({"project": NAME, "project_id": project["project_id"], "file": str(source),
                      "repository_copy": str(target), "nodes": len(final_nodes), "links": len(final_links),
                      "state": "Topologia creada; configuracion de invitados y pruebas pendientes"}, indent=2))


if __name__ == "__main__":
    main()
