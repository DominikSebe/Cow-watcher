import QtQuick
import QtQuick.Controls
import QtQml.Models

Rectangle {
    id: trackRoot
    property alias model: trackModel.model
    property alias rootIndex: trackModel.rootIndex
    property int selection: 0
    property double timeScale: 1.0

    signal clipClicked(var clipIndex)
    signal changeClipSource(var clipIndex)
    signal cutClip(var clipIndex)
    signal removeClip(var clipIndex)
    
    color: 'transparent'
    width: clipRow.width
    

    DelegateModel {
        id: trackModel
        Clip {
            clipIndex: index
            source: model.source
            name: model.name
            totalFrames: model.totalFrames
            frameRate: model.frameRate
            playRate: model.playRate
            inPoint: model.inPoint
            outPoint: model.outPoint
            frameDuration: model.frameDuration
            timeDuration: model.timeDuration
            selected: TimelineModel.selectedIndex == index
            valid: model.valid
            width: model.frameDuration / model.frameRate * TimelineModel.scaleFactor
            height: trackRoot.height
            onClicked: function (clipIndex) {
                trackRoot.clipClicked(clipIndex)
            }
            onChangeSource: function(clipIndex){
                trackRoot.changeClipSource(clipIndex)
            }
            onCut: function(clipIndex){
                trackRoot.cutClip(clipIndex)
            }
            onRemoved: function(clipIndex){
                trackRoot.removeClip(clipIndex)
            }
        }
    }

    Row {
        id: clipRow
        Repeater{
            id: repeater
            model: trackModel
        }
    }
}