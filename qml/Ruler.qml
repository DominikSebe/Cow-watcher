import QtQuick
import QtQuick.Controls

Rectangle {
    property int index: 100
    property double scaleValue: 1.0
    property int maxSeconds: 86400
    property int stepSize: 3600 * scaleValue

    id: rulerTop 
    height: 30

    function frameToTime(frames, fps) {
        var framePerMinute = fps * 60;
        var framePerHour = framePerMinute * 60;

        var hours = Math.floor(frames/framePerHour);
        
        var remainder = frames%framePerHour;
        var minutes = Math.floor(remainder/framePerMinute);

        remainder = remainder%framePerMinute;
        var seconds = Math.floor(remainder/fps);
        
        return (hours < 10 ? '0' : '') + hours.toString() + ':' + (minutes < 10 ? '0' : '') + minutes.toString() + ':' + (seconds < 10 ? '0' : '') + seconds.toString();
    }

    Repeater {
        model: Math.floor(parent.width / rulerTop.stepSize)
        anchors.fill: parent

        Column {
            Rectangle {
                height: Math.floor(rulerTop.height * 0.5)
                width: 3
                x: index * stepSize
                color: 'black'
            }
            Label {
                anchors.bottom: parent.bool
                x: index * stepSize - (index == 0? 0: Math.round(text.length/2 * 4))
                text: frameToTime(index * 3600 * 25, 25)
                font.pointSize: 8
            }
        }
    }
}