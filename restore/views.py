import os
from django.shortcuts import get_object_or_404
from .models import VirtualMachine, RestoreJob
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .tasks import perform_restore, perform_backup
from django.shortcuts import get_object_or_404

def _get_owned_vm(request, vmid: int):
    # Only return a VM if it is owned by the current user, else 404
    return get_object_or_404(VirtualMachine, vmid=vmid, owner=request.user)

# ---- SAFE MODE gate ----
REQUIRE_DRY = os.getenv("REQUIRE_DRY_RUN", "1") == "1"

def _assert_safe_mode():
    """Block action unless DRY-RUN is enabled (or override is disabled)."""
    if not REQUIRE_DRY:
        return None
    if os.getenv("FORCE_DRY_RUN", "0") == "1":
        return None
    if os.getenv("DRY_RUN", "0") == "1":
        return None
    return Response(
        {"detail": "Blocked: SAFE MODE requires DRY_RUN=1"},
        status=status.HTTP_403_FORBIDDEN,
    )

# ---- RESTORE (POST /api/v1/vms/<vmid>/restore/) ----
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vm_restore(request, vmid: int):
    # <<< THIS is the exact place for the guard >>>
    block = _assert_safe_mode()
    if block:
        return block

    vm = _get_owned_vm(request, vmid)
    data = request.data or {}
    backup_volid = data.get("backup_volid")  # e.g. lv1:backup/vzdump-qemu-206-....vma.zst
    target_node = data.get("target_node") or vm.node
    storage = data.get("storage") or "lv1"

    if not backup_volid:
        return Response({"detail": "backup_volid required"}, status=400)

    job = RestoreJob.objects.create(
        vm=vm,
        user=request.user,
        backup_id=backup_volid,
        target_node=target_node,
        status="PENDING",
        created_at=timezone.now(),
    )
    perform_restore.delay(job.id)
    return Response({"message": "Restore queued", "job_id": job.id, "queued": True})

# ---- BACKUP (POST /api/v1/vms/<vmid>/backup/) ----
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vm_backup(request, vmid: int):
    # <<< SAME guard here >>>
    block = _assert_safe_mode()
    if block:
        return block

    vm = _get_owned_vm(request, vmid)
    job = RestoreJob.objects.create(
        vm=vm,
        user=request.user,
        backup_id="",            # not used for backup
        target_node=vm.node,
        status="PENDING",
        created_at=timezone.now(),
    )
    perform_backup.delay(job.id)
    return Response({"message": "Backup queued", "job_id": job.id, "queued": True})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vms_list(request):
    vms = VirtualMachine.objects.filter(owner=request.user).order_by("vmid")
    data = [{"vmid": v.vmid, "name": v.name, "node": v.node} for v in vms]
    return Response({"vms": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def jobs_list(request):
    """
    Returns the user's jobs with optional query params:
      ?limit=50 (default 50)
      ?status=all|pending|running|success|failed  (default: all)
    """
    limit = int(request.GET.get("limit", "50") or 50)
    status_q = (request.GET.get("status") or "all").upper()

    qs = RestoreJob.objects.filter(user=request.user).order_by("-created_at")
    if status_q in {"PENDING", "RUNNING", "SUCCESS", "FAILED"}:
        qs = qs.filter(status=status_q)
    qs = qs[:limit]

    jobs = [{
        "id": j.id, "vm": j.vm.vmid, "status": j.status,
        "created_at": j.created_at,  # ISO formatted by DRF
    } for j in qs]

    # quick counts for client
    counts = {
        "all": RestoreJob.objects.filter(user=request.user).count(),
        "pending": RestoreJob.objects.filter(user=request.user, status="PENDING").count(),
        "running": RestoreJob.objects.filter(user=request.user, status="RUNNING").count(),
        "success": RestoreJob.objects.filter(user=request.user, status="SUCCESS").count(),
        "failed": RestoreJob.objects.filter(user=request.user, status="FAILED").count(),
    }
    return Response({"jobs": jobs, "counts": counts})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_detail(request, job_id: int):
    job = get_object_or_404(RestoreJob, id=job_id, user=request.user)
    return Response({
        "id": job.id,
        "vm": job.vm.vmid,
        "status": job.status,
        "log": job.log,
        "created_at": job.created_at,
    })


RESTORE_ENABLED = os.getenv("RESTORE_ENABLED", "0") == "1"
QUEUE_ENABLED = os.getenv("QUEUE_ENABLED", "0") == "1"

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_backups(request, vmid: int):
    from proxmox.api import ProxmoxAPI
    vm = get_object_or_404(VirtualMachine, vmid=vmid, owner=request.user)
    storage = request.query_params.get("storage", "local")
    prox = ProxmoxAPI(verify_ssl=False)
    try:
        items = prox.list_backups_pve(node=vm.node, storage=storage, vmid=vm.vmid)
        return Response({"vm": vm.vmid, "node": vm.node, "storage": storage, "backups": items})
    except Exception as e:
        return Response({"detail": f"{type(e).__name__}: {e}"}, status=502)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_restore(request, vmid: int):
    if not RESTORE_ENABLED:
        return Response({"detail": "Restore is disabled by policy (RESTORE_ENABLED=0)."}, status=403)

    vm = get_object_or_404(VirtualMachine, vmid=vmid, owner=request.user)
    archive_volid = request.data.get("backup_volid")
    target_node = request.data.get("target_node", vm.node)
    storage = request.data.get("storage", "local")
    if not archive_volid:
        return Response({"detail": "backup_volid is required (the 'volid' from list_backups)."}, status=400)

    job = RestoreJob.objects.create(
        vm=vm, user=request.user, backup_id=archive_volid, target_node=target_node
    )

    # Only enqueue if QUEUE_ENABLED=1 (Redis/Celery running). Otherwise, DB-only.
    if QUEUE_ENABLED:
        from .tasks import perform_restore
        perform_restore.delay(job.id)  # will require Redis
        return Response({"message": "Restore queued", "job_id": job.id, "queued": True})

    return Response({"message": "Job created (queue disabled)", "job_id": job.id, "queued": False})
