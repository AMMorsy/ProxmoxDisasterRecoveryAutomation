import os

def safe_mode(request):
    # Visible banner flag (true when DRY RUN is on)
    safe = os.getenv("FORCE_DRY_RUN", "0") == "1" or os.getenv("DRY_RUN", "0") == "1"
    return {"SAFE_MODE": safe}
