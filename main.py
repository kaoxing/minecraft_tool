import time

import cv2
import numpy
import numpy as np
from PIL import ImageGrab, Image
import win32api
import win32con
import win32gui
import keyboard
from threading import Lock

# 原始屏幕分辨率
screen_x = 1294
screen_y = 707


class Fisher:
    def __init__(self):
        self.end_button = None
        self.state = 0  # 0: waiting for start, 1: fishing, 2: eating, 3:stop
        self.start_button = None
        self.eat_button = None
        self.fish_button = None
        self.stop_button = None
        self.fishTemp = cv2.imread('fish.png', 0)
        self.hwnd = win32gui.FindWindow(None, 'Create Flavored 5.10')
        if self.hwnd == 0:
            print('未找到游戏窗口')
            exit(1)
        print('已找到游戏窗口')
        window_size = win32gui.GetWindowRect(self.hwnd)
        print(window_size)
        window_x = window_size[2] - window_size[0]
        window_y = window_size[3] - window_size[1]
        # 按当前窗口和原始窗口的比例缩放fishTemp
        x_rate = window_x / screen_x
        y_rate = window_y / screen_y
        print(self.fishTemp.shape)
        self.fishTemp = cv2.resize(self.fishTemp, (0, 0), fx=x_rate, fy=y_rate)
        print(self.fishTemp.shape)
        print(x_rate, y_rate)
        # cv2.imshow('fish', self.fishTemp)
        # cv2.waitKey(0)
        self.mid_x = int((window_size[0] + window_size[2]) / 2)
        self.mid_y = int((window_size[1] + window_size[3]) / 2)
        self.lock = Lock()

    def start_task(self):
        self.setting_keys()
        keyboard.add_hotkey(self.start_button, self.start_fishing)
        keyboard.wait(self.end_button)

    def setting_keys(self):
        print('请按下开始钓鱼的按键')
        self.start_button = self.get_keyboard_input()
        print('记录到的按键为：', self.start_button)
        print('请按下食物的按键')
        self.eat_button = self.get_keyboard_input()
        print('记录到的按键为：', self.eat_button)
        print('请按下鱼竿的按键')
        self.fish_button = self.get_keyboard_input()
        print('记录到的按键为：', self.fish_button)

    def get_keyboard_input(self):
        hotkey = keyboard.read_key()
        time.sleep(0.3)
        return hotkey

    def start_fishing(self):
        print('开始钓鱼!')
        i = 1
        while True:
            self.fish()
            while not self.fish_exists():
                time.sleep(0.5)
            self.catch_fish()
            if i % 50[12] == 0:
                self.eat()
            i += 1

    def right_click(self, x, y, hold_time=0.1):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        time.sleep(hold_time)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

    def eat(self):
        keyboard.press(self.eat_button)
        self.right_click(self.mid_x, self.mid_y, 3)

    def fish(self):
        keyboard.press(self.fish_button)
        self.right_click(self.mid_x, self.mid_y, 0.1)

    def catch_fish(self):
        self.right_click(self.mid_x, self.mid_y, 0.1)
        time.sleep(3.5)

    def get_screenshot(self):
        window_size = win32gui.GetWindowRect(self.hwnd)
        screenshot = ImageGrab.grab(window_size)
        screenshot_np = np.array(screenshot)
        return cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

    def match_template(self, threshold=0.85):
        template = self.fishTemp
        screenshot = self.get_screenshot()
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        # cv2.imshow('screenshot', screenshot)
        # cv2.waitKey(0)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > threshold:
            print('找到鱼了')
            return True
        print('没鱼', max_val)
        return False

    def fish_exists(self):
        return self.match_template()



if __name__ == '__main__':
    fisher = Fisher()
    fisher.start_task()
