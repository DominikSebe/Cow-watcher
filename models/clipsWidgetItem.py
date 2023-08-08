from PySide6.QtWidgets import QTreeWidgetItem

class VideoFileWidgetItem(QTreeWidgetItem):
    def __init__(self, source: str, *args, **kwargs):
        self._source = source
        super().__init__(*args, **kwargs)

    @property
    def source(self):
        return self._source

    @property
    def name(self):
        return self.source.split('/')[-1]