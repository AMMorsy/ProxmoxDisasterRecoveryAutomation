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

dr_automation/ # Django project
frontend/ # Templates and UI
restore/ # Core app: models, tasks, API endpoints
├─ models.py
├─ views.py
├─ tasks.py
├─ api.py (Proxmox interface)
templates/frontend/ # HTML templates
.env # Environment config


---

## 🔧 Setup & Run (Development)

### Prerequisites
- Python 3.11+
- Redis running locally (default port 6379)
- Proxmox VE with API access
- (Optional) Virtual environment recommended

### 1. Clone & Setup

```bash
git clone https://github.com/AMMorsy/ProxmoxDisasterRecoveryAutomation.git
cd ProxmoxDisasterRecoveryAutomation
python -m venv .venv
.venv\Scripts\activate   # on Windows
pip install -r requirements.txt
2. Configure .env
Example:

env
Copy code
# Proxmox API
PVE_HOST=https://pve.youruser.com:8006
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
REDIS_URL=redis://127.0.0.1:6379/0
3. Run Services
In separate terminals:

# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery worker
celery -A dr_automation worker -l info -P solo
4. Access Web UI
Go to: http://127.0.0.1:8000/
Login → My VMs → click Backup or Restore (DRY-RUN) → monitor in Jobs page.

🧠 Safety & Modes
Flag	Purpose
FORCE_DRY_RUN=1	Absolutely blocks any real API calls, even if DRY_RUN=0.
DRY_RUN=1	Simulate restore/backup actions (default safe mode).
REQUIRE_DRY_RUN=1	Prevents POST actions if DRY_RUN is off.
ALLOW_VMIDS	Restrict which VMIDs are allowed to run operations.
RESTORE_ENABLED / QUEUE_ENABLED	Master toggles for features.

When SAFE MODE is on, every page displays a banner and logs show mock actions.

🔐 Security Notes
API calls use the Proxmox Token API instead of username/password.

Each Django user owns explicit VM objects — no cross-access.

SAFE MODE ensures no real system modifications unless explicitly switched off.

🚀 Roadmap
 PBS integration for true live restore

 Node failover & IP swap orchestration

 Email/webhook job notifications

 OAuth / LDAP login

 REST API client packaging

🧾 License
MIT License © 2025 AMMorsy

