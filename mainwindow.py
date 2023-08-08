from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QDockWidget,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QSizePolicy,
    QMenu,
    QDialog,
    QSpacerItem,
    QFrame,
    QGroupBox,
    QCheckBox,
    QSpinBox,
    QSlider,
    QProgressDialog
)
from PySide6.QtCore import(
    QDir,
    QUrl,
    QFile,
    QTemporaryDir,
    Qt,
    QRegularExpression
)
from PySide6.QtGui import (
    QAction,
    QFont
)
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtQml import QQmlEngine

from qmlItems import registerTypes
from models import (
    IconProvider,
    CentralWidget,
    TimelineModel,
    VideoFileWidgetItem,
    ClipInfo,
    SignalLogger
)
import settings
from languages import importLanguage

from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.config import get_setting

from os import listdir
from subprocess import Popen, DEVNULL
from multiprocessing import cpu_count
from psutil import process_iter
from math import floor
from re import split, sub
from json import load, dump

language = importLanguage(settings.LANG)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        ### Create temporary directory for the project
        self.tempDir = QTemporaryDir()

        ### Read in adjecency file
        try:
            with open(settings.ADJACENT_FILE, 'r', encoding='utf-8') as f:
                self.setProperty('adjacency', load(f))
        except FileNotFoundError:
            self.setProperty('adjacency', {'WRAPPER': '(_|\.|-)[\\d_]+.(mp4|webm|dav)'})

        ### Window settings
        self.setWindowTitle(language.TITLE)
        self.setWindowIcon(QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_TitleBarMenuButton))
        self.setMinimumSize(1280, 720)

        ### Create UI
        self.init_UI()        

    def init_UI(self):
        
        # Central Widget
        self.initCentralWidget()
        # Menu
        self.initMenubar()

        # VideoBar
        self.initDockWidgets()

        # ErrorBox
        self.initErrorDialog()

    def initMenubar(self):
        """
        Initialize Menubar.
        """
        ### Get menu
        menu = self.menuBar()

        ### Build 'File' menu
        ## Create 'New' action
        new = QAction(language.NEW, self)
        new.setToolTip(language.NEW_HINT)
        new.triggered.connect(self.new_project)

        ## Create 'Save' action
        save = QAction(language.SAVE, self)
        save.setToolTip(language.SAVE_HINT)
        save.triggered.connect(self.save_project)

        ## Create 'Load' action
        load = QAction(language.LOAD, self)
        load.setToolTip(language.LOAD_HINT)
        load.triggered.connect(self.load_project)

        ## Create 'Export' action
        export = QAction(language.EXPORT, self)
        export.setToolTip(language.EXPORT_HINT)
        export.triggered.connect(self.export_project)

        ## Create 'Exit' action
        exit = QAction(language.EXIT, self)
        exit.setToolTip(language.EXIT_HINT)
        exit.triggered.connect(self.close)
        
        ## Create 'File' menu and add actions
        fileMenu = menu.addMenu(language.FILE)
        fileMenu.setObjectName('fileMenu')
        fileMenu.setToolTipsVisible(True)
        fileMenu.addActions((new, save, load))
        fileMenu.addSeparator()
        fileMenu.addAction(export)
        fileMenu.addSeparator()
        fileMenu.addAction(exit)

        ### Create 'settings' menu
        settingsMenu = menu.addMenu(language.SETTINGS)
        settingsMenu.setObjectName('settingsMenu')
        settingsMenu.setToolTipsVisible(True)

    def initDockWidgets(self):
        """
        Initialize a dockable window for the handling of imported files.
        """
        ### Create dockable Widget for importing and displaying files
        ## Create a Widget for displaying imported files
        fileDisplayWidget = QTreeWidget()
        fileDisplayWidget.setObjectName('fileDisplayWidget')
        fileDisplayWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        fileDisplayWidget.setHeaderHidden(True)
        fileDisplayWidget.setColumnCount(2)
        fileDisplayWidget.resizeColumnToContents(0)
        fileDisplayWidget.resizeColumnToContents(1)
        fileDisplayWidget.hide()

        ## Create button for opening a folder, displaying video files inside it
        openFolderButton = QPushButton(QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileDialogNewFolder), language.OPEN_FOLDER_BUTTON)
        openFolderButton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        openFolderButton.setToolTip(language.OPEN_FOLDER_HINT)
        openFolderButton.clicked.connect(self.open_folder)

        ## Create a button for import one or multiple video files
        importVideosButton = QPushButton(QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileIcon), language.IMPORT_VIDEOS_BUTTON)
        importVideosButton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        importVideosButton.setToolTip(language.IMPORT_VIDEOS_HINT)
        importVideosButton.clicked.connect(self.import_videos)

        ## Create layout for the central of Widget
        fileManagerLayout = QVBoxLayout()
        fileManagerLayout.addWidget(fileDisplayWidget)
        fileManagerLayout.addWidget(openFolderButton)
        fileManagerLayout.addWidget(importVideosButton)
        fileManagerLayout.addStretch(1)

        ## Create central Widget
        fileManagerWidget = QWidget()
        fileManagerWidget.setLayout(fileManagerLayout)

        ## Create Window for managing files
        fileManagerWindow = QDockWidget(language.FILE_MANAGER_TITLE)
        fileManagerWindow.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        fileManagerWindow.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)  
        fileManagerWindow.setMinimumWidth(200)
        fileManagerWindow.setMaximumWidth(500)
        fileManagerWindow.setWidget(fileManagerWidget)

        ### Create dockable Widget for displaying and editing clip information
        ## Create row for displaying/editing the source of the clip
        sourceLabel = QLabel('Source:')
        sourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sourceDisplay = QComboBox()
        sourceDisplay.setEnabled(False)
        sourceDisplay.setObjectName('sourceDisplay')
        sourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        sourceDisplay.currentIndexChanged.connect(self.findChild(TimelineModel, 'timeline').selectedIndexChanged)
        sourceDisplay.currentIndexChanged.connect(self.sourceCurrentIndexChanged)
        sourceRow = QHBoxLayout()
        sourceRow.addWidget(sourceLabel)
        sourceRow.addWidget(sourceDisplay)

        ## Create row for displaying/editing the inpoint of the clip
        inPointLabel = QLabel('Start:')
        inPointLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        inPointDisplay = QLineEdit()
        inPointDisplay.setObjectName('inPointDisplay')
        inPointDisplay.setInputMask('99:99:99.999')
        inPointDisplay.setEnabled(False)
        inPointDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        inPointDisplay.textEdited.connect(self.inPointEdited)
        inPointDisplay.returnPressed.connect(self.inPointReturnPressed)
        inPointRow = QHBoxLayout()
        inPointRow.addWidget(inPointLabel)
        inPointRow.addWidget(inPointDisplay)

        ## Create row for displaying/editing the inpoint of the clip
        outPointLabel = QLabel('End:')
        outPointLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        outPointDisplay = QLineEdit()
        outPointDisplay.setObjectName('outPointDisplay')
        outPointDisplay.setInputMask('99:99:99.999')
        outPointDisplay.setEnabled(False)
        outPointDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        outPointDisplay.textEdited.connect(self.outPointEdited)
        outPointDisplay.returnPressed.connect(self.outPointReturnPressed)
        outPointRow = QHBoxLayout()
        outPointRow.addWidget(outPointLabel)
        outPointRow.addWidget(outPointDisplay)

        ## Create a separator line
        seperatorLine = QFrame()
        seperatorLine.setFrameShape(QFrame.Shape.HLine)
        seperatorLine.setFrameShadow(QFrame.Shadow.Sunken)

        ## Create row for north adjacency
        northLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        northSourceLabel = QLabel('N:')
        northSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        northSourceDisplay = QComboBox()
        northSourceDisplay.setObjectName('northSourceDisplay')
        northSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        northSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        northSourceDisplay.addItem(None)
        northSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'N'))
        northSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', northSourceDisplay.objectName()))
        northSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        northSourceDisplay.setEnabled(False)
        northRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        northSourceRow = QHBoxLayout()
        northSourceRow.addSpacerItem(northLeftIndent)
        northSourceRow.addWidget(northSourceLabel)
        northSourceRow.addWidget(northSourceDisplay)
        northSourceRow.addSpacerItem(northRightIndent)

        ## Create row for northeast adjacency
        northeastLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        northeastSourceLabel = QLabel('NE:')
        northeastSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        northeastSourceDisplay = QComboBox()
        northeastSourceDisplay.setObjectName('northeastSourceDisplay')
        northeastSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        northeastSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        northeastSourceDisplay.addItem(None)
        northeastSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'NE'))
        northeastSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', northeastSourceDisplay.objectName()))
        northeastSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        northeastSourceDisplay.setEnabled(False)
        northeastRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        northeastSourceRow = QHBoxLayout()
        northeastSourceRow.addSpacerItem(northeastLeftIndent)
        northeastSourceRow.addWidget(northeastSourceLabel)
        northeastSourceRow.addWidget(northeastSourceDisplay)
        northeastSourceRow.addSpacerItem(northeastRightIndent)

        ## Create row for east adjacency
        eastLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        eastSourceLabel = QLabel('E:')
        eastSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        eastSourceDisplay = QComboBox()
        eastSourceDisplay.setObjectName('eastSourceDisplay')
        eastSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        eastSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        eastSourceDisplay.addItem(None)
        eastSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'E'))
        eastSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', eastSourceDisplay.objectName()))
        eastSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        eastSourceDisplay.setEnabled(False)
        eastRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        eastSourceRow = QHBoxLayout()
        eastSourceRow.addSpacerItem(eastLeftIndent)
        eastSourceRow.addWidget(eastSourceLabel)
        eastSourceRow.addWidget(eastSourceDisplay)
        eastSourceRow.addSpacerItem(eastRightIndent)

        ## Create row for southeast adjacency
        southeastLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        southeastSourceLabel = QLabel('SE:')
        southeastSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        southeastSourceDisplay = QComboBox()
        southeastSourceDisplay.setObjectName('southeastSourceDisplay')
        southeastSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        southeastSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        southeastSourceDisplay.addItem(None)
        southeastSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'SE'))
        southeastSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', southeastSourceDisplay.objectName()))
        southeastSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        southeastSourceDisplay.setEnabled(False)
        southeastRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        southeastSourceRow = QHBoxLayout()
        southeastSourceRow.addSpacerItem(southeastLeftIndent)
        southeastSourceRow.addWidget(southeastSourceLabel)
        southeastSourceRow.addWidget(southeastSourceDisplay)
        southeastSourceRow.addSpacerItem(southeastRightIndent)

        ## Create row for south adjacency
        southLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        southSourceLabel = QLabel('S:')
        southSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        southSourceDisplay = QComboBox()
        southSourceDisplay.setObjectName('southSourceDisplay')
        southSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        southSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        southSourceDisplay.addItem(None)
        southSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'S'))
        southSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', southSourceDisplay.objectName()))
        southSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        southSourceDisplay.setEnabled(False)
        southRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        southSourceRow = QHBoxLayout()
        southSourceRow.addSpacerItem(southLeftIndent)
        southSourceRow.addWidget(southSourceLabel)
        southSourceRow.addWidget(southSourceDisplay)
        southSourceRow.addSpacerItem(southRightIndent)

        ## Create row for southwest adjacency
        southwestLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        southwestSourceLabel = QLabel('SW:')
        southwestSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        southwestSourceDisplay = QComboBox()
        southwestSourceDisplay.setObjectName('southwestSourceDisplay')
        southwestSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        southwestSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        southwestSourceDisplay.addItem(None)
        southwestSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'SW'))
        southwestSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', southwestSourceDisplay.objectName()))
        southwestSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        southwestSourceDisplay.setEnabled(False)
        southwestRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        southwestSourceRow = QHBoxLayout()
        southwestSourceRow.addSpacerItem(southwestLeftIndent)
        southwestSourceRow.addWidget(southwestSourceLabel)
        southwestSourceRow.addWidget(southwestSourceDisplay)
        southwestSourceRow.addSpacerItem(southwestRightIndent)

        ## Create row for west adjacency
        westLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        westSourceLabel = QLabel('W:')
        westSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        westSourceDisplay = QComboBox()
        westSourceDisplay.setObjectName('westSourceDisplay')
        westSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        westSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        westSourceDisplay.addItem(None)
        westSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'W'))
        westSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', westSourceDisplay.objectName()))
        westSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        westSourceDisplay.setEnabled(False)
        westRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        westSourceRow = QHBoxLayout()
        westSourceRow.addSpacerItem(westLeftIndent)
        westSourceRow.addWidget(westSourceLabel)
        westSourceRow.addWidget(westSourceDisplay)
        westSourceRow.addSpacerItem(westRightIndent)

        ## Create row for northwest adjacency
        northwestLeftIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        northwestSourceLabel = QLabel('NW:')
        northwestSourceLabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        northwestSourceDisplay = QComboBox()
        northwestSourceDisplay.setObjectName('northwestSourceDisplay')
        northwestSourceDisplay.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        northwestSourceDisplay.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        northwestSourceDisplay.addItem(None)
        northwestSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('adjacencyDirection', 'NW'))
        northwestSourceDisplay.currentIndexChanged.connect(lambda: self.setProperty('sourceDisplayName', northwestSourceDisplay.objectName()))
        northwestSourceDisplay.currentIndexChanged.connect(self.adjacentCurrentIndexChanged)
        northwestSourceDisplay.setEnabled(False)
        northwestRightIndent = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        northwestSourceRow = QHBoxLayout()
        northwestSourceRow.addSpacerItem(northwestLeftIndent)
        northwestSourceRow.addWidget(northwestSourceLabel)
        northwestSourceRow.addWidget(northwestSourceDisplay)
        northwestSourceRow.addSpacerItem(northwestRightIndent)

        dataLayout = QVBoxLayout()
        dataLayout.addLayout(sourceRow)
        dataLayout.addLayout(inPointRow)
        dataLayout.addLayout(outPointRow)
        dataLayout.addWidget(seperatorLine)
        dataLayout.addLayout(northSourceRow)
        dataLayout.addLayout(northeastSourceRow)
        dataLayout.addLayout(eastSourceRow)
        dataLayout.addLayout(southeastSourceRow)
        dataLayout.addLayout(southSourceRow)
        dataLayout.addLayout(southwestSourceRow)
        dataLayout.addLayout(westSourceRow)
        dataLayout.addLayout(northwestSourceRow)
        dataLayout.addStretch(1)

        clipDataWidget = QWidget()
        clipDataWidget.setLayout(dataLayout)

        clipDataWindow = QDockWidget('Clip information')
        clipDataWindow.setObjectName('clipDataWindow')
        clipDataWindow.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        clipDataWindow.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        clipDataWindow.setMinimumWidth(200)
        clipDataWindow.setMaximumWidth(500)
        clipDataWindow.setWidget(clipDataWidget)
        clipDataWindow.hide()
        clipDataWindow.visibilityChanged.connect(self.clipDataVisibilityChanged)
        clipDataToggleAction = clipDataWindow.toggleViewAction()
        clipDataToggleAction.setEnabled(False)

        ### Retrieve the settings menu point and add toggle actions
        settingsMenu: QMenu = self.findChild(QMenu, 'settingsMenu')
        settingsMenu.addAction(fileManagerWindow.toggleViewAction())
        settingsMenu.addAction(clipDataToggleAction)

        ### Add dockable windows to DockAreas
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, fileManagerWindow)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, clipDataWindow)

    def initCentralWidget(self):
        """
        Initialize the central widget of this MainWindow.
        """
        ### Custom QML types
        registerTypes('Custom', 1, 0)
        
        timeline = TimelineModel(self)
        timeline.setObjectName('timeline')
        timeline.currentClipChanged.connect(self.currentClipChanged)
        timeline.selectedClipChanged.connect(self.selectedClipChanged)
        central = CentralWidget(QQmlEngine(), self)
        central.setObjectName('centralWidget')
        central.setMinimumSize(600, 400)
        central.engine().addImportPath(QDir.current().path() + '/qml')
        central.engine().addImageProvider('standardicons', IconProvider(self.style()))
        central.rootContext().setContextProperty('CentralWidget', central)
        central.rootContext().setContextProperty('TimelineModel', timeline)
        central.rootContext().setContextProperty('adjacentSources', None)
        central.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        central.setSource(QUrl('qml/central.qml'))
        central.clipClicked.connect(self.clipClicked)
        central.cameraChangeRequested.connect(self.cameraChangeRequested)
        central.warningRequested.connect(self.warningRequested)
        
        self.setCentralWidget(central)

    def initErrorDialog(self):
        errorLabel =  QLabel()
        errorLabel.setObjectName('errorLabel')
        errorLayout = QVBoxLayout()
        errorLayout.addWidget(errorLabel)
        errorDialog = QDialog(self)
        errorDialog.setObjectName('errorDialog')
        errorDialog.setWindowIcon(QStyle.standardIcon(errorDialog.style(), QStyle.StandardPixmap.SP_MessageBoxWarning))
        errorDialog.setWindowTitle(language.ERROR_TITLE)
        errorDialog.setLayout(errorLayout)

    def initExportDialog(self):
        audioCheck = QCheckBox('Audio')
        audioCheck.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        audioCheck.setChecked(True)
        resolutionLabel = QLabel('Felbontás')
        resolutionComboBox = QComboBox()
        resolutionComboBox.addItem('1920x1080')
        resolutionComboBox.addItem('1600x900')
        resolutionComboBox.addItem('1440x900')
        resolutionComboBox.addItem('1360x768')
        resolutionComboBox.addItem('1280x720')
        resolutionComboBox.addItem('1024x768')
        resolutionComboBox.addItem('800x600')
        resolutionComboBox.addItem('640x360')

        firstRowLayout = QHBoxLayout()
        firstRowLayout.addWidget(audioCheck, 1)
        firstRowLayout.addWidget(resolutionLabel)
        firstRowLayout.addWidget(resolutionComboBox, 4)

        codecLabel = QLabel('Codec')
        bitrateLabel = QLabel('Bitrate')

        secondRowLayout = QHBoxLayout()
        secondRowLayout.addWidget(codecLabel)
        secondRowLayout.addWidget(bitrateLabel)

        codecComboBox = QComboBox()
        codecComboBox.addItem('h264_nvenc')
        codecComboBox.addItem('hevc_nvenc')
        codecComboBox.addItem('mpeg4')
        codecComboBox.addItem('libx264') 
        bitrateSpinBox = QSpinBox()
        bitrateSpinBox.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        bitrateSpinBox.setCorrectionMode(QSpinBox.CorrectionMode.CorrectToNearestValue)
        bitrateSpinBox.setSuffix('k')
        bitrateSpinBox.setMinimum(5)
        bitrateSpinBox.setMaximum(5000)
        bitrateSpinBox.setValue(50)

        def coreSliderValueChanged(value):
            coreLabel.setText(f'Cores: {value}')

        coreLabel = QLabel('Cores: ')
        coreSlider = QSlider(Qt.Orientation.Horizontal)
        coreSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
        coreSlider.valueChanged.connect(coreSliderValueChanged)
        coreSlider.setMinimum(0)
        coreSlider.setMaximum(cpu_count())
        coreSlider.setValue(2 if cpu_count() >= 4 else 1)

        thirdRowLayout = QHBoxLayout()
        thirdRowLayout.addWidget(codecComboBox, 1)
        thirdRowLayout.addWidget(bitrateSpinBox, 1)

        def exportBrowseClicked():
            exportFileName, _ = QFileDialog.getSaveFileName(self, 'Fájl kiválasztása', QDir.currentPath(), 'Videos (*.mp4)')
            if exportFileName:
                exportFileLabel.setProperty('exportFile', exportFileName)
                exportFileLabel.setText(exportFileName.split('/')[-1])
        
        exportFileLabel = QLabel('')
        exportBrowseButton = QPushButton('Böngész...')
        exportBrowseButton.clicked.connect(exportBrowseClicked)

        fourthRowLayout = QHBoxLayout()
        fourthRowLayout.addWidget(exportFileLabel, 3)
        fourthRowLayout.addWidget(exportBrowseButton, 1)

        def exportButtonClicked():
            timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
            clips = timeline.data(timeline.createIndex(0, 0, 128))

            if len(clips):
                exportFile: str = exportFileLabel.property('exportFile')

                if exportFile:
                    audio = audioCheck.isChecked()
                    resolution = resolutionComboBox.currentText().split('x')
                    resolution = tuple(reversed([int(res) for res in resolution]))
                    codec = codecComboBox.currentText()
                    bitrate = bitrateSpinBox.text()
                    cores = coreSlider.value()
                    
                    videoclips: list[VideoFileClip] = []
                    for clip in clips:
                        clip: ClipInfo
                        start = self.frameToTimeString(clip.inPoint)
                        end = self.frameToTimeString(clip.outPoint)
                        videoclips.append(VideoFileClip(clip.source, target_resolution=resolution).subclip(start, end))

                                 
                    def loggerCalled(param: dict):
                        if progressDialog.wasCanceled():
                            for proc in process_iter(): 
                                if proc.name().startswith('ffmpeg'): proc.kill()
                        else:
                            key, value = param.popitem()
                            match key:
                                case 'chunk__total':
                                    progressDialog.setMaximum(value)
                                case 'chunk__index':
                                    progressDialog.setValue(value)
                                case 't__total':
                                    progressDialog.setMaximum(value)
                                case 't__index':
                                    progressDialog.setValue(value)
                                case _:
                                    progressDialog.setLabelText(value)                        

                    progressDialog = QProgressDialog(f'{exportFile} mentése...', 'Mégse', 0, 100, exportDialog)
                    progressDialog.setWindowModality(Qt.WindowModality.WindowModal)
                    progressDialog.setAutoReset(False)

                    logger = SignalLogger()
                    logger.loggerCalled.connect(loggerCalled)

                    temp_audiofile = ''.join(exportFile.split('.')[:-1]) + '_temp_audio.mp3'
                    try:
                        final = concatenate_videoclips(videoclips)
                        final.write_videofile(exportFile, codec=codec, bitrate=bitrate, audio=audio, temp_audiofile=temp_audiofile, threads=cores, logger=logger)

                        progressDialog.reset()

                    except OSError as e:
                        if (progressDialog.wasCanceled()):
                            QFile.remove(temp_audiofile)
                            QFile.remove(exportFile)
                        else:
                            self.findChild(QLabel, 'errorLabel').setText(f'Hiba történt a videó exportálása közben!\nA rendszer üzenete: {e}')
                            self.findChild(QDialog, 'errorDialog').exec()

                    finally:
                        for videoClip in videoclips: videoClip.close()
                else:
                    self.findChild(QLabel, 'errorLabel').setText('Válasszon ki egy fájlt mentésre')
                    self.findChild(QDialog, 'errorDialog').exec()
            else:
                self.findChild(QLabel, 'errorLabel').setText('A projekt nem tartalmaz videókat!')
                self.findChild(QDialog, 'errorDialog').exec()

        exportButton = QPushButton('Exportálás')
        exportButton.clicked.connect(exportButtonClicked)

        exportBoxLayout = QVBoxLayout()
        exportBoxLayout.addLayout(firstRowLayout)
        exportBoxLayout.addLayout(secondRowLayout)
        exportBoxLayout.addLayout(thirdRowLayout)
        exportBoxLayout.addWidget(coreLabel)
        exportBoxLayout.setAlignment(coreLabel, Qt.AlignmentFlag.AlignLeft)
        exportBoxLayout.addWidget(coreSlider)
        exportBoxLayout.addLayout(fourthRowLayout)
        exportBoxLayout.addWidget(exportButton)
        exportBoxLayout.setAlignment(exportButton, Qt.AlignmentFlag.AlignRight)

        exportGroupBox = QGroupBox('Exportálás')
        exportGroupBox.setLayout(exportBoxLayout)

        exportDialogLayout = QVBoxLayout()
        exportDialogLayout.addWidget(exportGroupBox)

        exportDialog = QDialog(self, Qt.WindowType.Dialog)
        exportDialog.setWindowTitle('Exportálás')
        exportDialog.setMinimumSize(250, 250)
        exportDialog.setMaximumSize(250, 250)
        exportDialog.setLayout(exportDialogLayout)

        return exportDialog

    def new_project(self):
        """
        """
        MainWindow().show()
        self.close()

    def save_project(self):
        """
        """
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        adjacency: dict[str, str|dict] = self.property('adjacency')
        
        clips = []
        for clip in timeline.data(timeline.createIndex(0, 0, 128)):
            clip: ClipInfo

            clipJson = {
                'source': sub(self.tempDir.path()+'/', '', clip.source),
                'name': clip.name,
                'playRate': clip.playRate,
                'inPoint': clip.inPoint,
                'outPoint': clip.outPoint
            }
            clips.append(clipJson)

        if not(self.property('saved')):
            saveDirPath, _ = QFileDialog.getSaveFileName(self, "Save", QDir.currentPath(), options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
            if not saveDirPath:
                return
            QDir('').mkpath(saveDirPath)
            self.setProperty('saveDirPath', saveDirPath)
            self.setProperty('saved', True)
        else:
            saveDirPath: str = self.property('saveDirPath')
        
        with open(saveDirPath+'/'+settings.ADJACENT_FILE, 'w', encoding='utf-8') as f:
            dump(adjacency, f)

        with open(saveDirPath+'/'+settings.CLIPS_FILE, 'w', encoding='utf-8') as f:
            dump(clips, f)

        for entry in QDir(self.tempDir.path()).entryInfoList(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot):
            if not QDir(saveDirPath).exists(): QDir(saveDirPath).mkdir(entry.fileName())
            if entry.isDir():
                for file in QDir(entry.absoluteFilePath()).entryInfoList(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot):
                    saveDirPath+'/'+entry.fileName()+'/'+file.fileName()
                    QFile.copy(file.absoluteFilePath(), saveDirPath+'/'+entry.fileName()+'/'+file.fileName())
            else:
                saveDirPath+'/'+entry.fileName()
                QFile.copy(entry.absoluteFilePath(), saveDirPath+'/'+entry.fileName())

    def load_project(self):
        """
        """
        loadDirPath = QFileDialog.getExistingDirectory(self, "Open Directory", QDir.currentPath(), QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if loadDirPath == '':
            return

        loadDir = QDir(loadDirPath)

        if not loadDir.exists(settings.ADJACENT_FILE) or not loadDir.exists(settings.CLIPS_FILE):
            errorDialog: QDialog = self.findChild(QDialog, 'errorDialog')
            errorLabel: QLabel = errorDialog.findChild(QLabel, 'errorLabel')
            
            errorLabel.setText(language.SAVE_DIR_HAS_NO_NECESSARY_FILES)
            return errorDialog.exec()

        with open(loadDirPath+'/'+settings.ADJACENT_FILE, 'r', encoding='utf-8') as f:
            self.setProperty('adjacency', load(f))
        
        with open(loadDirPath+'/'+settings.CLIPS_FILE, 'r', encoding='utf-8') as f:
            clips: list[dict[str]] = load(f)

        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        sourceDisplay: QComboBox = self.findChild(QComboBox, 'sourceDisplay', Qt.FindChildOption.FindChildrenRecursively)
        adjecentSourceDisplays: list[QComboBox] = self.findChildren(QComboBox, QRegularExpression(r'SourceDisplay'), Qt.FindChildOption.FindChildrenRecursively)
        fileDisplayWidget: QTreeWidget = self.findChild(QTreeWidget, 'fileDisplayWidget', Qt.FindChildOption.FindChildrenRecursively)

        while (timeline.rowCount(timeline.createIndex(0, 0, 128))):
            timeline.removeClip(0) 

        while (len(timeline.sources)):
            timeline.removeSource(0)

        fileDisplayWidget.clear()
        
        timeline.currentClip = None
        timeline.selectedClip = None
        timeline.position = 0

        while(sourceDisplay.count()):
            sourceDisplay.removeItem(0)

        for adjecentSourceDisplay in adjecentSourceDisplays:
            while(adjecentSourceDisplay.count()):
                adjecentSourceDisplay.removeItem(0)
            adjecentSourceDisplay.addItem(None)

        self.tempDir = QTemporaryDir()

        for entry in loadDir.entryInfoList(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot, QDir.SortFlag.DirsFirst | QDir.SortFlag.Name):
            if entry.isDir():
                QDir(self.tempDir.path()).mkdir(entry.fileName())

                FolderItem = QTreeWidgetItem(fileDisplayWidget)
                FolderItem.setIcon(0, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_DirIcon))
                FolderItem.setText(1, entry.fileName())
                FolderItem.setFont(1, QFont('Helvetica', 12, 2))

                for file in QDir(entry.absoluteFilePath()).entryInfoList(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot):
                    QFile.copy(file.absoluteFilePath(), self.tempDir.path()+'/'+entry.fileName()+'/'+file.fileName())

                    videoFileItem = VideoFileWidgetItem(self.tempDir.path() + '/' + entry.fileName() + '/' + file.fileName(), FolderItem)
                    videoFileItem.setIcon(1, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileIcon))
                    videoFileItem.setText(1, videoFileItem.name)
                    videoFileItem.setFont(1, QFont('Helvetica', 12, 1))
                    videoFileItem.setToolTip(1, videoFileItem.source)

                    timeline.addSource(self.tempDir.path()+'/'+entry.fileName()+'/'+file.fileName())
                    sourceDisplay.addItem(entry.fileName()+'/'+file.fileName())
                    sourceDisplay.setItemData(sourceDisplay.count()-1, entry.fileName()+'/'+file.fileName(), Qt.ItemDataRole.ToolTipRole)
                    for adjecentSourceDisplay in adjecentSourceDisplays:
                        adjecentSourceDisplay.addItem(entry.fileName()+'/'+file.fileName())
                        adjecentSourceDisplay.setItemData(adjecentSourceDisplay.count()-1, entry.fileName()+'/'+file.fileName(), Qt.ItemDataRole.ToolTipRole)
                
                FolderItem.setExpanded(True)

            elif not entry.fileName().endswith('.json'):
                QFile.copy(entry.absoluteFilePath(), self.tempDir.path()+'/'+entry.fileName())

                videoFileItem = VideoFileWidgetItem(entry.absoluteFilePath(), fileDisplayWidget)
                videoFileItem.setIcon(0, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileIcon))
                videoFileItem.setText(1, videoFileItem.name)
                videoFileItem.setFont(1, QFont('Helvetica', 12, 1))
                videoFileItem.setToolTip(0, videoFileItem.source)

                timeline.addSource(self.tempDir.path()+'/'+entry.fileName())
                sourceDisplay.addItem(entry.fileName())
                sourceDisplay.setItemData(sourceDisplay.count()-1, entry.fileName(), Qt.ItemDataRole.ToolTipRole)
                for adjecentSourceDisplay in adjecentSourceDisplays:
                    adjecentSourceDisplay.addItem(entry.fileName())
                    adjecentSourceDisplay.setItemData(adjecentSourceDisplay.count()-1, entry.fileName(), Qt.ItemDataRole.ToolTipRole)
        
        for index, clip in enumerate(clips):
            timeline.loadSource(self.tempDir.path()+'/'+clip['source'])
            timeline.setData(timeline.createIndex(index, 0, 0), clip['name'], timeline.Roles.NameRole)
            timeline.setData(timeline.createIndex(index, 0, 0), clip['playRate'], timeline.Roles.PlayRateRole)
            timeline.setData(timeline.createIndex(index, 0, 0), clip['inPoint'], timeline.Roles.InPointRole)
            timeline.setData(timeline.createIndex(index, 0, 0), clip['outPoint'], timeline.Roles.OutPointRole)

        timeline.currentIndex = 0

        self.setProperty('saveDirPath', loadDirPath)
        self.setProperty('saved', True)
        if fileDisplayWidget.isHidden(): fileDisplayWidget.show()

    def export_project(self):
        """
        """
        self.initExportDialog().exec()
        
    def open_folder(self):
        """
        Open a file dialog and import the selcted folder and the video files inside int.
        """
        ### Open a dialog for folder selection
        openedDirPath = QFileDialog.getExistingDirectory(self, "Open Directory", QDir.currentPath(), QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)

        if openedDirPath != '':
            ### Get necesarry items
            timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
            fileDisplayWidget: QTreeWidget = self.findChild(QTreeWidget, 'fileDisplayWidget', Qt.FindChildOption.FindChildrenRecursively)
            sourceDisplay: QComboBox = self.findChild(QComboBox, 'sourceDisplay', Qt.FindChildOption.FindChildrenRecursively)
            adjecentSourceDisplays: list[QComboBox] = self.findChildren(QComboBox, QRegularExpression(r'SourceDisplay'), Qt.FindChildOption.FindChildrenRecursively)   

            ### Make folder item
            FolderItem = QTreeWidgetItem(fileDisplayWidget)
            FolderItem.setIcon(0, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_DirIcon))
            FolderItem.setText(1, openedDirPath.split('/')[-1])
            FolderItem.setFont(1, QFont('Helvetica', 12, 2))

            ### Make folder
            QDir('').mkpath(self.tempDir.path() +'/'+ openedDirPath.split('/')[-1])
            ### Copy and convert dav files
            for file in listdir(openedDirPath):
                if file.split('.')[-1] == 'dav':
                    cmd =[get_setting("FFMPEG_BINARY"), "-i", openedDirPath+'/'+file, '-c', 'copy', sub('.dav', '.mp4', self.tempDir.path()+'/'+openedDirPath.split('/')[-1]+'/'+file)]
                    popen_params = {
                        "bufsize": int(10**5),
                        "stdout": DEVNULL,
                        "stderr": DEVNULL,
                    }
                    Popen(cmd, **popen_params).communicate()

                    videoFileItem = VideoFileWidgetItem(sub('.dav', '.mp4', self.tempDir.path()+'/'+openedDirPath.split('/')[-1]+'/'+file), FolderItem)
                    videoFileItem.setIcon(1, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileIcon))
                    videoFileItem.setText(1, videoFileItem.name)
                    videoFileItem.setFont(1, QFont('Helvetica', 12, 1))
                    videoFileItem.setToolTip(1, videoFileItem.source)

                    timeline.addSource(videoFileItem.source)
                    sourceDisplay.addItem(sub(self.tempDir.path()+'/', '', videoFileItem.source))
                    sourceDisplay.setItemData(sourceDisplay.count()-1, sub(self.tempDir.path()+'/', '', videoFileItem.source), Qt.ItemDataRole.ToolTipRole)
                    for adjecentSourceDisplay in adjecentSourceDisplays:
                        adjecentSourceDisplay.addItem(sub(self.tempDir.path()+'/', '', videoFileItem.source))
                        adjecentSourceDisplay.setItemData(adjecentSourceDisplay.count()-1, sub(self.tempDir.path()+'/', '', videoFileItem.source), Qt.ItemDataRole.ToolTipRole)

            openedDir = QDir(openedDirPath)
            files = openedDir.entryInfoList(['*.mp4', '*.webm'], QDir.Filter.Files, QDir.SortFlag.Name)
            if len(files): 

                for file in files:
                    QFile.copy(file.absoluteFilePath(), self.tempDir.path() + '/' + openedDir.dirName() + '/' + file.fileName())

                    videoFileItem = VideoFileWidgetItem(sub('.dav', '.mp4', self.tempDir.path()+'/'+openedDir.dirName()+'/'+file.fileName()), FolderItem)
                    videoFileItem.setIcon(1, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileIcon))
                    videoFileItem.setText(1, videoFileItem.name)
                    videoFileItem.setFont(1, QFont('Helvetica', 12, 1))
                    videoFileItem.setToolTip(1, videoFileItem.source)
                    
                    timeline.addSource(videoFileItem.source)
                    sourceDisplay.addItem(sub(self.tempDir.path()+'/', '', videoFileItem.source))
                    sourceDisplay.setItemData(sourceDisplay.count()-1, sub(self.tempDir.path()+'/', '', videoFileItem.source), Qt.ItemDataRole.ToolTipRole)
                    for adjecentSourceDisplay in adjecentSourceDisplays:
                        adjecentSourceDisplay.addItem(sub(self.tempDir.path()+'/', '', videoFileItem.source))
                        adjecentSourceDisplay.setItemData(adjecentSourceDisplay.count()-1, sub(self.tempDir.path()+'/', '', videoFileItem.source), Qt.ItemDataRole.ToolTipRole)

                if timeline.rowCount(timeline.createIndex(0, 0, 128)) == 0: 
                    timeline.loadSource(0)
                    timeline.currentIndex = 0
                    timeline.position = 0

                FolderItem.setExpanded(True)
                if fileDisplayWidget.isHidden(): fileDisplayWidget.show()

            else:
                errorDialog: QDialog = self.findChild(QDialog, 'errorDialog')
                errorLabel: QLabel = errorDialog.findChild(QLabel, 'errorLabel')
                
                errorLabel.setText(language.NO_VIDEO_FILES_IN_FOLDER_ERROR)
                errorDialog.exec()

    def import_videos(self, checked: bool):
        """
        """
        filenames: list[str]
        filenames, _ = QFileDialog.getOpenFileNames(self, 'Open Video', filter="Videos(*.mp4 *.webm *.dav)")

        if len(filenames):
            timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')   
            fileDisplayWidget: QTreeWidget = self.findChild(QTreeWidget, 'fileDisplayWidget', Qt.FindChildOption.FindChildrenRecursively)
            sourceDisplay: QComboBox = self.findChild(QComboBox, 'sourceDisplay', Qt.FindChildOption.FindChildrenRecursively)
            adjecentSourceDisplays: list[QComboBox] = self.findChildren(QComboBox, QRegularExpression(r'SourceDisplay'), Qt.FindChildOption.FindChildrenRecursively)

            for file in filenames:
                if file.split('.')[-1] == 'dav':
                        cmd =[get_setting("FFMPEG_BINARY"), "-i", file, '-c', 'copy', sub('.dav', '.mp4', self.tempDir.path()+'/'+file.split('/')[-1])]
                        popen_params = {
                            "bufsize": int(10**5),
                            "stdout": DEVNULL,
                            "stderr": DEVNULL,
                        }
                        Popen(cmd, **popen_params).communicate()
                else:
                    QFile.copy(file, self.tempDir.path()+'/'+file.split('/')[-1])
                videoFileItem = VideoFileWidgetItem(sub('.dav', '.mp4', self.tempDir.path()+'/'+file.split('/')[-1]), fileDisplayWidget)
                videoFileItem.setIcon(0, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileIcon))
                videoFileItem.setText(1, videoFileItem.name)
                videoFileItem.setFont(1, QFont('Helvetica', 12, 1))
                videoFileItem.setToolTip(0, videoFileItem.source)

                timeline.addSource(videoFileItem.source)
                sourceDisplay.addItem(sub(self.tempDir.path()+'/', '', videoFileItem.source))
                sourceDisplay.setItemData(sourceDisplay.count()-1, sub(self.tempDir.path()+'/', '', videoFileItem.source), Qt.ItemDataRole.ToolTipRole)
                for adjecentSourceDisplay in adjecentSourceDisplays:
                        adjecentSourceDisplay.addItem(sub(self.tempDir.path()+'/', '', videoFileItem.source))
                        adjecentSourceDisplay.setItemData(adjecentSourceDisplay.count()-1, sub(self.tempDir.path()+'/', '', videoFileItem.source), Qt.ItemDataRole.ToolTipRole)
                
            if timeline.rowCount(timeline.createIndex(0, 0, 128)) == 0: 
                timeline.loadSource(0)
                timeline.currentIndex = 0
                timeline.position = 0
            
            if fileDisplayWidget.isHidden(): fileDisplayWidget.show()

    def selectedClipChanged(self, selectedClip: ClipInfo):
        ### Populate the clip data window with the attributes of the selected clip
        ## If the selected clip is not None
        if selectedClip:
            ## Get needed objects
            adjacency: dict[str, str|dict] = self.property('adjacency') # the dictornary describing the relations of the source files
            timeline: TimelineModel = self.findChild(TimelineModel, 'timeline') # the timeline model
            clipDataWindow: QDockWidget = self.findChild(QDockWidget, name='clipDataWindow') # the clip data window
            sourceDisplay: QComboBox = clipDataWindow.findChild(QComboBox, 'sourceDisplay') # Combobox displaying the source of the selected clip
            inPointDisplay: QLineEdit = clipDataWindow.findChild(QLineEdit, 'inPointDisplay') # Lineedit displaying the inpoint of the selected clip
            outPointDisplay: QLineEdit = clipDataWindow.findChild(QLineEdit, 'outPointDisplay') # Lineedit displaying the outpoit of the selected clip
            adjecentSourceDisplays: list[QComboBox] = self.findChildren(QComboBox, QRegularExpression(r'SourceDisplay'), Qt.FindChildOption.FindChildrenRecursively) # Comoboxes displaying the adjacent sources

            ## Enable source display if needed
            if not sourceDisplay.isEnabled():  sourceDisplay.setEnabled(True)

            ## Enable the editing of inpoint if the selected clip is not the first
            if timeline.selectedIndex != 0:
                inPointDisplay.setEnabled(True)
            ## Otherwise disable it
            else:
                inPointDisplay.setEnabled(False)

            ## Enable the editing of outpoint if the selected clip is not the last
            if timeline.selectedIndex != timeline.rowCount(timeline.createIndex(0, 0, 128)) - 1:
                outPointDisplay.setEnabled(True)
            ## Otherwise disable it
            else:
                outPointDisplay.setEnabled(False)

            ## Enable toggling of the clip data window
            clipDataToggleAction = clipDataWindow.toggleViewAction()
            if not clipDataToggleAction.isEnabled(): clipDataToggleAction.setEnabled(True)

            ## Set the source of the selected clip to display
            sourceDisplay.setCurrentIndex(sourceDisplay.findText(sub(self.tempDir.path()+'/', '', selectedClip.source)))
            ## Convert and set the inpoint of the selected clip to display
            inPointDisplay.setText(self.frameToTimeString(selectedClip.inPoint, selectedClip.frameRate))
            ## Convert and set the outpoint of the selected clip to display
            outPointDisplay.setText(self.frameToTimeString(selectedClip.outPoint, selectedClip.frameRate))

            ## Loop through all the Comboboxes displaying the adjecent sources
            for adjecentSourceDisplay in adjecentSourceDisplays:
                ## Enable Conboboxes if needed
                if not adjecentSourceDisplay.isEnabled(): adjecentSourceDisplay.setEnabled(True)

                ## Hide source of the selected clip
                # Loop through all items in the Comboboxes
                for row in range(adjecentSourceDisplay.count()):
                    # Set all items visible
                    # QComboBox objects use a QListView, which has a `setRowHidden()` function
                    adjecentSourceDisplay.view().setRowHidden(row, False)

                # Find index of the source of the selected clip
                hideIndex = adjecentSourceDisplay.findText(sub(self.tempDir.path()+'/', '', selectedClip.source))
                # Hide item of found index
                adjecentSourceDisplay.view().setRowHidden(hideIndex, True)        

                ## Remove the name of the temporary directory from the source of the selcted clip
                file = sub(self.tempDir.path() +'/', '', selectedClip.source)
                
                ## Remove parts of source specified by the 'WRAPPER' to create the key
                adjecentKey = sub(adjacency['WRAPPER'], '', file)

                adjecentSourceDisplay.setCurrentIndex(0)
                ## If the source has an adjacency dictionary specified, populate the adjacency displays with the appropriate sources
                if adjecentKey in adjacency:
                    if adjecentSourceDisplay.objectName().startswith('northSource', 0, 11):
                        # Set source of 'north' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['N'], Qt.MatchFlag.MatchStartsWith))
                    elif adjecentSourceDisplay.objectName().startswith('northeastSource', 0, 16):
                        # Set source of 'northeast' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['NE'], Qt.MatchFlag.MatchStartsWith))
                    elif adjecentSourceDisplay.objectName().startswith('eastSource', 0, 10):
                        # Set source of 'east' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['E'], Qt.MatchFlag.MatchStartsWith))
                    elif adjecentSourceDisplay.objectName().startswith('southeastSource', 0, 16):
                        # Set source of 'sotheast' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['SE'], Qt.MatchFlag.MatchStartsWith))
                    elif adjecentSourceDisplay.objectName().startswith('southSource', 0, 11):
                        # Set source of 'south' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['S'], Qt.MatchFlag.MatchStartsWith))
                    elif adjecentSourceDisplay.objectName().startswith('southwestSource', 0, 16):
                        # Set source of 'southwest' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['SW'], Qt.MatchFlag.MatchStartsWith))
                    elif adjecentSourceDisplay.objectName().startswith('westSource', 0, 10):
                        # Set source of 'west' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['W'], Qt.MatchFlag.MatchStartsWith))
                    elif adjecentSourceDisplay.objectName().startswith('northwestSource', 0, 16):
                        # Set source of 'northwest' display
                        adjecentSourceDisplay.setCurrentIndex(adjecentSourceDisplay.findText(adjacency[adjecentKey]['NW'], Qt.MatchFlag.MatchStartsWith))

            ## Make the clip data window visible
            clipDataWindow.show()
    
    def currentClipChanged(self, currentClip: ClipInfo):
        if currentClip:
            ### Get necesarry objects
            adjacency: dict[str, str|dict[str|str]] = self.property('adjacency')
            central: CentralWidget = self.findChild(CentralWidget, 'centralWidget')
            
            ### Get adjacent sources
            key = sub(adjacency['WRAPPER'], '', sub(self.tempDir.path() + '/', '', currentClip.source))

            adjacentSources = {
                'N': False,
                'NE': False,
                'E': False,
                'SE': False,
                'S': False,
                'SW': False,
                'W': False,
                'NW': False
            }
            if (key in adjacency):
                for k, v in adjacency[key].items():
                    if (v): adjacentSources[k] = True

            ### Pass adjecent sources
            central.rootContext().setContextProperty('adjacentSources', adjacentSources)

    def itemDoubleClicked(self, item: VideoFileWidgetItem, column: int):
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        timeline.setData(timeline.createIndex(timeline.currentIndex, 0, 0), item.source, timeline.Roles.SourceRole)
        # timeline.data(timeline.createIndex(timeline.currentIndex, 0, 0), timeline.Roles.InPointRole)
        # timeline.data(timeline.createIndex(timeline.currentIndex, 0, 0), timeline.Roles.OutPointRole)

    def clipClicked(self, clipIndex: int):
        self.findChild(TimelineModel, 'timeline').selectedIndex=clipIndex

    def cameraChangeRequested(self, dircetion: str):
        """
        """
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        adjacency: dict[str, str|dict[str, str]] = self.property('adjacency')
        
        adjacentKey = sub(adjacency['WRAPPER'], '', sub(self.tempDir.path() + '/', '', timeline.currentClip.source))
        file = adjacency[adjacentKey][dircetion]
        for source in timeline.sources:
            if sub(self.tempDir.path() + '/', '', source).startswith(file):
                file = source
                break;
        
        timeline.setData(timeline.createIndex(timeline.currentIndex, 0, 0), file, timeline.Roles.SourceRole)

    def warningRequested(self, warning_text):
        self.findChild(QLabel, 'errorLabel').setText(warning_text)
        self.findChild(QDialog, 'errorDialog').exec()

    def sourceCurrentIndexChanged(self, index: int):
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        # try:
        timeline.setData(timeline.createIndex(timeline.selectedIndex, 0, 0), timeline.sources[index], timeline.Roles.SourceRole)

        # except IndexError:
        #     pass

    def adjacentCurrentIndexChanged(self, index: int):
        adjacency: dict[str, str|dict] = self.property('adjacency')
        adjacencyKey: str = self.property('adjacencyDirection')
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        if not timeline.selectedClip:
            return
        sourceKey = sub(adjacency['WRAPPER'], '', sub(self.tempDir.path() + '/', '', timeline.selectedClip.source))
        sourceDisplay: QComboBox = self.findChild(QComboBox, self.property('sourceDisplayName'), Qt.FindChildOption.FindChildrenRecursively)
        source = sourceDisplay.itemText(index)

        if sourceKey not in adjacency:
            adjacency[sourceKey] = {
                'N': None,
                'NE': None,
                'E': None,
                'SE': None,
                'S': None,
                'SW': None,
                'W': None,
                'NW': None
            }

        if source:
            adjacency[sourceKey][adjacencyKey] = sub(adjacency['WRAPPER'], '', source)
        else:
            adjacency[sourceKey][adjacencyKey] = None

        if (timeline.selectedClip == timeline.currentClip):
            central: CentralWidget = self.findChild(CentralWidget, 'centralWidget')
            adjacentSources = {
                'N': False,
                'NE': False,
                'E': False,
                'SE': False,
                'S': False,
                'SW': False,
                'W': False,
                'NW': False
            }
            for v, k in adjacency[sourceKey].items():
                if k: adjacentSources[v] = True

            central.rootContext().setContextProperty('adjacentSources', adjacentSources)
        self.setProperty('adjacency', adjacency)

    def inPointEdited(self, text: str):
        self.newInPointText = text

    def inPointReturnPressed(self):
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        timeline.setData(timeline.createIndex(timeline.selectedIndex, 0, 0), self.timeStringToFrames(self.newInPointText, timeline.selectedClip.frameRate), timeline.Roles.InPointRole)
        del self.newInPointText
    
    def outPointEdited(self, text: str):
        self.newOutPointText = text

    def outPointReturnPressed(self):
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        timeline.setData(timeline.createIndex(timeline.selectedIndex, 0, 0), self.timeStringToFrames(self.newOutPointText, timeline.selectedClip.frameRate), timeline.Roles.OutPointRole)
        del self.newInPointText

    def clipDataVisibilityChanged(self, visible: bool):
        if not visible:
            timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
            timeline.selectedIndex = -1

    def closeEvent(self, event):
        timeline: TimelineModel = self.findChild(TimelineModel, 'timeline')
        timeline.currentClip = None
        self.tempDir.remove()

        if not self.property('saved'):
            with open(settings.ADJACENT_FILE, 'w', encoding='utf-8') as f:
                dump(self.property('adjacency'), f, indent=4)
        return super(MainWindow, self).closeEvent(event)

    @staticmethod
    def frameToTimeString(frames: int, fps = 25):
        """
        Converts a number of `frames`, into a string of format 'HH:MM:SS.MIS', where `fps` is the ratio between frames and a second.

        :param int frames: Number of frames to convert.
        :param int fps: The number of frames that make up one second. (Default is 25)
        """
        hours = floor(frames / (fps * 3600))
        remainder = frames % (fps * 3600)
        minutes = floor(remainder / (fps* 60))
        remainder = remainder % (fps * 60)
        seconds = floor(remainder / fps)
        milliseconds = int(remainder % fps)

        return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'

    @staticmethod
    def timeStringToFrames(text: str, fps = 25):
        hours, minutes, seconds, millieseconds = tuple(split(':|\.', text))
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        millieseconds = int(millieseconds) / 1000

        return hours * fps * 3600 + minutes * fps * 60 + seconds * fps + floor(millieseconds * fps)