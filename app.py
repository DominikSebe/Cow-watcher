from sys import argv, exit
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir
from mainwindow import MainWindow

def main():
    APP = QApplication(argv)
    QDir.setCurrent('/'.join(argv[0].replace('\\','/').split('/')[:-1]))
    with open('style.qss', 'r') as f:
        APP.setStyleSheet(f.read())

    window=MainWindow()
    window.show()
    
    exit(APP.exec())

if __name__ == "__main__":
    main()