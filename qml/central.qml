import QtQuick
import QtQuick.Controls
import QtQml
import QtQml.Models
import QtMultimedia
import Custom

Rectangle {
    id: centralRoot
    color: 'transparent'
    anchors {
        fill: parent
        margins: 5
    }

    readonly property color selectedTrackColor: Qt.rgba(0.5, 0.5, 0, 0.5)
    readonly property color base: Qt.rgba(255/255, 215/255, 0/255, 1.0)
    readonly property int padding: 30
    readonly property int maxTime: 86400 // 24 hour => 60 * 60 * 24 = 86400 seconds
    property int execCounter: 0

    function milisecondToFrames(milliseconds, fps=25) {
        return milliseconds * fps / 1000;
    }
    function framestoMilliseconds(frames, fps=25){
        return frames * 1000 / fps;
    }

    // Bindigs - binding objects are not overwritten when the bound property is changed from outside of the binding
    Binding {
        // Binding the source of the video to the currentClip
        target: videoPlayer
        property: 'source'
        value: TimelineModel.currentClip != null? TimelineModel.currentClip.source : ''
    }
    Binding {
        // Binding position of cursor to the position of the video, when not dragging the cursor
        target: cursor
        delayed: true
        property: 'x'
        when: !cursorMouseArea.isActive
        value: videoPlayer.position / 1000 * TimelineModel.scaleFactor - viewPort.contentItem.contentX
    }

    Video {
        // Flags of the video (From least significant to most (right to left)):
        // 1st bit - Seek position, move the video to the position of the model
        // 2nd bit - Next Clip, continue with the next clip
        // 3rd bit - Log Position, print out the position of the video, when it changes
        property int flags: 0b0000

        id: videoPlayer
        height: parent.height - toolBar.height - ruler.height - tracksBackground.height
        anchors {
            left: parent.left
            top: parent.top
            right: parent.right
        }

        onPositionChanged: function(){
            if (framestoMilliseconds(TimelineModel.currentClip.outPoint) <= position){
                flags |= 0b0010;
                TimelineModel.currentIndex ++;
                return;
            }
            if (flags & 0b0001){
                flags &= 0b1110;
                seek(framestoMilliseconds(TimelineModel.position))
            }
        }
        onSourceChanged: {
            if (flags & 0b0010){
                flags ^= 0b0011;
                TimelineModel.position = TimelineModel.currentClip.inPoint;      
                play(); 
                return;       
            }
        }

        Rectangle {
            id: nRect

            anchors.top: parent.top
            width: parent.width / 5
            height: parent.height / 5
            x: 2 * parent.width / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['N']
            visible: adjacentSources != null && adjacentSources['N']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('N')
                }
            }
        }

        Rectangle {
            id: neRect

            anchors {
                top: parent.top
                right: parent.right
            }
            width: parent.width / 5
            height: parent.height / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['NE']
            visible: adjacentSources != null && adjacentSources['NE']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('NE')
                }
            }
        }
        
        Rectangle {
            id: eRect

            anchors.right: parent.right
            width: parent.width / 5
            height: parent.height / 5
            y: 2 * parent.height / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['E']
            visible: adjacentSources != null && adjacentSources['E']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('E')
                }
            }
        }

        Rectangle {
            id: seRect

            anchors {
                right: parent.right
                bottom: parent.bottom
            }
            width: parent.width / 5
            height: parent.height / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['SE']
            visible: adjacentSources != null && adjacentSources['SE']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('SE')
                }
            }
        }

        Rectangle {
            id: sRect

            anchors.bottom: parent.bottom
            width: parent.width / 5
            height: parent.height / 5
            x: 2 * parent.width / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['S']
            visible: adjacentSources != null && adjacentSources['S']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('S')
                }
            }
        }

        Rectangle {
            id: swRect

            anchors {
                bottom: parent.bottom
                left: parent.left
            }
            width: parent.width / 5
            height: parent.height / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['SW']
            visible: adjacentSources != null && adjacentSources['SW']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('SW')
                }
            }
        }

        Rectangle {
            id: wRect

            anchors.left: parent.left
            width: parent.width / 5
            height: parent.height / 5
            y: 2 * parent.height / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['W']
            visible: adjacentSources != null && adjacentSources['W']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('W')
                }
            }
        }

        Rectangle {
            id: nwRect

            anchors {
                top: parent.top
                left: parent.left
            }
            width: parent.width / 5
            height: parent.height / 5
            opacity: 0
            enabled: adjacentSources != null && adjacentSources['NW']
            visible: adjacentSources != null && adjacentSources['NW']
            color: 'lightgrey'
            border {
                color: 'grey'
                width: 2
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: function () {
                    parent.opacity = 0.5
                }
                onExited: function () {
                    parent.opacity = 0
                }
                onClicked: function (mouse) {
                    CentralWidget.cameraChangeRequested('NW')
                }
            }
        }
    }

    TimelineToolBar {
        id: toolBar
        anchors {
            left: parent.left
            top: videoPlayer.bottom
            right: parent.right
        }
        onSkippedBackward: function (sourceObject) {
            videoPlayer.seek(videoPlayer.position - Math.min(5000, videoPlayer.playbackRate * 5000))
        }
        onSoughtBackward: function (sourceObject) {
            if (0.25 <= videoPlayer.playbackRate) videoPlayer.playbackRate = videoPlayer.playbackRate / 2
        }
        onPlaybackChanged: function (sourceObject) {
            if (videoPlayer.playbackState == MediaPlayer.PlayingState) {
                videoPlayer.pause()
                sourceObject.icon.source = 'image://standardicons/SP_MediaPlay'
            }
            else {
                videoPlayer.play()
                sourceObject.icon.source = 'image://standardicons/SP_MediaPause'

            }
        }
        onSoughtForward: function (sourceObject) {
            if (videoPlayer.playbackRate <= 4) videoPlayer.playbackRate = videoPlayer.playbackRate * 2
        }
        onSkippedForward: function (sourceObject) {
            videoPlayer.seek(videoPlayer.position + Math.min(5000, videoPlayer.playbackRate * 5000))
        }
        onSliderMoved: function(position){
            TimelineModel.scaleFactor = position
        }
    }
    // ScrollView
    ScrollView {
        // Provide a viewport of limited size
        // for contents, by enabling scrolling if needed.
        id: viewPort
        anchors{
            left: parent.left
            top: toolBar.bottom
            right: parent.right
            bottom: parent.bottom
            margins: 2
        }
        contentWidth: timeline.width
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
        
        MouseArea {
            // Enable of moving the cursor by clicking on the ruler
            property int videoState: 0
            property bool isActive: false

            id: cursorMouseArea
            acceptedButtons: Qt.LeftButton
            // Area is attached to the parent from left, right and top
            anchors{
                left: parent.left
                top: parent.top
                right: parent.right
            }
            // The area overlaps the ruler
            height: ruler.height
            drag {
                target: cursor
                axis: Drag.XAxis
                minimumX: 0
                maximumX: viewPort.width
            }
            onPressed: function(mouse){
                // Move video position to cursor on press
                isActive = true;
                videoState = videoPlayer.playbackState
                videoPlayer.pause()
                TimelineModel.position = mouse.x * 25 / TimelineModel.scaleFactor
                if (TimelineModel.currentIndex != -1){
                    videoPlayer.flags |= 0b0001
                    videoPlayer.seek(framestoMilliseconds(TimelineModel.position))
                }
            }
            onReleased: function (mouse) {
                if (videoState == 1)
                    videoPlayer.play();
                else
                    videoPlayer.pause()
                isActive = false;
            }
            onPositionChanged: function(drag) {
                // Move video position to cursor when dragging
                TimelineModel.position = drag.x * 25 / TimelineModel.scaleFactor
                if (TimelineModel.currentIndex != -1) {
                    videoPlayer.flags |= 0b0001
                    videoPlayer.seek(framestoMilliseconds(TimelineModel.position))
                }
            }
        }

        Rectangle {
            // Container
            id: timeline
            width: centralRoot.maxTime * TimelineModel.scaleFactor >= centralRoot.width ? centralRoot.maxTime * TimelineModel.scaleFactor : centralRoot.width
             // Ruler
            Ruler {
                id: ruler
                maxSeconds: centralRoot.maxTime
                scaleValue: TimelineModel.scaleFactor
                width: parent.width
            }
            // Tracks
            Column {
                id: tracksBackground
                y: ruler.height
                height: TimelineModel.trackHeight
                Repeater {
                    model: tracksModel
                }
            }
        }
    }

    // The cursor, showing the current position
    Rectangle {
        id: cursor
        width: 3
        visible: true
        color: 'black'
        height: viewPort.height - viewPort.ScrollBar.horizontal.height
        y: videoPlayer.height + toolBar.height
        x: videoPlayer.position / 1000 * TimelineModel.scaleFactor - viewPort.contentItem.contentX
        Drag.active: cursorMouseArea.drag.active
        Drag.proposedAction: Qt.MoveAction

        HoverHandler {
            cursorShape: Drag.active? Qt.ClosedHandCursor: Qt.OpenHandCursor
        }

    }
    // Playhead, created in python
    Playhead {
        id: playhead
        visible: true
        x: cursor.x - 6
        y: videoPlayer.height + toolBar.height
        width: 15
        height: 10
    }

    // TrackModel created in python
    DelegateModel {
        id: tracksModel
        model: TimelineModel
        Track {
            model: TimelineModel
            rootIndex: tracksModel.modelIndex(index)
            color: base
            height: TimelineModel.trackHeight - viewPort.ScrollBar.horizontal.height
            width: timeline.width
            timeScale: TimelineModel.scaleFactor
            onClipClicked: function (clipIndex) {
                CentralWidget.clipClicked(clipIndex)
            }
            onChangeClipSource: function(clipIndex){
                CentralWidget.selection = clip.DelegateModel.itemsIndex
            }
            onCutClip: function(clipIndex){
                var clip = TimelineModel.atPosition(videoPlayer.position, true)
                var currentClipIndex = TimelineModel.indexOf(clip)
                if (currentClipIndex == clipIndex)
                    TimelineModel.splitClip(clipIndex, milisecondToFrames(videoPlayer.position, TimelineModel.currentClip.frameRate))
                else
                    CentralWidget.warningRequested('Az időcsúszka nem a vágni kívánt klip felett helyezkedik el.')
            }
            onRemoveClip: function(clipIndex){

            }
        }
    }
}