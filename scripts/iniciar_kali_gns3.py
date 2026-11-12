"""Start the existing Kali node and its GNS3 network bridge."""
import urllib.error
from gns3_local import GNS3

client = GNS3()
project = client.project()
node = next(n for n in client.nodes() if n["name"] == "KALI-ADMIN")
try:
    client.api(f"/projects/{project['project_id']}/nodes/{node['node_id']}/start", "POST")
except urllib.error.HTTPError as error:
    raise SystemExit(error.read().decode())
node = next(n for n in client.nodes() if n["name"] == "KALI-ADMIN")
print("KALI-ADMIN:", node["status"])
