import pyautogui
import webbrowser

def open_i3_screen(screen_num):
    pyautogui.keyDown('winleft')
    pyautogui.press(str(screen_num))
    pyautogui.keyUp('winleft')

def open_website(url):
    webbrowser.open(url, new=2)

def open_website_on_i3_screen(screen_num, url):
    open_i3_screen(screen_num)
    open_website(url)
