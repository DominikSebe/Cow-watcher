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
        self._frames = 0
        self._frameRate = 0
        self._playRate = 1.0
        self._inPoint = -1
        self._outPoint = -1
        self._duration = 0.0

        if source != ...:
            self.source = source

    ### Destructor
    def __del__(self):
        pass

    ### Signals (PySide)
    sourceChanged = Signal(str, name='sourceChanged', arguments=['source'])
    frameRateChanged = Signal(int, name="frameRateChanged", arguments=['frameRate'])
    durationChanged = Signal(int, name='durationChanged', arguments=['duration'])
    nameChanged = Signal(str, name='nameChanged', arguments=['name'])
    playRateChanged = Signal(float, name='playRateChanged', arguments=['playRate'])
    inPointChanged = Signal(int, name='inPointChanged', arguments=['inPoint'])
    outPointChanged = Signal(int, name='outPointChanged', arguments=['outPoint'])
    validityChanged = Signal(bool, name='valididtyChanged', arguments=['valid'])

    ### Proprerties (PySide)
    ## Getters
    @Property(str, notify=sourceChanged)
    def source(self):
        return self._source

    @Property(str, notify=nameChanged)
    def name(self):
        return self._name if self._name != '' else self._source

    @Property(int)
    def totalFrames(self):
        return self._frames

    @Property(int, notify=frameRateChanged)
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
    def length(self):
        inPoint = self._inPoint if 0 <= self._inPoint else 0
        outPoint = self._outPoint if 0 < self._outPoint else self._duration

        return outPoint - inPoint

    @Property(float, notify=durationChanged)
    def duration(self):
        return self._duration

    @Property(bool, notify=validityChanged)
    def valid(self):
        inPoint = self._inPoint if 0 <= self._inPoint else 0
        outPoint = self._outPoint if 0 < self._outPoint else self._duration

        return 0 < outPoint - inPoint <= self._duration and outPoint <= self._duration

    ## Setters
    @source.setter
    def source(self, value: str):
        if not path.exists(value):
            raise FileNotFoundError(
                f'File \'{value}\' does not exist'
            )
        
        if self._source != value:
            valid = self.valid

            file = VideoFileClip(value)

            self._source = file.filename
            self.sourceChanged.emit(self._source)

            self._frames: int = file.reader.nframes

            self._frameRate: int = file.fps
            self.frameRateChanged.emit(self._frameRate)

            self._duration: float = file.duration * 1000
            self.durationChanged.emit(self._duration)

            file.close()

            if self.valid != valid:
                self.validityChanged.emit(self.valid)

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
        valueValid = False

        if value == -1:
            valueValid = True

        elif self._outPoint >= 0:
            valueValid = (0 <= value < self._outPoint)

        else:
            valueValid = (0 <= value < self._duration)

        if valueValid:
            valid = self.valid
            
            self._inPoint = value
            self.inPointChanged.emit(self._inPoint)

            if self.valid != valid:
                self.validityChanged.emit(self.valid)

    @outPoint.setter
    def outPoint(self, value: int):
        inPoint = self._inPoint if 0 <= self._inPoint else 0

        if value == -1 or (inPoint < value < self._duration):
            valid = self.valid

            self._outPoint = value
            self.outPointChanged.emit(self._outPoint)

            if self.valid != valid:
                self.validityChanged.emit(valid)