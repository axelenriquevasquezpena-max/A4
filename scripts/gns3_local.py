"""Local GNS3 API client; credentials stay in the Windows GNS3 config."""
import base64
import configparser
import json
from pathlib import Path
import urllib.request


class GNS3:
    def __init__(self):
        config = configparser.ConfigParser(interpolation=None)
        config.read(Path.home() / "AppData/Roaming/GNS3/2.2/gns3_server.ini")
        self.config = config
        server = config["Server"]
        self.base = f"http://localhost:{server.get('port', '3080')}/v2"
        self.headers = {"Content-Type": "application/json"}
        if server.getboolean("auth", fallback=False):
            token = base64.b64encode(f"{server['user']}:{server['password']}".encode()).decode()
            self.headers["Authorization"] = "Basic " + token

    def api(self, path, method="GET", body=None, raw=False):
        request = urllib.request.Request(self.base + path, method=method, headers=self.headers,
                                         data=json.dumps(body).encode() if body is not None else None)
        with urllib.request.urlopen(request, timeout=180) as response:
            data = response.read()
            return data if raw else (json.loads(data) if data else None)

    def project(self):
        projects = [p for p in self.api("/projects") if p["name"] == "A4-CIS-2024-2388"]
        if len(projects) != 1:
            raise RuntimeError("Expected exactly one A4 project")
        return projects[0]

    def nodes(self):
        return self.api("/projects/" + self.project()["project_id"] + "/nodes")


if __name__ == "__main__":
    client = GNS3()
    print(json.dumps([{k: n.get(k) for k in ("name", "node_id", "status", "console", "console_host", "compute_id")}
                      for n in client.nodes()], indent=2))
