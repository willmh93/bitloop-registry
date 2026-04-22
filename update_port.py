#!/usr/bin/env python3
import argparse
import hashlib
import json
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


def sha512_file(path: Path) -> str:
    h = hashlib.sha512()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dst: Path) -> None:
    print(f"Downloading: {url}")
    with urllib.request.urlopen(url) as response, open(dst, "wb") as file:
        shutil.copyfileobj(response, file)
    print(f"Saved to: {dst}")


def detect_newline(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def dump_json_with_original_newline(obj, newline: str) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    return text.replace("\n", newline) + newline


def replace_repo_ref_and_sha(portfile_text: str, repo: str, tag: str, sha: str) -> str:
    updated = re.sub(
        r"(\bSHA512\s+)[0-9a-fA-F]+",
        r"\g<1>" + sha,
        portfile_text,
        count=1,
    )

    updated = re.sub(
        r'(\bREPO\s+")([^"]+)(")',
        r'\g<1>' + repo + r'\g<3>',
        updated,
        count=1,
    )

    if "${VERSION}" not in updated:
        updated = re.sub(
            r'(\bREF\s+")([^"]+)(")',
            r'\g<1>' + tag + r'\g<3>',
            updated,
            count=1,
        )
        updated = re.sub(
            r'(\bREF\s+)([^\s\)]+)',
            r'\g<1>' + tag,
            updated,
            count=1,
        )

    return updated


def ask_non_empty(prompt: str, default: str | None = None) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default:
            return default
        print("A value is required")


def normalize_tag(tag_text: str) -> str:
    tag = tag_text.strip()
    if not tag:
        raise ValueError("Tag is required")
    if not tag.startswith("v"):
        tag = f"v{tag}"
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", tag):
        raise ValueError('Tag must look like "v0.1.3"')
    return tag


def version_from_tag(tag: str) -> str:
    return tag[1:]


def find_manifest_version_field(manifest_obj: dict) -> str:
    for key in ("version", "version-semver", "version-date", "version-string"):
        if key in manifest_obj:
            return key
    return "version"


def main():
    parser = argparse.ArgumentParser(description="Update a vcpkg port from a GitHub tag")
    parser.add_argument("--repo", help="GitHub repo owner/name, e.g. willmh93/fltx")
    parser.add_argument("--tag", help='Git tag to publish, e.g. v0.1.3')
    parser.add_argument("--port-name", help="Port name directory under ports/")
    parser.add_argument("--ports-root", default="ports", help="Path to ports root")
    parser.add_argument("--versions-dir", default="versions", help="Path to versions dir")
    parser.add_argument("--vcpkg", default="vcpkg", help="Path to vcpkg executable")
    parser.add_argument("--port-version", type=int, help="Optional vcpkg port-version for same-upstream repackaging")
    parser.add_argument("--no-vcpkg-steps", action="store_true", help="Do not run format-manifest or x-add-version")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing files")
    args = parser.parse_args()

    repo = (args.repo or ask_non_empty("Enter the repo owner/name")).strip().strip("/")
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", repo):
        sys.exit('ERROR: repo must look like "owner/name"')

    try:
        tag = normalize_tag(args.tag or ask_non_empty("Enter the tag to base the port on"))
    except ValueError as exc:
        sys.exit(f"ERROR: {exc}")

    version = version_from_tag(tag)
    default_port_name = repo.rsplit("/", 1)[1]
    port_name = (args.port_name or ask_non_empty("Enter the port name", default_port_name)).strip()

    ports_root = Path(args.ports_root).resolve()
    versions_dir = Path(args.versions_dir).resolve()
    port_dir = ports_root / port_name
    manifest_path = port_dir / "vcpkg.json"
    portfile_path = port_dir / "portfile.cmake"

    if not manifest_path.is_file():
        sys.exit(f"ERROR: {manifest_path} not found")
    if not portfile_path.is_file():
        sys.exit(f"ERROR: {portfile_path} not found")

    url = f"https://github.com/{repo}/archive/refs/tags/{tag}.tar.gz"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_tar = Path(temp_dir) / f"{port_name}-{tag}.tar.gz"
        download(url, temp_tar)
        sha = sha512_file(temp_tar)

    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_newline = detect_newline(manifest_text)
    manifest_obj = json.loads(manifest_text)
    version_field = find_manifest_version_field(manifest_obj)
    old_version = str(manifest_obj.get(version_field, ""))

    manifest_obj[version_field] = version

    # _ChatGPT_: tag-based publishes normally mean a new upstream version, so reset port-version
    if args.port_version is None:
        manifest_obj.pop("port-version", None)
    else:
        manifest_obj["port-version"] = args.port_version

    manifest_updated = dump_json_with_original_newline(manifest_obj, manifest_newline)

    portfile_text = portfile_path.read_text(encoding="utf-8")
    portfile_updated = replace_repo_ref_and_sha(portfile_text, repo, tag, sha)

    print(f"repo:    {repo}")
    print(f"port:    {port_name}")
    print(f"tag:     {tag}")
    print(f"version: {version}")
    print(f"SHA512:  {sha}")
    if old_version:
        print(f"previous manifest version: {old_version}")

    if args.dry_run:
        print("\n--- vcpkg.json (after) ---\n")
        print(manifest_updated)
        print("\n--- portfile.cmake (after) ---\n")
        print(portfile_updated)
        print("\nDry run complete. No files were modified.")
        return

    manifest_path.write_text(manifest_updated, encoding="utf-8")
    portfile_path.write_text(portfile_updated, encoding="utf-8")
    print(f"Updated {manifest_path}")
    print(f"Updated {portfile_path}")

    if not args.no_vcpkg_steps:
        run([args.vcpkg, f"--x-builtin-ports-root={ports_root}", "format-manifest", "--all"])
        run(["git", "add", str(manifest_path), str(portfile_path)])
        run([
            args.vcpkg,
            f"--x-builtin-ports-root={ports_root}",
            f"--x-builtin-registry-versions-dir={versions_dir}",
            "x-add-version",
            port_name,
        ])
        run(["git", "add", str(versions_dir)])

    print("\nDone.")


if __name__ == "__main__":
    main()
