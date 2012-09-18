# -*- coding: utf-8 -*-
# Author: Jorge A. Toro
#
import sys
import datetime
import StringIO
from UserDict import UserDict
import simplejson as json
from Gps.Antares.convert import latWgs84ToDecimal, lngWgs84ToDecimal
from Gps.common import MphToKph
import Location.geomapgoogle


def tagData(dFile, position, bit=None, seek=0):
    """
        Toma un punto de partida (position), cantidad de bit y un punto de 
        referencia para leer los bit(según el método seek() de los fichero).
        Además dataFile el cual es objeto StringIO.
    """
    try:
        dFile.seek(position, seek)
        tagdata =  dFile.read(bit)
    except: sys.stderr.write("Error al obtener el Tag Data")
            
    return tagdata


# Clase que actua como un diccionario
class Device(UserDict):
    """ Store Device"""
    def __init__(self, deviceData=None, address=None):
        UserDict.__init__(self)
        self["data"] = deviceData
        #self["address"] = address
        self["address"] = "%s,%s" % address
        #self["geocoding"] = None
        # Fecha y hora (del sistema)
        self["datetime"] = datetime.datetime.now()


class ANTDevice(Device):
    """
        Dispositivo Antares
    """
    tagDataANT = {  # (position, bit, seek, function_tagData, function_convert )
                    #"id"        : (-6, 6, 2, tagData)#, # ID de la unidad
                    "id"        : (-6, None, 2, tagData, None), # ID de la unidad
                    "type"      : (0, 1, 0, tagData, None),
                    "typeEvent" : (1, 2, 0, tagData, None),     # 
                    "codEvent"  : (3, 2, 0, tagData, None),     # Codigo de evento activado (en Antares de 00 a 49, en e.Track de 00 a 99)
                    "weeks"     : (5, 4, 0, tagData, None),     # Es el numero de semanas desde 00:00AM del 6 de enero de 1980.
                    "dayWeek"   : (9, 1, 0, tagData, None),     # 0=Domingo, 1=Lunes, etc hasta 6=sabado.
                    "time"      : (10, 5, 0, tagData, None),    # Hora expresada en segundos desde 00:00:00AM
                    "lat"       : (15, 8, 0, tagData, latWgs84ToDecimal),    # Latitud
                    "lng"       : (23, 9, 0, tagData, lngWgs84ToDecimal),    # Longitud
                    "speed"     : (-18, 3, 2, tagData, MphToKph),   # Velocidad en MPH
                    "course"    : (-15, 3, 2, tagData, None),   # Curso en grados
                    "gpsSource" : (-12, 1, 2, tagData, None),   # Fuente GPS. Puede ser 0=2D GPS, 1=3D GPS, 2=2D DGPS, 3=3D DGPS, 6=DR, 8=Degraded DR.     
                    "ageData"   : (-11, 1, 2, tagData, None)    # Edad del dato. Puede ser 0=No disponible, 1=viejo (10 segundos) ó 2=Fresco (menor a 10 segundos)
                 }


    def __parse(self, data):
        self.clear()
        try:
            dataFile = StringIO.StringIO(data[1:-1]) # remove '<' y '>'
            #
            for tag, (position, bit, seek, parseFunc, convertFunc) in self.tagDataANT.items():
                self[tag] = convertFunc and convertFunc(parseFunc(dataFile, position, bit, seek)) or parseFunc(dataFile, position, bit, seek)

            # Creamos una key para la altura (estandar), ya que las tramas actuales no la incluyen:
            self['altura'] = None
            # Creamos una key para el dato position:
            self['position'] = "(%(lat)s,%(lng)s)" % self

            # Realizamos la Geocodificación. Tratar de no hacer esto
            # es mejor que se realize por cada cliente con la API de GoogleMap
            self["geocoding"] = None 
            self["geocoding"] = json.loads(Location.geomapgoogle.regeocode('%s,%s' % (self["lat"], self["lng"])))[0]

        except: print(sys.exc_info()) #sys.stderr.write('Error Inesperado:', sys.exc_info())
        finally: dataFile.close()


    def __setitem__(self, key, item):
        if key == "data" and item:
            self.__parse(item)
        # Llamamos a __setitem__ de nuestro ancestro
        Device.__setitem__(self, key, item) 

        
    
