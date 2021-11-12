"""A helper class to make it easier to generate a wheel.
"""

import hashlib
import os
import posixpath
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import TracebackType
from typing import IO, List, Optional, Set, Tuple, Type

_HASH_ALGORITHM = "sha256"

# Borrowed from CPython's shutil.py
# https://github.com/python/cpython/blob/v3.9.1/Lib/shutil.py#L52
_WINDOWS = os.name == "nt"
_COPY_BUFSIZE = 1024 * 1024 if _WINDOWS else 64 * 1024


# Borrowed from pradyunsg/installer
# https://github.com/pradyunsg/installer/blob/0.4.0/src/installer/utils.py#L95
def copyfileobj_with_hashing(
    source: IO[bytes],
    dest: IO[bytes],
    hash_algorithm: str,
) -> Tuple[str, int]:
    """Copy a buffer while computing the content's hash and size.

    Copies the source buffer into the destination buffer while computing the
    hash of the contents. Adapted from :any:`shutil.copyfileobj`.

    :param source: buffer holding the source data
    :param dest: destination buffer
    :param hash_algorithm: hashing algorithm
    :return: size, hash digest of the contents
    """

    hasher = hashlib.new(hash_algorithm)
    size = 0
    while True:
        buf = source.read(_COPY_BUFSIZE)
        if not buf:
            break
        hasher.update(buf)
        dest.write(buf)
        size += len(buf)

    return hasher.hexdigest(), size


def include_parent_paths(posix_style_paths: List[str]) -> Tuple[str, ...]:
    names: Set[str] = set()
    for path_str in posix_style_paths:
        path = PurePosixPath(path_str)
        names.update(parent.as_posix() for parent in path.parents)
        names.add(path_str)
    return tuple(names)


@dataclass
class RecordEntry:
    """A single entry in a RECORD file."""

    path: str
    hash_value: str
    hash_algorithm: str
    size: str

    def to_line(self) -> str:
        if self.hash_value:
            return ",".join(
                (self.path, f"{self.hash_algorithm}={self.hash_value}", self.size)
            )
        else:
            assert not self.hash_algorithm
            return ",".join((self.path, "", self.size))


class WheelFile:
    """A helper class to generate wheels."""

    def __init__(
        self,
        *,
        path: Path,
        tracked_names: Optional[Tuple[str, ...]],
        compiled_assets: Tuple[str, ...],
    ) -> None:
        self._path = path
        self._tracked_names = tracked_names
        self._compiled_assets = compiled_assets
        self._compiled_assets_and_parents = include_parent_paths(list(compiled_assets))
        self._zipfile = zipfile.ZipFile(path, mode="w")
        self._records: List[RecordEntry] = []

    def __enter__(self) -> "WheelFile":
        return self

    def __exit__(
        self,
        type_: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._zipfile.close()

    def _exclude(self, path: Path, *, base: Optional[Path]) -> bool:
        # Exclude compiled pyc files.
        if path.name == "__pycache__":
            return True

        # Include all not-based-on-source-tree files.
        if base is None:
            return False

        normalised_path = path.relative_to(base).as_posix()

        # Definitely include compiled assets.
        if normalised_path in self._compiled_assets_and_parents:
            return False

        for asset_path in self._compiled_assets:
            if normalised_path.startswith(asset_path + "/"):
                return False

        # Exclude things that are excluded from version control.
        if self._tracked_names is not None:
            if normalised_path not in self._tracked_names:
                return True

        # If we're here, we've excluded all the files that needed to be excluded.
        return False

    @property
    def name(self) -> str:
        """Name of the wheel."""
        return self._path.name

    def write_record(self, *, dest: str) -> None:
        """Write the record, in the provided destination.

        :param dest: The exact ``{package}-{version}.dist-info/RECORD`` to write to.
        """
        assert self._zipfile.fp is not None

        self._records.append(RecordEntry(dest, "", "", ""))
        lines = [record.to_line() for record in self._records]
        self._zipfile.writestr(dest, data="\n".join(lines))

    def add_string(self, content: str, *, dest: str) -> None:
        """Add a file at ``dest``, with the given ``content``."""
        assert self._zipfile.fp is not None

        data = content.encode()
        self._zipfile.writestr(dest, data=data)
        self._records.append(
            RecordEntry(
                path=dest,
                hash_algorithm=_HASH_ALGORITHM,
                hash_value=hashlib.new(_HASH_ALGORITHM, data=data).hexdigest(),
                size=str(len(data)),
            )
        )

    def add_file(self, file: Path, *, dest: str, base: Optional[Path]) -> None:
        """Add a file at ``dest``, with the contents of ``file``."""
        assert self._zipfile.fp is not None

        if self._exclude(file, base=base):
            return

        # Copy the file object.
        zipinfo = zipfile.ZipInfo.from_file(file, dest)
        with file.open("rb") as source_stream:
            with self._zipfile.open(zipinfo, "w") as dest_stream:
                hash_value, size = copyfileobj_with_hashing(
                    source_stream, dest_stream, hash_algorithm=_HASH_ALGORITHM
                )
        self._records.append(
            RecordEntry(
                path=dest,
                hash_algorithm=_HASH_ALGORITHM,
                hash_value=hash_value,
                size=str(size),
            )
        )

    def add_directory(
        self, directory: Path, *, dest: str, base: Optional[Path]
    ) -> None:
        """Add the directory to the archive, recursively."""
        assert directory.is_dir()
        assert self._zipfile.fp is not None

        if self._exclude(directory, base=base):
            return

        for item in sorted(directory.iterdir()):
            if item.is_dir():
                self.add_directory(
                    item, dest=posixpath.join(dest, item.name), base=base
                )
            else:
                self.add_file(item, dest=posixpath.join(dest, item.name), base=base)
