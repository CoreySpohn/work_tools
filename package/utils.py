import webbrowser

import pyautogui


def open_i3_screen(screen_num: int) -> None:
    pyautogui.keyDown("winleft")
    pyautogui.press(str(screen_num))
    pyautogui.keyUp("winleft")


def open_website(url: str) -> None:
    webbrowser.open(url, new=2)


def open_website_on_i3_screen(screen_num: int, url: str) -> None:
    open_i3_screen(screen_num)
    open_website(url)
