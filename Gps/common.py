# -*- coding: utf-8 -*-
"""
 Módulo de funciones corriente o cumunes para los dispositivos.
"""

def MphToKph(speed):
    import math
    return math.floor(float(speed) * 1.609344)
