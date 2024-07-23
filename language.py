import hashlib
import logging
import os
import subprocess
import zipfile
from pathlib import Path
from string import Template

from defs import *
from source import Source

logger = logging.getLogger(__name__)

with open("init.lua.in", "r") as f:
    INIT_LUA_TEMPLATE = Template(f.read())


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
        subprocess.run(["git", "clone", "--depth", "1", self.remote, path])
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
        logger.info(f"{self.name}: Found dependencies: {', '.join(sorted(self.deps))}")

    @staticmethod
    def digests(dir: Path, files: list[Path] | list[str]):
        digests = {}
        for file in files:
            fpath = dir / file
            with open(fpath, "rb") as f:
                digests[str(fpath.relative_to(dir))] = hashlib.file_digest(
                    f, "sha256"
                ).hexdigest()

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

            lang_license = next(self.source.dir.glob("LICENSE*", case_sensitive=False), None)
            if lang_license:
                ar.write(lang_license, arcname=LANGUAGE_LICENSE_FILE)

        for query in self.queries:
            ar.write(
                self.queries_dir / query,
                arcname=QUERY_PATH / query,
            )

        ar.writestr("init.lua", self.get_initlua())

        ar.write("LICENSE", arcname=LICENSE_FILE)
        ar.write(NVTS_LICENSE_FILE, arcname=QUERY_LICENSE_FILE)

    def get_initlua(self) -> str:
        ps = ", ".join(f"'{p}'" for p in self.patterns)
        so = "'parser{SOEXT}'" if self.source else "nil"

        return INIT_LUA_TEMPLATE.substitute(
            MODVERSION=MODVERSION, NAME=self.name, PATTERNS=ps, SOFILE_NAME=so
        )
