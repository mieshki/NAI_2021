"""
If you're new to the world of fuzzy control systems, you might want
to check out the `Fuzzy Control Primer
<../userguide/fuzzy_control_primer.html>`_
before reading through this worked example.

The Tipping Problem
-------------------

Let's create a fuzzy control system which models how you might choose to tip
at a restaurant.  When tipping, you consider the service and food quality,
rated between 0 and 10.  You use this to leave a tip of between 0 and 25%.

We would formulate this problem as:

* Antecednets (Inputs)
   - `service`
      * Universe (ie, crisp value range): How good was the service of the wait
        staff, on a scale of 0 to 10?
      * Fuzzy set (ie, fuzzy value range): poor, acceptable, amazing
   - `food quality`
      * Universe: How tasty was the food, on a scale of 0 to 10?
      * Fuzzy set: bad, decent, great
* Consequents (Outputs)
   - `tip`
      * Universe: How much should we tip, on a scale of 0% to 25%
      * Fuzzy set: low, medium, high
* Rules
   - IF the *service* was good  *or* the *food quality* was good,
     THEN the tip will be high.
   - IF the *service* was average, THEN the tip will be medium.
   - IF the *service* was poor *and* the *food quality* was poor
     THEN the tip will be low.
* Usage
   - If I tell this controller that I rated:
      * the service as 9.8, and
      * the quality as 6.5,
   - it would recommend I leave:
      * a 20.2% tip.


Creating the Tipping Controller Using the skfuzzy control API
-------------------------------------------------------------

We can use the `skfuzzy` control system API to model this.  First, let's
define fuzzy variables
"""
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from skfuzzy_helper import *


