import QtQuick
import QtQuick.Controls
import QtQml

Rectangle {
    // Id
    id: clipRoot
    
    // Properties
    property int clipIndex: -1
    property string source: ''
    property string name: ''
    property int totalFrames: 0
    property int frameRate: 0
    property double playRate: 1.0
    property int inPoint: -1
    property int outPoint: -1
    property int frameDuration: 0
    property double timeDuration: 0.0
    property bool selected: false
    property bool valid: false
    
    // Signals
    signal clicked(var clipclipIndex)
    signal changeSource(var clipclipIndex)
    signal cut(var clipclipIndex)
    signal removed(var clipclipIndex)

    onWidthChanged: function(){
        print(width)
        print(inPoint)
        print(outPoint)
        print(frameDuration)
        print(frameRate)
        print(totalFrames)
        print('-----------------')
    }

    SystemPalette {
        id: activePalette
    }

    gradient: Gradient {
        GradientStop {
            id: gradientStop
            position: 0.00
            color: 'red'
        }
        GradientStop {
            id: gradientStop2
            position: 1.0
            color: 'green'
        }
    }
    
    radius: 10
    visible: valid
    clip: true

    states: [
        State {
            name: 'unselected'
            when: !clipRoot.selected
            PropertyChanges {
                target: clipRoot
                border {
                    color: 'transparent'
                    width: 1
                }
            }
        },
        State {
            name: 'selected'
            when: clipRoot.selected
            PropertyChanges {
                target: clipRoot
                border {
                    color: 'black'
                    width: 3
                }
            }
        }
    ]

    Rectangle {
        // Text background
        color: 'lightgray'
        opacity: 0.5
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.topMargin: parent.border.width
        anchors.leftMargin: parent.border.width
        width: label.width + 2
        height: label.height
    }

    Text {
        id: label
        text: clipRoot.name
        font.pointSize: 8
        anchors {
            top: parent.top
            left: parent.left
            topMargin: parent.border.width + 1
            leftMargin: parent.border.width + 1
        }
        color: 'black'
    }
        
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        propagateComposedEvents: true
        cursorShape: Qt.ArrowCursor
        onClicked: function (mouse) {
            if (mouse.button == Qt.LeftButton){
                clipRoot.clicked(clipRoot.clipIndex)
            }
            else {
                menu.popup()
            }
        }
    }

    Rectangle {
        id: trimIn
        anchors.left: parent.left
        anchors.leftMargin: 0
        height: parent.height
        width: 5
        color: 'lawngreen'
        opacity: 0
        Drag.active: trimInMouseArea.drag.active
        Drag.proposedAction: Qt.MoveAction
        
        MouseArea {
            id: trimInMouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.SizeHorCursor
            drag.target: parent
            drag.axis: Drag.XAxis
            property double startX

            onPressed: {

            }
            onReleased:{

            }
            onPositionChanged: {
                
            }
            onEntered: {
                parent.opacity = 0.5
            }
            onExited: {
                parent.opacity = 0
            }
        }
    }

    Rectangle {
        id: trimOut
        anchors.right: parent.right
        anchors.rightMargin: 0
        height: parent.height
        width: 5
        color: 'lawngreen'
        opacity: 0
        Drag.active: trimOutMouseArea.drag.active
        Drag.proposedAction: Qt.MoveAction

        MouseArea {
            id: trimOutMouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.SizeHorCursor
            drag.target: parent
            drag.axis: Drag.XAxis
            property double startX

            onPressed: {

            }
            onReleased: {

            }
            onPositionChanged: {

            }
            onEntered: {
                parent.opacity = 0.5
            }
            onExited: {
                parent.opacity = 0
            }
        }
    }

    Menu {
        id: menu

        MenuItem {
            text: qsTr('Change source...')
            onTriggered: clipRoot.changeSource(clipRoot.clipIndex)
        }
        MenuItem {
            text: qsTr('Cut...')
            onTriggered: clipRoot.cut(clipRoot.clipIndex)
        }
        MenuItem {
            text: qsTr('Remove...')
            onTriggered: clipRoot.removed(clipRoot.clipIndex)
        }

    }
    
}