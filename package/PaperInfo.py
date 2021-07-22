from package.ui.paper_info_ui import Ui_Form as PaperInfo_Ui_Form
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw


class PaperInfo(qtw.QWidget):
    got_data = qtc.pyqtSignal(str, str, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pi_ui = PaperInfo_Ui_Form()
        self.pi_ui.setupUi(self)
        self.pi_ui.done_button.clicked.connect(self.collect_paper_info)

    def collect_paper_info(self):
        self.title = self.pi_ui.paper_title_line_edit.text()
        self.author = self.pi_ui.paper_author_line_edit.text()
        self.year = self.pi_ui.paper_year_line_edit.text()
        self.got_data.emit(self.title, self.author, self.year)
