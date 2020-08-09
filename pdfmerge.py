import os
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyPDF2 import PdfFileMerger, PdfFileReader


class App(QMainWindow):

	def __init__(self):
		super().__init__()
		self.title = 'PDFMerger'
		self.left = 200
		self.top = 70
		self.width = 200
		self.height = 100
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.table_widget = UIWindow(self)
		self.setCentralWidget(self.table_widget)

		self.show()
		self.statusBar().showMessage('Opening application', 2000)


class UIWindow(QWidget):
	def __init__(self, parent=None):
		super(QWidget, self).__init__(parent)
		self.initUI()


	def initUI(self):
		self.pdf_list=[]
		self.scrlboxFileList = QScrollArea()
		self.scrlboxFileList.setWidget(QWidget())

		self.hbox = QHBoxLayout()
		self.hbox.addWidget(self.scrlboxFileList)

		btnAddFiles = QPushButton('Add file(s)')
		btnAddFiles.clicked.connect(self.add_files)
		btnAddFolder = QPushButton('Add folder')
		btnAddFolder.clicked.connect(self.add_folder)
		btnMoveUp = QPushButton(u'\u02c4')
		btnMoveUp.clicked.connect(lambda: self.move_pdfs(up=True))
		btnMoveDown = QPushButton(u'\u02c5')
		btnMoveDown.clicked.connect(lambda: self.move_pdfs(up=False))
		btnRemove = QPushButton('Remove')
		btnRemove.clicked.connect(self.remove_pdfs)
		btnRemoveAll = QPushButton('Remove all')
		btnRemoveAll.clicked.connect(self.reset_pdf_list)
		btnMerge = QPushButton('Merge')
		btnMerge.clicked.connect(self.merge_pdf)
		btnExit = QPushButton('Exit')
		btnExit.clicked.connect(QCoreApplication.instance().quit)

		vboxBtns = QVBoxLayout()

		vboxAddFileBtns = QVBoxLayout()
		vboxAddFileBtns.addWidget(btnAddFiles)
		vboxAddFileBtns.addWidget(btnAddFolder)
		vboxBtns.addLayout(vboxAddFileBtns)

		hboxMoveBtns = QHBoxLayout()
		hboxMoveBtns.addWidget(btnMoveUp)
		hboxMoveBtns.addWidget(btnMoveDown)
		vboxBtns.addLayout(hboxMoveBtns)

		vboxRemoveBtns = QVBoxLayout()
		vboxRemoveBtns.addWidget(btnRemove)
		vboxRemoveBtns.addWidget(btnRemoveAll)
		vboxBtns.addLayout(vboxRemoveBtns)

		vboxBtns.addWidget(btnMerge)
		vboxBtns.addWidget(btnExit)

		vboxMain = QVBoxLayout()
		vboxMain.addLayout(self.hbox)
		self.hbox.addLayout(vboxBtns)

		self.setLayout(vboxMain)
		self.show()

	def updateUI(self):
		self.pdf_file_UI = []
		vboxFiles = QVBoxLayout()
		for item in self.pdf_list:
			print(item)
			pdf_file = os.path.basename(item['file'])
			chkbox = QCheckBox(pdf_file)
			chkbox.setChecked(item['checked'])
			chkbox.stateChanged.connect(self.updateChecked)
			self.pdf_file_UI.append(chkbox)
			vboxFiles.addWidget(chkbox)

		widgetFileList = QWidget()
		widgetFileList.setLayout(vboxFiles)

		self.scrlboxFileList.setWidget(widgetFileList)
		self.scrlboxFileList.update()

	def updateChecked(self):
		self.pdf_list = []
		for item in self.pdf_file_UI:
			self.pdf_list.append({'file':item.text(), 'checked':item.isChecked()})

	@pyqtSlot()
	def merge(self):
		self.parent().statusBar().showMessage('Merging')

	@pyqtSlot()
	def statusMsg(self, msg, t=2000):
		self.parent().statusBar().showMessage(msg, t)

	@pyqtSlot()
	def toggleStatusBar(self):
		if self.parent().statusBar().isHidden():
			self.parent().statusBar().show()
		else:
			self.parent().statusBar().hide()

	def add_files(self):
		pdf_file = QFileDialog.getOpenFileNames(self, 'Select PDFs', os.getcwd(), 'PDF files (*.pdf)')
		# add pdf files
		for file in pdf_file[0]:
			if os.path.splitext(file)[-1] != '.pdf':
				self.statusMsg('Skipping files that aren\'t PDFs', 1000)
				continue
			self.pdf_list.append({'file':file, 'checked':False})
		self.updateUI()
	
	def add_folder(self):
		pdf_folder = QFileDialog.getExistingDirectory(self, 'Select PDFs', os.getcwd())
		if not os.path.exists(pdf_folder):
			return
		for file in os.listdir(pdf_folder):
			if os.path.splitext(file)[-1] == '.pdf':
				self.pdf_list.append({'file':os.path.join(pdf_folder, file), 'checked':False})
		self.updateUI()

	def move_pdfs(self, up):
		# up = True
		if not up:
			self.pdf_list, self.pdf_file_UI = self.pdf_list[::-1], self.pdf_file_UI[::-1]
		for n, item in enumerate(self.pdf_file_UI):
			if item.isChecked():
				if n>0 and not self.pdf_list[n-1]['checked']:
					self.pdf_list[n], self.pdf_list[n-1] = self.pdf_list[n-1], self.pdf_list[n]
		if not up:
			self.pdf_list, self.pdf_file_UI = self.pdf_list[::-1], self.pdf_file_UI[::-1]
		self.updateUI()

	def remove_pdfs(self):
		i = 0
		for n, item in enumerate(self.pdf_file_UI):
			if item.isChecked():
				del(self.pdf_list[n-i])
				i += 1
		self.updateUI()

	def reset_pdf_list(self):
		self.pdf_list=[]
		self.updateUI()
	
	def merge_pdf(self):
		if len(self.pdf_list)==0:
			self.statusMsg('There is nothing to merge!')
		elif len(self.pdf_list)==1:
			self.statusMsg('Only single file is present. No need to merge.')
		else:
			self.statusMsg('Merging files', 5000)
			merger = PdfFileMerger()
			for item in self.pdf_list:
				merger.append(open(item['file'], 'rb'))
			savename = QFileDialog.getSaveFileName(self, 'Save merged PDF', os.getcwd(), 'PDF files (*.pdf)')[0]
			with open(savename , 'wb') as fout:
				merger.write(fout)
			self.statusMsg('Merge Complete!!!')



if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)

	wind = App()
	wind.resize(600, 500)
	wind.move(50,150)
	wind.show()

	sys.exit(app.exec_())