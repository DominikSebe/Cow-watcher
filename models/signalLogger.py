from PySide6.QtCore import QObject, Signal
from proglog import ProgressBarLogger

class SignalLogger(QObject, ProgressBarLogger):
    def __init__(self, parent: QObject = None, init_state = None) -> None:
        QObject.__init__(self, parent)
        ProgressBarLogger.__init__(self, init_state)

    loggerCalled = Signal(dict, name='loggerCalled', arguments=['param'])

    def __call__(self, **kw):
        self.loggerCalled.emit(kw.copy())
        return super().__call__(**kw)
        