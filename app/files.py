"""Asset download endpoint.

`resolve_asset` maps a user-supplied relative path onto the asset root and
refuses anything that escapes it. The containment check is the security
control this demo is built around: it is three lines, it is easy to "simplify"
away, and removing it turns a static-file helper into arbitrary file read.
"""

from __future__ import annotations

import os
from pathlib import Path


class AssetError(ValueError):
    """Raised when a requested asset path is rejected."""


def resolve_asset(asset_root: str | os.PathLike[str], requested: str) -> Path:
    """Return the on-disk path for ``requested`` inside ``asset_root``.

    Raises ``AssetError`` when the request is empty, absolute, or resolves
    (after following symlinks) to a location outside the asset root.
    """
    if not requested or requested.strip() != requested:
        raise AssetError("empty or padded asset path")
    if os.path.isabs(requested):
        raise AssetError("absolute asset paths are not allowed")

    root = Path(asset_root).resolve()
    candidate = (root / requested).resolve()

    # Containment guard: the resolved path must stay under the resolved root.
    # ``resolve()`` follows symlinks, so a symlink inside the asset tree that
    # points outside it is rejected here as well.
    if root != candidate and root not in candidate.parents:
        raise AssetError(f"asset path escapes the asset root: {requested!r}")

    if not candidate.is_file():
        raise AssetError(f"asset not found: {requested!r}")
    return candidate


def read_asset(asset_root: str | os.PathLike[str], requested: str) -> bytes:
    """Read an asset's bytes after validating the path."""
    return resolve_asset(asset_root, requested).read_bytes()
