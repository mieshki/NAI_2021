"""
Download firefox driver form https://github.com/mozilla/geckodriver/releases
Full Install instruction on https://www.selenium.dev/documentation/getting_started/installing_browser_drivers/
"""
import multiprocessing
import os
import time
import pyautogui
import pathlib

from enum import Enum
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from fuzzy_logic import *

# region GLOBALS
counter = None
altitude = None
horizontal_velocity = None
vertical_velocity = None
angle = None

fuzzy_output_throttle_out = None
fuzzy_output_direction_out = None
fuzzy_output_slow = None

start_fuzzy_logic_computing = None
# endregion

# region PY_AUTO_GUI PROCESS
def py_auto_gui_process():
    PROCESS_HEADER = '[PY_AUTO_GUI_PROCESS] '

    # region GLOBALS
    global counter

    global altitude
    global horizontal_velocity
    global vertical_velocity
    global angle

    global fuzzy_output_throttle_out
    global fuzzy_output_direction_out
    global fuzzy_output_slow

    global start_fuzzy_logic_computing
    # endregion

    # region HELPERS
    def game_launch():
        """
            game_launch() It locates main point of the window and click mouse button to start game.
            To achieve that used image detection from pyautogui lib
        """
        while pyautogui.locateOnScreen('starter.png', confidence=0.5) is None:
            print(f'{PROCESS_HEADER}Waiting for starting screen...')
            time.sleep(2)

        print(f'{PROCESS_HEADER}Starting game!')
        game_location = pyautogui.locateOnScreen('starter.png', confidence=0.5)

        with start_fuzzy_logic_computing.get_lock():
            start_fuzzy_logic_computing.value = 1

        startPoint = pyautogui.center(game_location)
        x, y = startPoint
        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.click()

    def changeDirection(step):
        """ changeDirection(power) This function handles rocket angle.
        :param level: Integer from 1 to 3. It will correct the angle of rocket by pressing right key provided times.
        :return:
        """
        sign = abs(step) == step
        print(sign)
        if sign:
            direction = "left"
        else:
            direction = "right"
        print(direction)
        pyautogui.keyDown(direction)
        time.sleep(abs(step) / 100)
        pyautogui.keyUp(direction)

    def translate(value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    def throttle(power):
        """ throttle(power) This function handles usage of rockets.
        :param power: Integer from 1 to 3. It will turn on engine for provided amount of seconds.
        :return:
        """
        pyautogui.keyDown("up")
        time.sleep(power)
        pyautogui.keyUp("up")
    # endregion

    print(f'Launching game')
    game_launch()

    _throttle = 0
    _slow = 0
    _direction = 0

    while True:
        with fuzzy_output_throttle_out.get_lock():
            _throttle_time_in_seconds = translate(fuzzy_output_throttle_out.value, 1, 101, 0, 3)
            throttle_copy = fuzzy_output_throttle_out.value
            _slow = translate(fuzzy_output_slow.value, 1, 101, 0, 3)
            _direction = fuzzy_output_direction_out.value
        # 1 - 10ms
        if abs(_direction) < 1:
            pass
        else:
            changeDirection(_direction)
            if _slow <= 0:
                pass
            else:
                throttle(_slow)
        # print(output)
        # output <0, 100>
        if throttle_copy < 5:
            pass
        else:
            print(f'{PROCESS_HEADER}Throttle for={_throttle_time_in_seconds}')
            throttle(_throttle_time_in_seconds)
# endregion


# region DATA_COLLECTOR_PROCESS
def get_info(driver):
    """getInfo() gives information about our ship position in space
    :param driver: current session with loaded webpage
    :return: Four variables describing speed, angle and Altitude of our ship
    """
    _altitude = driver.find_elements(By.ID, 'Altitude').pop().text
    _horizSpeed = driver.find_elements(By.ID, 'HorizSpeed').pop().text
    _vertSpeed = driver.find_elements(By.ID, 'VertSpeed').pop().text
    _angle = driver.find_elements(By.ID, 'Angle').pop().text
    return int(_altitude), int(_horizSpeed), int(_vertSpeed), int(_angle)


def data_collector_process():
    PROCESS_HEADER = '[DATA_COLLECTOR_PROCESS] '

    # region GLOBALS
    global counter

    global altitude
    global horizontal_velocity
    global vertical_velocity
    global angle

    global fuzzy_output_throttle_out
    global fuzzy_output_direction_out
    global fuzzy_output_slow

    global start_fuzzy_logic_computing
    # endregion

    driver = Chrome()
    # driver = Firefox()

    web_path = f'{pathlib.Path().resolve()}\moonlander-simple-v1\index.html'

    print(f'Attempting to open: {web_path}')

    driver.get(web_path)

    delta_time = time.time()
    while True:
        with altitude.get_lock():
            _altitude, _horizontal_velocity, _vertical_velocity, _angle = get_info(driver)
            altitude.value = _altitude
            horizontal_velocity.value = _horizontal_velocity
            vertical_velocity.value = _vertical_velocity
            angle.value = _angle
            if time.time() - delta_time >= 1:
                print(f'{PROCESS_HEADER}Data received, altitude={altitude.value}, hV={horizontal_velocity.value}, vV={vertical_velocity.value}, angle={angle.value} releasing lock')
                delta_time = time.time()
# endregion


# region FUZZY_LOGIC_PROCESS

def fuzzy_logic_process():
    PROCESS_HEADER = '[FUZZY_LOGIC_PROCESS] '

    # region GLOBALS
    global counter

    global altitude
    global horizontal_velocity
    global vertical_velocity
    global angle

    global fuzzy_output_throttle_out
    global fuzzy_output_direction_out
    global fuzzy_output_slow

    global start_fuzzy_logic_computing
    # endregion

    angle_antecedent = ctrl.Antecedent(np.arange(-90, 90, 1), 'angle')
    drag_antecedent = ctrl.Antecedent(np.arange(-100, 100, 1), 'drag')
    altitude_antecedent = ctrl.Antecedent(np.arange(0, 400, 1), 'altitude')
    velocity_antecedent = ctrl.Antecedent(np.arange(-100, 100, 1), 'velocity')
    throttle_consequent = ctrl.Consequent(np.arange(-100, 100, 1), 'throttle')
    direction_consequent = ctrl.Consequent(np.arange(-3, 3, 0.2), 'direction')

    # region MEMBERSHIP FUNCTIONS

    """ Altitude membership functions """
    altitude_antecedent['NEAR_ZERO'] = trimf(altitude_antecedent.universe, [0, 0, 200])
    altitude_antecedent['SMALL'] = trimf(altitude_antecedent.universe, [-66, 116, 300])
    altitude_antecedent['MEDIUM'] = trimf(altitude_antecedent.universe, [116, 316, 466])
    altitude_antecedent['LARGE'] = trimf(altitude_antecedent.universe, [200, 400, 400])

    """ Velocity membership functions """
    velocity_antecedent['UP_LARGE'] = trapmf(velocity_antecedent.universe, [-100, -100, -66, -33])
    velocity_antecedent['UP_SMALL'] = trimf(velocity_antecedent.universe, [-66, -33, 0])
    velocity_antecedent['ZERO'] = trimf(velocity_antecedent.universe, [-33, 0, 33])
    velocity_antecedent['DOWN_SMALL'] = trimf(velocity_antecedent.universe, [0, 33, 66])
    velocity_antecedent['DOWN_LARGE'] = trapmf(velocity_antecedent.universe, [33, 66, 100, 100])

    """ Drag membership functions """
    drag_antecedent['LEFT_LARGE'] = trapmf(drag_antecedent.universe, [-100, -100, -66, -33])
    drag_antecedent['LEFT_SMALL'] = trimf(drag_antecedent.universe, [-66, -33, 0])
    drag_antecedent['ZERO'] = trimf(drag_antecedent.universe, [-33, 0, 33])
    drag_antecedent['RIGHT_SMALL'] = trimf(drag_antecedent.universe, [0, 33, 66])
    drag_antecedent['RIGHT_LARGE'] = trapmf(drag_antecedent.universe, [33, 66, 100, 100])

    """ Force membership functions """
    throttle_consequent['DOWN_LARGE'] = trapmf(throttle_consequent.universe, [-100, -100, -66, -33])
    throttle_consequent['DOWN_SMALL'] = trimf(throttle_consequent.universe, [-66, -33, 0])
    throttle_consequent['ZERO'] = trimf(throttle_consequent.universe, [-33, 0, 33])
    throttle_consequent['UP_SMALL'] = trimf(throttle_consequent.universe, [0, 33, 66])
    throttle_consequent['UP_LARGE'] = trapmf(throttle_consequent.universe, [33, 66, 100, 100])

    """ Angle membership functions """
    angle_antecedent['RIGHT'] = trimf(angle_antecedent.universe, [-90, -90, 0])
    angle_antecedent['CENTER'] = trimf(angle_antecedent.universe, [-20, 0, 20])
    angle_antecedent['LEFT'] = trimf(angle_antecedent.universe, [0, 90, 90])

    """ Direction membership functions """
    direction_consequent['LEFT'] = trimf(direction_consequent.universe, [-3, -3, 0])
    direction_consequent['CENTER'] = trimf(direction_consequent.universe, [-0.2, 0, 0.2])
    direction_consequent['RIGHT'] = trimf(direction_consequent.universe, [0, 3, 3])
    direction_consequent['ZERO'] = trimf(direction_consequent.universe, [0, 0, 0])

    #endregion

    # region OPTIONAL_DEBUG_VIEWS
    # direction.view()
    # altitude.view()
    # velocity.view()
    # throttle.view()
    # angle.view()
    # endregion

    # region THROTTLE RULES
    rule1 = ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['ZERO'])
    rule2 = ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['DOWN_LARGE'])
    rule3 = ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['ZERO'], throttle_consequent['DOWN_LARGE'])
    rule4 = ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_LARGE'])
    rule5 = ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_LARGE'])

    rule6 = ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['UP_SMALL'])
    rule7 = ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['ZERO'])
    rule8 = ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['ZERO'], throttle_consequent['DOWN_SMALL'])
    rule9 = ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_LARGE'])
    rule10 = ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_LARGE'])

    rule11 = ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['UP_SMALL'])
    rule12 = ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['DOWN_SMALL'])
    rule13 = ctrl.Rule(altitude_antecedent['SMALL'] | velocity_antecedent['ZERO'], throttle_consequent['DOWN_SMALL'])
    rule14 = ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['ZERO'], throttle_consequent['DOWN_LARGE'])
    rule15 = ctrl.Rule(altitude_antecedent['SMALL'] | velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_SMALL'])
    rule16 = ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_LARGE'])

    rule17 = ctrl.Rule(altitude_antecedent['NEAR_ZERO'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['UP_LARGE'])
    rule18 = ctrl.Rule(altitude_antecedent['NEAR_ZERO'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['UP_LARGE'])
    rule19 = ctrl.Rule(altitude_antecedent['NEAR_ZERO'] | velocity_antecedent['ZERO'], throttle_consequent['DOWN_SMALL'])
    rule20 = ctrl.Rule(altitude_antecedent['NEAR_ZERO'] | velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_SMALL'])
    rule21 = ctrl.Rule(altitude_antecedent['NEAR_ZERO'] | velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_SMALL'])
    # endregion

    # region DIRECTION rules
    rule22 = ctrl.Rule((angle_antecedent['CENTER'] & ~(angle_antecedent['LEFT'] | angle_antecedent['RIGHT'])) & (altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), direction_consequent['CENTER'])
    rule23 = ctrl.Rule(angle_antecedent['RIGHT'] & (altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), direction_consequent['LEFT'])
    rule24 = ctrl.Rule(angle_antecedent['LEFT'] & (altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), direction_consequent['RIGHT'])
    rule25 = ctrl.Rule(~(altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), direction_consequent['ZERO'])
    rule26 = ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & (altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), direction_consequent['RIGHT'])
    rule27 = ctrl.Rule(drag_antecedent['LEFT_LARGE'] & (altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), direction_consequent['LEFT'])
    rule28 = ctrl.Rule((drag_antecedent['LEFT_LARGE'] | drag_antecedent['RIGHT_LARGE']) & (altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), throttle_consequent['UP_LARGE'])
    rule29 = ctrl.Rule((drag_antecedent['LEFT_SMALL'] | drag_antecedent['RIGHT_SMALL']) & (altitude_antecedent['LARGE'] | altitude_antecedent['MEDIUM']), throttle_consequent['UP_SMALL'])
    rule30 = ctrl.Rule((drag_antecedent['LEFT_SMALL'] | drag_antecedent['LEFT_LARGE']) & angle_antecedent['RIGHT'], throttle_consequent['DOWN_LARGE'])
    rule31 = ctrl.Rule((drag_antecedent['RIGHT_SMALL'] | drag_antecedent['RIGHT_LARGE']) & angle_antecedent['LEFT'], throttle_consequent['DOWN_LARGE'])
    rule32 = ctrl.Rule((drag_antecedent['LEFT_SMALL'] | drag_antecedent['RIGHT_SMALL']), direction_consequent['ZERO'])
    # endregion

    # region CONTROL_SYSTEMS
    throttling_ctrl = ctrl.ControlSystem(
        [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15,
         rule16, rule17, rule18, rule19, rule20, rule21])

    angle_ctrl = ctrl.ControlSystem(
        [rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29, rule30, rule31, rule32])

    throttling = ctrl.ControlSystemSimulation(throttling_ctrl)
    angling = ctrl.ControlSystemSimulation(angle_ctrl)
    # endregion

    def gather_data():
        with altitude.get_lock():
            throttling.input['altitude'] = altitude.value
            throttling.input['velocity'] = vertical_velocity.value
            angling.input['altitude'] = altitude.value
            angling.input['angle'] = angle.value
            angle_copy = angle.value
            angling.input['drag'] = horizontal_velocity.value
            drag_copy = horizontal_velocity.value

            return angle_copy, drag_copy

    def update_fuzzy_outputs(_throttle_out, _direction_out, _slow):
        with fuzzy_output_throttle_out.get_lock():
            fuzzy_output_throttle_out.value = float(_throttle_out)
            fuzzy_output_direction_out.value = float(_direction_out)
            fuzzy_output_slow.value = float(_slow)

    delta_time = time.time()

    is_fuzzy_logic_currently_running = False

    while True:
        with start_fuzzy_logic_computing.get_lock():
            if start_fuzzy_logic_computing.value == 0:
                print(f'{PROCESS_HEADER}Not computing fuzzy logic...')
                is_fuzzy_logic_currently_running = False
                time.sleep(2)
                continue
            else:
                if is_fuzzy_logic_currently_running is False:
                    print(f'{PROCESS_HEADER}Starting computing fuzzy logic...')
                    is_fuzzy_logic_currently_running = True

        angle_copy, drag_copy = gather_data()

        # print(f'altitude={_altitude}, speed={speed}')

        throttling.compute()

        if angle_copy == 0 and drag_copy <= 30:
            direction_out = 0
            slow = 0
        else:
            angling.compute()
            direction_out = angling.output['direction']
            slow = angling.output['throttle']

        throttle_out = throttling.output['throttle']
        update_fuzzy_outputs(throttle_out, direction_out, slow)
        if time.time() - delta_time >= 1:
            print(f'{PROCESS_HEADER}Updating value from fuzzy logic, throttle={float(throttle_out)}, direction={float(direction_out)}, slow={float(slow)}')
            delta_time = time.time()

# endregion


# region PROCESS_INITIALIZER
class Process(Enum):
    fuzzy_logic = 1,
    data_collector = 2,
    py_auto_gui = 3


def init_new_process(process_type):
    print(f'New process: {process_type}')

    if process_type == Process.fuzzy_logic:
        try:
            fuzzy_logic_process()
        except Exception as e:
            print(f'Fuzzy logic process died, reason: {str(e)}')
    elif process_type == Process.data_collector:
        try:
            data_collector_process()
        except Exception as e:
            print(f'Data collector process died, reason: {str(e)}')
    elif process_type == Process.py_auto_gui:
        try:
            py_auto_gui_process()
        except Exception as e:
            print(f'Py auto gui process died, reason: {str(e)}')


def process_variables_initializer(_counter, _altitude, _horizontal_velocity, _vertical_velocity, _angle, _fuzzy_output_throttle_out, _fuzzy_output_direction_out, _fuzzy_output_slow, _start_fuzzy_logic_computing):
    # region GLOBALS
    global counter

    global altitude
    global horizontal_velocity
    global vertical_velocity
    global angle

    global fuzzy_output_throttle_out
    global fuzzy_output_direction_out
    global fuzzy_output_slow

    global start_fuzzy_logic_computing
    # endregion

    counter = _counter
    altitude = _altitude
    horizontal_velocity = _horizontal_velocity
    vertical_velocity = _vertical_velocity
    angle = _angle

    fuzzy_output_throttle_out = _fuzzy_output_throttle_out
    fuzzy_output_direction_out = _fuzzy_output_direction_out
    fuzzy_output_slow = _fuzzy_output_slow

    start_fuzzy_logic_computing = _start_fuzzy_logic_computing

# endregion


if __name__ == '__main__':
    counter = multiprocessing.Value('i', 0)

    altitude = multiprocessing.Value('i', 0)
    horizontal_velocity = multiprocessing.Value('i', 0)
    vertical_velocity = multiprocessing.Value('i', 0)
    angle = multiprocessing.Value('i', 5)

    fuzzy_output_throttle_out = multiprocessing.Value('f', 0)
    fuzzy_output_direction_out = multiprocessing.Value('f', 0)
    fuzzy_output_slow = multiprocessing.Value('f', 0)

    start_fuzzy_logic_computing = multiprocessing.Value('i', 0)

    pool = multiprocessing.Pool(processes=3,
                                initializer=process_variables_initializer,
                                initargs=(counter, altitude, horizontal_velocity, vertical_velocity, angle,
                                          fuzzy_output_throttle_out, fuzzy_output_direction_out, fuzzy_output_slow, start_fuzzy_logic_computing))
    pool.map(init_new_process, [Process.fuzzy_logic, Process.data_collector, Process.py_auto_gui])

"""
        altitude_sqrt = math.sqrt(altitude)

        # Some examples:
        #    - 0.10 and 5 - crash
        #    - 0.13 and 5 - 919 very hard landing
        #    - 0.15 and 5 - 906
        #    - 0.20 and 5 - 879
        # the lower the more aggressive and fuel saving
        AGGRESSIVENESS_LEVEL = 0.14
        CUTOFF_THRESHOLD = 5

        print(f'altitude_sqrt={altitude_sqrt}, velocity={vertical_velocity}')
        if altitude < CUTOFF_THRESHOLD:
            print('Landed')
            play = False
        elif altitude_sqrt < int(vertical_velocity * AGGRESSIVENESS_LEVEL) and vertical_velocity > CUTOFF_THRESHOLD:
            print('throttle for 1s')
            throttle(1)
        else:
            pass
"""
