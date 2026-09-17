import importlib.util
import os
import shutil
import subprocess
import sys


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cloudflare_src = os.path.join(root_dir, "cloudflare", "src")

    # 1. Copy local ytmusicapi package from root into cloudflare/src/ytmusicapi
    src_ytmusicapi = os.path.join(root_dir, "ytmusicapi")
    target_ytmusicapi = os.path.join(cloudflare_src, "ytmusicapi")
    if os.path.exists(target_ytmusicapi):
        shutil.rmtree(target_ytmusicapi)
    shutil.copytree(
        src_ytmusicapi,
        target_ytmusicapi,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    # 2. Copy pyodide_http from environment site-packages into cloudflare/src/pyodide_http
    target_pyodide_http = os.path.join(cloudflare_src, "pyodide_http")
    if os.path.exists(target_pyodide_http):
        shutil.rmtree(target_pyodide_http)

    spec = importlib.util.find_spec("pyodide_http")
    if spec and spec.origin:
        src_pyodide_http = os.path.dirname(spec.origin)
        shutil.copytree(
            src_pyodide_http,
            target_pyodide_http,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    else:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pyodide-http",
                "-t",
                cloudflare_src,
                "--no-deps",
            ],
            check=False,
        )


if __name__ == "__main__":
    main()
