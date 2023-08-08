from PySide6.QtCore import (
    QObject,
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
    Property,
    QByteArray,
    Slot
)
from typing import Any, overload
from enum import IntEnum, auto, unique
from .clipInfo import ClipInfo

TRACK_ID = 128

class TimelineModel(QAbstractItemModel):
   
    ### Constructor
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._position = 0
        self._currentIndex = -1
        self._selectedIndex = -1
        self._scaleFactor = 1.0
        self._trackHeight = 100
        self._storedSources : list[str] = []
        self._clips: list[ClipInfo] = []
    
    ### Destructor
    def __del__(self):
        pass
    
    ### Enums (Roles)
    @unique
    class Roles(IntEnum):
        """
        Hold values for roles of different data types.
        """
        def _generate_next_value_(name: str, start: int, count: int, last_values: list):
            ### Generate the next available value for the enum class
            return Qt.ItemDataRole.UserRole + count

        # Symbolic names and assigned values
        SourceRole = auto()
        NameRole = auto()
        TotalFramesRole = auto()
        FrameRateRole = auto()
        PlayRateRole = auto()
        InPointRole = auto()
        OutPointRole = auto()
        FrameDurationRole = auto()
        TimeDurationRole = auto()
        ValidRole = auto()
        AdjecentRole = auto()
    
    ### Signals
    positionChanged = Signal(int, name='positionChanged', arguments=['position'])
    currentIndexChanged = Signal(int, name='currentIndexChanged', arguments=['index'])
    currentClipChanged = Signal(ClipInfo, name='currentClipChanged', arguments=['clip'])
    selectedIndexChanged = Signal(int, name='selectedIndexChanged', arguments=['index'])
    selectedClipChanged = Signal(ClipInfo, name='selectedClipChanged', arguments=['clip'])
    scaleFactorChanged = Signal(float, name='scaleFacttorChanged', arguments=['scaleFactor'])
    trackHeightChanged = Signal(int, name='trackHeightChanged', arguments=['trackHeight'])
    storedSourcesChanged = Signal(name='storedClipsChanged')

    ### Properties
    ## Getters
    @Property(int, notify=positionChanged)
    def position(self):
        return self._position

    @Property(int, notify=currentIndexChanged)
    def currentIndex(self):
        return self._currentIndex

    @Property(ClipInfo, notify=currentClipChanged)
    def currentClip(self):
        if not(0 <= self._currentIndex < len(self._clips)):
            return None
            
        return self._clips[self._currentIndex]

    @Property(int, notify=selectedIndexChanged)
    def selectedIndex(self):
        return self._selectedIndex

    @Property(ClipInfo, notify=selectedClipChanged)
    def selectedClip(self):
        if self._selectedIndex == -1:
            return None
        return self._clips[self._selectedIndex]

    @Property(float, notify=scaleFactorChanged)
    def scaleFactor(self):
        return self._scaleFactor

    @Property(int, notify=trackHeightChanged)
    def trackHeight(self):
        return self._trackHeight

    @Property(list, notify=storedSourcesChanged)
    def sources(self):
        return self._storedSources

    ## Setters
    @position.setter
    def position(self, value: int):
        if 0 <= value:
            if self._position != value:
                self._position = value
                self.positionChanged.emit(self._position)

                clip = self.atPosition(self._position)
                self.currentClip = clip

    @currentIndex.setter
    def currentIndex(self, value: int):
        if not(-1 <= value < len(self._clips)):
            raise IndexError(f'Value must be between 0 and {len(self._clips)-1} or -1')
        if self._currentIndex != value:
            self._currentIndex = value
            self.currentIndexChanged.emit(self._currentIndex)
            if self._currentIndex == -1:
                self.currentClipChanged.emit(None)
            else:
                self.currentClipChanged.emit(self._clips[self._currentIndex])
        

    @currentClip.setter
    def currentClip(self, value: ClipInfo):
        if value == None:
            self.currentIndex = -1      
            return  

        self.currentIndex = self.indexOf(value)

    @selectedIndex.setter
    def selectedIndex(self, value: int):
        if not(-1 <= value < len(self._clips)):
            raise IndexError(f'Value must be between 0 and {len(self._clips)-1} or -1')
        elif self._selectedIndex != value:
            self._selectedIndex = value
            self.selectedIndexChanged.emit(self._selectedIndex)
            if self._selectedIndex == -1:
                self.selectedClipChanged.emit(None)
            else:
                self.selectedClipChanged.emit(self._clips[self._selectedIndex])

    @selectedClip.setter
    def selectedClip(self, value: ClipInfo):
        if value == None:
            self.selectedIndex = -1
            return
            
        self.selectedIndex = self.indexOf(value)
    
    @scaleFactor.setter
    def scaleFactor(self, value: float):
        if 0.0 < value:
            if self._scaleFactor != value:
                self._scaleFactor = value
                self.scaleFactorChanged.emit(self._scaleFactor)

    @trackHeight.setter
    def trackHeight(self, value: int):
        if 0 <= value:
            if self._trackHeight != value:
                self._trackHeight = value
                self.trackHeightChanged.emit(self._trackHeight)

    ### Implementations
    def index(self, row: int, column: int, parent: QModelIndex = ...):
        # Default value to return is an invalid QModelIndex object
        result = QModelIndex()
        
        # Only the first column is used
        if column > 0:
            return result

        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        if isinstance(parent, QModelIndex) and parent.isValid():
            # If row index is out of range of the underlying list, the index is invalid
            if not(0 <= row < len(self._clips)):
                return result

            # A valid parent indicates that the item is a clip
            # Index of clip: row(index in list), coulmn(0), and row of parent(currently there is only 1 track)
            result = self.createIndex(row, column, parent.row())
        elif row == 0:
            # An invalid parent indicates that the item is the rrack
            # A track has no valid parent and an internal id equal to TRACK_ID constant
            result = self.createIndex(row, column, TRACK_ID)

        return result
        
    def parent(self, child: QModelIndex):
        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        if not child.isValid() or child.internalId() >= TRACK_ID:
            # If the child is invalid or has the TRACK_ID constant or a greater value set as an internal id
            # the child is a top-level track with no parent, and an invalid QModelIndex is returned
            return QModelIndex()
        else: 
            # The child is valid and its internal id is less than the TRACK_ID constant, and is the row index of the track the clip is a part of
            # A QModelIndex with the internal id set to the TRACK_ID constant is returned
            return self.createIndex(child.internalId(), 0, TRACK_ID)

    def rowCount(self, parent: QModelIndex = ...):
        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        if isinstance(parent, QModelIndex) and parent.isValid():
            # The parent is a QModelIndex and valid
            if parent.internalId() < TRACK_ID:
                # If the internal id of the parent is less than the TRACK_ID constant,
                # then it can not be a track, and a clip should have a valid parent
                # and children to be counted
                return 0
            
            # Number of clips in a track
            return len(self._clips)
        
        # Number of tracks (currently 1)
        return 1

    def columnCount(self, parent: QModelIndex = ...) -> int:
        # Columns are unused
        return 1

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlags:
        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        if not index.isValid():
            # Invalid index has no flags
            return None

        # Get default flags for an index
        flags = super().flags(index)

        # An index with an internal id, that is less than the TRACK_ID constant is a clip
        if index.internalId() < TRACK_ID:
            # Clip should never have children, an therefore an extra flag is combined into the default ones
            flags = flags | Qt.ItemFlag.ItemNeverHasChildren
            
        return flags

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        if index.isValid():
            # An index with an internal id, that is less than the TRACK_ID constant is a clip
            if index.internalId() < TRACK_ID:
                # If row index is out of range of the underlying list, the index is invalid
                if not(0 <= index.row() < len(self._clips)):
                    return None

                # Get the ClipInfo object under the row index
                clip = self._clips[index.row()]

                # Return data for the matching role value
                match role:
                    case Qt.ItemDataRole.DisplayRole:
                        return clip.name
                    case self.Roles.SourceRole:
                        return clip.source
                    case self.Roles.NameRole:
                        return clip.name
                    case self.Roles.TotalFramesRole:
                        return clip.totalFrames
                    case self.Roles.FrameRateRole:
                        return clip.frameRate
                    case self.Roles.PlayRateRole:
                        return clip.playRate
                    case self.Roles.InPointRole:
                        return clip.inPoint
                    case self.Roles.OutPointRole:
                        return clip.outPoint
                    case self.Roles.FrameDurationRole:
                        return clip.frameDuration
                    case self.Roles.TimeDurationRole:
                        return clip.timeDuration
                    case self.Roles.ValidRole:
                        return clip.valid
                    case self.Roles.AdjecentRole:
                        return clip.adjecent
                    case _:
                        return clip;
            else:
                # An index with an internal id equal to or greater than the TRACK_ID constant is a track
                # Return data for the matching role value
                match role:
                    case Qt.ItemDataRole.DisplayRole:
                        return "VideoTrack"
                    case self.Roles.SourceRole:
                        return [clip.source for clip in self._clips]
                    case self.Roles.NameRole:
                        return [clip.name for clip in self._clips]
                    case self.Roles.TotalFramesRole:
                        return [clip.totalFrames for clip in self._clips]
                    case self.Roles.FrameRateRole:
                        return [clip.frameRate for clip in self._clips]
                    case self.Roles.PlayRateRole:
                        return [clip.playRate for clip in self._clips]
                    case self.Roles.InPointRole:
                        return [clip.inPoint for clip in self._clips]
                    case self.Roles.OutPointRole:
                        return [clip.outPoint for clip in self._clips]
                    case self.Roles.FrameDurationRole:
                        return [clip.frameDuration for clip in self._clips]
                    case self.Roles.TimeDurationRole:
                        return [clip.timeDuration for clip in self._clips]
                    case self.Roles.ValidRole:
                        return [clip.valid for clip in self._clips]
                    case self.Roles.AdjecentRole:
                        return [clip.adjecent for clip in self._clips]
                    case _:
                        return self._clips;
        return None

    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = ...) -> bool:
        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        if index.isValid():
            # An index with an internal id, that is less than the TRACK_ID constant is a clip
            if index.internalId() < TRACK_ID:
                # If row index is out of range of the underlying list, the index is invalid
                if not(0 <= index.row() < len(self._clips)):
                    return None

                clipIndex = index.row()

                match role:
                    case Qt.ItemDataRole.DisplayRole:
                        self._clips[clipIndex].name = value
                        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                    case self.Roles.SourceRole:
                        changedRoles = [self.Roles.SourceRole, self.Roles.TotalFramesRole, self.Roles.FrameRateRole]

                        onNameChanged = lambda name: changedRoles.append(self.Roles.NameRole)
                        onValidChanged = lambda valid: changedRoles.append(self.Roles.ValidRole)
                        onOutPointChanged = lambda outPoint: changedRoles.append(self.Roles.OutPointRole)

                        self._clips[clipIndex].nameChanged.connect(onNameChanged)
                        self._clips[clipIndex].validChanged.connect(onValidChanged)
                        self._clips[clipIndex].outPointChanged.connect(onOutPointChanged)

                        self._clips[clipIndex].source = value

                        self._clips[clipIndex].nameChanged.disconnect(onNameChanged)
                        self._clips[clipIndex].validChanged.disconnect(onValidChanged)
                        self._clips[clipIndex].outPointChanged.disconnect(onOutPointChanged)

                        self.dataChanged.emit(index, index, changedRoles)
                    case self.Roles.NameRole:
                        self._clips[clipIndex].name = value
                        self.dataChanged.emit(index, index, [self.Roles.NameRole])
                    case self.Roles.PlayRateRole:
                        self._clips[clipIndex].playRate = value
                        self.dataChanged.emit(index, index, [self.Roles.PlayRateRole])
                    case self.Roles.InPointRole:
                        self.layoutAboutToBeChanged.emit()

                        self._clips[clipIndex].inPoint = value
                        self.dataChanged.emit(index, index, [self.Roles.InPointRole])

                        if 0 < clipIndex:
                            self._clips[clipIndex-1].outPoint = value-1
                            self.dataChanged.emit(clipIndex-1, clipIndex-1, [self.Roles.OutPointRole])
                            
                        self.layoutChanged.emit()
                    case self.Roles.OutPointRole:
                        self.layoutAboutToBeChanged.emit()

                        self._clips[clipIndex].outPoint = value
                        self.dataChanged.emit(index, index, [self.Roles.OutPointRole])

                        if clipIndex < len(self._clips) - 1:
                            self._clips[clipIndex+1].inPoint = value+1
                            self.dataChanged.emit(clipIndex+1, clipIndex+1, [self.Roles.InPointRole])

                        self.layoutChanged.emit()
                    case self.Roles.AdjecentRole:
                        if isinstance(value, dict[str, str]) and len(dict) == 0:
                            key, value = tuple(value.items())[0]
                            self._clips[clipIndex].setAdjecent(key, value)
                            return True
                        else:
                            return False
                    case _:
                        if isinstance(value, ClipInfo):
                            self._clips[clipIndex] = value
                            self.dataChanged.emit(index, index)
                            return True

                        return False

                # setData was successful
                return True

        # setData was unsuccessful
        return False

    def insertRows(self, row: int, count: int, parent: QModelIndex | QPersistentModelIndex = ...) -> bool:
        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        # Only a track has children, a track has an internal id equal to or greater than the TRACK_ID constant
        if parent.isValid() and parent.internalId() >= TRACK_ID:
            # Begin row insertion
            self.beginInsertRows(parent, row, row+count-1)
            
            # Change underlying list
            for i in range(row, row+count):
                self._clips.insert(i, ClipInfo())

            # End row insertion
            self.endInsertRows()

            # insertRows was successful
            return True

        # insertRows was unsuccesful
        return False

    def removeRows(self, row: int, count: int, parent:QModelIndex | QPersistentModelIndex = ...) -> bool:
        # QModelIndex is valid, if it is the part of an object with non-negative row and column indecies
        # Only a track has children, a track has an internal id equal to or greater than the TRACK_ID constant
        if parent.isValid() and parent.internalId() >= TRACK_ID:
            # Begin row removal
            self.beginRemoveRows(parent, row, row+count-1)
            
            # Change underlying list
            for i in reversed(range(row, row+count)):
                del self._clips[i]

            # End row removal
            self.endRemoveRows()

            # removeRows was successful
            return True

        # removeRows was unsuccesful
        return False

    def roleNames(self):
        ### Expose to QML
        # Default roles
        roles = super().roleNames()     

        # Custom roles
        roles[self.Roles.SourceRole] = QByteArray(b'source')
        roles[self.Roles.NameRole] = QByteArray(b'name')
        roles[self.Roles.TotalFramesRole] = QByteArray(b'totalFrames')
        roles[self.Roles.FrameRateRole] = QByteArray(b'frameRate')
        roles[self.Roles.PlayRateRole] = QByteArray(b'playRate')
        roles[self.Roles.InPointRole] = QByteArray(b'inPoint')
        roles[self.Roles.OutPointRole] = QByteArray(b'outPoint')
        roles[self.Roles.FrameDurationRole] = QByteArray(b'frameDuration')
        roles[self.Roles.TimeDurationRole] = QByteArray(b'timeDuration')
        roles[self.Roles.ValidRole] = QByteArray(b'valid')

        return roles

    ### Functions
    @Slot(name='reload')
    def reload(self):
        """
        Resets the model.
        """
        self.beginResetModel()
        self.endResetModel()
    
    @Slot(ClipInfo, name='indexOf', result=int)
    def indexOf(self, clip: ClipInfo):
        """
        Returns index of a clip in the underlying list.
        """
        return self._clips.index(clip)

    @Slot(int, bool, name='atPosition', result=ClipInfo)
    def atPosition(self, position: int, inMilliseconds = False):
        """
        Returns the clip at the given postion if there is one.
        """
        if 0 <= position:
            if inMilliseconds:
                beginning = 0.0
                for clip in self._clips:
                    end = beginning + clip.frameDuration * 1000 / clip.frameRate
                    if beginning <= position <= end:
                        return clip
                    
                    beginning += end
            else:
                for clip in self._clips:
                    if isinstance(clip, ClipInfo) and clip.inPoint <= position <= clip.outPoint:
                        return clip
        return

    @Slot(int, int, name='splitClip')
    def splitClip(self, clipIndex: int, position: int):
        """
        Split a clip at the given position

        :param int clipIndex: The index of the clip to split.
        :param int position: The point where to split the clip.
        """
        print(f'Cutting: {clipIndex} at {position}')
        self.layoutAboutToBeChanged.emit()
        # Insert a new row (ClipInfo)
        self.insertRows(clipIndex+1, 1, self.createIndex(0, 0, TRACK_ID))
        
        # Save original source an out point
        originalSource = self._clips[clipIndex].source
        originalOutPoint = self._clips[clipIndex].outPoint

        # Change original clip
        self._clips[clipIndex].outPoint = position
        self.setData(self.createIndex(clipIndex, 0, 0), position, self.Roles.OutPointRole)
        
        # Change inserted clip
        self.setData(self.createIndex(clipIndex+1, 0, 0), originalSource, self.Roles.SourceRole)
        self.setData(self.createIndex(clipIndex+1, 0, 0), position+1, self.Roles.InPointRole)
        self.setData(self.createIndex(clipIndex+1, 0, 0), originalOutPoint, self.Roles.OutPointRole)
        self.layoutChanged.emit()

    def indexOfSource(self, source: str):
        """
        Returns the index of the specified `source` from the list of stored sources or -1 if not present.

        :param str source: The filepath to look for among the sroted sources.
        """
        try:
            return self._storedSources.index(source)
        except ValueError as e:
            return -1

    def addSource(self, source: str):
        """
        Store a source for a video file, to later insert into the datastucture of the model as a clip.

        :param str source: Path to a video file.
        """
        if (source not in self._storedSources):
            self._storedSources.append(source)
            self.storedSourcesChanged.emit()

    def removeSource(self, sourceIndex: int):
        del self._storedSources[sourceIndex]
        self.storedSourcesChanged.emit()

    @overload
    def loadSource(self, source: str, insertIndex: int = ...):
        """
        Create a clip from a stored `source` and add ti the datastructure of the model

        :param str source: The source to create a clip from.
        :param int insertIndex: Optionally index where clip is to be inserted can be given. Otherwise the clip is appended at the end.
        """

    @overload
    def loadSource(self, sourceIndex: int, insertIndex: int = ...):
        """
        Create a clip from the source stored at `index` into the data strucutre of the model.

        :param int sourceIndex: Index of teh source to create a clip from.
        :param int insertIndex: Optionally index where clip is to be inserted can be given. Otherwise the clip is appended at the end.
        """
    
    def loadSource(self, source, insertIndex: int = ...):
        if isinstance(source, str):
            sourceIndex = self._storedSources.index(source)
        elif isinstance(source, int):
            sourceIndex = source
        else:
            raise ValueError(
                f'Expected type \'ClipInfo\' or \'int\', got \'{type(source)}\' instead'
            )

        insertIndex = insertIndex if insertIndex != ... else len(self._clips)
        parent = self.createIndex(0, 0, TRACK_ID)

        self.beginInsertRows(parent, insertIndex, insertIndex)
        self._clips.insert(insertIndex, ClipInfo(self._storedSources[sourceIndex]))
        self._clips[insertIndex].inPoint = 0
        self._clips[insertIndex].outPoint = self._clips[insertIndex].totalFrames
        self.endInsertRows()

    def removeClip(self, clipIndex: int):
        self.beginRemoveRows(self.createIndex(0, 0, 128), clipIndex, clipIndex)
        del self._clips[clipIndex]
        self.endRemoveRows()