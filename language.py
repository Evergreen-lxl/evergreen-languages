import hashlib
import logging
import os
import subprocess
import zipfile
from pathlib import Path
from source import Source

logger = logging.getLogger(__name__)

QUERY_PATH = Path("queries")
QUERY_FILES = ["highlights.scm"]


class Language:
    def __init__(
        self, name: str, remote: str | None, queries_dir: Path, patterns: list[str]
    ):
        self.name = name
        self.remote = remote

        self.queries_dir = queries_dir
        self.queries: list[str] = []

        self.deps: set[str] = set()
        self.source: Source | None = None

        self.patterns = patterns

    def ensure_source(self, path: Path):
        if not self.remote:
            return

        if self.source:
            logger.info(f"{self.name}: Already fetched source")
            return

        logger.info(f"{self.name}: Fetching source")
        os.makedirs(path, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", self.remote, path],
            stderr=subprocess.DEVNULL,
        )
        self.source = Source(self.name, path)

    def find_queries(self):
        if self.queries:
            return

        for query in QUERY_FILES:
            if (self.queries_dir / query).exists():
                self.queries.append(query)

            with open(self.queries_dir / query, "r") as f:
                while True:
                    line = f.readline()
                    if not line or line[0] != ";":
                        break

                    if line.startswith("; inherits: "):
                        self.deps |= set(dep.strip() for dep in line[12:].split(","))

    @staticmethod
    def digests(dir: Path, files: list[Path] | list[str]):
        digests = {}
        for file in files:
            fpath = dir / file
            with open(fpath, "rb") as f:
                digests[fpath.name] = hashlib.file_digest(f, "sha256").hexdigest()

        return digests

    def src_digests(self):
        assert self.source
        return Language.digests(self.source.dir, self.source.srcs)

    def inc_digests(self):
        assert self.source
        return Language.digests(self.source.dir, self.source.incs)

    def query_digests(self):
        return Language.digests(self.queries_dir, self.queries)

    def package_source(self, ar: zipfile.ZipFile):
        assert self.queries

        if self.source:
            for src in self.source.srcs:
                ar.write(self.source.dir / src, arcname=src)

            for inc in self.source.incs:
                ar.write(self.source.dir / inc, arcname=inc)

            ar.writestr("Makefile", self.source.get_makefile())

        for query in self.queries:
            ar.write(self.queries_dir / query, arcname=QUERY_PATH / query)

        ar.writestr("init.lua", self.get_initlua())

    def get_initlua(self) -> str:
        ps = ", ".join(f"'{p}'" for p in self.patterns)
        return (
            "-- mod-version: 3\n"
            "local evergreen_languages = require 'plugins.evergreen.languages'\n"
            "evergreen_languages.addDef {\n"
            f"\tname = '{self.name}',\n"
            f"\tfiles = {{ {ps} }},\n"
            f"\tpath = USERDIR .. '/plugins/evergreen_{self.name}',\n"
            "\tqueryFiles = {},\n"
            "}\n"
        )
