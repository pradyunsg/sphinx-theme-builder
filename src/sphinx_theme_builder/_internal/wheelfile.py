"""A helper class to make it easier to generate a wheel.
"""

import hashlib
import os
import posixpath
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import IO, List, Optional, Tuple, Type

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


@dataclass
class RecordEntry:
    """A single entry in a RECORD file."""

    path: str
    hash_: str
    size: str

    def to_line(self) -> str:
        return ",".join((self.path, self.hash_, self.size))


class WheelFile:
    """A helper class to generate wheels."""

    def __init__(
        self,
        path: Path,
        tracked_files: Optional[Tuple[str, ...]],
        compiled_assets: Tuple[str, ...],
    ) -> None:
        self._path = path
        self._tracked_files = tracked_files
        self._compiled_assets = compiled_assets
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

    def _exclude(self, path: Path) -> bool:
        # Exclude compiled pyc files.
        if path.name == "__pycache__":
            return True

        # Definitely include compiled assets.
        if path.as_posix() in self._compiled_assets:
            return False

        # Exclude things that are excluded from version control.
        if self._tracked_files is not None:
            if os.fsdecode(path) not in self._tracked_files:
                return True

        return False

    @property
    def name(self) -> str:
        """Name of the wheel."""
        return self._path.name

    def write_record(self, *, dest: str) -> None:
        """Write the record, in the provided destination.

        :param dest: The exact ``{package}-{version}.dist-info/RECORD`` to write to.
        """
        # DEBUG: write_record(dest={dest!r})
        assert self._zipfile.fp is not None

        self._records.append(RecordEntry(dest, "", ""))
        lines = [record.to_line() for record in self._records]
        self._zipfile.writestr(dest, data="\n".join(lines))

    def add_string(self, content: str, *, dest: str) -> None:
        """Add a file at ``dest``, with the given ``content``."""
        # DEBUG: add_string({content!r}, dest={dest!r})
        assert self._zipfile.fp is not None

        data = content.encode()
        self._zipfile.writestr(dest, data=data)
        self._records.append(
            RecordEntry(
                path=dest,
                hash_=hashlib.new(_HASH_ALGORITHM, data=data).hexdigest(),
                size=str(len(data)),
            )
        )

    def add_file(self, file: Path, *, dest: str) -> None:
        """Add a file at ``dest``, with the contents of ``file``."""
        # DEBUG: add_file({file!r}, dest={dest!r})
        assert self._zipfile.fp is not None

        if self._exclude(file):
            # DEBUG: excluded {file}
            return

        # Copy the file object.
        zipinfo = zipfile.ZipInfo.from_file(file, dest)
        with file.open("rb") as source_stream:
            with self._zipfile.open(zipinfo, "w") as dest_stream:
                hash_, size = copyfileobj_with_hashing(
                    source_stream, dest_stream, hash_algorithm=_HASH_ALGORITHM
                )
        self._records.append(
            RecordEntry(
                path=dest,
                hash_=hash_,
                size=str(size),
            )
        )

    def add_directory(self, directory: Path, *, dest: str) -> None:
        """Add the directory to the archive, recursively."""
        # DEBUG: add_directory({directory!r}, dest={dest!r})
        assert directory.is_dir()
        assert self._zipfile.fp is not None

        if self._exclude(directory):
            # DEBUG: excluded {directory}
            return

        for item in sorted(directory.iterdir()):
            if item.is_dir():
                self.add_directory(item, dest=posixpath.join(dest, item.name))
            else:
                self.add_file(item, dest=posixpath.join(dest, item.name))
