import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen

def compute_sha512(file_path: Path) -> str:
    """Compute SHA512 hash of the given file."""
    h = hashlib.sha512()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def bump_version(version: str):
    # Set up paths
    repo_root = Path(__file__).parent.resolve()
    port_dir = repo_root / "ports" / "bitloop"
    versions_dir = repo_root / "versions"
    baseline_file = versions_dir / "baseline.json"
    port_name = port_dir.name               # "bitloop"
    letter    = port_name[0].lower()        # "b"
    tree_dir  = versions_dir / f"{letter}-" # versions/b-
    tree_file = tree_dir / "bitloop.json"
    tag_url = f"https://github.com/willmh93/bitloop/archive/refs/tags/v{version}.tar.gz"

    # 1) Update vcpkg.json
    vcpkg_json_path = port_dir / "vcpkg.json"
    vcpkg_data = json.loads(vcpkg_json_path.read_text())
    vcpkg_data["version-string"] = version
    vcpkg_json_path.write_text(json.dumps(vcpkg_data, indent=2) + "\n")

    # 2) Download tarball
    tmp_file = Path(tempfile.gettempdir()) / f"bitloop-v{version}.tar.gz"
    with urlopen(tag_url) as response, open(tmp_file, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    # 3) Compute SHA512
    new_sha = compute_sha512(tmp_file)

    # 4) Update portfile.cmake
    portfile_path = port_dir / "portfile.cmake"
    portfile_lines = portfile_path.read_text().splitlines()
    updated_lines = []
    for line in portfile_lines:
        if line.strip().startswith("SHA512"):
            updated_lines.append(f"    SHA512           {new_sha}")
        else:
            updated_lines.append(line)
    portfile_path.write_text("\n".join(updated_lines) + "\n")

    # 5) Update baseline.json
    baseline_data = json.loads(baseline_file.read_text())
    baseline_data.setdefault("default", {})
    baseline_data["default"]["bitloop"] = {
        "baseline": version,
        "port-version": 0
    }
    baseline_file.write_text(json.dumps(baseline_data, indent=2) + "\n")

    # 6) Lookup git-tree for the port directory in the registry repo
    # Ensure we run inside the registry repo
    
    # Stage updated port dir (after editing vcpkg.json/portfile.cmake)
    subprocess.run(["git", "add", "ports/bitloop"], cwd=repo_root, check=True)
    
    # Snapshot index as a tree (no commit required)
    root_tree = subprocess.run(
        ["git", "write-tree"], cwd=repo_root,
        capture_output=True, text=True, check=True
    ).stdout.strip()
    
    # Extract subtree SHA for ports/bitloop
    subtree_sha = subprocess.run(
        ["git", "ls-tree", root_tree, "ports/bitloop"],
        cwd=repo_root, capture_output=True, text=True, check=True
    ).stdout.split()[2]
    
    # Write versions/<letter>-/bitloop.json
    tree_dir.mkdir(parents=True, exist_ok=True)
    tree_data = {
        "versions": [{
            "git-tree": subtree_sha,
            "version-string": version,
            "port-version": 0
        }]
    }
    tree_file.write_text(json.dumps(tree_data, indent=2) + "\n")
    print("git-tree:", subtree_sha)

    tree_file.write_text(json.dumps(tree_data, indent=2) + "\n")

    # 8) Commit changes
    #subprocess.run(["git", "add",
    #                str(vcpkg_json_path),
    #                str(portfile_path),
    #                str(baseline_file),
    #                str(tree_file)],
    #               check=True)
    #subprocess.run(["git", "commit", "-m", f"bitloop: bump version to {version}"], check=True)
    
    print(f"✔ Bumped bitloop to {version}")

def main():
    parser = argparse.ArgumentParser(description="Bump bitloop port version in registry")
    parser.add_argument("version", help="New version string, e.g. 0.9.1")
    args = parser.parse_args()
    bump_version(args.version)

if __name__ == "__main__":
    main()
