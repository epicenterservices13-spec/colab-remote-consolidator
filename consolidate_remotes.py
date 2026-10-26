#!/usr/bin/env python3
"""
Imperial Cloud Remote Consolidator & Purge Engine
Target: Google Colab VM / Cloud Executor
Objective: Consolidate satellite remotes & photos onto epic: and purge sources
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("/content/consolidation.log")
STDOUT_FILE = Path("/content/consolidation.stdout")
RCLONE_CONF_SRC = Path("/content/rclone.conf")
RCLONE_CONF_DEST = Path.home() / ".config" / "rclone" / "rclone.conf"

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def ensure_rclone():
    if shutil.which("rclone"):
        log("[✓] Rclone binary already installed.")
        return
    log("[*] Installing rclone binary...")
    subprocess.check_call("curl -s https://rclone.org/install.sh | bash", shell=True)
    log("[✓] Rclone installed successfully.")

def ensure_config():
    RCLONE_CONF_DEST.parent.mkdir(parents=True, exist_ok=True)
    if RCLONE_CONF_SRC.exists():
        shutil.copy2(RCLONE_CONF_SRC, RCLONE_CONF_DEST)
        log(f"[✓] Rclone configuration deployed to {RCLONE_CONF_DEST}")
    elif RCLONE_CONF_DEST.exists() and RCLONE_CONF_DEST.stat().st_size > 0:
        log(f"[✓] Existing rclone configuration found at {RCLONE_CONF_DEST}")
    else:
        log(f"[-] ERROR: No rclone config found at {RCLONE_CONF_SRC} or {RCLONE_CONF_DEST}")
        sys.exit(1)

def run_cmd(cmd, desc):
    log(f"[*] Starting: {desc}")
    log(f"[*] Command: {' '.join(cmd)}")
    with open(LOG_FILE, "a", encoding="utf-8") as log_out:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in iter(proc.stdout.readline, ""):
            if not line:
                break
            clean = line.strip()
            if any(k in clean for k in ["Transferred:", "ETA", "ERROR", "NOTICE", "Elapsed time", "Deleted:"]):
                log(clean)
            else:
                log_out.write(line)
        proc.stdout.close()
        rc = proc.wait()
    if rc == 0:
        log(f"[✓] Completed successfully: {desc}")
    else:
        log(f"[-] Warning: {desc} exited with code {rc}")
    return rc

def execute_consolidation():
    log("==========================================================")
    log("⚡ LAUNCHING IMPERIAL REMOTE CONSOLIDATION ENGINE")
    log("==========================================================")

    ensure_rclone()
    ensure_config()

    remotes_out = subprocess.check_output(["rclone", "listremotes"], text=True)
    available_remotes = [r.strip().rstrip(":") for r in remotes_out.splitlines() if r.strip()]
    log(f"[*] Detected remotes: {', '.join(available_remotes)}")

    # 1. OneDrive move -> epic:od/
    if "onedrive" in available_remotes:
        log(">>> Phase 1: Evacuating and purging OneDrive -> epic:od/")
        cmd = [
            "rclone", "move",
            "onedrive:", "epic:od/",
            "--exclude", "Personal Vault/**",
            "--size-only",
            "--fast-list",
            "--delete-empty-src-dirs",
            "--transfers", "16",
            "--checkers", "32",
            "--stats", "15s",
            "--stats-one-line",
            "-v"
        ]
        run_cmd(cmd, "OneDrive -> epic:od/ move & purge")

    # 2. Google Drive Satellite Remotes -> epic:CONSOLIDATED_REMOTES/<remote>/
    gdrive_satellites = ["turbo", "brainrot", "epicdev", "longden", "sneaky", "tech", "yola"]
    for remote in gdrive_satellites:
        if remote in available_remotes:
            log(f">>> Phase 2: Server-side move {remote}: -> epic:CONSOLIDATED_REMOTES/{remote}/")
            cmd = [
                "rclone", "move",
                f"{remote}:", f"epic:CONSOLIDATED_REMOTES/{remote}/",
                "--drive-server-side-across-configs",
                "--fast-list",
                "--delete-empty-src-dirs",
                "--transfers", "16",
                "--checkers", "32",
                "--stats", "15s",
                "--stats-one-line",
                "-v"
            ]
            run_cmd(cmd, f"{remote}: -> epic:CONSOLIDATED_REMOTES/{remote}/ server-side move")

    log("==========================================================")
    log("✨ [✓] ALL REMOTE PHASES EXECUTED.")
    log("==========================================================")

def main():
    if os.environ.get("COLAB_DAEMON") == "1":
        execute_consolidation()
        return

    print("[*] Spawning detached consolidation daemon on Colab VM...")
    env = os.environ.copy()
    env["COLAB_DAEMON"] = "1"

    proc = subprocess.Popen(
        [sys.executable, __file__],
        env=env,
        stdout=open(STDOUT_FILE, "a", encoding="utf-8"),
        stderr=open(STDOUT_FILE, "a", encoding="utf-8"),
        start_new_session=True
    )
    print(f"[✓] Daemon spawned successfully. PID={proc.pid}")
    print("[*] Live logs at: /content/consolidation.log")

if __name__ == "__main__":
    main()
