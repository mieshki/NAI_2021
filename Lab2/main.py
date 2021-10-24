"""
Dowload firefox driver form https://github.com/mozilla/geckodriver/releases
Full Install instruction on https://www.selenium.dev/documentation/getting_started/installing_browser_drivers/
"""

import os
import time

import pyautogui
#import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

def getInfo(driver):
    """getInfo() gives information about our ship position in space
    :param driver: current session with loaded webpage
    :return: Four variables describing speed, angle and Altitude of our ship
    """
    altitude = driver.find_elements(By.ID, 'Altitude').pop().text
    horizSpeed = driver.find_elements(By.ID, 'HorizSpeed').pop().text
    vertSpeed = driver.find_elements(By.ID, 'VertSpeed').pop().text
    angle = driver.find_elements(By.ID, 'Angle').pop().text
    return altitude, horizSpeed, vertSpeed, angle

def game_launch():
    """
        game_launch() It locates main point of the window and click mouse button to start game.
        To achieve that used image detection from pyautogui lib
    """
    time.sleep(2)
    gameLocation = pyautogui.locateOnScreen('starter.png', confidence=0.5)
    startPoint = pyautogui.center(gameLocation)
    x,y = startPoint
    pyautogui.moveTo(x, y)
    pyautogui.click()
    pyautogui.click()

def throttle(power):
    """ throttle(power) This function handles usage of rockets.
    :param power: Integer from 1 to 3. It will turn on engine for provided amount of seconds.
    :return:
    """
    pyautogui.keyDown("up")
    time.sleep(power)
    pyautogui.keyUp("up")

def changeDirection(step, sign):
    """ changeDirection(power) This function handles rocket angle.
    :param level: Integer from 1 to 3. It will correct the angle of rocket by pressing right key provided times.
    :return:
    """
    if sign:
        direction = "left"
    else:
        direction = "right"
    print(direction)
    pyautogui.keyDown(direction)
    time.sleep(step)
    pyautogui.keyUp(direction)


if __name__ == '__main__':

    driver = Firefox()
    web_path = "file:///D:/Python/GameAI/NAI_2021/Lab2/moonlander-simple-v1/index.html"
    driver.get(web_path)

    game_launch()

    #for _ in range(5):
    while(True):
        altitude ,horizSpeed ,vertSpeed ,angle = getInfo(driver)
        sign = abs(int(horizSpeed)) == int(horizSpeed)
        horizSpeed = abs(int(horizSpeed))
        """if 15 > int(horizSpeed):
            changeDirection(0.3, sign)
            throttle(1)
        elif 30 > int(horizSpeed):
            changeDirection(0.3, sign)
            throttle(2)
        elif int(horizSpeed) > 40:
            throttle(3)
        time.sleep(1)"""
        if 10 > int(vertSpeed):
            time.sleep(4)
        elif 20 > int(vertSpeed):
            throttle(2)
        elif int(vertSpeed) > 40:
            throttle(3)
"""print("alt" + altitude)
        print("horiz" + horizSpeed)
        print("vert" + vertSpeed)
        print("angle" + angle)"""


    #driver.quit()

"""    with pyautogui.hold('shift'):  # Press the Shift key down and hold it.
        pyautogui.press(['left', 'left', 'left', 'left'])  # Press the left arrow key 4 times.
    pyautogui.press("up")
    print(f'w= {X} H={Y}')
"""