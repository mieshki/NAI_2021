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

def fuzzy_benchmark(_altitude, speed):
    altitude = ctrl.Antecedent(np.arange(0, 420, 1), 'altitude')
    velocity = ctrl.Antecedent(np.arange(0, 100, 1), 'velocity')
    throttle = ctrl.Consequent(np.arange(0, 1001, 1), 'throttle')

    altitude.automf(3, 'quant')
    velocity.automf(3, 'quant')

    throttle['low'] = fuzz.trimf(throttle.universe, [1, 1, 10])
    # throttle['medium'] = fuzz.trimf(throttle.universe, [0, 13, 25])
    throttle['high'] = fuzz.trimf(throttle.universe, [500, 800, 1000])

    # altitude: low, average, high
    # velocity: low, average, high
    # throttle: low, medium, high
    rule1 = ctrl.Rule(altitude['high'] | velocity['low'], throttle['low'])
    # rule2 = ctrl.Rule(altitude['average'] | velocity['average'], throttle['medium'])
    rule3 = ctrl.Rule(altitude['low'] & velocity['high'], throttle['high'])

    #rule2 = ctrl.Rule(velocity['low'] & velocity['average'], throttle['medium'])
    #rule3 = ctrl.Rule(velocity['average'] & velocity['high'], throttle['high'])

    #rule4 = ctrl.Rule(altitude['average'] & altitude['high'], throttle['low'])
    #rule5 = ctrl.Rule(altitude['low'], throttle['medium'], throttle['medium'])
    #rule6 = ctrl.Rule(altitude['lowest'] | altitude['lower'], throttle['high'])

    #throttling_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
    throttling_ctrl = ctrl.ControlSystem([rule1, rule3])

    throttling = ctrl.ControlSystemSimulation(throttling_ctrl)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
    throttling.input['altitude'] = _altitude
    throttling.input['velocity'] = speed

    # Crunch the numbers
    throttling.compute()
    print(f'altitude={_altitude}, speed={speed}')
    output = throttling.output['throttle']
    print(output)
    return output

def fuzzy_test():
    altitude = ctrl.Antecedent(np.arange(0, 11, 1), 'altitude')
    velocity = ctrl.Antecedent(np.arange(0, 11, 1), 'velocity')
    throttle = ctrl.Consequent(np.arange(0, 26, 1), 'throttle')

    # Auto-membership function population is possible with .automf(3, 5, or 7)
    altitude.automf(3)
    velocity.automf(3)

    throttle['low'] = fuzz.trimf(throttle.universe, [0, 0, 13])
    throttle['medium'] = fuzz.trimf(throttle.universe, [0, 13, 25])
    throttle['high'] = fuzz.trimf(throttle.universe, [13, 25, 25])

    # You can see how these look with .view()
    altitude['average'].view()
    velocity.view()
    throttle.view()

    rule1 = ctrl.Rule(altitude['poor'] | velocity['poor'], throttle['low'])
    rule2 = ctrl.Rule(velocity['average'], throttle['medium'])
    rule3 = ctrl.Rule(velocity['good'] | altitude['good'], throttle['high'])
    rule4 = ctrl.Rule(velocity['low'] )

    throttling_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])

    throttling = ctrl.ControlSystemSimulation(throttling_ctrl)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
    throttling.input['altitude'] = 401
    throttling.input['velocity'] = 13

    # Crunch the numbers
    throttling.compute()

    """
    Once computed, we can view the result as well as visualize it.
    """
    print(throttling.output['throttle'])
    throttle.view(sim=throttling)

    """
    .. image:: PLOT2RST.current_figure

    The resulting suggested throttle is **20.24%**.

    Final thoughts
    --------------

    The power of fuzzy systems is allowing complicated, intuitive behavior based
    on a sparse system of rules with minimal overhead. Note our membership
    function universes were coarse, only defined at the integers, but
    ``fuzz.interp_membership`` allowed the effective resolution to increase on
    demand. This system can respond to arbitrarily small changes in inputs,
    and the processing burden is minimal.
    """
    plt.show()

