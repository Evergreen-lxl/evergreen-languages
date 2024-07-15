#!/usr/bin/env python3

import logging
import json
import os
import subprocess
import tomllib
import zipfile
from typing import Tuple

from defs import *
from language import Language

logger = logging.getLogger(__name__)


def git_remote_commit(url: str, rev: str = "HEAD") -> str:
    return (
        subprocess.check_output(["git", "ls-remote", url, rev])
        .split(b"\t", 1)[0]
        .decode()
    )


def ensure_nvts():
    if not NVTS_DIR.exists():
        logger.info("nvim-treesitter: Fetching queries")
        subprocess.run(["git", "clone", "--depth", "1", NVTS_URL, NVTS_DIR])
    else:
        logger.info("nvim-treesitter: Already fetched queries")


def check_nvts(commit_lock) -> Tuple[bool, str]:
    commit = git_remote_commit(NVTS_URL)

    logger.info(f"nvim-treesitter: Last commit: {commit_lock}")
    logger.info(f"nvim-treesitter: Remote commit: {commit}")

    updated = commit != commit_lock

    if updated:
        ensure_nvts()
    else:
        logger.info("nvim-treesitter: Skipping checks for query updates")

    return updated, commit


def check_lang(
    lock, name, opts, queries_updated=True
) -> Tuple[bool, Language, str | None, dict]:
    cmt_lock = lock.get("commit")
    ds_lock = lock.get("files", {})
    src_ds_lock = ds_lock.get("srcs", {})
    inc_ds_lock = ds_lock.get("incs", {})
    qry_ds_lock = ds_lock.get("queries", {})

    lang = Language(
        name, opts.get("remote"), NVTS_QUERY_DIR / name, opts.get("files", [])
    )

    changed = False
    cmt = None
    digests = {}

    # if there is a remote, check if remote has updated
    if "remote" in opts:
        logger.info(f"{name}: Checking for source updates")

        cmt = git_remote_commit(opts["remote"])

        logger.info(f"{name}: Last commit: {cmt_lock}")
        logger.info(f"{name}: Remote commit: {cmt}")

        if cmt != cmt_lock:
            lang.ensure_source(BUILD_DIR / lang.name)

            src_ds = lang.src_digests()
            inc_ds = lang.inc_digests()
            digests["srcs"] = src_ds
            digests["incs"] = inc_ds

            logger.info(f"{name}: Last source digests: {src_ds_lock}")
            logger.info(f"{name}: Current source digests: {src_ds}")
            logger.info(f"{name}: Last include digests: {inc_ds_lock}")
            logger.info(f"{name}: Current include digests: {inc_ds}")

            if (src_ds, inc_ds) != (src_ds_lock, inc_ds_lock):
                changed = True
        else:
            logger.info(f"{name}: Skipping checks for source updates")
    else:
        logger.info(f"{name}: No source defined")

    # if nvts has updated, check queries
    if queries_updated:
        logger.info(f"{name}: Checking for query updates")

        lang.find_queries()
        qry_ds = lang.query_digests()
        digests["queries"] = qry_ds

        logger.info(f"{name}: Last query digests: {qry_ds_lock}")
        logger.info(f"{name}: Current query digests: {qry_ds}")

        if qry_ds != qry_ds_lock:
            changed = True

    return changed, lang, cmt, digests


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    os.makedirs(BUILD_DIR, exist_ok=True)
    os.makedirs(SRCPKG_DIR, exist_ok=True)

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
    with open(LOCK_FILE, "rb") as f:
        lock = json.load(f)
    # with open(MANIFEST_FILE, "rb") as f:
    #    manifest = json.load(f)

    nvts_update, nvts_commit = check_nvts(lock.get("nvim-treesitter"))
    lock["nvim-treesitter"] = nvts_commit

    langs_lock = lock.get("languages", {})
    lock["languages"] = langs_lock

    updated = []
    failed = []

    for name, opts in config.items():
        try:
            lang_lock = langs_lock.get(name, {})

            lang_update, lang, lang_commit, lang_digests = check_lang(
                lang_lock, name, opts, nvts_update
            )

            if lang_update:
                logger.info(f"{name}: Creating source package")

                lang.ensure_source(BUILD_DIR / lang.name)
                ensure_nvts()
                lang.find_queries()

                with zipfile.ZipFile(
                    SRCPKG_DIR / f"{NAME_PREFIX}{name}.zip",
                    "w",
                    compression=zipfile.ZIP_DEFLATED,
                ) as ar:
                    lang.package_source(ar)

                updated.append(name)
            else:
                logger.info(f"{name}: Skipping creation of source package")

            if lang_commit:
                lang_lock["commit"] = lang_commit

            if "files" not in lang_lock:
                lang_lock["files"] = {}

            for k, v in lang_digests.items():
                lang_lock["files"][k] = v

            langs_lock[name] = lang_lock
        except Exception as e:
            logger.error(f"{name}: Error: {repr(e)}")
            failed.append(name)

    with open(LOCK_FILE, "w") as f:
        json.dump(lock, f, indent=4)

    logger.info(f"Created source packages for: {' '.join(updated)}")
    logger.info(f"Failed to create source packages for: {' '.join(failed)}")
