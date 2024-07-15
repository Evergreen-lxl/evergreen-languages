import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SRC_PATH = Path("src/")
INC_PATH = Path("src/")
PARSER_FILE = SRC_PATH / "parser.c"
SCANNER_FILE = SRC_PATH / "scanner.c"
INC_FILES = [
    INC_PATH / "tree_sitter/alloc.h",
    INC_PATH / "tree_sitter/array.h",
    INC_PATH / "tree_sitter/parser.h",
]

DEFAULT_CSTD = "c11"


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
        for inc_src in INC_FILES:
            if (dir / inc_src).exists():
                logger.info(f"{name}: Found {inc_src.name}")
                self.incs.append(inc_src)
            else:
                logger.info(f"{name}: No {inc_src.name} found")

    def get_makefile(self) -> str:
        return (
            "STRIP ?= strip --strip-unneeded\n"
            "CFLAGS ?= -Os\n"
            f"CFLAGS += -fPIC -std={DEFAULT_CSTD}\n"
            "SOEXT ?= so\n"
            "\n"
            f"INCS := -I{INC_PATH}\n"
            f"SRCS := {' '.join(map(str, self.srcs))}\n"
            "OBJS := $(SRCS:.c=.o)\n"
            f"SOFILE := parser.$(SOEXT)\n"
            "\n"
            "all: _all\n"
            "_all: $(SOFILE)\n"
            "\n"
            "$(SOFILE): $(OBJS)\n"
            "\t$(CC) -shared -o $@ $^ $(LDFLAGS)\n"
            "\t$(STRIP) $@\n"
            "\n"
            "%.o: %.c\n"
            "\t$(CC) -c -o $@ $< $(CFLAGS) $(INCS)\n"
            "\n"
            "clean:\n"
            "\t$(RM) $(OBJS) $(SOFILE)\n"
            "\n"
            ".PHONY: all _all clean\n"
        )
