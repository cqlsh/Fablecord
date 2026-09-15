"""
Fablecord
~~~~~~~~~

A fast Discord API wrapper for Python, built on the standard library alone.

:copyright: (c) 2026-present cqlsh
:license: MIT, see LICENSE for more details.

"""

import logging
import re
from typing import Literal, NamedTuple, Self

__title__ = "fablecord"
__author__ = "cqlsh"
__license__ = "MIT"
__copyright__ = "Copyright 2026-present cqlsh"
__version__ = "0.1.0a0"

type ReleaseLevel = Literal["alpha", "beta", "candidate", "final"]

_VERSION_PATTERN = re.compile(
    r"""
    (?P<major>\d+) \. (?P<minor>\d+) \. (?P<micro>\d+)
    (?: (?P<level>a|b|rc) (?P<serial>\d+) )?
    """,
    re.VERBOSE
)

_RELEASE_LEVELS: dict[str, ReleaseLevel] = {"a": "alpha", "b": "beta", "rc": "candidate"}

class VersionInfo(NamedTuple):
    """
    Represents the version of the installed Fablecord package.

    This mirrors :data:`sys.version_info` so version checks read the same
    way as they do for the interpreter itself.

    Attributes
    -----------
    major: :class:`int`
        The major version. Breaking changes bump this number.
    minor: :class:`int`
        The minor version. New features bump this number.
    micro: :class:`int`
        The micro version. Bug fixes bump this number.
    releaselevel: :class:`str`
        One of ``alpha``, ``beta``, ``candidate`` or ``final``.
    serial: :class:`int`
        The serial number within the release level.
    """

    major: int
    minor: int
    micro: int
    releaselevel: ReleaseLevel
    serial: int

    @classmethod
    def from_string(cls, version: str) -> Self:
        """
        Parses a version string such as ``2.6.0rc1`` into a :class:`VersionInfo`.

        Only the release segment and an optional pre-release suffix are
        supported, which is exactly what :data:`__version__` uses.

        Parameters
        -----------
        version: :class:`str`
            The version string to parse.

        Raises
        -------
        ValueError
            The string is not a valid version.

        Returns
        --------
        :class:`VersionInfo`
            The parsed version.
        """
        match = _VERSION_PATTERN.fullmatch(version)
        if match is None:
            raise ValueError(f"invalid version string: {version!r}")

        major = int(match["major"])
        minor = int(match["minor"])
        micro = int(match["micro"])

        releaselevel: ReleaseLevel = "final"
        serial = 0
        if match["level"] is not None:
            releaselevel = _RELEASE_LEVELS[match["level"]]
            serial = int(match["serial"])

        return cls(major=major, minor=minor, micro=micro, releaselevel=releaselevel, serial=serial)

version_info: VersionInfo = VersionInfo.from_string(__version__)

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["ReleaseLevel", "VersionInfo", "version_info"]