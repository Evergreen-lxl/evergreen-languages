#!/usr/bin/env python3

import logging
import os
import subprocess
import tomllib
import zipfile

from defs import *

logger = logging.getLogger(__name__)

PLATFORM = os.environ.get("PLATFORM", "unknown")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    os.makedirs(DIST_DIR, exist_ok=True)

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)

    for name in config:
        prefix = Path(f"{NAME_PREFIX}{name}")
        srcpkg = SRCPKG_DIR / prefix
        srcpkg_ar = SRCPKG_DIR / f"{NAME_PREFIX}{name}.zip"

        if srcpkg_ar.exists():
            logger.info(f"{name}: Extracting source package")

            with zipfile.ZipFile(srcpkg_ar, "r") as ar:
                ar.extractall(path=SRCPKG_DIR)

            has_so = (srcpkg / "Makefile").exists()

            if has_so:
                logger.info(f"{name}: Building shared library")

                subprocess.run(["make"], cwd=SRCPKG_DIR / f"{NAME_PREFIX}{name}")

            logger.info(f"{name}: Creating package")

            with zipfile.ZipFile(
                DIST_DIR / f"{NAME_PREFIX}{name}-{PLATFORM}.zip",
                "w",
                compression=zipfile.ZIP_DEFLATED,
            ) as ar:
                ar.write(srcpkg / "init.lua", arcname=prefix / "init.lua")

                if has_so:
                    so = next(srcpkg.glob("parser.*"))
                    ar.write(so, arcname=prefix / so.name)

                for qry in (srcpkg / "queries").iterdir():
                    ar.write(qry, arcname=prefix / "queries" / qry.name)
