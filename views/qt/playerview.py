from PyQt5.QtCore import QFileInfo, QTime, QUrl, Qt, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoProbe
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QListView, \
    QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget

from views.qt.playercontrolview import PlayerControls
from views.qt.playlistview import PlaylistModel
from views.qt.videoview import VideoWidget, HistogramWidget


class Player(QWidget):

    fullScreenChanged = pyqtSignal(bool)
    videoWidget = None
    colorDialog = None
    videoWidget = None
    trackInfo = ""
    statusInfo = ""
    duration = 0

    def __init__(self, playlist, parent=None):
        """

        :param playlist:
        :param parent:
        """

        super(Player, self).__init__(parent)

        self._init_audio_player()
        self._init_video_player()
        self._init_addtional_controls()
        control_layout, controls, open_button = self._init_player_controls_layout()
        self._init_playlist_view()
        self._init_layout(control_layout=control_layout)
        self.check_for_player_service(controls=controls, open_button=open_button)
        self.meta_data_changed()
        self.add_to_playlist(playlist)

    def check_for_player_service(self, controls, open_button):
        """

        :param controls:
        :param open_button:
        :return:
        """

        if not self.player.isAvailable():
            QMessageBox.warning(self, "Service not available",
                                "The QMediaPlayer object does not have a valid service.\n"
                                "Please check the media service plugins are installed.")

            controls.setEnabled(False)
            self.playlistView.setEnabled(False)
            open_button.setEnabled(False)
            self.colorButton.setEnabled(False)
            self.fullScreenButton.setEnabled(False)

    def _init_layout(self, control_layout):
        """

        :param control_layout:
        :return:
        """

        display_layout = QHBoxLayout()
        if self.videoWidget:
            display_layout.addWidget(self.videoWidget, 2)
        if self.playlistView:
            display_layout.addWidget(self.playlistView)

        layout = QVBoxLayout()
        layout.addLayout(display_layout)
        if self.slider or self.labelDuration:
            h_layout = QHBoxLayout()
            if self.slider:
                h_layout.addWidget(self.slider)
            if self.labelDuration:
                h_layout.addWidget(self.labelDuration)
            layout.addLayout(h_layout)

        if control_layout:
            layout.addLayout(control_layout)

        layout.addLayout(self._get_histogram_layout())

        self.setLayout(layout)

    def _init_playlist_view(self):
        """

        :return:
        """

        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.activated.connect(self.jump)

    def _init_addtional_controls(self):
        """

        :return:
        """

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.player.duration() / 1000)

        self.labelDuration = QLabel()
        self.slider.sliderMoved.connect(self.seek)

        self.fullScreenButton = QPushButton("FullScreen")
        self.fullScreenButton.setCheckable(True)

        self.colorButton = QPushButton("Color Options...")
        self.colorButton.setEnabled(False)
        self.colorButton.clicked.connect(self.show_color_dialog)

    def _init_player_controls_layout(self):
        """

        :return:
        """

        openButton = QPushButton("Open", clicked=self.open)

        controls = PlayerControls()
        controls.set_state(self.player.state())
        controls.set_volume(self.player.volume())
        controls.set_muted(controls.is_muted())

        controls.play.connect(self.player.play)
        controls.pause.connect(self.player.pause)
        controls.stop.connect(self.player.stop)
        controls.next.connect(self.playlist.next)
        controls.previous.connect(self.previous_clicked)
        controls.changeVolume.connect(self.player.setVolume)
        controls.changeMuting.connect(self.player.setMuted)
        controls.changeRate.connect(self.player.setPlaybackRate)

        if self.videoWidget:
            controls.stop.connect(self.videoWidget.update)

        self.player.stateChanged.connect(controls.set_state)
        self.player.volumeChanged.connect(controls.set_volume)
        self.player.mutedChanged.connect(controls.set_muted)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addStretch(1)
        controlLayout.addWidget(controls)
        controlLayout.addStretch(1)
        if self.fullScreenButton:
            controlLayout.addWidget(self.fullScreenButton)
        if self.colorButton:
            controlLayout.addWidget(self.colorButton)

        return controlLayout, controls, openButton

    def _init_audio_player(self):
        """

        :return:
        """

        self.playlist = QMediaPlaylist()
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)

        self.player.durationChanged.connect(self.duration_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.metaDataChanged.connect(self.meta_data_changed)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)
        self.player.mediaStatusChanged.connect(self.status_changed)
        self.player.bufferStatusChanged.connect(self.buffering_progress)
        self.player.videoAvailableChanged.connect(self.video_available_changed)
        self.player.error.connect(self.display_error_message)

        self.playlistModel = PlaylistModel()
        self.playlistModel.set_playlist(self.playlist)

    def _init_video_player(self):
        """

        :return:
        """
        self.histogram = HistogramWidget()

        self.videoWidget = VideoWidget()
        self.player.setVideoOutput(self.videoWidget)

        self.probe = QVideoProbe()
        self.probe.videoFrameProbed.connect(self.histogram.process_frame)
        self.probe.setSource(self.player)

    def _get_histogram_layout(self):
        """

        :return:
        """
        self.labelHistogram = QLabel()
        self.labelHistogram.setText("Histogram:")

        histogramLayout = QHBoxLayout()
        histogramLayout.addWidget(self.labelHistogram)
        if self.histogram:
            histogramLayout.addWidget(self.histogram, 1)

        return histogramLayout

    def open(self):
        """

        :return:
        """

        file_names, _ = QFileDialog.getOpenFileNames(self, "Open Files")
        self.add_to_playlist(file_names)

    def add_to_playlist(self, file_names):
        """

        :param file_names:
        :return:
        """

        for name in file_names:
            file_info = QFileInfo(name)
            if file_info.exists():
                url = QUrl.fromLocalFile(file_info.absoluteFilePath())
                if file_info.suffix().lower() == 'm3u':
                    self.playlist.load(url)

                else:
                    self.playlist.addMedia(QMediaContent(url))

            else:
                url = QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))

    def duration_changed(self, duration):
        """

        :param duration:
        :return:
        """

        duration /= 1000

        self.duration = duration
        self.slider.setMaximum(duration)

    def position_changed(self, progress):
        """

        :param progress:
        :return:
        """

        progress /= 1000

        if not self.slider.isSliderDown():
            self.slider.setValue(progress)

        self.update_duration_info(progress)

    def meta_data_changed(self):
        """

        :return:
        """

        if self.player.isMetaDataAvailable():
            self.set_track_info("%s - %s" % (
                self.player.metaData(QMediaMetaData.AlbumArtist),
                self.player.metaData(QMediaMetaData.Title)))

    def previous_clicked(self):
        """

        :return:
        """

        if self.player.position() <= 5000:
            self.playlist.previous()
        else:
            self.player.setPosition(0)

    def jump(self, index):
        """

        :param index:
        :return:
        """

        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.player.play()

    def playlist_position_changed(self, position):
        """

        :param position:
        :return:
        """

        self.playlistView.setCurrentIndex(self.playlistModel.index(position, 0))

    def seek(self, seconds):
        """

        :param seconds:
        :return:
        """
        self.player.setPosition(seconds * 1000)

    def status_changed(self, status):
        """

        :param status:
        :return:
        """

        self.handle_cursor(status)

        if status == QMediaPlayer.LoadingMedia:
            self.set_status_info("Loading...")

        elif status == QMediaPlayer.StalledMedia:
            self.set_status_info("Media Stalled")

        elif status == QMediaPlayer.EndOfMedia:
            QApplication.alert(self)

        elif status == QMediaPlayer.InvalidMedia:
            self.display_error_message()

        else:
            self.set_status_info("")

    def handle_cursor(self, status):
        """

        :param status:
        :return:
        """

        if status in (QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.StalledMedia):
            self.setCursor(Qt.BusyCursor)

        else:
            self.unsetCursor()

    def buffering_progress(self, progress):
        """

        :param progress:
        :return:
        """

        self.set_status_info("Buffering %d%" % progress)

    def video_available_changed(self, available):
        """

        :param available:
        :return:
        """

        if available:
            self.fullScreenButton.clicked.connect(
                self.videoWidget.setFullScreen)
            self.videoWidget.fullScreenChanged.connect(
                self.fullScreenButton.setChecked)

            if self.fullScreenButton.isChecked():
                self.videoWidget.setFullScreen(True)
        else:
            self.fullScreenButton.clicked.disconnect(
                self.videoWidget.setFullScreen)
            self.videoWidget.fullScreenChanged.disconnect(
                self.fullScreenButton.setChecked)

            self.videoWidget.setFullScreen(False)

        self.colorButton.setEnabled(available)

    def set_track_info(self, info):
        """

        :param info:
        :return:
        """
        self.trackInfo = info

        if self.statusInfo != "":
            self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def set_status_info(self, info):
        """

        :param info:
        :return:
        """

        self.statusInfo = info

        if self.statusInfo != "":
            self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def display_error_message(self):
        """

        :return:
        """

        self.set_status_info(self.player.errorString())

    def update_duration_info(self, current_info):
        """

        :param current_info:
        :return:
        """
        result = ""
        duration = self.duration

        if current_info or duration:
            current_time = QTime((current_info / 3600) % 60, (current_info / 60) % 60,
                                current_info % 60, (current_info * 1000) % 1000)
            total_time = QTime((duration/3600) % 60, (duration/60) % 60, duration % 60, (duration*1000) % 1000)
            if duration > 3600:
                format = 'hh:mm:ss'
            else:
                format = 'mm:ss'

            result = current_time.toString(format) + " / " + total_time.toString(format)

        self.labelDuration.setText(result)

    def show_color_dialog(self):
        """

        :return:
        """

        if self.colorDialog is None:
            brightness_slider = QSlider(Qt.Horizontal)
            brightness_slider.setRange(-100, 100)
            brightness_slider.setValue(self.videoWidget.brightness())
            brightness_slider.sliderMoved.connect(self.videoWidget.setBrightness)
            self.videoWidget.brightnessChanged.connect(brightness_slider.setValue)

            contrast_slider = QSlider(Qt.Horizontal)
            contrast_slider.setRange(-100, 100)
            contrast_slider.setValue(self.videoWidget.contrast())
            contrast_slider.sliderMoved.connect(self.videoWidget.setContrast)
            self.videoWidget.contrastChanged.connect(contrast_slider.setValue)

            hue_slider = QSlider(Qt.Horizontal)
            hue_slider.setRange(-100, 100)
            hue_slider.setValue(self.videoWidget.hue())
            hue_slider.sliderMoved.connect(self.videoWidget.setHue)
            self.videoWidget.hueChanged.connect(hue_slider.setValue)

            saturation_slider = QSlider(Qt.Horizontal)
            saturation_slider.setRange(-100, 100)
            saturation_slider.setValue(self.videoWidget.saturation())
            saturation_slider.sliderMoved.connect(self.videoWidget.setSaturation)
            self.videoWidget.saturationChanged.connect(saturation_slider.setValue)

            layout = QFormLayout()
            layout.addRow("Brightness", brightness_slider)
            layout.addRow("Contrast", contrast_slider)
            layout.addRow("Hue", hue_slider)
            layout.addRow("Saturation", saturation_slider)

            button = QPushButton("Close")
            layout.addRow(button)

            self.colorDialog = QDialog(self)
            self.colorDialog.setWindowTitle("Color Options")
            self.colorDialog.setLayout(layout)

            button.clicked.connect(self.colorDialog.close)

        self.colorDialog.show()
