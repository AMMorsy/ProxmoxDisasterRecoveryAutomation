import os
import requests

PVE_BASE = os.getenv("PVE_URL", "").rstrip("/") + "/api2/json"
PVE_USER = os.getenv("PVE_USER", "")
PVE_PASS = os.getenv("PVE_PASS", "")

class ProxmoxAPI:
    def __init__(self, verify_ssl: bool = False):
        self.session = requests.Session()
        self.verify = verify_ssl
        self._login()

    def _login(self):
        r = self.session.post(
            f"{PVE_BASE}/access/ticket",
            data={"username": PVE_USER, "password": PVE_PASS},
            verify=self.verify,
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()["data"]
        self.session.headers.update({"CSRFPreventionToken": data["CSRFPreventionToken"]})
        self.session.cookies.set("PVEAuthCookie", data["ticket"])

    def list_vms(self, node: str):
        r = self.session.get(f"{PVE_BASE}/nodes/{node}/qemu", verify=self.verify, timeout=30)
        r.raise_for_status()
        return r.json()["data"]

    def list_backups_pve(self, node: str, storage: str, vmid: int):
        r = self.session.get(
            f"{PVE_BASE}/nodes/{node}/storage/{storage}/content",
            params={"content": "backup"},
            verify=self.verify,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["data"]

    def restore_vm(self, node: str, archive_volid: str, storage: str, new_vmid: int):
        """
        Correct PVE endpoint: POST /nodes/{node}/qemu/restore
        Required params: vmid, archive; Optional: storage, force
        """
        payload = {
            "vmid": new_vmid,
            "archive": archive_volid,   # e.g. 'lv1:backup/vzdump-qemu-206-.....vma.zst'
            "storage": storage,
            "force": 1,
        }
        r = self.session.post(
            f"{PVE_BASE}/nodes/{node}/qemu/restore",
            data=payload,
            verify=self.verify,
            timeout=600,
        )
        r.raise_for_status()
        return r.json()
