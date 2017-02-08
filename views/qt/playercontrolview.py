from PyQt5.QtCore import Qt, qFuzzyCompare, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QSlider, QStyle, QToolButton, QWidget


class PlayerControls(QWidget):

    play = pyqtSignal()
    pause = pyqtSignal()
    stop = pyqtSignal()
    next = pyqtSignal()
    previous = pyqtSignal()
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    changeRate = pyqtSignal(float)

    def __init__(self, parent=None):
        super(PlayerControls, self).__init__(parent)
        self.build_buttons()
        self.build_addtional_controls()
        self.build_layout()

    def build_addtional_controls(self):
        """

        :return:
        """

        self.volumeSlider = QSlider(Qt.Horizontal, sliderMoved=self.changeVolume)
        self.volumeSlider.setRange(0, 100)

        self.rateBox = QComboBox(activated=self.update_rate)
        self.rateBox.addItem("0.5x", 0.5)
        self.rateBox.addItem("1.0x", 1.0)
        self.rateBox.addItem("2.0x", 2.0)
        self.rateBox.setCurrentIndex(1)

    def build_buttons(self):
        """

        :return:
        """

        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False

        self.playButton = QToolButton(clicked=self.play_clicked)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.stopButton = QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

        self.nextButton = QToolButton(clicked=self.next)
        self.nextButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))

        self.previousButton = QToolButton(clicked=self.previous)
        self.previousButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))

        self.muteButton = QToolButton(clicked=self.mute_clicked)
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

    def build_layout(self):
        """

        :return:
        """

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.rateBox)
        self.setLayout(layout)

    def state(self):
        """

        :return:
        """

        return self.playerState

    def set_state(self, state):
        """

        :param state:
        :return:
        """

        if state != self.playerState:
            self.playerState = state

            if state == QMediaPlayer.StoppedState:
                self.stopButton.setEnabled(False)
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
            elif state == QMediaPlayer.PlayingState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
            elif state == QMediaPlayer.PausedState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def volume(self):
        """

        :return:
        """

        return self.volumeSlider.value()

    def set_volume(self, volume):
        """

        :param volume:
        :return:
        """

        self.volumeSlider.setValue(volume)

    def is_muted(self):
        """

        :return:
        """

        return self.playerMuted

    def set_muted(self, muted):
        """

        :param muted:
        :return:
        """

        if muted != self.playerMuted:
            self.playerMuted = muted
            self.muteButton.setIcon(
                self.style().standardIcon(
                    QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume
                )
            )

    def play_clicked(self):
        """

        :return:
        """

        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.pause.emit()

    def mute_clicked(self):
        """

        :return:
        """

        self.changeMuting.emit(not self.playerMuted)

    def playback_rate(self):
        """

        :return:
        """

        return self.rateBox.itemData(
            self.rateBox.currentIndex()
        )

    def set_playback_rate(self, rate):
        """

        :param rate:
        :return:
        """

        for i in range(self.rateBox.count()):
            if qFuzzyCompare(rate, self.rateBox.itemData(i)):
                self.rateBox.setCurrentIndex(i)
                return
#
        self.rateBox.addItem("%dx" % rate, rate)
        self.rateBox.setCurrentIndex(self.rateBox.count() - 1)

    def update_rate(self):
        """

        :return:
        """
        self.changeRate.emit(self.playback_rate())
