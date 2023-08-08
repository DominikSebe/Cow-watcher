from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtQml import qmlRegisterType
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPalette
)

class Playhead(QQuickPaintedItem):
    def paint(self, painter: QPainter) -> None:
        path = QPainterPath()
        path.moveTo(self.width(), 0.0)

        path.lineTo(self.width()/2.0, self.height())
        path.lineTo(0, 0)

        palette = QPalette()
        painter.fillPath(path, palette.color(QPalette.ColorRole.WindowText))

    @staticmethod
    def registerType(library: str, version_major: int, version_minor: int, name: str):
        """
        Register `Playhead` type in QML.

        ## Example
        ### Register in python
        ```python
            Playhead.registerType('Custom', 1, 0, 'Playhead')
        ```
        ### Use in QML
        ```qml
            import Cutsom 1.0

            Playhead {
                ...
            }
        ```

        :param str libary: Module to import `Playhead` from in QML.
        :param int version_major: Major version of the module.
        :paramt int version_minor: Minor version of the module.
        :param str name: Name of the type inside QML.
        """
        qmlRegisterType(Playhead, library, version_major, version_minor, name)