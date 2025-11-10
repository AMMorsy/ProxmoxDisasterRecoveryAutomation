"""
URL configuration for dr_automation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from restore.views import list_backups, trigger_restore
from restore.views import vms_list, jobs_list, job_detail
from frontend import views as fviews
from django.urls import include
from restore.views import vms_list, jobs_list, job_detail, vm_backup

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/vms/<int:vmid>/backups/", list_backups),
    path("api/v1/vms/<int:vmid>/restore/", trigger_restore),
    path("", include("frontend.urls")),
    # helper API endpoints used by the frontend:
    path("api/v1/vms_list/", vms_list),
    path("api/v1/jobs_list/", jobs_list),
    path("api/v1/jobs/<int:job_id>/", job_detail),
    path("api/v1/vms/<int:vmid>/backup/", vm_backup), 
]
