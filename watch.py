import os
import shutil
import time
from pathlib import Path
from ingest import ingest_documents
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PENDING_DIR = Path("./files/pending")
PROCESSED_DIR = Path("./files/processed")


def load_and_extract(file_path: str) -> bool:
    print(f"Loading and extracting: {file_path}")
    return ingest_documents(file_path)


def processed(file_path: str) -> None:
    """Move a successfully processed file into files/processed."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dest = PROCESSED_DIR / Path(file_path).name
    shutil.move(file_path, dest)
    print(f"Moved to processed: {dest}")


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        print(f"File created: {file_path}")

        # Brief wait so the file is fully written before we touch it
        time.sleep(0.5)

        if not os.path.isfile(file_path):
            return

        if load_and_extract(file_path):
            processed(file_path)


if __name__ == "__main__":
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(Handler(), path=str(PENDING_DIR))
    observer.start()
    print(f"Watching {PENDING_DIR.resolve()} ...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
