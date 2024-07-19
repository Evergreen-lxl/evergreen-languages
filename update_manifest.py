#!/usr/bin/env python3

import hashlib
import json
import logging
import re
from string import Template
from typing import Any

from defs import *

logger = logging.getLogger(__name__)

FILE_URL_TEMPLATE = Template(
    "https://github.com/Evergreen-lxl/evergreen-languages/releases/download/"
    "$PLATFORM/$FILENAME"
)


def get_addons(manifest: dict) -> dict[str, dict]:
    addons_dict = {}
    addons = manifest.get("addons", {})

    for addon in addons:
        addons_dict[addon["id"].replace("evergreen_", "")] = addon

    return addons_dict


def make_addon(name: str) -> dict[str, Any]:
    return {
        "id": f"evergreen_{name}",
        "version": "0",
        "mod_version": MODVERSION,
        "type": "plugin",
        "dependencies": {"evergreen": {}},
        "files": [],
    }


def update_file(files: list[dict], platform: str, filename: str, checksum: str):
    entry = next((f for f in files if f["arch"] == platform), None)
    if not entry:
        logger.info(f"Created missing entry for {name} on {platform}")

        entry = {"arch": platform}
        files.append(entry)

    entry["url"] = FILE_URL_TEMPLATE.substitute(PLATFORM=platform, FILENAME=filename)
    entry["checksum"] = checksum


def make_manifest(addons: dict[str, dict]) -> dict:
    addons_ls = sorted(addons.values(), key=lambda v: v["id"])

    for addon in addons_ls:
        addon["files"].sort(key=lambda v: v["arch"])

    return {"addons": addons_ls}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open(MANIFEST_FILE, "r") as f:
        addons = get_addons(json.load(f))

    updated: set[str] = set()

    for file in DIST_DIR.iterdir():
        m = re.fullmatch(r"evergreen_(.*?)\-(.*).zip", file.name)
        if not m:
            continue

        name, platform = m.groups()

        logger.info(f"Updating manifest for {name} on {platform}")

        entry = addons.get(name, None)
        if not entry:
            logger.info(f"Created missing entry for {name}")

            entry = make_addon(name)
            addons[name] = entry

        with open(file, "rb") as f:
            checksum = hashlib.file_digest(f, "sha256").hexdigest()

        update_file(entry["files"], platform, file.name, checksum)

    with open(MANIFEST_FILE, "w") as f:
        json.dump(make_manifest(addons), f, indent=4)
