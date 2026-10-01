from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path


def normalize_repository(value: str) -> str:
    text = str(value or "").strip().rstrip("/")
    text = re.sub(r"^https?://github\.com/", "", text, flags=re.IGNORECASE)
    text = text.removesuffix(".git").strip("/")
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", text):
        return ""
    return text


def parse_version(value: str) -> tuple[int, ...]:
    match = re.search(r"(?<!\d)v?(\d+(?:\.\d+){1,3})(?!\d)", str(value or ""), re.IGNORECASE)
    if not match:
        return ()
    return tuple(int(part) for part in match.group(1).split("."))


def is_newer_version(remote: str, current: str) -> bool:
    remote_version = parse_version(remote)
    current_version = parse_version(current)
    if not remote_version:
        return False
    width = max(len(remote_version), len(current_version), 3)
    return remote_version + (0,) * (width - len(remote_version)) > current_version + (0,) * (width - len(current_version))


def release_from_payload(payload: dict, asset_name: str) -> dict:
    assets = payload.get("assets") if isinstance(payload, dict) else []
    assets = assets if isinstance(assets, list) else []
    asset = next((item for item in assets if str(item.get("name", "")) == asset_name), None)
    if not isinstance(asset, dict):
        asset = next((item for item in assets if str(item.get("name", "")).lower().endswith(".exe")), None)
    if not isinstance(asset, dict):
        raise ValueError(f"Release asset not found: {asset_name}")
    digest = str(asset.get("digest") or "")
    if digest.startswith("sha256:"):
        digest = digest.split(":", 1)[1].strip().lower()
    if not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
        digest = ""
    return {
        "version": str(payload.get("tag_name") or payload.get("name") or "").strip(),
        "tag": str(payload.get("tag_name") or "").strip(),
        "name": str(payload.get("name") or payload.get("tag_name") or "").strip(),
        "body": str(payload.get("body") or "").strip(),
        "published_at": str(payload.get("published_at") or "").strip(),
        "html_url": str(payload.get("html_url") or "").strip(),
        "asset_name": str(asset.get("name") or asset_name),
        "asset_url": str(asset.get("browser_download_url") or "").strip(),
        "sha256": digest,
    }


def fetch_latest_release(repository: str, asset_name: str = "Danyria.exe", timeout: float = 15.0) -> dict:
    repo = normalize_repository(repository)
    if not repo:
        raise ValueError("GitHub repository is not configured")
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Danyria-Updater",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return release_from_payload(payload, asset_name)


def download_asset(url: str, destination: Path, expected_sha256: str = "", timeout: float = 30.0) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Danyria-Updater"})
    digest = hashlib.sha256()
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, destination.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
        value = digest.hexdigest().lower()
        if expected_sha256 and value != expected_sha256.lower():
            raise ValueError("Downloaded update checksum does not match the release digest")
        return value
    except Exception:
        try:
            destination.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def powershell_encoded_command(pid: int, target: Path, package: Path) -> str:
    script = """
$ErrorActionPreference = 'Stop'
$processId = __PID__
$target = [IO.Path]::GetFullPath('__TARGET__')
$package = [IO.Path]::GetFullPath('__PACKAGE__')
while (Get-Process -Id $processId -ErrorAction SilentlyContinue) { Start-Sleep -Milliseconds 250 }
$backup = "$target.danyria-backup"
try {
    if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
    if (Test-Path -LiteralPath $target) { Move-Item -LiteralPath $target -Destination $backup -Force }
    Move-Item -LiteralPath $package -Destination $target -Force
    $workingDirectory = Split-Path -LiteralPath $target -Parent
    Start-Process -FilePath $target -WorkingDirectory $workingDirectory -ErrorAction Stop
    if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
} catch {
    if (-not (Test-Path -LiteralPath $target) -and (Test-Path -LiteralPath $backup)) { Move-Item -LiteralPath $backup -Destination $target -Force }
    throw
}
""".strip()
    script = script.replace("__PID__", str(int(pid)))
    script = script.replace("__TARGET__", str(target).replace("'", "''"))
    script = script.replace("__PACKAGE__", str(package).replace("'", "''"))
    return base64.b64encode(script.encode("utf-16le")).decode("ascii")


def launch_replacement(pid: int, target: Path, package: Path) -> None:
    encoded = powershell_encoded_command(pid, target, package)
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-EncodedCommand", encoded],
        close_fds=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
