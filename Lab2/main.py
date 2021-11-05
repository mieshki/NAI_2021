"""
Moon Lander using fuzzy logic.

Authors:
Reiter, Aleksander <https://github.com/block439>
Dziadowiec, Mieszko <https://github.com/mieshki>

How to run:
(optional): `pip install -r requirements.txt`
`python main.py`
"""
import multiprocessing
import time
import pyautogui
import pathlib

from enum import Enum
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from skfuzzy_helper import *

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
    """
    Function creates process responsible for steering our game. It uses pyautogui to scrap and walk through page.
    """
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
        :param step: Integer from 1 to 3. It will correct the angle of rocket by pressing right key provided times.
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
        """
        This function translates input values to specified range
        :param value: input value which should be translated
        :param leftMin: input min value
        :param leftMax: input max value
        :param rightMin: output min value
        :param rightMax: output min value
        :return: Value from range leftMin to leftMax according to input value
        """
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
    _horizontal_throttle = 0
    _direction = 0

    while True:
        with fuzzy_output_throttle_out.get_lock():
            _throttle_time_in_seconds = translate(fuzzy_output_throttle_out.value, 1, 101, 0, 3)
            throttle_copy = fuzzy_output_throttle_out.value
            _horizontal_throttle = translate(fuzzy_output_slow.value, 1, 101, 0, 3)
            _direction = fuzzy_output_direction_out.value

        with altitude.get_lock():
            if abs(horizontal_velocity.value) <= 20 and angle.value == 0:
                _horizontal_throttle = 0
                pass
            else:
                changeDirection(_direction)

        if _horizontal_throttle <= 0:
            pass
        else:
            throttle(_horizontal_throttle)

        # print(output)
        # output <0, 100>
        if throttle_copy < 5:
            pass
        else:
            print(f'{PROCESS_HEADER}Throttle for={round(_throttle_time_in_seconds, 3)} seconds')
            throttle(_throttle_time_in_seconds)

        with altitude.get_lock():
            if altitude.value <= 5:
                print(f'{PROCESS_HEADER}(maybe) landed! Waiting 4 seconds to next game...')
                with start_fuzzy_logic_computing.get_lock():
                    start_fuzzy_logic_computing.value = 0
                time.sleep(4)
                with start_fuzzy_logic_computing.get_lock():
                    start_fuzzy_logic_computing.value = 1

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
    """
    Function creates process responsible for scraping our page.
    """
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

    try:
        driver = Chrome()
    except:
        driver = Firefox()

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
    """
    Function creates process responsible for all calculations. This is the brain.
    """
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
    drag_antecedent['LEFT_SMALL'] = trimf(drag_antecedent.universe, [-66, -25, 0])
    drag_antecedent['ZERO'] = trimf(drag_antecedent.universe, [-25, 0, 25])
    drag_antecedent['RIGHT_SMALL'] = trimf(drag_antecedent.universe, [0, 25, 66])
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
    throttle_control_system_rules = \
    [
        ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['ZERO']),
        ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['DOWN_LARGE']),
        ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['ZERO'], throttle_consequent['DOWN_LARGE']),
        ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_LARGE']),
        ctrl.Rule(altitude_antecedent['LARGE'] & velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_LARGE']),

        ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['ZERO']),
        ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['ZERO'], throttle_consequent['DOWN_SMALL']),
        ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_LARGE']),
        ctrl.Rule(altitude_antecedent['MEDIUM'] & velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_LARGE']),

        ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['DOWN_SMALL']),
        ctrl.Rule(altitude_antecedent['SMALL'] | velocity_antecedent['ZERO'], throttle_consequent['DOWN_SMALL']),
        ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['ZERO'], throttle_consequent['DOWN_LARGE']),
        ctrl.Rule(altitude_antecedent['SMALL'] | velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_SMALL']),
        ctrl.Rule(altitude_antecedent['SMALL'] & velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_LARGE']),

        ctrl.Rule(altitude_antecedent['NEAR_ZERO'] & velocity_antecedent['DOWN_LARGE'], throttle_consequent['UP_LARGE']),
        ctrl.Rule(altitude_antecedent['NEAR_ZERO'] & velocity_antecedent['DOWN_SMALL'], throttle_consequent['UP_LARGE']),
        ctrl.Rule(altitude_antecedent['NEAR_ZERO'] | velocity_antecedent['ZERO'], throttle_consequent['DOWN_SMALL']),
        ctrl.Rule(altitude_antecedent['NEAR_ZERO'] | velocity_antecedent['UP_SMALL'], throttle_consequent['DOWN_SMALL']),
        ctrl.Rule(altitude_antecedent['NEAR_ZERO'] | velocity_antecedent['UP_LARGE'], throttle_consequent['DOWN_SMALL'])
    ]



    # endregion

    """
    LEFT_LARGE [-100, -100, -66, -33])
    LEFT_SMALL [-66, -33, 0])
    ZERO [-33, 0, 33])
    RIGHT_SMALL [0, 33, 66])
    RIGHT_LARGE [33, 66, 100, 100])
    """
    # region DIRECTION rules

    angle_control_system_rules = \
    [
        ctrl.Rule(drag_antecedent['LEFT_LARGE'] & angle_antecedent['RIGHT'], direction_consequent['LEFT']),
        ctrl.Rule(drag_antecedent['LEFT_LARGE'] & angle_antecedent['LEFT'], direction_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['LEFT_LARGE'] & angle_antecedent['CENTER'], direction_consequent['LEFT']),

        ctrl.Rule(drag_antecedent['LEFT_SMALL'] & angle_antecedent['RIGHT'], direction_consequent['LEFT']),
        ctrl.Rule(drag_antecedent['LEFT_SMALL'] & angle_antecedent['LEFT'], direction_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['LEFT_SMALL'] & angle_antecedent['CENTER'], direction_consequent['LEFT']),

        ctrl.Rule(drag_antecedent['ZERO'] & angle_antecedent['RIGHT'], direction_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['ZERO'] & angle_antecedent['LEFT'], direction_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['ZERO'] & angle_antecedent['CENTER'], direction_consequent['ZERO']),

        ctrl.Rule(drag_antecedent['RIGHT_SMALL'] & angle_antecedent['RIGHT'], direction_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['RIGHT_SMALL'] & angle_antecedent['LEFT'], direction_consequent['RIGHT']),
        ctrl.Rule(drag_antecedent['RIGHT_SMALL'] & angle_antecedent['CENTER'], direction_consequent['LEFT']),

        ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & angle_antecedent['RIGHT'], direction_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & angle_antecedent['LEFT'], direction_consequent['RIGHT']),
        ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & angle_antecedent['CENTER'], direction_consequent['RIGHT']),

        ctrl.Rule(drag_antecedent['LEFT_LARGE'] & altitude_antecedent['NEAR_ZERO'], throttle_consequent['UP_LARGE']),
        ctrl.Rule(drag_antecedent['LEFT_LARGE'] & altitude_antecedent['SMALL'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['LEFT_LARGE'] & altitude_antecedent['MEDIUM'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['LEFT_LARGE'] & altitude_antecedent['LARGE'], throttle_consequent['UP_SMALL']),

        ctrl.Rule(drag_antecedent['LEFT_SMALL'] & altitude_antecedent['NEAR_ZERO'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['LEFT_SMALL'] & altitude_antecedent['SMALL'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['LEFT_SMALL'] & altitude_antecedent['MEDIUM'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['LEFT_SMALL'] & altitude_antecedent['LARGE'], throttle_consequent['UP_SMALL']),

        ctrl.Rule(drag_antecedent['ZERO'] & altitude_antecedent['NEAR_ZERO'], throttle_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['ZERO'] & altitude_antecedent['SMALL'], throttle_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['ZERO'] & altitude_antecedent['MEDIUM'], throttle_consequent['ZERO']),
        ctrl.Rule(drag_antecedent['ZERO'] & altitude_antecedent['LARGE'], throttle_consequent['ZERO']),

        ctrl.Rule(drag_antecedent['RIGHT_SMALL'] & altitude_antecedent['NEAR_ZERO'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['RIGHT_SMALL'] & altitude_antecedent['SMALL'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['RIGHT_SMALL'] & altitude_antecedent['MEDIUM'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['RIGHT_SMALL'] & altitude_antecedent['LARGE'], throttle_consequent['UP_SMALL']),

        ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & altitude_antecedent['NEAR_ZERO'], throttle_consequent['UP_LARGE']),
        ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & altitude_antecedent['SMALL'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & altitude_antecedent['MEDIUM'], throttle_consequent['UP_SMALL']),
        ctrl.Rule(drag_antecedent['RIGHT_LARGE'] & altitude_antecedent['LARGE'], throttle_consequent['UP_SMALL'])

    ]


    # endregion

    # region CONTROL_SYSTEMS
    throttling_ctrl = ctrl.ControlSystem(throttle_control_system_rules)
    angle_ctrl = ctrl.ControlSystem(angle_control_system_rules)

    throttling = ctrl.ControlSystemSimulation(throttling_ctrl)
    angling = ctrl.ControlSystemSimulation(angle_ctrl)
    # endregion

    def gather_data():
        """
        This function adds inputs to our fuzzy set.
        :return: copy of angle value and drag value
        """
        with altitude.get_lock():
            throttling.input['altitude'] = altitude.value
            throttling.input['velocity'] = vertical_velocity.value
            angling.input['altitude'] = altitude.value
            angling.input['angle'] = angle.value
            angle_copy = angle.value
            angling.input['drag'] = horizontal_velocity.value
            drag_copy = horizontal_velocity.value

            return angle_copy, drag_copy

    def update_fuzzy_outputs(_throttle_out, _direction_out, _horizontal_throttling):
        """
        This function updates three main steering values.
        :param _throttle_out: Throttle time
        :param _direction_out: Change direction time
        :param _horizontal_throttling: Horizontal corrections
        :return:
        """
        with fuzzy_output_throttle_out.get_lock():
            fuzzy_output_throttle_out.value = float(_throttle_out)
            fuzzy_output_direction_out.value = float(_direction_out)
            fuzzy_output_slow.value = float(_horizontal_throttling)

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

        try:
            angle_copy, drag_copy = gather_data()

            throttling.compute()
            angling.compute()
            direction_out = angling.output['direction']
            horizontal_throttling = angling.output['throttle']

            throttle_out = throttling.output['throttle']
            update_fuzzy_outputs(throttle_out, direction_out, horizontal_throttling)
            if time.time() - delta_time >= 1:
                print(f'{PROCESS_HEADER}Updating value from fuzzy logic, throttle={round(float(throttle_out), 2)}, direction={round(float(direction_out), 2)}, horizontal_throttling={round(float(horizontal_throttling), 2)}')
                delta_time = time.time()
        except Exception as e:
            print(f'Exception while computing fuzzy logic, reason: {str(e)}')

# endregion


# region PROCESS_INITIALIZER
class Process(Enum):
    fuzzy_logic = 1,
    data_collector = 2,
    py_auto_gui = 3


def init_new_process(process_type):
    """
    This function initializes all processes
    :param process_type: Process type stored in enum
    """
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
    """
    This function initializes all global variables. This is required to access global variables in multiprocessing
    :param _counter:
    :param _altitude: altitude value of our ship
    :param _horizontal_velocity: horizontal velocity of our ship
    :param _vertical_velocity: vertical velocity of our ship
    :param _angle: ship angle
    :param _fuzzy_output_throttle_out: value in seconds how long we need to throttle
    :param _fuzzy_output_direction_out: value in seconds how long and in which direction should we rotate ship
    :param _fuzzy_output_slow: value in seconds used to slow down horizontal speed
    :param _start_fuzzy_logic_computing:
    :return:
    """
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
