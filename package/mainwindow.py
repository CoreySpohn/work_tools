import datetime
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import package.utils as utils
import pyautogui
from package.PaperInfo import PaperInfo
from package.ui.mainwindow_ui import Ui_Form
from pynotifier import Notification
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw


class MainWindow(qtw.QWidget):  # Would be something else if you didn't use widget above
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Connection to ticktick
        self.ui.daily_setup_button.clicked.connect(self.daily_setup)

        # Setting up timer
        self.ui.deep_work_button.clicked.connect(self.start_deep_work_timing)
        self.ui.deep_work_label.setText("1:30:00 s")
        self.ui.deep_work_label.setFont(qtg.QFont("Arial", 30))

        self.deep_work_timer = qtc.QTimer(self)
        self.deep_work_timer.start(1000)
        self.deep_work_start = False
        self.deep_work_counter = datetime.timedelta(minutes=90).seconds
        self.deep_work_timer.timeout.connect(self.show_deep_work_timing)

        # Paper reading
        self.paper_path = Path(
            Path.home(), "Documents/github/research-notes/paper_notes"
        )
        self.paper_info = PaperInfo()
        self.paper_info.got_data.connect(self.save_paper_data)
        self.ui.paper_button.clicked.connect(self.paper_reading_popup)

        # Flash card stuff
        self.ui.write_flash_cards_button.clicked.connect(self.write_flash_cards)
        self.ui.add_flash_cards_button.clicked.connect(self.add_flash_cards_to_anki)

    def pop_up_str_input(self, prompt):
        text, _ = qtw.QInputDialog.getText(
            self, "Getting string", prompt, qtw.QLineEdit.Normal, ""
        )
        return text

    def daily_setup(self):
        utils.open_website_on_i3_screen(1, "https://www.ticktick.com")
        utils.open_website("https://mail.google.com")

    def start_deep_work_timing(self) -> None:
        self.ui.deep_work_button.setEnabled(False)
        self.deep_work_start = True

    def show_deep_work_timing(self) -> None:
        if self.deep_work_start:
            self.deep_work_counter -= 1
            if self.deep_work_counter == 0:
                # timing completed
                self.ui.deep_work_label.setText("Done")
                Notification(
                    title="Deep work is done",
                    description="You should go do something for a few minutes, good job!",
                    duration=10,
                    urgency="critical",
                ).send()
                self.deep_work_start = False
            self.ui.deep_work_label.setText(
                f"{datetime.timedelta(seconds = self.deep_work_counter)} s"
            )

    def paper_reading_popup(self) -> None:
        utils.open_i3_screen(5)
        subprocess.Popen("/usr/bin/mendeleydesktop")
        time.sleep(1)

        self.paper_info.show()
        # After opening mendeley open a pop-up for when the paper has been found
        # Then it'll get the paper information from mendeley so that it can write it into the tex files
        # I need the paper title, author, and year

    def save_paper_data(
        self, field: str, title: str, authors: str, journal: str, year: str, tags: str
    ) -> None:
        """
        After the pop-up window is closed it will trigger this which saves all
        of the data and then calls the function that opens the tex file to
        write notes in
        """
        self.paper_field = field
        self.paper_title = title
        self.paper_authors = authors
        self.paper_journal = journal
        self.paper_year = year
        self.paper_tags = tags
        self.paper_info.close()
        self.handle_paper_tex_files()

    def handle_paper_tex_files(self) -> None:
        utils.open_i3_screen(5)
        # TODO Figure out alll the places I need references in the paper-notes repository
        # So it needs to make the field folder if it doesn't exist, if that's
        # the case then it also needs to write in the main.tex document an
        # \input{field/field.tex}
        self.paper_field_path = Path(
            self.paper_path, self.paper_field.lower().replace(" ", "_")
        )
        self.paper_field_tex_path = Path(
            self.paper_field_path, self.paper_field.lower()
        ).with_suffix(".tex")
        if not self.paper_field_tex_path.exists():
            # Make the directory and primary tex file for the field if it doesn't exist
            self.paper_field_path.mkdir(parents=True, exist_ok=True)

            # Create the paper_notes/field/field.tex file
            field_tex_str = f"\chapter{{{self.paper_field.capitalize()}}}"
            with open(self.paper_field_tex_path, "w") as tex_file:
                tex_file.write(field_tex_str)

            # Then input that chapter to the main.tex file
            main_tex_file_path = Path(self.paper_path, "main.tex")
            with open(main_tex_file_path, "r") as main_tex_file:
                main_tex_lines = main_tex_file.readlines()

            # After loading all of the lines duplicate the last line (end
            # document), and then above the end of the document write the line
            # inputting the new section
            main_tex_lines.append(main_tex_lines[-1])
            main_tex_lines[
                -2
            ] = f"\input{{{self.paper_field.lower()}/{self.paper_field.lower()}.tex}}\n"

            # Write changes to main.tex
            with open(main_tex_file_path, "w") as main_tex_file:
                main_tex_file.writelines(main_tex_lines)

        # Make for the paper specific information, starting with making the tex file
        self.paper_first_author = self.paper_authors.split("\n")[0].split(",")[0]

        # Now to abbreviate the title and create the filename
        paper_title_cut = self.paper_title[:60].lower().replace(" ", "_")
        self.paper_title_abbrev = re.sub(r"[^\w\s]", "", paper_title_cut)
        self.paper_tex_filename = (
            f"{self.paper_first_author}_{self.paper_year}_{self.paper_title_abbrev}.tex"
        )
        self.paper_tex_filename_path = Path(
            self.paper_field_path, self.paper_tex_filename
        )

        # Now set up the formatting for what we'll write to the file before opening it
        # Rewriting the names in first last order, god that's ugly
        self.paper_authors_first_last = "".join(
            [
                f"{first} {last},"
                for last, first in [
                    name.split(",") for name in self.paper_authors.split("\n")
                ]
            ]
        )[1:-1]
        raw_paper_write_lines = f"\\newpage\n\paper{{{self.paper_title}}}\n\paperauthor{{{self.paper_authors_first_last}}}\n\paperjournal{{{self.paper_journal}}}\n\paperyear{{{self.paper_year}}}\n\papertags{{{self.paper_tags}}}\n\\reviewdate{{{datetime.date.today().strftime('%A, %B %d %Y')}}}\n\section{{Summary of paper}}\n"

        # Use regex to escape the latex symbols that need to be escaped
        escaped_symbols = r"(?=[&%$#_~^])"
        self.paper_write_lines = re.sub(escaped_symbols, r"\\", raw_paper_write_lines)

        # Write that to the file
        with open(self.paper_tex_filename_path, "w") as paper_file:
            paper_file.writelines(self.paper_write_lines)

        # Now add that file into the field/field.tex file
        with open(self.paper_field_tex_path, "r") as paper_field_file:
            paper_field_lines = paper_field_file.readlines()

        paper_field_lines.append(
            f"\input{{{self.paper_field.lower()}/{self.paper_tex_filename}}}"
        )
        with open(self.paper_field_tex_path, "w") as paper_field_file:
            paper_field_file.writelines(paper_field_lines)

        # Now open up the created file in vim for editing
        os.system(
            f"gnome-terminal -e 'bash -c \"vim {self.paper_tex_filename_path}; exec bash\"'"
        )
        pyautogui.press("G")
        pyautogui.press("o")

    def write_flash_cards(self) -> None:
        utils.open_i3_screen(7)
        self.study_deck = self.pop_up_str_input("What Anki deck?").replace(" ", "_")
        os.system(
            f"gnome-terminal -e 'bash -c \"anki-vim {self.study_deck}; exec bash\"'"
        )

    def add_flash_cards_to_anki(self) -> None:
        utils.open_i3_screen(7)
        subprocess.Popen("anki")
        time.sleep(2)
        # ctrl+shift+I
        pyautogui.hotkey("ctrl", "shift", "i")
