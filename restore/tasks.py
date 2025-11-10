import os
from celery import shared_task
from django.db import transaction
from .models import RestoreJob
from proxmox.api import ProxmoxAPI

# Safety flags
FORCE_DRY_RUN = os.getenv("FORCE_DRY_RUN", "0") == "1"
DRY_RUN = True if FORCE_DRY_RUN else (os.getenv("DRY_RUN", "1") == "1")
ALLOW_VMIDS = {int(v.strip()) for v in os.getenv("ALLOW_VMIDS", "").split(",") if v.strip()}

def _blocked(job):
    if ALLOW_VMIDS and job.vm.vmid not in ALLOW_VMIDS:
        job.status = "FAILED"
        job.log = f"Blocked: VMID {job.vm.vmid} not in ALLOW_VMIDS={sorted(list(ALLOW_VMIDS))}"
        job.save()
        return True
    return False

@shared_task
def perform_restore(job_id: int):
    job = RestoreJob.objects.select_related("vm", "user").get(id=job_id)
    if _blocked(job):
        return

    with transaction.atomic():
        if job.status not in ("PENDING", "FAILED"):
            return
        job.status = "RUNNING"
        job.save()

    try:
        if DRY_RUN:
            job.log = (
                "DRY_RUN=1 — would call PVE restore with:\n"
                f" node={job.target_node}\n"
                f" archive_volid={job.backup_id}\n"
                f" storage=lv1\n"
                f" vmid={job.vm.vmid}\n"
            )
            job.status = "SUCCESS"
        else:
            prox = ProxmoxAPI(verify_ssl=False)
            result = prox.restore_vm(
                node=job.target_node,
                archive_volid=job.backup_id,
                storage="lv1",
                new_vmid=job.vm.vmid,   # in-place intended; you can change to temp here if needed
            )
            job.log = str(result)
            job.status = "SUCCESS"

    except Exception as e:
        job.status = "FAILED"
        job.log = f"{type(e).__name__}: {e}"
    job.save()

@shared_task
def perform_backup(job_id: int):
    """
    Uses the same RestoreJob row just to keep a single Jobs list.
    In DRY_RUN it only logs intent. In real mode you'd call Proxmox vzdump.
    """
    job = RestoreJob.objects.select_related("vm", "user").get(id=job_id)
    if _blocked(job):
        return

    with transaction.atomic():
        if job.status not in ("PENDING", "FAILED"):
            return
        job.status = "RUNNING"
        job.save()

    try:
        if DRY_RUN:
            job.log = (
                "DRY_RUN=1 — would call PVE backup (vzdump) with:\n"
                f" node={job.target_node}\n"
                f" vmid={job.vm.vmid}\n"
                f" storage=lv1  mode=snapshot  compress=zstd\n"
            )
            job.status = "SUCCESS"
        else:
            # Real backup example (uncomment/implement when you go live)
            # prox = ProxmoxAPI(verify_ssl=False)
            # result = prox.backup_vm(node=job.target_node, vmid=job.vm.vmid, storage="lv1")
            # job.log = str(result)
            # job.status = "SUCCESS"
            raise NotImplementedError("Live backup not implemented in this build.")
    except Exception as e:
        job.status = "FAILED"
        job.log = f"{type(e).__name__}: {e}"
    job.save()
