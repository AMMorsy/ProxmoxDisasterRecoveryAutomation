# Proxmox Disaster Recovery Automation

A lightweight Django-based dashboard that automates **backup** and **restore** operations for Proxmox VE environments.  
Built with a focus on safety, transparency, and controlled automation — supporting **DRY-RUN mode**, **Celery job queue**, and **per-user VM ownership**.

---

## 🌍 Overview

This system provides a simple web interface and API to:
- View all VMs owned by the logged-in user.
- Trigger **Backup** and **Restore (DRY-RUN)** operations safely.
- Monitor job progress and logs with auto-refresh.
- Enforce ownership (RBAC) and isolation for each user.
- Operate in **Safe Mode (DRY-RUN)** to guarantee no real change to Proxmox until explicitly disabled.

It is designed as a foundation for full Disaster Recovery automation — ready to extend toward true PBS-based live restore or cross-node failover orchestration.

---

## ⚙️ Features

| Feature | Description |
|----------|-------------|
| **Web Dashboard** | Simple Django frontend for users to trigger backups/restores. |
| **DRY-RUN Safe Mode** | Ensures no real operations are sent to Proxmox (used for testing or demo). |
| **Celery + Redis Engine** | Handles queued jobs asynchronously and logs each step. |
| **Per-User RBAC** | Each user sees and acts only on their own VMs and jobs. |
| **Job Monitoring** | Auto-refresh list with live job counts and full log view. |
| **Environment-based Security Flags** | `.env` toggles to enforce safe/real modes, queues, or allowed VMIDs. |

---

## 🧩 Tech Stack

- **Backend:** Django 5 + Django REST Framework  
- **Worker:** Celery + Redis  
- **Frontend:** Minimal Django templates + JavaScript (fetch API)  
- **Integration:** Proxmox VE API (REST)  
- **Auth:** Django built-in users & session login  

---
## 📦 Project Structure
<details><summary><b>Click to expand full Project Structure</b></summary>
<br>
<pre>
ProxmoxDisasterRecoveryAutomation/
├─ manage.py
├─ db.sqlite3
├─ .env
│
├─ dr_automation/
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ celery.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
│
├─ accounts/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ views.py
│  └─ migrations/
│
├─ dashboard/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ views.py
│  └─ migrations/
│
├─ frontend/
│  ├─ __init__.py
│  ├─ context_processors.py
│  ├─ urls.py
│  └─ views.py
│
├─ proxmox/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ api.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ views.py
│  └─ migrations/
│
├─ restore/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ tasks.py
│  ├─ tests.py
│  ├─ views.py
│  └─ migrations/
│
├─ templates/
│  └─ frontend/
│     ├─ jobs.html
│     ├─ login.html
│     ├─ my_vms.html
│     ├─ safe_banner.html
│     └─ vm_detail.html
│
└─ .venv/                        # Virtual environment (ignored in .gitignore)
</pre>
</details>



---

## 🔧 Setup & Run (Development)

### Prerequisites
- Python 3.11+
- Redis running locally (default port 6379)
- Proxmox VE with API access
- (Optional) Virtual environment recommended

## 🧠 **Safety & Modes**

| Flag | Purpose |
|------|----------|
| **FORCE_DRY_RUN=1** | Blocks all real API calls, even if `DRY_RUN=0`. |
| **DRY_RUN=1** | Simulates backup/restore operations safely (default). |
| **REQUIRE_DRY_RUN=1** | Disables any POST action when `DRY_RUN` is off. |
| **ALLOW_VMIDS** | Restrict which VMIDs can run operations. |
| **RESTORE_ENABLED / QUEUE_ENABLED** | Toggles for enabling restore and queuing features. |

> ✅ When **SAFE MODE** is active, every page shows a visible banner, and all operations are mock executions only.

---

## 🔐 **Security Notes**

- Uses **Proxmox Token API** (no password authentication).  
- Each Django user can access only their assigned VMs.  
- **SAFE MODE** guarantees zero real system changes unless explicitly disabled.  

---

## 🚀 **Roadmap**

- Proxmox Backup Server (PBS) integration for live restore  
- Node failover & IP reconfiguration automation  
- Email / webhook notifications  
- OAuth / LDAP authentication  
- REST API client packaging  

---

## 🧩 **Clone & Setup**

<details>
<summary><b>Click to expand full setup guide</b></summary>

```bash
# 1️⃣ Clone Repository
git clone https://github.com/AMMorsy/ProxmoxDisasterRecoveryAutomation.git
cd ProxmoxDisasterRecoveryAutomation
python -m venv .venv
.venv\Scripts\activate   # on Windows
pip install -r requirements.txt

# 2️⃣ Configure .env
# Example configuration:

# Proxmox API
PVE_HOST=https://pve.your's.com:port
PVE_USER=user@pve
PVE_TOKEN_NAME=apitoken
PVE_TOKEN_VALUE=xxxxxxxx

# Behavior flags
FORCE_DRY_RUN=1
DRY_RUN=1
RESTORE_ENABLED=1
QUEUE_ENABLED=1
REQUIRE_DRY_RUN=1
ALLOW_VMIDS=*

# Redis
REDIS_URL=redis://localhost:6379

# 3️⃣ Run Services
python manage.py runserver
celery -A dr_automation worker -l info -P solo

# 4️⃣ Access Web UI
# http://localhost:8000 → My VMs → Backup / Restore (DRY-RUN) → Jobs
