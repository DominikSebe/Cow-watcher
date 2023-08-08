from . import eng, hu

__all__ = [
    'eng',
    'hu'
]

def importLanguage(code: str):
    """
    Import a language modul.

    :paramt str code: Two-letter code for a language. The official name for the rquired codes is the ISO 639-1 codes.
    """
    match(code.lower()):
        case 'hu':
            return hu;
        case 'eng':
            return eng;