from package.ui.paper_info_ui import Ui_Form as PaperInfo_Ui_Form
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw


class PaperInfo(qtw.QWidget):
    got_data = qtc.pyqtSignal(str, str, str, str, str, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pi_ui = PaperInfo_Ui_Form()
        self.pi_ui.setupUi(self)
        self.pi_ui.done_button.clicked.connect(self.collect_paper_info)

    def collect_paper_info(self) -> None:
        self.field = self.pi_ui.paper_field_line_edit.text()
        self.title = self.pi_ui.paper_title_line_edit.text()
        self.authors = self.pi_ui.paper_authors_line_edit.text()
        self.journal = self.pi_ui.paper_journal_line_edit.text()
        self.year = self.pi_ui.paper_year_line_edit.text()
        self.tags = self.pi_ui.paper_tags_line_edit.text()
        self.got_data.emit(
            self.field, self.title, self.authors, self.journal, self.year, self.tags
        )
