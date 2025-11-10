from django.urls import path
from . import views

app_name = "frontend"

urlpatterns = [
    path("", views.home, name="home"),
    path("vms/", views.my_vms, name="my_vms"),
    path("vms/<int:vmid>/", views.vm_detail, name="vm_detail"),
    path("jobs/", views.jobs, name="jobs"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
