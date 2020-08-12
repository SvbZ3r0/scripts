import cv2
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor, QImage, QPixmap

class VideoThread(QThread):
	changePixmap = pyqtSignal(QImage)

	def __init__(self):
		super().__init__()
		self.is_running = True

	def run(self):
		cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
		while self.is_running:
			ret, frame = cap.read()
			if ret:
				# https://stackoverflow.com/a/55468544/6622587
				rgbImage = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),1)
				h, w, ch = rgbImage.shape
				bytesPerLine = ch * w
				convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
				p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
				self.changePixmap.emit(p)
				# Added to reduce crashes when moving the window
				QThread.msleep(125)
		cap.release()

	def stop(self):
		self.is_running = False
		self.wait()


class App(QMainWindow):

	def __init__(self):
		super().__init__()
		self.title = 'PDFMerger'
		self.setWindowTitle(self.title)

		self.table_widget = UIWindow(self)
		self.setCentralWidget(self.table_widget)
		self.setFixedSize(self.size())

		self.show()

	def closeEvent(self, event):
		self.table_widget.th.stop()
		event.accept()

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.table_widget.th.stop()
			self.close()


class UIWindow(QWidget):
	def __init__(self, parent=None):
		super(QWidget, self).__init__(parent)
		self.initUI()

	@pyqtSlot(QImage)
	def setImage(self, image):
		self.labelVideo.setPixmap(QPixmap.fromImage(image))

	def initUI(self):
		self.widgetDisp = QWidget()
		vbox = QVBoxLayout(self.widgetDisp)
		
		self.labelVideo = QLabel(self)
		self.labelVideo.resize(640, 480)
		vbox.addWidget(self.labelVideo)
		self.setLayout(vbox)
		self.th = VideoThread()
		self.th.changePixmap.connect(self.setImage)
		self.th.start()
		self.show()

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)

	palette = QPalette()
	palette.setColor(QPalette.Window, QColor(53, 53, 53))
	app.setPalette(palette)

	wind = App()
	wind.resize(640, 480)
	wind.show()

	sys.exit(app.exec_()) 