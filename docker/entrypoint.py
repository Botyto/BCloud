import logging
import os
import shlex
import shutil
import subprocess
import sys
import threading
from typing import List, Tuple

logging.basicConfig(level=logging.DEBUG, format="entrypoint | %(asctime)s %(levelname)s %(message)s")

background_processes: List[Tuple[str, subprocess.Popen]] = []
def wait_all():
    for prefix, proc in background_processes:
        proc.wait()
        if proc.returncode == 0:
            continue
        logging.error("%s exited with code %d", prefix, proc.returncode)

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
        background_processes.append((prefix, proc))
    elif mode == FG:
        proc.wait()
        logging.info("%s exited with code %d", prefix, proc.returncode)
    return proc

def execpy(mode, file: str, args: str, prefix: str|None = None, cwd: str|None = None):
    python_path = shutil.which("python3")
    return exec(mode, f"{python_path} {file} {args}", prefix=prefix, cwd=cwd)

def start_backend():
    logging.info("Starting backend")
    main_path = os.path.join("/", "app", "backend", "main.py")
    workdir = os.path.join("/", "data")
    execpy(BG, main_path, "", prefix="backend", cwd=workdir)

def start_nginx():
    logging.info("Starting nginx")
    exec(BG, "nginx", prefix="nginx")

def main():
    logging.info("Starting")
    start_backend()
    start_nginx()

    logging.info("Done")
    wait_all()

    threading.Event().wait()

if __name__ == "__main__":
    main()
