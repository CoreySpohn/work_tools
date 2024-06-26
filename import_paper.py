import datetime

# import os
import re

# import subprocess
# import time
from pathlib import Path

# import pyautogui
# from pynotifier import Notification
# from PyQt5 import QtCore as qtc
# from PyQt5 import QtGui as qtg
# from PyQt5 import QtWidgets as qtw
from pyzotero import zotero

# import package.utils as utils
# from package.AnkiSubject import AnkiSubject
# from package.PaperInfo import PaperInfo
# from package.ui.mainwindow_ui import Ui_Form


# class MainWindow(qtw.QWidget):  # Would be something else if you didn't use widget above
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.ui = Ui_Form()
#         self.ui.setupUi(self)

#         # Connection to ticktick
#         self.ui.daily_setup_button.clicked.connect(self.daily_setup)

#         # Setting up timer
#         self.ui.work_button.clicked.connect(self.start_work_timing)
#         self.ui.stop_work_button.clicked.connect(self.stop_work_timing)
#         self.ui.work_label.setText("6:00:00 s")
#         self.ui.work_label.setFont(qtg.QFont("Arial", 30))

#         self.work_timer = qtc.QTimer(self)
#         self.work_timer.start(1000)
#         self.work_start = False
#         self.work_timer.timeout.connect(self.show_work_timing)
#         self.work_counter = datetime.timedelta(hours=6).seconds

#         # Paper reading
#         # self.paper_path.mkdir(parents=True, exist_ok=True)
#         self.paper_info = PaperInfo()
#         self.paper_info.got_data.connect(self.save_paper_data)
#         self.ui.paper_button.clicked.connect(self.paper_reading_popup)
#         self.zot = zotero.Zotero("6928401", "user", "tWkNdtZH1tr9Z3AYs2iX0IIr")
#         # zot.item('ARIJYDQQ') In zotero right click -> copy URI, the end is the itemID
#         # https://pyzotero.readthedocs.io/en/latest/#zotero.Zotero.item

#         # Flash card stuff
#         self.anki_subject = AnkiSubject()
#         self.anki_subject.got_subject.connect(self.write_flash_cards)
#         self.ui.write_flash_cards_button.clicked.connect(self.anki_subject_popup)
#         self.ui.add_flash_cards_button.clicked.connect(self.add_flash_cards_to_anki)

#     def daily_setup(self):
#         utils.open_website_on_i3_screen(1, "https://www.ticktick.com")
#         utils.open_website("https://mail.google.com/mail/u/1")
#         self.work_counter = datetime.timedelta(hours=6).seconds
#         if self.work_start is False:
#             self.work_start = True
#         else:
#             print("Already started")

#     def start_work_timing(self) -> None:
#         # self.ui.work_button.setEnabled(False)
#         if self.work_start is False:
#             self.work_start = True
#         else:
#             print("Already started")

#     def stop_work_timing(self) -> None:
#         # self.ui.work_button.setEnabled(False)
#         if self.work_start is True:
#             self.work_start = False
#         else:
#             print("Already stopped")

#     def show_work_timing(self) -> None:
#         if self.work_start:
#             self.work_counter -= 1
#             if self.work_counter == 0:
#                 # timing completed
#                 self.ui.work_label.setText("Done")
#                 Notification(
#                     title="Work is done for today",
#                     description="Good shit my dude",
#                     duration=10,
#                     urgency="critical",
#                 ).send()
#                 self.work_start = False
#             self.ui.work_label.setText(
#                 f"{datetime.timedelta(seconds = self.work_counter)} s"
#             )

#     def paper_reading_popup(self) -> None:
#         utils.open_i3_screen(5)
#         subprocess.Popen("/usr/bin/zotero")
#         time.sleep(1)

#         self.paper_info.show()
#         # After opening mendeley open a pop-up for when the paper has been found
#         # Then it'll get the paper information from mendeley so that it can write
#         # it into the md files
#         # I need the paper title, author, and year

#     def save_paper_data(
#         self,
#         uri: str,
#     ) -> None:
#         """
#         After the pop-up window is closed it will trigger this which saves all
#         of the data and then calls the function that opens the md file to
#         write notes in
#         """
#         self.paper_uri = uri
#         itemID = uri.split("/")[-1]
#         item_info = self.zot.item(itemID)
#         self.paper_data = item_info["data"]
#         self.paper_info.close()
#         self.handle_paper_files()


#     def anki_subject_popup(self) -> None:
#         """
#         This goes to the proper i3 screen and opens up a menu to select the study
#         subject
#         """
#         utils.open_i3_screen(7)
#         self.anki_subject.show()

