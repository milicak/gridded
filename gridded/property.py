#!/usr/bin/env python

# py2/3 compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np


class EnvProp(object):

    def __init__(self,
                 name=None,
                 units=None,
                 time=None,
                 data=None,
                 **kwargs):
        '''
        A class that represents a natural phenomenon and provides an interface to get
        the value of the phenomenon at a position in space and time. EnvProp is the base
        class, and returns only a single value regardless of the time.

        :param name: Name
        :param units: Units
        :param time: Time axis of the data
        :param data: Value of the property
        :type name: string
        :type units: string
        :type time: [] of datetime.datetime, netCDF4.Variable, or Time object
        :type data: netCDF4.Variable or numpy.array
        '''

        self.name = self._units = self._time = self._data = None

        self.name = name
        self.units = units
        self.data = data
        self.time = time
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('{0.__class__.__module__}.{0.__class__.__name__}('
                'name="{0.name}", '
                'time="{0.time}", '
                'units="{0.units}", '
                'data="{0.data}", '
                ')').format(self)

    '''
    Subclasses should override\add any attribute property function getter/setters as needed
    '''

#     @property
#     def data(self):
#         '''
#         Underlying data
#
#         :rtype: netCDF4.Variable or numpy.array
#         '''
#         return self._data

    @property
    def units(self):
        '''
        Units of underlying data

        :rtype: string
        '''
        return self._units

    @units.setter
    def units(self, unit):
#         if unit is not None:
#             if not unit_conversion.is_supported(unit):
#                 raise ValueError('Units of {0} are not supported'.format(unit))
        self._units = unit

    @property
    def time(self):
        '''
        Time axis of data

        :rtype: gnome.environment.property.Time
        '''
        return self._time

    @time.setter
    def time(self, t):
        if t is None:
            self._time = None
        elif isinstance(t, Time):
            self._time = t
        elif isinstance(t, collections.Iterable):
            self._time = Time(t)
        else:
            raise ValueError("Object being assigned must be an iterable or a Time object")

    def at(self, *args, **kwargs):
        '''
        Find the value of the property at positions P at time T

        :param points: Coordinates to be queried (P)
        :param time: The time at which to query these points (T)
        :param time: Specifies the time level of the variable
        :param units: units the values will be returned in (or converted to)
        :param extrapolate: if True, extrapolation will be supported
        :type points: Nx2 array of double
        :type time: datetime.datetime object
        :type time: integer
        :type units: string such as ('m/s', 'knots', etc)
        :type extrapolate: boolean (True or False)
        :return: returns a Nx1 array of interpolated values
        :rtype: double
        '''

        raise NotImplementedError()

#     def in_units(self, unit):
#         '''
#         Returns a full cpy of this property in the units specified.
#         WARNING: This will cpy the data of the original property!
#
#         :param units: Units to convert to
#         :type units: string
#         :return: Copy of self converted to new units
#         :rtype: Same as self
#         '''
#         cpy = copy.copy(self)
#         if hasattr(cpy.data, '__mul__'):
#             cpy.data = unit_conversion.convert(cpy.units, unit, cpy.data)
#         else:
#             warnings.warn('Data was not converted to new units and was not copied because it does not support multiplication')
#         cpy._units = unit
#         return cpy


class VectorProp(object):

    def __init__(self,
                 name=None,
                 units=None,
                 time=None,
                 variables=None,
                 **kwargs):
        '''
        A class that represents a vector natural phenomenon and provides an interface to get the value of
        the phenomenon at a position in space and time. VectorProp is the base class

        :param name: Name of the Property
        :param units: Unit of the underlying data
        :param time: Time axis of the data
        :param variables: component data arrays
        :type name: string
        :type units: string
        :type time: [] of datetime.datetime, netCDF4.Variable, or Time object
        :type variables: [] of EnvProp or numpy.array (Max len=2)
        '''

        self.name = self._units = self._time = self._variables = None

        self.name = name

        if all([isinstance(v, EnvProp) for v in variables]):
            if time is not None and not isinstance(time, Time):
                time = Time(time)
            units = variables[0].units if units is None else units
            time = variables[0].time if time is None else time
        if units is None:
            units = variables[0].units
        self._units = units
        if variables is None or len(variables) < 2:
            raise ValueError('Variables must be an array-like of 2 or more Property objects')
        self.variables = variables
        self._time = time
        unused_args = kwargs.keys() if kwargs is not None else None
        if len(unused_args) > 0:
#             print(unused_args)
            kwargs = {}
        super(VectorProp, self).__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('{0.__class__.__module__}.{0.__class__.__name__}('
                'name="{0.name}", '
                'time="{0.time}", '
                'units="{0.units}", '
                'variables="{0.variables}", '
                ')').format(self)

    @property
    def time(self):
        '''
        Time axis of data

        :rtype: gnome.environment.property.Time
        '''
        return self._time

    @property
    def units(self):
        '''
        Units of underlying data

        :rtype: string
        '''
        if hasattr(self._units, '__iter__'):
            if len(set(self._units) > 1):
                return self._units
            else:
                return self._units[0]
        else:
            return self._units

    @units.setter
    def units(self, unit):
        self._units = unit
        if self.variables is not None:
            for v in self.variables:
                v.units = unit

    @property
    def varnames(self):
        '''
        Names of underlying variables

        :rtype: [] of strings
        '''
        return [v.varname if hasattr(v, 'varname') else v.name for v in self.variables ]

    def _check_consistency(self):
        '''
        Checks that the attributes of each GriddedProp in varlist are the same as the GridVectorProp
        '''
        raise NotImplementedError()

    def at(self, *args, **kwargs):
        '''
        Find the value of the property at positions P at time T

        :param points: Coordinates to be queried (P)
        :param time: The time at which to query these points (T)
        :param time: Specifies the time level of the variable
        :param units: units the values will be returned in (or converted to)
        :param extrapolate: if True, extrapolation will be supported
        :type points: Nx2 array of double
        :type time: datetime.datetime object
        :type time: integer
        :type units: string such as ('m/s', 'knots', etc)
        :type extrapolate: boolean (True or False)
        :return: returns a Nx2 array of interpolated values
        :rtype: double
        '''
        return np.column_stack([var.at(*args, **kwargs) for var in self.variables])