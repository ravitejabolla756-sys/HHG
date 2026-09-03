import argparse, sys
from .config import Settings
from .pipeline.runner import run
def main():
    parser = argparse.ArgumentParser(description="Hacker House Goa Task 3 verification pipeline")
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    try: run(args.image, Settings())
    except Exception as exc: print(f"ERROR: {exc}", file=sys.stderr); return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
