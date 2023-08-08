from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtQml import QQmlEngine
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy
)
from PySide6.QtCore import Signal

class CentralWidget(QQuickWidget):
    clipClicked = Signal(int, name='clipClicked', arguments=['clipIndex'])
    cameraChangeRequested = Signal(str, name='cameraChangeRequested', arguments=['direction'])
    warningRequested = Signal(str, name='warningRequested', arguments=['warning_text'])

    def __init__(self, qmlEngine: QQmlEngine, parent: QWidget | None):
        super().__init__(qmlEngine, parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