def fuzzy_benchmark(_altitude, speed, _angle, _drag):
    angle = ctrl.Antecedent(np.arange(-90, 90, 1), 'angle')
    drag = ctrl.Antecedent(np.arange(-100, 100, 1), 'drag')
    altitude = ctrl.Antecedent(np.arange(0, 400, 1), 'altitude')
    velocity = ctrl.Antecedent(np.arange(-100, 100, 1), 'velocity')
    throttle = ctrl.Consequent(np.arange(-100, 100, 1), 'throttle')
    direction = ctrl.Consequent(np.arange(-3, 3, 0.2), 'direction')

    # Altitude membership functions
    altitude['NEAR_ZERO'] = trimf(altitude.universe, [0, 0, 200])
    altitude['SMALL'] = trimf(altitude.universe, [-66, 116, 300])
    altitude['MEDIUM'] = trimf(altitude.universe, [116, 316, 466])
    altitude['LARGE'] = trimf(altitude.universe, [200, 400, 400])

    # Velocity membership functions
    velocity['UP_LARGE'] = trapmf(velocity.universe, [-100, -100, -66, -33])
    velocity['UP_SMALL'] = trimf(velocity.universe, [-66, -33, 0])
    velocity['ZERO'] = trimf(velocity.universe, [-33, 0, 33])
    velocity['DOWN_SMALL'] = trimf(velocity.universe, [0, 33, 66])
    velocity['DOWN_LARGE'] = trapmf(velocity.universe, [33, 66, 100, 100])

    # Drag membership functions
    drag['LEFT_LARGE'] = trapmf(drag.universe, [-100, -100, -66, -33])
    drag['LEFT_SMALL'] = trimf(drag.universe, [-66, -33, 0])
    drag['ZERO'] = trimf(drag.universe, [-33, 0, 33])
    drag['RIGHT_SMALL'] = trimf(drag.universe, [0, 33, 66])
    drag['RIGHT_LARGE'] = trapmf(drag.universe, [33, 66, 100, 100])

    # Force membership functions
    throttle['DOWN_LARGE'] = trapmf(throttle.universe, [-100, -100, -66, -33])
    throttle['DOWN_SMALL'] = trimf(throttle.universe, [-66, -33, 0])
    throttle['ZERO'] = trimf(throttle.universe, [-33, 0, 33])
    throttle['UP_SMALL'] = trimf(throttle.universe, [0, 33, 66])
    throttle['UP_LARGE'] = trapmf(throttle.universe, [33, 66, 100, 100])

    # Angle membership functions
    angle['RIGHT'] = trimf(angle.universe, [-90, -90, 0])
    angle['CENTER'] = trimf(angle.universe, [-20, 0, 20])
    angle['LEFT'] = trimf(angle.universe, [0, 90, 90])

    # Direction membership functions
    direction['LEFT'] = trimf(direction.universe, [-3, -3, 0])
    direction['CENTER'] = trimf(direction.universe, [-0.2, 0, 0.2])
    direction['RIGHT'] = trimf(direction.universe, [0, 3, 3])
    direction['ZERO'] = trimf(direction.universe, [0,0,0])

    #direction.view()
    #altitude.view()
    #velocity.view()
    #throttle.view()
    #angle.view()

    rule1 = ctrl.Rule(altitude['LARGE'] & velocity['DOWN_LARGE'], throttle['ZERO'])
    rule2 = ctrl.Rule(altitude['LARGE'] & velocity['DOWN_SMALL'], throttle['DOWN_LARGE'])
    rule3 = ctrl.Rule(altitude['LARGE'] & velocity['ZERO'], throttle['DOWN_LARGE'])
    rule4 = ctrl.Rule(altitude['LARGE'] & velocity['UP_SMALL'], throttle['DOWN_LARGE'])
    rule5 = ctrl.Rule(altitude['LARGE'] & velocity['UP_LARGE'], throttle['DOWN_LARGE'])

    rule6 = ctrl.Rule(altitude['MEDIUM'] & velocity['DOWN_LARGE'], throttle['UP_SMALL'])
    rule7 = ctrl.Rule(altitude['MEDIUM'] & velocity['DOWN_SMALL'], throttle['ZERO'])
    rule8 = ctrl.Rule(altitude['MEDIUM'] & velocity['ZERO'], throttle['DOWN_SMALL'])
    rule9 = ctrl.Rule(altitude['MEDIUM'] & velocity['UP_SMALL'], throttle['DOWN_LARGE'])
    rule10 = ctrl.Rule(altitude['MEDIUM'] & velocity['UP_LARGE'], throttle['DOWN_LARGE'])

    rule11 = ctrl.Rule(altitude['SMALL'] & velocity['DOWN_LARGE'], throttle['UP_SMALL'])
    rule12 = ctrl.Rule(altitude['SMALL'] & velocity['DOWN_SMALL'], throttle['DOWN_SMALL'])
    rule13 = ctrl.Rule(altitude['SMALL'] | velocity['ZERO'], throttle['DOWN_SMALL'])
    rule14 = ctrl.Rule(altitude['SMALL'] & velocity['ZERO'], throttle['DOWN_LARGE'])
    rule15 = ctrl.Rule(altitude['SMALL'] | velocity['UP_SMALL'], throttle['DOWN_SMALL'])
    rule16 = ctrl.Rule(altitude['SMALL'] & velocity['UP_LARGE'], throttle['DOWN_LARGE'])

    rule17 = ctrl.Rule(altitude['NEAR_ZERO'] & velocity['DOWN_LARGE'], throttle['UP_LARGE'])
    rule18 = ctrl.Rule(altitude['NEAR_ZERO'] & velocity['DOWN_SMALL'], throttle['UP_LARGE'])
    rule19 = ctrl.Rule(altitude['NEAR_ZERO'] | velocity['ZERO'], throttle['DOWN_SMALL'])
    rule20 = ctrl.Rule(altitude['NEAR_ZERO'] | velocity['UP_SMALL'], throttle['DOWN_SMALL'])
    rule21 = ctrl.Rule(altitude['NEAR_ZERO'] | velocity['UP_LARGE'], throttle['DOWN_SMALL'])

    throttling_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21])

    # direction rules
    rule22 = ctrl.Rule((angle['CENTER'] & ~(angle['LEFT'] | angle['RIGHT'])) & (altitude['LARGE'] | altitude['MEDIUM']), direction['CENTER'])
    rule23 = ctrl.Rule(angle['RIGHT'] & (altitude['LARGE'] | altitude['MEDIUM']), direction['LEFT'])
    rule24 = ctrl.Rule(angle['LEFT'] & (altitude['LARGE'] | altitude['MEDIUM']), direction['RIGHT'])
    rule25 = ctrl.Rule(~(altitude['LARGE'] | altitude['MEDIUM']), direction['ZERO'])
    rule26 = ctrl.Rule(drag['RIGHT_LARGE'] & (altitude['LARGE'] | altitude['MEDIUM']), direction['RIGHT'])
    rule27 = ctrl.Rule(drag['LEFT_LARGE'] & (altitude['LARGE'] | altitude['MEDIUM']), direction['LEFT'])
    rule28 = ctrl.Rule((drag['LEFT_LARGE'] | drag['RIGHT_LARGE']) & (altitude['LARGE'] | altitude['MEDIUM']), throttle['UP_LARGE'])
    rule29 = ctrl.Rule((drag['LEFT_SMALL'] | drag['RIGHT_SMALL']) & (altitude['LARGE'] | altitude['MEDIUM']), throttle['UP_SMALL'])
    rule30 = ctrl.Rule((drag['LEFT_SMALL'] | drag['LEFT_LARGE']) & angle['RIGHT'], throttle['DOWN_LARGE'])
    rule31 = ctrl.Rule((drag['RIGHT_SMALL'] | drag['RIGHT_LARGE']) & angle['LEFT'], throttle['DOWN_LARGE'])
    rule32 = ctrl.Rule((drag['LEFT_SMALL'] | drag['RIGHT_SMALL']), direction['ZERO'])

    angle_ctrl = ctrl.ControlSystem([rule22, rule23, rule24, rule25, rule26, rule27, rule28, rule29, rule30, rule31, rule32])

    throttling = ctrl.ControlSystemSimulation(throttling_ctrl)
    angling = ctrl.ControlSystemSimulation(angle_ctrl)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
    throttling.input['altitude'] = _altitude
    throttling.input['velocity'] = speed

    angling.input['altitude'] = _altitude
    angling.input['angle'] = _angle
    angling.input['drag'] = _drag


    # Crunch the numbers

    # print(f'altitude={_altitude}, speed={speed}')

    throttling.compute()

    if _angle == 0 and _drag <= 30:
        direction_out = 0
        slow = 0
    else:
        angling.compute()
        direction_out = angling.output['direction']
        slow = angling.output['throttle']

    throttle_out = throttling.output['throttle']

    return float(throttle_out), float(direction_out), float(slow)
