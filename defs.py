from pathlib import Path

CONFIG_FILE = Path("languages.toml")
LOCK_FILE = Path("lock.json")
MANIFEST_FILE = Path("manifest.json")

BUILD_DIR = Path("build")
SRCPKG_DIR = Path("srcpkg")
DIST_DIR = Path("dist")

NVTS_URL = "https://github.com/nvim-treesitter/nvim-treesitter.git"
NVTS_DIR = BUILD_DIR / "nvim-treesitter"
NVTS_QUERY_DIR = NVTS_DIR / "queries"

QUERY_PATH = Path("queries")
QUERY_FILES = ["highlights.scm"]

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

NAME_PREFIX = 'evergreen_'
