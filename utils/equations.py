import numpy as np
def pacejka_magic_formula(alpha, B, C, D, E):
    """Empirical mathematical model used to predict the forces a tire produces based on slip
    D: The Peak - Must be positive
    High D -> Car can handle huge forces, You can take a corner fast, tires will stick to the road
    Low D -> If you take corner fast, Tires can't produce enough force, you fly off the track. 

    B: Stiffness
    High B -> As soon as you turn the steering wheel like 1 or 2 deg, tire bites the road and turning the car, very sharp
    Low B -> When you turn the wheel, you have to turn the wheel further to get the same amount of turning force. 

    Now it is related to the personality of the tire
    C: Shape Factor - Control the drop-off after the peak
    Low C -> If you are drifting, the car feels predictable and easy to hold
    High C -> One second you're turning, the next second you've lost almost all control

    E: Curvature Factor
    +E -> The transition from 'gripping' to 'sliding' is very slow and gradual 
    -E -> You have 100% grip, then snap you have significanly less. 

    BCDE - Are the magic numbers, we need to find them for each tire. and they are constants for each tire. 

    """
    Bx = B * alpha
    inner = Bx - E * (Bx - np.arctan(Bx))
    return D * np.sin(C * np.arctan(inner))
