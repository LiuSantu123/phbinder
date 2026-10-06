from pathlib import Path
import subprocess, shutil

def executable(configured, default):
    return configured or shutil.which(default)

def run(cmd, cwd=None, timeout=3600):
    p=subprocess.run([str(x) for x in cmd], cwd=cwd, text=True, capture_output=True, timeout=timeout)
    if p.returncode: raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str,cmd))}\n{p.stderr[-1000:]}")
    return p

def propka_available(cfg): return bool(executable(cfg.get("propka"), "propka3"))
def apbs_available(cfg): return bool(executable(cfg.get("pdb2pqr"), "pdb2pqr") and executable(cfg.get("apbs"), "apbs"))
