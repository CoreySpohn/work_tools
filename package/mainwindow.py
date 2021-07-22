import datetime
import os
import subprocess
import sys
import time

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
        self.paper_info = PaperInfo()
        self.paper_info.got_data.connect(self.save_paper_data)
        self.ui.paper_button.clicked.connect(self.paper_reading_popup)

        # Independent study
        self.ui.independent_study_button.clicked.connect(self.independent_study)

    def pop_up_str_input(self, prompt):
        text, _ = qtw.QInputDialog.getText(
            self, "Getting string", prompt, qtw.QLineEdit.Normal, ""
        )
        return text

    def daily_setup(self):
        utils.open_website_on_i3_screen(1, "https://www.ticktick.com")
        utils.open_website("https://mail.google.com")

    def start_deep_work_timing(self):
        self.ui.deep_work_button.setEnabled(False)
        self.deep_work_start = True

    def show_deep_work_timing(self):
        if self.deep_work_start:
            self.deep_work_counter -= 1
            if self.deep_work_counter == 0:
                # timing completed
                self.ui.deep_work_label.setText("Done")
                # TODO Add system notification
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

    def paper_reading_popup(self):
        utils.open_i3_screen(5)
        # subprocess.call("/usr/bin/mendeleydesktop")

        self.paper_info.show()
        # After opening mendeley open a pop-up for when the paper has been found
        # Then it'll get the paper information from mendeley so that it can write it into the tex files
        # I need the paper title, author, and year

    def save_paper_data(self, title, author, year):
        self.paper_title = title
        self.paper_author = author
        self.paper_year = year
        self.paper_info.close()

    def open_paper_tex_files(self):
        utils.open_i3_screen(5)

    def independent_study(self):
        utils.open_i3_screen(7)
        # os.system("gnome-terminal -e 'bash -c \"sudo apt-get update; exec bash\"'")
        study_deck = self.pop_up_str_input("What Anki deck?").replace(" ", "_")
        os.system("gnome-terminal")
        time.sleep(0.25)
        pyautogui.write(f"anki-vim {study_deck}")
        pyautogui.press("enter")
