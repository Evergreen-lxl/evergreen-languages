import logging
from pathlib import Path
from string import Template

from defs import *

logger = logging.getLogger(__name__)

with open("Makefile.in", "r") as f:
    MAKEFILE_TEMPLATE = Template(f.read())


class Source:
    def __init__(self, name: str, dir: Path):
        self.name = name
        self.dir = dir

        if (dir / PARSER_FILE).exists():
            logger.info(f"{name}: Found parser.c")
            self.srcs = [PARSER_FILE]
        else:
            logger.error(f"{name}: No parser.c found")
            return

        if (dir / SCANNER_FILE).exists():
            logger.info(f"{name}: Found scanner.c")
            self.srcs.append(SCANNER_FILE)
        else:
            logger.info(f"{name}: No scanner.c found")

        self.incs = []
        for inc_src in (dir / INC_PATH).rglob("*.h"):
            logger.info(f"{name}: Found {inc_src.relative_to(dir)}")
            self.incs.append(inc_src.relative_to(dir))

    def get_makefile(self) -> str:
        return MAKEFILE_TEMPLATE.substitute(
            CSTD=DEFAULT_CSTD, INC_PATH=INC_PATH, SRCS=" ".join(map(str, self.srcs))
        )
