
from .playhead import Playhead

def registerTypes(library: str, major_version: int, minor_version: int):
    """
    Register all types in timelineItems in QML with their class names.

    :param str libary: Module to import custom types from.
    :param int version_major: Major version of the module.
    :paramt int version_minor: Minor version of the module.
    """
    Playhead.registerType(library, major_version, minor_version, Playhead.__name__)

__all__ = [
    'Playhead',
    'registerTypes'
]