class SKPDevice(Device):
    """
        Dispositivo Skypatrol
    """
    pass


class HUNTDevice(Device):
    """
        Dispositivo Hunter
    """
    pass



def typeDevice(data):
    """
        Determina que tipo de Dispositivo GPS es dueña de la data.

        Usage:
            >>> import devices
            >>> 
            >>> data='>REV041674684322+0481126-0757378200000012;ID=ANT001<'
            >>> devices.typeDevice(data)
            'ANT'
            >>>
            >>> type(devices.typeDevice(''))
            <type 'NoneType'>
            >>>
            >>> if devices.typeDevice('') is not None: print "Seguir con el programa..."
            ... 
            >>> if devices.typeDevice(data) is not None: print "Seguir con el programa..."
            ... 
            Seguir con el programa...
            >>> 
    """
    # Dispositivos soportados:
    types = ('ANT', 'SKP', 'HUNT')

    typeDev = lambda dat: ("".join(
                            [d for d in types 
                            if dat.find(d) is not -1])
                        )
    return typeDev(data) or None #raise


#
def getTypeClass(data, address=None, module=sys.modules[Device.__module__]):
    """
        Determina que clase debe manejar un determinado dispositivo y
        retorna un diccionario con la trama procesada.

        Recibe la data enviada por el dispositivo (data), y opcionalmente 
        el nombre del módulo donde se encuentra la clase que manipula este 
        tipo de dispositivo (module). La clase manejador debe tener un 
        formato compuesto por 'TIPO_DISPOSITIVO + Device' por ejemplo: ANTDevice,
        SKPDevice, etc.

        Usage:
            >>> import devices
            >>> 
            >>> data='>REV001447147509+2578250-0802813901519512;ID=ANT001<'
            >>> devices.getTypeClass(data)
            {'codEvent': '00', 'weeks': '1447', 'dayWeek': '1', 'ageData': '2', \
            'type': 'R', 'data': '>REV001447147509+2578250-0802813901519512;ID=ANT001<', \
            'course': '195', 'gpsSource': '1', 'time': '47509', 'lat': '+2578250', \
            'typeEvent': 'EV', 'lng': '-08028139', 'speed': '015', 'id': 'ANT001'}
            >>> print "\n".join(["%s=%s" % (key,value) for key, value in devices.getTypeClass(data).items()])
            codEvent=00
            weeks=1447
            dayWeek=1
            ageData=2
            type=R
            data=>REV001447147509+2578250-0802813901519512;ID=ANT001<
            course=195
            gpsSource=1
            time=47509
            lat=+2578250
            typeEvent=EV
            lng=-08028139
            speed=015
            id=ANT001
            >>> 
    """
    import re

    #data = data.replace('\n','')
    #data = data.strip('\n')
    data = re.sub(r"[\r\n]+", "", data)

    # Determinamos la clase manejadora adecuado según el dispositivo
    dev = "%sDevice" % typeDevice(data)

    #return dev
    def getClass(module, dev): 
        """ 
            Retorna una referencia a la clase manejadora. 
            Usage:
            >>> getClass(module, 'ANTDevice')
            <class devices.ANTDevice at 0xb740435c>
            >>> getClass(module, 'SKPDevice')
            <class devices.SKPDevice at 0xb740438c>
            >>> getClass(module, '')
            <class devices.Device at 0xb740426c>
            >>> 
        """
        return hasattr(module, dev) and getattr(module, dev) or Device

    return getClass(module, dev)(data, address)

     

