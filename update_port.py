#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

def run(cmd, cwd=None):
    print("> " + " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def sha512_file(path):
    h = hashlib.sha512()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def download(url, dst):
    print(f"Downloading: {url}")
    with urllib.request.urlopen(url) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f)
    print(f"Saved to: {dst}")

def replace_ref_and_sha(portfile_text, version, sha):
    # Update SHA512 (use \g<1> so \1 + a digit isn't misread as \12)
    portfile_text_new = re.sub(
        r"(\bSHA512\s+)[0-9a-fA-F]+",
        r"\g<1>" + sha,
        portfile_text,
        count=1,
    )

    # Update REF if it's a concrete tag; leave REF v${VERSION} alone
    if "${VERSION}" not in portfile_text_new:
        portfile_text_new = re.sub(
            r"(\bREF\s+v)[^\s]+",
            r"\g<1>" + version,
            portfile_text_new,
            count=1,
        )

    return portfile_text_new


def main():
    ap = argparse.ArgumentParser(description="Update a vcpkg port to a new version and SHA512.")
    ap.add_argument("--version", required=True, help="Version string (e.g. 0.9.15)")
    ap.add_argument("--repo", default="willmh93/bitloop", help="GitHub repo owner/name")
    ap.add_argument("--port-name", default="bitloop", help="Port name directory under ports/")
    ap.add_argument("--ports-root", default="ports", help="Path to ports root")
    ap.add_argument("--versions-dir", default="versions", help="Path to versions dir (for x-add-version)")
    ap.add_argument("--vcpkg", default="vcpkg", help="Path to vcpkg executable (or in PATH)")
    ap.add_argument("--no-vcpkg-steps", action="store_true", help="Do not run format-manifest or x-add-version")
    ap.add_argument("--dry-run", action="store_true", help="Compute and show changes but do not write files")
    args = ap.parse_args()

    version = args.version
    ports_root = Path(args.ports_root).resolve()
    port_dir = ports_root / args.port_name
    manifest_path = port_dir / "vcpkg.json"
    portfile_path = port_dir / "portfile.cmake"

    if not manifest_path.is_file():
        print(f"ERROR: {manifest_path} not found", file=sys.stderr)
        sys.exit(1)
    if not portfile_path.is_file():
        print(f"ERROR: {portfile_path} not found", file=sys.stderr)
        sys.exit(1)

    url = f"https://github.com/{args.repo}/archive/refs/tags/v{version}.tar.gz"

    # 1) download and hash
    with tempfile.TemporaryDirectory() as td:
        tmp_tar = Path(td) / f"{args.port_name}-{version}.tar.gz"
        download(url, tmp_tar)
        sha = sha512_file(tmp_tar)
    print(f"SHA512: {sha}")

    # 2) update vcpkg.json
    manifest_obj = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_before = json.dumps(manifest_obj, indent=2, sort_keys=False)
    manifest_obj["version-semver"] = version
    manifest_after = json.dumps(manifest_obj, indent=2, sort_keys=False)

    # 3) update portfile.cmake
    portfile_text = portfile_path.read_text(encoding="utf-8")
    portfile_updated = replace_ref_and_sha(portfile_text, version, sha)

    # Show changes in dry-run
    if args.dry_run:
        print("\n--- vcpkg.json (before) ---\n" + manifest_before)
        print("\n--- vcpkg.json (after) ---\n" + manifest_after)
        print("\n--- portfile.cmake (before) ---\n" + portfile_text)
        print("\n--- portfile.cmake (after) ---\n" + portfile_updated)
        print("\nDry run complete. No files were modified.")
        return

    # Write changes
    manifest_path.write_text(manifest_after + "\n", encoding="utf-8")
    portfile_path.write_text(portfile_updated, encoding="utf-8")
    print(f"Updated {manifest_path}")
    print(f"Updated {portfile_path}")

    # 4) optional vcpkg steps
    if not args.no_vcpkg_steps:
        run([args.vcpkg, f"--x-builtin-ports-root={str(ports_root)}", "format-manifest", "--all"])
        run(["git", "add", str(manifest_path), str(portfile_path)])
        run([
            args.vcpkg,
            f"--x-builtin-ports-root={str(ports_root)}",
            f"--x-builtin-registry-versions-dir={args.versions_dir}",
            "x-add-version",
            args.port_name
        ])
        run(["git", "add", args.versions_dir])

    print("\nDone.")

if __name__ == "__main__":
    main()
