import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQml

ToolBar {
    id: toolBarRoot
    property color checkedColor: Qt.rgba(activePalette.highlight.r, activePalette.highlight.g, activePalette.highlight.b, 0.3)
    property bool enableButtons: true
    property alias scaleValue: scaleSlider.value
    property bool playButto: false

    signal skippedBackward(var sourceObject)
    signal soughtBackward(var sourceObject)
    signal playbackChanged(var sourceObject)
    signal soughtForward(var sourceObject)
    signal skippedForward(var sourceObject)
    signal sliderMoved(var position)

    SystemPalette { id: activePalette }

    width: 200
    height: 36
    anchors.margins: 0

    RowLayout {
        spacing: 5
        anchors {
            top: parent.top
            bottom: parent.bottom
            centerIn: parent
        }
        ToolButton {
            id: skipBackwardButton
            action: skipBackwardAction
            enabled: toolBarRoot.enableButtons
            implicitWidth: 0.05 * toolBarRoot.width
            implicitHeight: toolBarRoot.height
            icon.source: 'image://standardicons/SP_MediaSkipBackward'
        }

        ToolButton {
            id: seekBackwardButton
            action: seekBackwardAction
            enabled: toolBarRoot.enableButtons
            implicitWidth: 0.05 * toolBarRoot.width
            implicitHeight: toolBarRoot.height
            icon.source: 'image://standardicons/SP_MediaSeekBackward'
        }

        ToolButton {
            id: playButton
            action: changePlayback
            enabled: toolBarRoot.enableButtons
            implicitWidth: 0.05 * toolBarRoot.width
            implicitHeight: toolBarRoot.height
            icon.source: 'image://standardicons/SP_MediaPlay'
        } 

        ToolButton {
            id: seekForwardButton
            action: seekForwardAction
            enabled: toolBarRoot.enableButtons
            implicitWidth: 0.05 * toolBarRoot.width
            implicitHeight: toolBarRoot.height
            icon.source: 'image://standardicons/SP_MediaSeekForward'
        }

        ToolButton {
            id: skipForwardButton
            action: skipForwardAction
            enabled: toolBarRoot.enableButtons
            implicitWidth: 0.05 * toolBarRoot.width
            implicitHeight: toolBarRoot.height
            icon.source: 'image://standardicons/SP_MediaSkipForward'
        } 
    } 
    Slider {
        id: scaleSlider
        orientation: Qt.Horizontal
        width: 0.2 * toolBarRoot.width
        from: 1.0
        to: 0.05
        stepSize: 0.01
        value: 0.5
        anchors {
            top: parent.top
            right: parent.right
            bottom: parent.bottom
            rightMargin: 5
        }
        onMoved: {
            toolBarRoot.sliderMoved(value)
        }
    }

    Action {
        id: skipBackwardAction 
        onTriggered: function (source) {
            toolBarRoot.skippedBackward(source)
        }
    }

    Action {
        id: seekBackwardAction
        onTriggered: function (source) {
            toolBarRoot.soughtBackward(source)
        }
    }
     
    Action {
        id: changePlayback
        onTriggered: function (source) {
            toolBarRoot.playbackChanged(source)
        }
    }

    Action {
        id: seekForwardAction
        onTriggered: function (source) {
            toolBarRoot.soughtForward(source)
        }
    }

    Action {
        id: skipForwardAction
        onTriggered: function (source) {
            toolBarRoot.skippedForward(source)
        }
    }   
}