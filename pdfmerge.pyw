import os
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor
from PyPDF2 import PdfFileMerger, PdfFileReader


class App(QMainWindow):

	def __init__(self):
		super().__init__()
		self.title = 'PDFMerger'
		self.setWindowTitle(self.title)

		self.table_widget = UIWindow(self)
		self.setCentralWidget(self.table_widget)

		self.show()
		self.statusBar().showMessage('Opening application', 1000)


class ConfirmSkipInvalidPdfDialog(QDialog):

	def __init__(self, *args, **kwargs):
		super(ConfirmSkipInvalidPdfDialog, self).__init__(*args, **kwargs)
		
		self.setWindowTitle('Invalid PDF')

		self.text = QLabel('Unable to merge file')
		self.filename = QLabel()
		
		QBtn = QDialogButtonBox.Ignore | QDialogButtonBox.Abort
		
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.text)
		self.layout.addWidget(self.filename)
		self.layout.addWidget(self.buttonBox)
		self.setLayout(self.layout)


class UIWindow(QWidget):

	def __init__(self, parent=None):
		super(QWidget, self).__init__(parent)
		self.initUI()

	def initUI(self):
		self.pdf_list=[]
		self.scrlboxFileList = QScrollArea()
		self.scrlboxFileList.setWidget(QWidget())

		hbox = QHBoxLayout()
		hbox.addWidget(self.scrlboxFileList)

		btnAddFiles = QPushButton('Add file(s)')
		btnAddFiles.clicked.connect(self.add_files)
		btnAddFolder = QPushButton('Add folder')
		btnAddFolder.clicked.connect(self.add_folder)
		btnMoveUp = QPushButton(u'\u02c4')
		btnMoveUp.clicked.connect(lambda: self.move_pdfs(up=True))
		btnMoveDown = QPushButton(u'\u02c5')
		btnMoveDown.clicked.connect(lambda: self.move_pdfs(up=False))
		btnMoveAllUp = QPushButton(u'\u2b71')
		btnMoveAllUp.clicked.connect(lambda: self.move_all_pdfs(up=True))
		btnMoveAllDown = QPushButton(u'\u2b73')
		btnMoveAllDown.clicked.connect(lambda: self.move_all_pdfs(up=False))
		btnRemove = QPushButton('Remove')
		btnRemove.clicked.connect(self.remove_pdfs)
		btnRemoveAll = QPushButton('Remove all')
		btnRemoveAll.clicked.connect(self.reset_pdf_list)
		btnMerge = QPushButton('Merge')
		btnMerge.clicked.connect(self.merge_pdf)
		btnExit = QPushButton('Exit')
		btnExit.clicked.connect(QCoreApplication.instance().quit)

		widgetBtns = QWidget()
		vboxBtns = QVBoxLayout()

		vboxAddFileBtns = QVBoxLayout()
		vboxAddFileBtns.addWidget(btnAddFiles)
		vboxAddFileBtns.addWidget(btnAddFolder)
		vboxBtns.addLayout(vboxAddFileBtns)

		vboxAllMoveBtns = QVBoxLayout()
		hboxMoveAllBtns = QHBoxLayout()
		hboxMoveAllBtns.addWidget(btnMoveAllUp)
		hboxMoveAllBtns.addWidget(btnMoveAllDown)
		vboxAllMoveBtns.addLayout(hboxMoveAllBtns)

		hboxMoveBtns = QHBoxLayout()
		hboxMoveBtns.addWidget(btnMoveUp)
		hboxMoveBtns.addWidget(btnMoveDown)
		vboxAllMoveBtns.addLayout(hboxMoveBtns)
		vboxBtns.addLayout(vboxAllMoveBtns)

		vboxRemoveBtns = QVBoxLayout()
		vboxRemoveBtns.addWidget(btnRemove)
		vboxRemoveBtns.addWidget(btnRemoveAll)
		vboxBtns.addLayout(vboxRemoveBtns)

		vboxBtns.addWidget(btnMerge)
		vboxBtns.addWidget(btnExit)

		widgetBtns.setLayout(vboxBtns)
		widgetBtns.setFixedWidth(80)

		vboxMain = QVBoxLayout()
		vboxMain.addLayout(hbox)
		hbox.addWidget(widgetBtns)

		self.setLayout(vboxMain)
		self.show()

	def updateUI(self):
		self.pdf_file_UI = []
		vboxFiles = QVBoxLayout()
		for item in self.pdf_list:
			pdf_file = os.path.basename(item['file'])
			chkbox = QCheckBox(pdf_file)
			chkbox.setChecked(item['checked'])
			chkbox.stateChanged.connect(self.updateCheckedPdfList)
			self.pdf_file_UI.append(chkbox)
			vboxFiles.addWidget(chkbox)

		widgetFileList = QWidget()
		widgetFileList.setLayout(vboxFiles)

		self.scrlboxFileList.setWidget(widgetFileList)
		self.scrlboxFileList.update()

	def updateCheckedPdfList(self):
		for n, item in enumerate(self.pdf_file_UI):
			self.pdf_list[n]['checked'] = item.isChecked()

	@pyqtSlot()
	def statusMsg(self, msg, t=2000):
		self.parent().statusBar().showMessage(msg, t)

	def get_skip_confirmation(self, file):
		dlg = ConfirmSkipInvalidPdfDialog(self)
		dlg.filename.setText(f'{file}')
		return dlg.exec_()

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
		if not up:
			self.pdf_list, self.pdf_file_UI = self.pdf_list[::-1], self.pdf_file_UI[::-1]
		for n, item in enumerate(self.pdf_file_UI):
			if item.isChecked():
				if n>0 and not self.pdf_list[n-1]['checked']:
					self.pdf_list[n], self.pdf_list[n-1] = self.pdf_list[n-1], self.pdf_list[n]
		if not up:
			self.pdf_list, self.pdf_file_UI = self.pdf_list[::-1], self.pdf_file_UI[::-1]
		self.updateUI()

	def move_all_pdfs(self, up):
		i = 0
		if not up:
			self.pdf_list, self.pdf_file_UI = self.pdf_list[::-1], self.pdf_file_UI[::-1]
		for n, item in enumerate(self.pdf_file_UI):
			if item.isChecked():
				self.pdf_list.insert(i, self.pdf_list[n])
				del(self.pdf_list[n+1])
				i += 1
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
				try:
					merger.append(open(item['file'], 'rb'))
				except OSError:
					if self.get_skip_confirmation(item['file']):
						pass
					else:
						return
				except Exception as e:
					self.statusMsg(str(e))
					return
			savename = QFileDialog.getSaveFileName(self, 'Save merged PDF', os.getcwd(), 'PDF files (*.pdf)')[0]
			if savename == '': return
			with open(savename , 'wb') as fout:
				merger.write(fout)
			self.statusMsg('Merge Complete!!!')



if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)

	# https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
	# Force the style to be the same on all OSs:
	app.setStyle("Fusion")

	# Now use a palette to switch to dark colors:
	palette = QPalette()
	palette.setColor(QPalette.Window, QColor(53, 53, 53))
	palette.setColor(QPalette.WindowText, Qt.white)
	palette.setColor(QPalette.Base, QColor(25, 25, 25))
	palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
	palette.setColor(QPalette.ToolTipBase, Qt.white)
	palette.setColor(QPalette.ToolTipText, Qt.white)
	palette.setColor(QPalette.Text, Qt.white)
	palette.setColor(QPalette.Button, QColor(53, 53, 53))
	palette.setColor(QPalette.ButtonText, Qt.white)
	palette.setColor(QPalette.BrightText, Qt.red)
	palette.setColor(QPalette.Link, QColor(42, 130, 218))
	palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
	palette.setColor(QPalette.HighlightedText, Qt.black)
	app.setPalette(palette)

	wind = App()
	wind.resize(600, 500)
	wind.show()

	sys.exit(app.exec_())
