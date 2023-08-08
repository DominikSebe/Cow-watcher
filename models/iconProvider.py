from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtQml import QQmlImageProviderBase
from PySide6.QtWidgets import QStyle
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize

class IconProvider(QQuickImageProvider):
    """
    Provides the built-in standard Icons of a style as pixmaps to be used in QML.
    """
    def __init__(self, style: QStyle) -> None:
        self._style = style
        super().__init__(QQmlImageProviderBase.ImageType.Pixmap)

    def requestPixmap(self, id: str, size: QSize, requestedSize: QSize) -> QPixmap:
        return QStyle.standardIcon(self._style, QStyle.StandardPixmap[id]).pixmap(requestedSize)