from django.contrib import admin
from .models import VirtualMachine, RestoreJob

@admin.register(VirtualMachine)
class VMAdmin(admin.ModelAdmin):
    list_display = ("vmid", "name", "owner", "node")
    search_fields = ("vmid", "name", "owner__username", "node")

@admin.register(RestoreJob)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "vm", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "vm__vmid", "user__username", "backup_id")
