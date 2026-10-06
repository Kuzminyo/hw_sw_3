import argparse
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

_guard = Lock()


def copy_file(file: Path, output: Path) -> None:
    ext = file.suffix.lstrip(".").lower() or "no_extension"
    target_dir = output / ext
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / file.name
    # avoid overwriting same-named files from different directories
    with _guard:
        counter = 1
        while target.exists():
            target = target_dir / f"{file.stem}_{counter}{file.suffix}"
            counter += 1
        target.touch()  # reserve the name before the actual copy
    try:
        shutil.copy2(file, target)
    except OSError as e:
        logging.error("Cannot copy %s: %s", file, e)


def process_dir(source: Path, output: Path, pool: ThreadPoolExecutor, futures: list) -> None:
    """Scan one directory; subdirectories and files are submitted to the pool."""
    try:
        for item in source.iterdir():
            if item.is_dir():
                if item.resolve() == output.resolve():
                    continue  # do not process the destination itself
                futures.append(pool.submit(process_dir, item, output, pool, futures))
            elif item.is_file():
                futures.append(pool.submit(copy_file, item, output))
    except OSError as e:
        logging.error("Cannot read %s: %s", source, e)


def sort_files(source: Path, output: Path, workers: int = 8) -> None:
    output.mkdir(parents=True, exist_ok=True)
    futures = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures.append(pool.submit(process_dir, source, output, pool, futures))
        # tasks spawn new tasks, so wait until the list stops growing
        i = 0
        while i < len(futures):
            futures[i].result()
            i += 1


def main():
    parser = argparse.ArgumentParser(description="Sort files by extension using threads")
    parser.add_argument("source", type=Path, help="directory with files to process")
    parser.add_argument("output", type=Path, nargs="?", default=Path("dist"),
                        help="destination directory (default: dist)")
    args = parser.parse_args()

    if not args.source.is_dir():
        parser.error(f"{args.source} is not a directory")
    sort_files(args.source, args.output)


if __name__ == "__main__":
    main()
