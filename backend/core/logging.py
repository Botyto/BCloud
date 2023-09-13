from datetime import datetime, timedelta
import logging
import os
import shutil


class TruncatedStreamHandler(logging.StreamHandler):
    maxlen: int

    def __init__(self, maxlen: int, stream=None):
        super().__init__(stream)
        self.maxlen = shutil.get_terminal_size((maxlen, 1)).columns

    def format(self, record):
        record = super().format(record)
        lines = record.splitlines()
        for i, line in enumerate(lines):
            line = lines[i]
            if len(line) > self.maxlen:
                lines[i] = line[:(self.maxlen - 3)] + "..."
        record = "\n".join(lines)
        return record

def clear_old_logs(logs_path: str, max_age: timedelta|None):
    if not os.path.isdir(logs_path):
        return
    now = datetime.now()
    too_old = []
    for file in os.listdir(logs_path):
        filepath = os.path.join(logs_path, file)
        mtime = os.path.getmtime(filepath)
        age = now - datetime.fromtimestamp(mtime)
        if max_age is not None and age <= max_age:
            continue
        too_old.append(filepath)
    if not too_old:
        return
    logging.warning(f"Clearing {len(too_old)} old log files")
    for filepath in too_old:
        os.remove(filepath)

def default_setup(level: int, logs_path: str):
    root_logger = logging.root
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = TruncatedStreamHandler(165)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    local_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_path = os.path.join(logs_path, f"{local_time_str}.log")
    os.makedirs(logs_path, exist_ok=True)
    file_handler = logging.FileHandler(file_path, mode="wt", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
