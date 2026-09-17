import os
import shutil
import subprocess
import sys


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cloudflare_src = os.path.join(root_dir, "cloudflare", "src")

    # 1. Copy ytmusicapi package from root into cloudflare/src/ytmusicapi
    src_ytmusicapi = os.path.join(root_dir, "ytmusicapi")
    target_ytmusicapi = os.path.join(cloudflare_src, "ytmusicapi")
    if os.path.exists(target_ytmusicapi):
        shutil.rmtree(target_ytmusicapi)
    shutil.copytree(
        src_ytmusicapi,
        target_ytmusicapi,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    # 2. Install dependencies (pyodide-http) into cloudflare/src/
    req_file = os.path.join(root_dir, "cloudflare", "requirements.txt")
    if os.path.exists(req_file):
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                req_file,
                "-t",
                cloudflare_src,
                "--no-deps",
                "--upgrade",
            ]
        )


if __name__ == "__main__":
    main()
