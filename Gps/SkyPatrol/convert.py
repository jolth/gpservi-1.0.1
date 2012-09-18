# -*- coding: utf-8 -*-

def deg_to_dms(num, signo):       
    """
    """
    point = num.find('.')
    d = num[:point-2]
    m = num[point-2:]
    m = float(m) / 60
    numero = float(d) + m
    if signo in ['S','W']:
        return numero * (-1)
    return numero


def degTodms(s):       
    """
    """
    #s = s.split(',')
    num = s[0]
    signo = s[1]
    point = num.find('.')
    d = num[:point-2]
    m = num[point-2:]
    m = float(m) / 60
    numero = float(d) + m
    if signo in ['S','W']:
        return numero * (-1)
    return numero
