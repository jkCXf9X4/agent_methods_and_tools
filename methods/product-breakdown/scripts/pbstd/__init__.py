"""pbstd — the reusable product-breakdown standard.

Config-driven checks and register generation for the D2 breakdown model: a
seven-layer current-state hierarchy plus one flat, dated decision stream, with
registers generated from record front-matter.

The standard is described by a ``pb.toml`` at the breakdown root (the directory
that contains ``decisions/``). Every value also has a built-in default, so the
tools run with no config at all. See the repository README for the schema and how
to consume the standard from another repository.
"""
from .config import Config, find_root, load_config, resolve_root

__all__ = ["Config", "find_root", "load_config", "resolve_root"]
__version__ = "0.1.0"
