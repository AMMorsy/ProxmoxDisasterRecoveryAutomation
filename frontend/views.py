from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("frontend:my_vms")
        return render(request, "frontend/login.html", {"error": "Invalid credentials"})
    return render(request, "frontend/login.html")

def logout_view(request):
    logout(request)
    return redirect("frontend:login")

@login_required
def home(request):
    return redirect("frontend:my_vms")

@login_required
def my_vms(request):
    # page will call API via JS to list VMs owned by user
    return render(request, "frontend/my_vms.html")

@login_required
def vm_detail(request, vmid):
    return render(request, "frontend/vm_detail.html", {"vmid": vmid})

@login_required
def jobs(request):
    return render(request, "frontend/jobs.html")
