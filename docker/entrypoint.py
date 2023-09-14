import logging
import os
import shlex
import shutil
import subprocess
import sys
import threading
from typing import List

logging.basicConfig(level=logging.DEBUG, format="entrypoint | %(asctime)s %(levelname)s %(message)s")

background_processes: List[subprocess.Popen] = []
def wait_all():
    for proc in background_processes:
        proc.wait()

BG = 0
FG = 1

def exec(mode, cmd: str, *, prefix: str|None = None, cwd: str|None = None):
    args = shlex.split(cmd)
    output = not not prefix
    if not prefix:
        prefix = os.path.basename(args[0])
    def relay(stream, out_stream, prefix):
        for line in stream:
            print(prefix, "|", line, end="", file=out_stream)
    proc = subprocess.Popen(
        args=args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
    )
    if output:
        threading.Thread(target=relay, args=(proc.stdout, sys.stdout, prefix)).start()
    threading.Thread(target=relay, args=(proc.stderr, sys.stderr, prefix)).start()
    if mode == BG:
        background_processes.append(proc)
    elif mode == FG:
        proc.wait()
    return proc

def execpy(mode, file: str, args: str, prefix: str|None = None, cwd: str|None = None):
    python_path = shutil.which("python3")
    return exec(mode, f"{python_path} {file} {args}", prefix=prefix, cwd=cwd)

def start_backend():
    logging.info("Starting backend")
    root = os.path.join("/", "app", "backend")
    main_path = os.path.join(root, "main.py")
    execpy(BG, main_path, "", prefix="backend", cwd=root)

def start_frontend():
    logging.info("Starting frontend")
    root = os.path.join("/", "app", "frontend")
    exec(BG, "npm start", prefix="frontend", cwd=root)

def start_nginx():
    logging.info("Starting nginx")
    exec(BG, "nginx", prefix="nginx")

def main():
    logging.info("Starting")
    start_backend()
    start_frontend()
    start_nginx()

    logging.info("Done")
    wait_all()

if __name__ == "__main__":
    main()

