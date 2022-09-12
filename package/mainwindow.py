import datetime
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import package.utils as utils
import pyautogui
from package.AnkiSubject import AnkiSubject
from package.PaperInfo import PaperInfo
from package.ui.mainwindow_ui import Ui_Form
from pynotifier import Notification
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from pyzotero import zotero


class MainWindow(qtw.QWidget):  # Would be something else if you didn't use widget above
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Connection to ticktick
        self.ui.daily_setup_button.clicked.connect(self.daily_setup)

        # Setting up timer
        self.ui.work_button.clicked.connect(self.start_work_timing)
        self.ui.stop_work_button.clicked.connect(self.stop_work_timing)
        self.ui.work_label.setText("6:00:00 s")
        self.ui.work_label.setFont(qtg.QFont("Arial", 30))

        self.work_timer = qtc.QTimer(self)
        self.work_timer.start(1000)
        self.work_start = False
        self.work_timer.timeout.connect(self.show_work_timing)
        self.work_counter = datetime.timedelta(hours=6).seconds

        # Paper reading
        self.paper_path = Path(
            Path.home(), "Documents/github/research-notes/paper_notes"
        )
        self.paper_info = PaperInfo()
        self.paper_info.got_data.connect(self.save_paper_data)
        self.ui.paper_button.clicked.connect(self.paper_reading_popup)
        self.zot = zotero.Zotero('6928401', 'user', 'tWkNdtZH1tr9Z3AYs2iX0IIr')
        # zot.item('ARIJYDQQ') In zotero right click -> copy URI, the end is the itemID
        # https://pyzotero.readthedocs.io/en/latest/#zotero.Zotero.item

        # Flash card stuff
        self.anki_subject = AnkiSubject()
        self.anki_subject.got_subject.connect(self.write_flash_cards)
        self.ui.write_flash_cards_button.clicked.connect(self.anki_subject_popup)
        self.ui.add_flash_cards_button.clicked.connect(self.add_flash_cards_to_anki)

    def daily_setup(self):
        utils.open_website_on_i3_screen(1, "https://www.ticktick.com")
        utils.open_website("https://mail.google.com/mail/u/1")
        self.work_counter = datetime.timedelta(hours=6).seconds
        if self.work_start is False:
            self.work_start = True
        else:
            print('Already started')

    def start_work_timing(self) -> None:
        # self.ui.work_button.setEnabled(False)
        if self.work_start is False:
            self.work_start = True
        else:
            print('Already started')

    def stop_work_timing(self) -> None:
        # self.ui.work_button.setEnabled(False)
        if self.work_start is True:
            self.work_start = False
        else:
            print('Already stopped')

    def show_work_timing(self) -> None:
        if self.work_start:
            self.work_counter -= 1
            if self.work_counter == 0:
                # timing completed
                self.ui.work_label.setText("Done")
                Notification(
                    title="Work is done for today",
                    description="Good shit my dude",
                    duration=10,
                    urgency="critical",
                ).send()
                self.work_start = False
            self.ui.work_label.setText(
                f"{datetime.timedelta(seconds = self.work_counter)} s"
            )

    def paper_reading_popup(self) -> None:
        utils.open_i3_screen(5)
        subprocess.Popen("/usr/bin/zotero")
        time.sleep(1)

        self.paper_info.show()
        # After opening mendeley open a pop-up for when the paper has been found
        # Then it'll get the paper information from mendeley so that it can write it into the tex files
        # I need the paper title, author, and year

    def save_paper_data(
        self, uri: str, field: str, title: str, authors: str, journal: str, year: str, tags: str
    ) -> None:
        """
        After the pop-up window is closed it will trigger this which saves all
        of the data and then calls the function that opens the tex file to
        write notes in
        """
        self.paper_uri = uri
        itemID = uri.split('/')[-1]
        item_info = self.zot.item(itemID)
        self.paper_data = item_info['data']
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
        paper_field_path = Path(
            self.paper_path, self.paper_field.lower().replace(" ", "_")
        )
        paper_field_tex_path = Path(
            paper_field_path, self.paper_field.lower()
        ).with_suffix(".tex")
        if not paper_field_tex_path.exists():
            # Make the directory and primary tex file for the field if it doesn't exist
            paper_field_path.mkdir(parents=True, exist_ok=True)

            # Create the paper_notes/field/field.tex file
            field_tex_str = f"\chapter{{{self.paper_field.capitalize()}}}"
            with open(paper_field_tex_path, "w") as tex_file:
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

        # Get paper author information
        paper_authors = self.paper_data['creators']
        author_str = ''
        for i, author in enumerate(paper_authors):
            if i==0:
                paper_first_author = author['lastName']
            if i+1 == len(paper_authors):
                author_str += f"{author['firstName']} {author['lastName']}"             
            else:
                author_str += f"{author['firstName']} {author['lastName']}, "

        paper_title = self.paper_data['title']
        paper_year = self.paper_data['date'].split('-')[0]
        journal = self.paper_data['publicationTitle']
        tags = self.paper_data['tags']
        tags_str = ''
        for i, tag in enumerate( tags ):
            if i+1 == len(tags):
                tags_str += tag['tag']
            else:
                tags_str += f"{tag['tag']}, "
        paper_abstract = self.paper_data['abstractNote']
        paper_doi = self.paper_data['DOI']
        # Now to abbreviate the title and create the filename
        paper_title_cut = paper_title[:60].lower().replace(" ", "_")
        paper_title_abbrev = re.sub(r"[^\w\s]", "", paper_title_cut)
        paper_tex_filename = (
            f"{paper_first_author}_{paper_year}_{paper_title_abbrev}.tex"
        )
        paper_tex_filename_path = Path(
            paper_field_path, paper_tex_filename
        )

        # Now set up the formatting for what we'll write to the file before opening it
        # Rewriting the names in first last order, god that's ugly
        # self.paper_authors_first_last = "".join(
            # [
                # f"{first} {last},"
                # for last, first in [
                    # name.split(",") for name in self.paper_authors.split("\n")
                # ]
            # ]
        # )[1:-1]
        raw_paper_write_lines = f"\\newpage\n\paper{{{paper_title}}}\n\paperauthor{{{author_str}}}\n\paperjournal{{{journal}}}\n\paperyear{{{paper_year}}}\n\papertags{{{tags_str}}}\n\\reviewdate{{{datetime.date.today().strftime('%A, %B %d %Y')}}}\n\DOI{{{paper_doi}}}\n\\abstractsmall{{{paper_abstract}}}\n\section{{Summary of paper}}\n"

        # Use regex to escape the latex symbols that need to be escaped
        escaped_symbols = r"(?=[&%$#_~^])"
        paper_write_lines = re.sub(escaped_symbols, r"\\", raw_paper_write_lines)

        # Write that to the file
        with open(paper_tex_filename_path, "w") as paper_file:
            paper_file.writelines(paper_write_lines)

        # Now add that file into the field/field.tex file
        with open(paper_field_tex_path, "r") as paper_field_file:
            paper_field_lines = paper_field_file.readlines()

        paper_field_lines.append(
            f"\n\input{{{self.paper_field.lower()}/{paper_tex_filename}}}"
        )
        with open(paper_field_tex_path, "w") as paper_field_file:
            paper_field_file.writelines(paper_field_lines)

        # Now open up the created file in vim for editing
        os.system(
            f"gnome-terminal -e 'bash -c \"nvim {paper_tex_filename_path}; exec bash\"'"
        )
        pyautogui.press("G")
        pyautogui.press("o")

    def anki_subject_popup(self) -> None:
        """
        This goes to the proper i3 screen and opens up a menu to select the study subject
        """
        utils.open_i3_screen(7)
        self.anki_subject.show()

    def write_flash_cards(self, subject: str) -> None:
        """
        This opens after the self.anki_subject popup done button is clicked thanks to the
        self.anki_subject.got_subject.connect(self.write_flash_cards)
        line. Then it opens that subject
        """
        self.anki_subject.close()
        self.anki_subject_str = subject
        os.system(
            f"gnome-terminal -e 'bash -c \"anki-vim {self.anki_subject_str}; exec bash\"'"
        )

    def add_flash_cards_to_anki(self) -> None:
        """
        This will open up the anki app and then the import card menu
        """
        utils.open_i3_screen(7)
        subprocess.Popen("anki")
        time.sleep(2)
        # ctrl+shift+I
        pyautogui.hotkey("ctrl", "shift", "i")
