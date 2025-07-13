from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, QTime

def create_widget():
    widget = QWidget()
    layout = QVBoxLayout()
    label = QLabel()
    label.setStyleSheet("font-size: 20px;")
    layout.addWidget(label)
    widget.setLayout(layout)

    timer = QTimer(widget)
    timer.timeout.connect(lambda: label.setText(QTime.currentTime().toString("hh:mm:ss")))
    timer.start(1000)

    return widget