#     def write_flash_cards(self, subject: str) -> None:
#         """
#         This opens after the self.anki_subject popup done button is clicked thanks to
#         the self.anki_subject.got_subject.connect(self.write_flash_cards)
#         line. Then it opens that subject
#         """
#         self.anki_subject.close()
#         self.anki_subject_str = subject
#         os.system(
#             (
#                 "gnome-terminal -e 'bash -c \"anki-vim "
#                 f"{self.anki_subject_str}; exec bash\"'"
#             )
#         )


#     def add_flash_cards_to_anki(self) -> None:
#         """
#         This will open up the anki app and then the import card menu
#         """
#         utils.open_i3_screen(7)
#         subprocess.Popen("anki")
#         time.sleep(2)
#         # ctrl+shift+I
#         pyautogui.hotkey("ctrl", "shift", "i")
def handle_paper_files(paper_data) -> None:
    # utils.open_i3_screen(5)

    # Get paper author information
    paper_authors = paper_data["creators"]
    author_str = ""
    for i, author in enumerate(paper_authors):
        # if i + 1 == len(paper_authors):
        #     author_str += f"[[{author['firstName']} {author['lastName']}]]"
        # else:
        #     author_str += f"[[{author['firstName']} {author['lastName']}]], "
        if i + 1 == len(paper_authors):
            author_str += f"{author['firstName']} {author['lastName']}"
        else:
            author_str += f"{author['firstName']} {author['lastName']}, "

    paper_title = paper_data["title"]
    paper_year = paper_data["date"].split("-")[0]
    if paper_data["itemType"] == "conferencePaper":
        journal = paper_data["proceedingsTitle"]
    elif paper_data["itemType"] == "preprint":
        journal = "arXiv"
    elif paper_data["itemType"] == "book":
        journal = "Book"
    else:
        journal = paper_data["publicationTitle"]
    tags = paper_data["tags"]
    tags_str = ""
    for i, tag in enumerate(tags):
        if i + 1 == len(tags):
            tags_str += f"[[{tag['tag']}]]"
        else:
            tags_str += f"[[{tag['tag']}]], "
    paper_abstract = paper_data["abstractNote"]
    # Replace ':' with '-' because the ':' is used for the front matter in the markdown
    paper_title = paper_title.replace(":", "-")
    paper_abstract = paper_abstract.replace(":", "-")
    if "DOI" not in paper_data:
        paper_doi = ""
    else:
        paper_doi = paper_data["DOI"]
    paper_filename = f"{paper_title}.md"
    # MAC
    # paper_path = Path(Path.home(), "Documents/ideaverse/Knowledge/Notes/Sources/Papers")
    # DESKTOP
    paper_path = Path(Path.home(), ".vault/ideaverse/Knowledge/Notes/Sources/Papers")
    paper_filename_path = Path(paper_path, paper_filename)

    # Now set up the formatting for what we'll write to the file before opening it
    # Rewriting the names in first last order, god that's ugly
    raw_paper_write_lines = (
        "---\n"
        f"tags: paper\n"
        f"aliases: {paper_title}\n"
        f"abstract: {paper_abstract}\n"
        "---\n"
        f"# {paper_title}\n"
        "\n"
        "---\n"
        "\n"
        f"Title:: {paper_title}\n"
        f"Author:: {author_str}\n"
        f"Journal:: {journal}\n"
        f"Year:: {paper_year}\n"
        f"Tags:: {tags_str}\n"
        f"DOI:: {paper_doi}\n"
        f"ReviewedDate:: {datetime.date.today().strftime('%A, %B %d %Y')}\n"
        "\n---\n\n"
        f"## Abstract\n{paper_abstract}\n\n"
        "## Reading checklist\n"
        "- [ ] Write questions\n"
        "- [ ] Abstract\n"
        "- [ ] Conclusion\n"
        "- [ ] Introduction\n"
        "- [ ] Skim figures and middle\n"
        "- [ ] Re-read\n"
        "- [ ] Answer questions\n"
        "- [ ] Check for other papers that cite it\n\n"
        "## Questions to be answered\n"
        "### What is this paper about, as a whole?\n"
        "- \n"
        "### What is being said in detail and with what methods?\n"
        "- \n"
        "### Is this true? In whole or in part?\n"
        "- \n"
        "### What of it?\n"
        "- \n"
        "## Useful points\n- \n\n"
        "## Interesting references\n-\n"
    )

    # Use regex to escape the latex symbols that need to be escaped
    escaped_symbols = r"(?=[&%$_~^])"
    paper_write_lines = re.sub(escaped_symbols, r"\\", raw_paper_write_lines)

    # Write that to the file
    with open(paper_filename_path, "w") as paper_file:
        paper_file.writelines(paper_write_lines)


if __name__ == "__main__":
    zot = zotero.Zotero("6928401", "user", "tWkNdtZH1tr9Z3AYs2iX0IIr")
    uri = input("Enter paper URI: ")
    itemID = uri.split("/")[-1]
    item_info = zot.item(itemID)
    paper_data = item_info["data"]
    handle_paper_files(paper_data)
