from os import path
from moviepy.editor import VideoFileClip
from PySide6.QtCore import QObject, Property, Signal

class ClipInfo(QObject):
    """
    Holds metadata about a clip of a video file.
    """
    def __init__(self, source: str = ...):
        super().__init__()

        self._source = ''
        self._name = ''
        self._totalFrames: int = 0
        self._frameRate = 0
        self._playRate = 1.0
        self._inPoint = -1
        self._outPoint = -1

        if source != ...:
            if not path.exists(source):
                raise FileNotFoundError(
                    f'File \'{source}\' does not exist'
                )

            file = VideoFileClip(source)
            self._source = file.filename
            self._name = file.filename.split('/')[-1]
            self._totalFrames: int = file.reader.nframes
            self._frameRate: int = file.fps

            file.close()

    ### Destructor
    def __del__(self):
        pass

    ### Signals (PySide)
    clipChanged = Signal(str, int, int, name='clipChanged', arguments=['source', 'totalFrames', 'frameRate'])
    nameChanged = Signal(str, name='nameChanged', arguments=['name'])
    playRateChanged = Signal(float, name='playRateChanged', arguments=['playRate'])
    inPointChanged = Signal(int, name='inPointChanged', arguments=['inPoint'])
    outPointChanged = Signal(int, name='outPointChanged', arguments=['outPoint'])
    validChanged = Signal(bool, name='validChanged', arguments=['valid'])

    ### Proprerties (PySide)
    ## Getters
    @Property(str, notify=clipChanged)
    def source(self):
        return self._source

    @Property(str, notify=nameChanged)
    def name(self):
        return self._name

    @Property(int)
    def totalFrames(self):
        return self._totalFrames

    @Property(int)
    def frameRate(self):
        return self._frameRate

    @Property(int, notify=playRateChanged)
    def playRate(self):
        return self._playRate

    @Property(int, notify=inPointChanged)
    def inPoint(self):
        return self._inPoint

    @Property(int, notify=outPointChanged)
    def outPoint(self):
        return self._outPoint

    @Property(int)
    def frameDuration(self):
        return self._outPoint - self._inPoint

    @Property(float)
    def timeDuration(self):
        print(f"Frames: {self._outPoint - self._inPoint}")
        print(f"Dividing by {((self._frameRate if self._frameRate != 0 else 24) * self._playRate)}")
        return (self._outPoint - self._inPoint) / ((self._frameRate if self._frameRate != 0 else 24) * self._playRate)

    @Property(bool, notify=validChanged)
    def valid(self):
        return -1 < self._inPoint < self._outPoint and self._inPoint < self._outPoint <= self._totalFrames

    ## Setters
    @source.setter
    def source(self, value: str):
        if not path.exists(value):
            raise FileNotFoundError(
                f'File \'{value}\' does not exist'
            )
        if self._source != value:
            timeDur = self.timeDuration
            oldOutPoint = self._outPoint
            oldValid = self.valid

            file = VideoFileClip(value)
            self._source = file.filename
            self._totalFrames:int = file.reader.nframes
            self._frameRate: int = file.fps

            file.close()

            print(f'Original dur: {timeDur}')
            self._outPoint = self._inPoint + timeDur * (self._frameRate if self._frameRate != 0 else 24) / self._playRate
            print(f'New outpoint: {self._outPoint:2f}')

            self.clipChanged.emit(self._source, self._totalFrames, self._frameRate)

            if self._outPoint != oldOutPoint:
                self.outPointChanged.emit(self._outPoint)
                
            if self._name != self._source.split('/')[-1]:
                self._name = self._source.split('/')[-1]
                self.nameChanged.emit(self._name)

            if self.valid != oldValid:
                self.validChanged.emit(self.valid)

    @name.setter
    def name(self, value: str):
        if self._name != value:
            self._name = value
            self.nameChanged.emit(self._name)

    @playRate.setter
    def playRate(self, value: float):
        if self._playRate != value:
            self._playRate = value
            self.playRateChanged.emit(self._playRate)

    @inPoint.setter
    def inPoint(self, value: int):
        if 0 <= value < (self._outPoint if self._outPoint > -1 else self._totalFrames):
            if self._inPoint != value:
                oldValid = self.valid

                self._inPoint = value
                self.inPointChanged.emit(self._inPoint)

                if self.valid != oldValid:
                    self.validChanged.emit(self.valid)

    @outPoint.setter
    def outPoint(self, value: int):
        if self._inPoint < value <= self._totalFrames:
            if self._outPoint != value:
                oldValid = self.valid

                self._outPoint = value
                self.outPointChanged.emit(self._outPoint)

                if self.valid != oldValid:
                    self.validChanged.emit(self.valid)