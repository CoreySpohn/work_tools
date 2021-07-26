from pathlib import Path

from package.ui.anki_subject_ui import Ui_Form as AnkiSubject_Ui_Form
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw


class AnkiSubject(qtw.QWidget):
    got_subject = qtc.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.as_ui = AnkiSubject_Ui_Form()
        self.as_ui.setupUi(self)
        self.as_ui.done_button.clicked.connect(self.collect_subject)

        # Autocomplete stuff for the field so I don't misspell stuff
        self.field_autocomplete_model = qtg.QStandardItemModel()
        p = Path(Path.home(), ".ankivim/decks/")
        subdirs = [d for d in p.iterdir() if d.is_dir()]
        ignored_dirs = ["build"]
        for d in subdirs:
            field = d.parts[-1]
            if field not in ignored_dirs:
                self.field_autocomplete_model.appendRow(qtg.QStandardItem(field))
        self.completer = qtw.QCompleter(self.field_autocomplete_model, self)
        self.as_ui.subject_line_edit.setCompleter(self.completer)

    def collect_subject(self) -> None:
        self.subject = self.as_ui.subject_line_edit.text()
        self.got_subject.emit(self.subject)
