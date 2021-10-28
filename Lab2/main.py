"""
Download firefox driver form https://github.com/mozilla/geckodriver/releases
Full Install instruction on https://www.selenium.dev/documentation/getting_started/installing_browser_drivers/
"""
import math
import time
import pathlib
import pyautogui
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from fuzzy_logic import *

def get_info(driver):
    """getInfo() gives information about our ship position in space
    :param driver: current session with loaded webpage
    :return: Four variables describing speed, angle and Altitude of our ship
    """
    altitude = driver.find_elements(By.ID, 'Altitude').pop().text
    horizSpeed = driver.find_elements(By.ID, 'HorizSpeed').pop().text
    vertSpeed = driver.find_elements(By.ID, 'VertSpeed').pop().text
    angle = driver.find_elements(By.ID, 'Angle').pop().text
    return int(altitude), int(horizSpeed), int(vertSpeed), int(angle)

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

    driver = Chrome()
    web_path = f'{pathlib.Path().resolve()}\moonlander-simple-v1\index.html'
    print(web_path)
    driver.get(web_path)

    game_launch()
    time.sleep(2)
    play = True
    while(play):
        altitude, horizontal_speed, velocity, angle = get_info(driver)

        altitude_sqrt = math.sqrt(altitude)

        """
        Some examples:
            - 0.10 and 5 - crash
            - 0.13 and 5 - 919 very hard landing
            - 0.15 and 5 - 906
            - 0.20 and 5 - 879
        """
        # the lower the more aggressive and fuel saving
        AGGRESSIVENESS_LEVEL = 0.14
        CUTOFF_THRESHOLD = 5

        print(f'altitude_sqrt={altitude_sqrt}, velocity={velocity}')
        if altitude < CUTOFF_THRESHOLD:
            print('Landed')
            play = False
        elif altitude_sqrt < int(velocity * AGGRESSIVENESS_LEVEL) and velocity > CUTOFF_THRESHOLD:
            print('throttle for 1s')
            throttle(1)
        else:
            pass
        ###output = fuzzy_benchmark(int(altitude), int(vertSpeed)) / 100
        ###throttle(output)
