from PyQt5.QtCore import QMetaObject, QObject, QThread, Qt, pyqtSlot, Q_ARG, pyqtSignal
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette
from PyQt5.QtMultimedia import QAbstractVideoBuffer, QVideoFrame
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QSizePolicy, QWidget


class VideoWidget(QVideoWidget):

    def __init__(self, parent=None):
        """

        :param parent:
        """

        super(VideoWidget, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def keyPressEvent(self, event):
        """

        :param event:
        :return:
        """

        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
            self.setFullScreen(not self.isFullScreen())
            event.accept()
        else:
            super(VideoWidget, self).keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """

        :param event:
        :return:
        """

        self.setFullScreen(not self.isFullScreen())
        event.accept()


class FrameProcessor(QObject):

    histogram_ready = pyqtSignal(list)

    @pyqtSlot(QVideoFrame, int)
    def process_frame(self, frame, levels):
        """

        :param frame:
        :param levels:
        :return:
        """

        histogram = [0.0] * levels
        if levels and frame.map(QAbstractVideoBuffer.ReadOnly):
            pixel_format = frame.pixelFormat()

            if pixel_format == QVideoFrame.Format_YUV420P or pixel_format == QVideoFrame.Format_NV12:
                # Process YUV data.
                bits = frame.bits()
                for idx in range(frame.height() * frame.width()):
                    histogram[(bits[idx] * levels) >> 8] += 1.0

            else:
                image_format = QVideoFrame.imageFormatFromPixelFormat(pixel_format)
                if image_format != QImage.Format_Invalid:
                    # Process RGB data.
                    image = QImage(frame.bits(), frame.width(), frame.height(), image_format)

                    for y in range(image.height()):
                        for x in range(image.width()):
                            pixel = image.pixel(x, y)
                            histogram[(qGray(pixel) * levels) >> 8] += 1.0

            # Find the maximum value.
            max_value = 0.0
            for value in histogram:
                if value > max_value:
                    max_value = value

            # Normalise the values between 0 and 1.
            if max_value > 0.0:
                for i in range(len(histogram)):
                    histogram[i] /= max_value

            frame.unmap()

        self.histogram_ready.emit(histogram)


class HistogramWidget(QWidget):

    def __init__(self, parent=None):
        """

        :param parent:
        """

        super(HistogramWidget, self).__init__(parent)

        self.m_levels = 128
        self.m_isBusy = False
        self.m_histogram = []
        self.m_processor = FrameProcessor()
        self.m_processorThread = QThread()

        self.m_processor.moveToThread(self.m_processorThread)
        self.m_processor.histogram_ready.connect(self.set_histogram)

    def __del__(self):
        """

        :return:
        """

        self.m_processorThread.quit()
        self.m_processorThread.wait(10000)

    def set_levels(self, levels):
        """

        :param levels:
        :return:
        """

        self.m_levels = levels

    def process_frame(self, frame):
        """

        :param frame:
        :return:
        """

        if self.m_isBusy:
            return

        self.m_isBusy = True
        QMetaObject.invokeMethod(self.m_processor, 'process_frame',  Qt.QueuedConnection, Q_ARG(QVideoFrame, frame),
                                 Q_ARG(int, self.m_levels))

    @pyqtSlot(list)
    def set_histogram(self, histogram):
        """

        :param histogram:
        :return:
        """

        self.m_isBusy = False
        self.m_histogram = list(histogram)
        self.update()

    def paintEvent(self, event):
        """

        :param event:
        :return:
        """

        painter = QPainter(self)

        if len(self.m_histogram) == 0:
            painter.fillRect(0, 0, self.width(), self.height(),
                             QColor.fromRgb(0, 0, 0))
            return

        barWidth = self.width() / float(len(self.m_histogram))

        for i, value in enumerate(self.m_histogram):
            h = value * self.height()
            # Draw the level.
            painter.fillRect(barWidth * i, self.height() - h,
                             barWidth * (i + 1), self.height(), Qt.red)
            # Clear the rest of the control.
            painter.fillRect(barWidth * i, 0, barWidth * (i + 1),
                             self.height() - h, Qt.black)