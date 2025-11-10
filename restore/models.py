from django.db import models
from django.contrib.auth.models import User

class VirtualMachine(models.Model):
    vmid = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    node = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vmid} - {self.name}"

class RestoreJob(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    backup_id = models.CharField(max_length=255)
    target_node = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    log = models.TextField(blank=True)

    def __str__(self):
        return f"Job #{self.id} for VM {self.vm.vmid} [{self.status}]"
