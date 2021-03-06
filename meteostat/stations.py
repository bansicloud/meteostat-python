"""
Stations Class

Meteorological data provided by Meteostat (https://dev.meteostat.net)
under the terms of the Creative Commons Attribution-NonCommercial
4.0 International Public License.

The code is licensed under the MIT license.
"""

from math import cos, sqrt, radians
from copy import copy
from datetime import timedelta
import pandas as pd
from meteostat.core import Core

class Stations(Core):

    """
    Select weather stations from the full list of stations
    """

    # The cache subdirectory
    cache_subdir = 'stations'

    # The list of selected weather Stations
    _stations = None

    # Columns
    _columns = [
        'id',
        'name',
        'country',
        'region',
        'wmo',
        'icao',
        'latitude',
        'longitude',
        'elevation',
        'timezone',
        'hourly_start',
        'hourly_end',
        'daily_start',
        'daily_end'
    ]

    _types = {
        'id': 'string',
        'name': 'object',
        'country': 'string',
        'region': 'string',
        'wmo': 'string',
        'icao': 'string',
        'latitude': 'float64',
        'longitude': 'float64',
        'elevation': 'float64',
        'timezone': 'string'
    }

    # Columns for date parsing
    _parse_dates = [10, 11, 12, 13]

    def __init__(
        self
    ):

        # Get all weather stations
        try:
            file = self._load(['stations/lib.csv.gz'])[0]
            self._stations = pd.read_parquet(file['path'])
        except BaseException as read_error:
            raise Exception('Cannot read weather station directory') from read_error

        # Clear cache
        self.clear_cache()

    def id(self, organization, code):

        """
        Get weather station by identifier
        """

        # Create temporal instance
        temp = copy(self)

        if isinstance(code, str):
            code = [code]

        if organization == 'meteostat':
            temp._stations = temp._stations[temp._stations.index.isin(code)]
        else:
            temp._stations = temp._stations[temp._stations[organization].isin(code)]

        # Return self
        return temp

    def nearby(self, lat, lon, radius=None):

        """
        Sort/filter weather stations by physical distance
        """

        # Create temporal instance
        temp = copy(self)

        # Calculate distance between weather station and geo point
        def distance(station, point):

            # Earth radius in m
            radius = 6371000

            x = (radians(point[1]) - radians(station['longitude'])) * \
                cos(0.5 * (radians(point[0]) + radians(station['latitude'])))
            y = (radians(point[0]) - radians(station['latitude']))

            return radius * sqrt(x * x + y * y)

        # Get distance for each stationsd
        temp._stations['distance'] = temp._stations.apply(
            lambda station: distance(station, [lat, lon]), axis=1)

        # Filter by radius
        if radius is not None:
            temp._stations = temp._stations[temp._stations['distance'] <= radius]

        # Sort stations by distance
        temp._stations.columns.str.strip()
        temp._stations = temp._stations.sort_values('distance')

        # Return self
        return temp

    def region(self, country, state=None):

        """
        Filter weather stations by country/region code
        """

        # Create temporal instance
        temp = copy(self)

        # Country code
        temp._stations = temp._stations[temp._stations['country'] == country]

        # State code
        if state is not None:
            temp._stations = temp._stations[temp._stations['region'] == state]

        # Return self
        return temp

    def bounds(self, top_left, bottom_right):

        """
        Filter weather stations by geographical bounds
        """

        # Create temporal instance
        temp = copy(self)

        # Return stations in boundaries
        temp._stations = temp._stations[
            (temp._stations['latitude'] <= top_left[0]) &
            (temp._stations['latitude'] >= bottom_right[0]) &
            (temp._stations['longitude'] <= bottom_right[1]) &
            (temp._stations['longitude'] >= top_left[1])
        ]

        # Return self
        return temp

    def inventory(self, granularity, required):

        """
        Filter weather stations by inventory data
        """

        # Create temporal instance
        temp = copy(self)

        if required is True:
            # Make sure data exists at all
            temp._stations = temp._stations[
                (pd.isna(temp._stations[granularity + '_start']) == False)
            ]
        elif isinstance(required, tuple):
            # Make sure data exists across period
            temp._stations = temp._stations[
                (pd.isna(temp._stations[granularity + '_start']) == False) &
                (temp._stations[granularity + '_start'] <= required[0]) &
                (
                    temp._stations[granularity + '_end'] +
                    timedelta(seconds=temp.max_age)
                    >= required[1]
                )
            ]
        else:
            # Make sure data exists on a certain day
            temp._stations = temp._stations[
                (pd.isna(temp._stations[granularity + '_start']) == False) &
                (temp._stations[granularity + '_start'] <= required) &
                (
                    temp._stations[granularity + '_end'] +
                    timedelta(seconds=temp.max_age)
                    >= required
                )
            ]

        return temp

    def convert(self, units):

        """
        Convert columns to a different unit
        """

        # Create temporal instance
        temp = copy(self)

        # Change data units
        for parameter, unit in units.items():
            if parameter in temp._stations.columns.values:
                temp._stations[parameter] = temp._stations[parameter].apply(
                    unit)

        # Return class instance
        return temp

    def count(self):

        """
        Return number of weather stations in current selection
        """

        return len(self._stations.index)

    def fetch(self, limit=None, sample=False):

        """
        Fetch all weather stations or a (sampled) subset
        """

        # Copy DataFrame
        temp = copy(self._stations)

        # Return limited number of sampled entries
        if sample and limit:
            return temp.sample(limit)

        # Return limited number of entries
        if limit:
            return temp.head(limit)

        # Return all entries
        return temp
