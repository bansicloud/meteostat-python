"""
Unit Tests - Stations Class

The code is licensed under the MIT license.
"""

import unittest
from meteostat import Stations


class TestStations(unittest.TestCase):

    """
    Stations class tests
    """

    def test_nearby(self):
        """
        Test: Nearby stations
        """

        # Selecting closest weather station to Frankfurt Airport
        station = Stations().nearby(50.05, 8.6).fetch(1).to_dict('records')[0]

        # Check if country code matches Germany
        self.assertEqual(
            station['country'],
            'DE',
            'Closest weather stations returns country code ' +
            station['country'] +
            ', should be DE')

    def test_identifier(self):
        """
        Test: Stations by identifier
        """

        # Select weather station 'Toronto Pearson Airport'
        station = Stations().id('wmo', '71624').fetch(1).to_dict('records')[0]

        # Check if ICAO ID matches CYYZ
        self.assertEqual(
            station['icao'],
            'CYYZ',
            'Weather station returns ICAO ID ' +
            station['icao'] +
            ', should be CYYZ')

    def test_regional(self):
        """
        Test: Stations by country/region code
        """

        # Select a weather station in Ontario, Canada
        station = Stations().region('CA', 'ON').fetch(
            1).to_dict('records')[0]

        # Check if country code matches Canada
        self.assertEqual(
            station['country'],
            'CA',
            'Weather station returns country code ' +
            station['country'] +
            ', should be CA')

        # Check if region code matches Ontario
        self.assertEqual(
            station['region'],
            'ON',
            'Weather station returns province code ' +
            station['region'] +
            ', should be ON')

    def test_area(self):
        """
        Test: Stations by geographical area
        """

        # Select weather stations in southern hemisphere
        station = Stations().bounds(
            (0, -180), (-90, 180)).fetch(1).to_dict('records')[0]

        # Check if -90 <= latitude <= 0
        self.assertTrue(
            -90 <= station['latitude'] <= 0,
            'Weather station is not in latitude range'
        )


if __name__ == '__main__':
    unittest.main()
