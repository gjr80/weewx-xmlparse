#!/usr/bin/python
# xmlparse.py
#
# A weeWX driver that reads data from a XML file.
#
# Copyright (C) 2018 Gary Roderick                  gjroderick<at>gmail.com
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.
#
# Version: 0.1.0                                    Date: 3 October 2018
#
# Revision History
#   3 October       v0.1.0
#       - initial release
#
"""A weeWX driver that reads data from a XML file.

This driver will poll a XML format file and map data from user specified XML
elements and attributes to WeeWX fields. The driver may operate in one of two
modes. Timestamp slave mode where the timestamp of loop packets emitted by the
driver is derived from a XML element or attribute. Timestamp master mode is
where the driver allocates the timestamp to loop packets emitted by the driver
based on the WeeWX system clock. XML elements and/or attributes are mapped to
WeeWX fields via user specified XPath expressions.
Refer https://www.w3.org/TR/1999/REC-xpath-19991116/

To use this driver:

1.  Copy this file to /home/weewx/bin/user or /usr/share/weewx/user depending
on your WeeWX install.

2.  Add the following section to weewx.conf setting options as required:

##############################################################################
[XML]

    # Time between polls of the XML source file in seconds
    poll_interval = 10

    # Location of the XML source file, includes path and file name
    path = /var/tmp/sensor.xml

    # the driver to use
    driver = user.xmlparse

    # Format of the date-time string used to determine the data timestamp. Uses
    # python strptime() format codes. Enclose in quotes.
    date_time_format = "%Y-%m-%d %H:%M:%S"

    # Timezone of the date-time string used to determine the data tiemstamp.
    # Can be 'GMT' or 'UTC' to use GMT or UTC or can be an XPath spec and
    # attribute if the timezone is specified in the XML file. If omitted local
    # time is assumed.
    time_zone = devices/device[name='Weatherstation']/records/record/time, zone

    # Timestamp mode. When in 'timestamp slave' mode loop packet timestamps are
    # determined from an element/attribute in the XML data. 'timestamp master'
    # mode uses the WeeWX system clock for loop packet timestamps.
    # String slave|master. Default is master.
    timestamp_mode = master

    # Maps used to map XML data to WeeWX fields
    [[sensor_map]]

        # Mapping of XML data to WeeWX fields. Must include a map for WeeWX field dateTime.
        #
        # Entries to be in the format:
        #
        #    WeeeWX field = XPath spec[, attribute]
        #
        # where
        #
        #   WeeWX field: A WeeWX archive table field name, eg outTemp,
        #                windSpeed.
        #   XPath spec:  An XPath specifcation string that will identify the
        #                XML element containing the data concerned. Ideally
        #                the XPath spec should uniquely identify the required
        #                element. Refer https://docs.python.org/2/library/xml.etree.elementtree.html#xpath-support
        #   attribute:   Attritute of the element idenfified by the XPath spec
        #                to used as the data source. Optional.
        #
        # eg:
        #
        #   outTemp = devices/device[name='Weatherstation']/records/record/point[@name='Temperature'], value

        [[[obs]]]
            dateTime = XPath spec[, attribute]
            # insert other maps as requried

        # Define units used for the source data. Units may be contained in the
        # XML data or may be explicity defined as a WeeWX unit string. If units
        # for a WeeWX field are omitted or otherwise invalid no unit conversion
        # of the raw data isperformed for that field.
        #
        # Entries to be in the format:
        #
        #   WeeeWX field = XPath spec[, attribute]
        #
        #   or
        #
        #   WeeWX field = WeeWX unit code
        #
        # where
        #
        #   WeeWX field: A WeeWX archive table field name, eg outTemp,
        #                windSpeed.
        #   XPath spec:  An XPath specifcation string that will identify the
        #                XML element containing the unit data concerned.
        #                Ideally the XPath spec should uniquely identify the
        #                required element.
        #                Refer https://docs.python.org/2/library/xml.etree.elementtree.html#xpath-support
        #   attribute:   Attritute of the element idenfified by the XPath spec
        #                to used as the unit string. Optional.
        #   WeeWX unit code: A WeeWX unit, eg meter, degree_C. WeeWX units are
        #                    listed at http://weewx.com/docs/customizing.htm#units
        #
        # eg:
        #
        #   outTemp = devices/device[name='Weatherstation']/records/record/point[@name='Temperature'], value
        #
        #   or
        #
        #   outTemp = degree_C
        [[[units]]]
            outTemp = devices/device[name='Weatherstation']/records/record/point[@name='Temperature'], units
            windSpeed = km_per_hour

##############################################################################

3.  Make the following further changes to weewx.conf as follows:
    - under [Station] set station_type = XML
    - under [StdArchive] ensure record_generation = software

4.  To run the driver in standalone mode for testing/development:

    $ PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/xmlparse.py

    or

    $ PYTHONPATH=/usr/share/weewx python /usr/share/weewx/user/xmlparse.py

5.  To run the driver under WeeWX stop then start WeeWX:

    $ sudo systemctl restart weewx

    or

    $ sudo service weewx restart

    or

    $ sudo /etc/init.d/weewx restart


Known issues/limitations:
-   Only supports decoding of XML sourced date-time data in local time or
    GMT/UTC.
-   loop packets are emitted using the METRICWX units, any sensor values that
    use different units (degrees F) need to have a suitable units mapping and
    conversion functions. At present only the following unit codes are
    implemented for non-METRICWX units:
    -   'Degrees F'
    -   'km/h'
    -   'hPa'
"""

from __future__ import with_statement
import calendar
import datetime
import syslog
import time
import xml.etree.ElementTree as ET

import weecfg
import weeutil
import weewx
import weewx.drivers
import weewx.units
import weewx.wxformulas
from weeutil.weeutil import ListOfDicts

DRIVER_NAME = 'XmlParse'
DRIVER_VERSION = '0.1.0'
SUPPORTED_TIMEZONES = ('GMT', 'UTC')
CONV_FUNCS = ListOfDicts({'Degrees F': weewx.units.FtoC,
                          'km/h': weewx.units.conversionDict['km_per_hour']['meter_per_second'],
                          'hPa': weewx.units.conversionDict['hPa']['mbar']})

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("WeeWX 3.x or greater is required, found %s" %
                                   weewx.__version__)


class MissingOption(StandardError):
    """Exception thrown when a mandatory option is invalid or otherwise has not
    been included in a config stanza."""


def logmsg(dst, msg):
    syslog.syslog(dst, 'xmlparse: %s' % msg)


def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)


def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)


def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


def loader(config_dict, engine):
    return XmlParseDriver(**config_dict[DRIVER_NAME])


def confeditor_loader():
    return XmlParseConfEditor()


class XmlParseDriver(weewx.drivers.AbstractDevice):
    """WeeWX driver that reads data from a XML file."""

    DEFAULT_POLL = 10
    DEFAULT_PATH = 'enter path and file name of XML source'

    def __init__(self, **xml_config_dict):
        # where to find the xml file
        self.path = xml_config_dict.get('path', '/var/tmp/sensor.xml')
        # get an XmlObject to facilitate reading data from the XML file
        self.xml = XmlObject(self.path)
        # how often to poll the xml file, seconds
        # wrap in try..except so we can trap an invalid or missing
        # poll_interval config option
        try:
            self.poll_interval = float(xml_config_dict.get('poll_interval'))
        except ValueError, TypeError:
            raise MissingOption("Missing or invalid 'poll_interval' config option")
        # operate in master or slave mode
        self.mode = xml_config_dict.get('timestamp_mode', 'master').lower()
        # date-time format string
        self.date_time_format = xml_config_dict.get('date_time_format')
        # time zone
        _time_zone = xml_config_dict.get('time_zone')
        if _time_zone is not None:
            # we have a specified time zone, is it an Xpath spec or a timezone code
            if hasattr(_time_zone, '__iter__'):
                # its a list so treat it as a complex Xpath spec
                _arg = _time_zone[1] if len(_time_zone) > 1 else None
                _time_zone = (_time_zone[0], _arg)
            elif _time_zone.upper() in SUPPORTED_TIMEZONES:
                # its a timezone code
                _time_zone = _time_zone.upper()
            else:
                # treat it as a simple Xpath spec
                _time_zone = (_time_zone[0], None)
        self.time_zone = _time_zone

        # get sensor map
        # start with an empty dict
        _sensor_map = dict()
        # get some config dicts we need to simply the code
        _map_dict = xml_config_dict.get('sensor_map', dict())
        _obs_dict = _map_dict.get('obs', dict())
        _units_dict = _map_dict.get('units', dict())
        # iterate over all of the sensor map obs entries
        for _field, _m in _obs_dict.iteritems():
            # build the XML data to WeeWX field portion of the sensor map
            _mapping = weeutil.weeutil.option_as_list(_m)
            _arg = _mapping[1] if len(_mapping) > 1 else None
            # construct the map
            _sensor_map[_field] = dict()
            _sensor_map[_field]['obs'] = dict()
            # the Xpath spec to be used
            _sensor_map[_field]['obs']['xpath'] = _mapping[0]
            #
            _sensor_map[_field]['obs']['arg'] = _arg
            # units map
            _um = _units_dict.get(_field)
            if _um is not None:
                if hasattr(_um, '__iter__'):
                    # assume we have an Xpath spec
                    _mapping = weeutil.weeutil.option_as_list(_um)
                    _arg = _mapping[1] if len(_mapping) > 1 else None
                    _sensor_map[_field]['units'] = (_mapping[0], _arg)
                elif _um in weewx.units.conversionDict:
                    # we have a WeeWX unit code
                    _sensor_map[_field]['units'] = _um
                else:
                    print "ingoring invalid unit specification"
        self.sensor_map = _sensor_map

        # is the rain field cumulative or a delta
        self.rain_delta = weeutil.weeutil.to_bool(xml_config_dict.get('rain_delta',
                                                                      False))
        self.old_rain = None

        # log key config items
        loginf("data file is %s" % self.path)
        loginf("polling interval is %s" % self.poll_interval)
        if self.mode == 'master':
            # timestamps are derived from system clock
            loginf("timestamps will be derived from the WeeWX system clock")
        else:
            # timestamps are derived from the XML data
            loginf("timestamps will be derived from the XML source")
            loginf("time_zone is %s" % (self.time_zone, ))
        loginf('sensor map is %s' % self.sensor_map)

    def genLoopPackets(self):
        """Generate loop packets continuously."""

        # there is a check that the timestamp of the current packet is later
        # than that of the previous packet, so initialise with a timestamp
        # from the past
        _last_dateTime = int(time.time() - 1)
        while True:
            # read xml from the source file
            self.xml.read_file()
            # get the timestamp we might use
            _ts = int(time.time())
            # read whatever values we can get from the file
            _raw_data = self.get_xml()
            # parse the raw data
            _parsed_data = self.parse_raw_data(_raw_data)
            # convert the parsed data
            _converted_data = self.convert_data(_parsed_data)
            # we are going to pop off any xxxx_units fields so take a copy of
            # our converted data dict
            _packet_data = dict(_converted_data)
            # now pop off any xxxx_units fields
            for _keys in _converted_data:
                if _keys.endswith('_units'):
                    _ = _packet_data.pop(_keys)
            # convert rain to a delta if required
            if 'rain' in _packet_data and not self.rain_delta:
                _old_rain = _packet_data['rain']
                _packet_data['rain'] = weewx.wxformulas.calculate_rain(_packet_data['rain'],
                                                                       self.old_rain)
                self.old_rain = _old_rain
            # map the data into a weewx loop packet
            _packet = {'usUnits': weewx.METRICWX}
            _packet.update(_packet_data)
            # if operating in timestamp master mode set the dateTime field to a
            # system generated timestamp
            if self.mode == 'master':
                _packet['dateTime'] = _ts
            # we only yield a packet if this packets dateTime is greter than
            # that of the last
            if _packet['dateTime'] > _last_dateTime:
                yield _packet
                _last_dateTime = _packet['dateTime']
            # sleep until its time to do it all again
            time.sleep(self.poll_interval)

    @property
    def hardware_name(self):
        """Property to return the 'hardware' name."""
        return "XmlParse"

    def get_xml(self):
        """Get a dict of raw data from the XML source file.

        Iterates over the sensor map looking for sensor values and units in the
        XML tree. If found the sensor value is added to a dict. Time zone is
        only considerd if operating in timezone slave mode.

        Returns:
            Dict containing sensor values and units.
        """

        _data = dict()
        # get sensor mapped data
        for _sensor, _map in self.sensor_map.iteritems():
            _data[_sensor] = self.xml.get_xpath(_map['obs']['xpath'], _map['obs']['arg'])
        # get timezone data
        if self.mode == 'slave':
            if hasattr(self.time_zone, '__iter__'):
                _data['timezone'] = self.xml.get_xpath(self.time_zone[0], self.time_zone[1])
            else:
                _data['timezone'] = self.time_zone
        # get unit data
        for _sensor, _map in self.sensor_map.iteritems():
            if 'units' in _map and hasattr(_map['units'], '__iter__'):
                # we have a units map and its a list/tuple (so its a Xpath spec)
                _field = '_'.join((_sensor, 'units'))
                _data[_field] = self.xml.get_xpath(_map['units'][0], _map['units'][1])
        return _data

    def parse_raw_data(self, raw_data):
        """Parse a dict of raw data.

        Takes a data dict of raw data in string format and parses fields
        appropriately. The following parsing is applied:

            dateTime:     interpreted as a timestamp if operating in slave
                          timestamp mode
            timezone:     unchanged
            units fields: unchanged
            other fields: converted to float or None if float conversion is not
                          possible

        Input:
            raw_data: dict containing the raw data (including units fields) in
                      obs:value format

        Returns:
            Dict containing all original fields with data parsed appropriately.
        """

        # empty dict for parsed data
        _data = dict()
        # iterate over all input data fields
        for _field, _value in raw_data.iteritems():
            # interpret dateTime formatted string as a timestamp if we are in
            # timestamp slave mode
            if _field == 'dateTime' and self.mode == 'slave':
                # store the parsed dateTime field in our results dict
                _data[_field] = self.parse_time(_value, raw_data['timezone'])
            # pass field timezone and any units fields through unchanged
            elif _field == 'timezone' or _field.endswith('_units'):
                # store the field in our results dict
                _data[_field] = _value
            # otherwise treat the field as a numeric obs and try to convert to
            # a float
            else:
                try:
                    _parsed = float(_value)
                except ValueError:
                    # cannot convert to a float so set to None - there is
                    # something there but its not valid
                    _parsed = None
                # store the parsed obs in our results dict
                _data[_field] = _parsed
        # timezone is no longer needed so pop off the timezone field
        _ = _data.pop('timezone', None)
        # return the parsed data dict
        return _data

    def parse_time(self, value, zone):
        """Parse a formatted string and return a Unix epoch timestamp.

        Takes a string representing a date-time and returns the corresponding
        epoch timestamp. WeeWX is not timezone aware so only limited timezone
        support is provided through use of the zone parameter.

        Inputs:
            value: String containing the date-time to be parsed.
            zone:  String containing time zone code of the time zone that value
                   is to be interpreted as. At present only local time and
                   GMT/UTC is supported.

        Returns:
            Epoch timestamp of value and zone.
        """

        try:
            _dt = datetime.datetime.strptime(value,
                                             self.date_time_format)
        except ValueError:
            return None
        if zone is None or zone not in SUPPORTED_TIMEZONES:
            # we have a local time
            _ts = time.mktime(_dt.timetuple())
        else:
            # we have a time in GMT/UTC
            _ts = calendar.timegm(_dt.timetuple())
        return int(_ts)

    @staticmethod
    def convert_data(data):
        """Convert a dict of parsed data.

        The xmlparse driver yields METRICWX packets. Parsed XML data may use units
        that are unknown to WeeWX or may use unit codes that are different to
        those used by WeeWX. Parsed data is converted to the relevant WeeWX
        METRICWX units by use of standard conversion functions defined in
        weewx.units where possible. Additional XML unit codes may be supported
        by adding appropriate key-value pairs to CONV_FUNCS.

        Parsed data that does not have a corresponding units field entry or for
        which there is no conversion function lookup entry is left unchanged.

        Input:
            data: dict containing the parsed data (including units fields) in
                  obs:value format

        Returns:
            Dict containing all original data with obs values converted to
            METRICWX units.
        """

        # empty dict for converted data
        _converted = dict()
        # iterate over all input data fields
        for _field, _value in data.iteritems():
            # assume the converted value is the starting value
            _conv_value = _value
            # if there was a units field for this field what would it be
            _units_field = ''.join((_field, '_units'))
            # do we have a units field
            if _units_field in data:
                # we have a units field for _field so what function do we use
                # to convert the data
                _conv_func = CONV_FUNCS.get(data[_units_field])
                # if we have a conversion function then apply it
                if _conv_func:
                    _conv_value = _conv_func(_value)
            # add the converted data the results dict
            _converted[_field] = _conv_value
        # return the converted data dict
        return _converted


class XmlObject(object):
    """Class to obtain data from an XML source.

    This class allows basic data extraction from an XML structured source file
    using the python ElementTree XML API. The class only requires a path and
    file name of a valid XML structured file. The get_xpath() method supports
    the use of an XPath specification to identify and return a data element of
    interest. The root and tostring properties provide a means of obtaining the
    XML root element.

    Required parameters:
        path: string containing the path and file name of a vild XML format
              text file

    Methods:
        read_file: Read an XM file and parse the contents using the ElementTree
                   library.
        get_xpath: Extract an XML data value given an XPath specification. If
                   an optional attrib value is given the data extracted is the
                   'attrib' attribute of the element specified is returned.

    Properties:
        root: return the root element of the XML tree

        tostring: returns a string representation of the entire XML tree
    """

    def __init__(self, path):
        """Initialise our class."""

        # the path and file name of the xml source file
        self.path = path
        # initialise the xml tree
        self.tree = None

    def read_file(self):
        """Read xml data from our file."""

        # get the parsed xml tree, log an error if it cannot be parsed
        try:
            self.tree = ET.parse(self.path)
        except Exception as e:
            logerr("xml parse failed: %s" % e)

    def get_xpath(self, xpath, attrib=None):
        """Return a value from an XML tree given an get XPath spec.

        The data sought from an XML source may be either an element or an
        attribute. Consider the following XML extract:

        <book>
            <title lang="en">Harry Potter</title>
            <author>J K. Rowling</author>
            <year>2005</year>
            <price>29.99</price>
        </book>

        In this case the 'price' element is 29.99 and the 'title' element is
        'Harry Potter'. The 'lang' attribute of the 'Title' element is 'en'.
        If no attrib parameter is passed the text value of the element defined
        by XPath spec passed in the xpath parameter is returned. If an attrib
        parameter is passed then the 'attrib' attribute of the element defined
        by the XPath spec in the xpath parameter it returned.

        If xpath identifies more then one element then the first element found
        is used. If xpath results in no elements being found or if attrib does
        not match any attributres for the element concerned then None is
        returned.

        Parameters:
            xpath:  string containing a valid XPath specification
            attrib: string containing the name of the element attribute to be
                    returned
        """

        if attrib is None:
            return self.tree.find(xpath).text
        else:
            return self.tree.find(xpath).get(attrib, None)

    @property
    def root(self):
        """Return the root element for the XML tree."""

        return self.tree.getroot()

    @property
    def tostring(self):
        """Return a string representation of the entire XML tree."""

        return ET.tostring(self.root)


class XmlParseConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[XML]
    # This section is for the XML parse driver.

    # Time between polls of the XML source file in seconds
    poll_interval = %s

    # Location of the XML source file, includes path and file name
    path = %s

    # The driver to use
    driver = user.xmlparse

    # Format of the date-time string used to determine the data timestamp. Uses
    # python strptime() format codes. Enclose in quotes.
    date_time_format = "%Y-%m-%d %H:%M:%S"

    # Timezone of the date-time string used to determine the data tiemstamp.
    # Can be 'GMT' or 'UTC' to use GMT or UTC or can be an XPath spec and
    # attribute if the timezone is specified in the XML file. If omitted local
    # time is assumed.
    time_zone = enter time zone code or XPath spec

    # Maps used to map XML data to WeeWX fields
    [[sensor_map]]

        # Mapping of XML data to WeeWX fields. Must include a map for WeeWX field dateTime.
        #
        # Entries to be in the format:
        #
        #    WeeeWX field = XPath spec[, attribute]
        #
        # where
        #
        #   WeeWX field: A WeeWX archive table field name, eg outTemp,
        #                windSpeed.
        #   XPath spec:  An XPath specification string that will identify the
        #                XML element containing the data concerned. Ideally
        #                the XPath spec should uniquely identify the required
        #                element. Refer https://docs.python.org/2/library/xml.etree.elementtree.html#xpath-support
        #   attribute:   Attribute of the element identified by the XPath spec
        #                to used as the data source. Optional.
        #
        # eg:
        #
        #   outTemp = devices/device[name='Weatherstation']/records/record/point[@name='Temperature'], value

        [[[obs]]]
            dateTime = XPath spec[, attribute]
            # insert other maps as requried

        # Define units used for the source data. Units may be contained in the
        # XML data or may be explicitly defined as a WeeWX unit string. If units
        # for a WeeWX field are omitted or otherwise invalid no unit conversion
        # of the raw data is performed for that field.
        #
        # Entries to be in the format:
        #
        #   WeeeWX field = XPath spec[, attribute]
        #
        #   or
        #
        #   WeeWX field = WeeWX unit code
        #
        # where
        #
        #   WeeWX field: A WeeWX archive table field name, eg outTemp,
        #                windSpeed.
        #   XPath spec:  An XPath specification string that will identify the
        #                XML element containing the unit data concerned.
        #                Ideally the XPath spec should uniquely identify the
        #                required element.
        #                Refer https://docs.python.org/2/library/xml.etree.elementtree.html#xpath-support
        #   attribute:   Attribute of the element identified by the XPath spec
        #                to used as the unit string. Optional.
        #   WeeWX unit code: A WeeWX unit, eg meter, degree_C. WeeWX units are
        #                    listed at http://weewx.com/docs/customizing.htm#units
        #
        # eg:
        #
        #   outTemp = devices/device[name='Weatherstation']/records/record/point[@name='Temperature'], value
        #
        #   or
        #
        #   outTemp = degree_C
        [[[units]]]
            # insert maps as required
""" % (XmlParseDriver.DEFAULT_POLL, XmlParseDriver.DEFAULT_PATH)

    def prompt_for_settings(self):
        settings = dict()
        print "Specify the polling interval to be used in seconds."
        settings['poll_interval'] = self._prompt('polling interval',
                                                 XmlParseDriver.DEFAULT_POLL)
        print "Specify the path and file name of the XML source file,"
        print "eg /var/tmp/sensor.xml"
        settings['path'] = self._prompt('path',
                                        XmlParseDriver.DEFAULT_PATH)
        return settings


# To use this driver in standalone mode for testing or development, use one of
# the following commands (depending on your WeeWX install):
#
#   $ PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/xmlparse.py
#
#   or
#
#   $ PYTHONPATH=/usr/share/weewx python /usr/share/weewx/user/xmlparse.py
#
#   The above commands will display details of available command line options.

if __name__ == "__main__":
    usage = """%prog [options] [--help]"""

    def main():
        import optparse

        syslog.openlog('xmlparse', syslog.LOG_PID | syslog.LOG_CONS)
        parser = optparse.OptionParser(usage=usage)
        parser.add_option('--version', dest='version', action='store_true',
                          help='display driver version number')
        parser.add_option('--config', dest='config_path', metavar='CONFIG_FILE',
                          help="use configuration file CONFIG_FILE.")
        parser.add_option('--debug', dest='debug', action='store', type='int',
                          help='display diagnostic information while running')
        parser.add_option('--run-driver', dest='run_driver', action='store_true',
                          metavar='RUN_DRIVER', help='run the xmlparse driver')
        # yet to be implemented
        # parser.add_option('--run-service', dest='run_service', action='store_true',
        #                    metavar='RUN_SERVICE', help='run the Bloomsky service')
        parser.add_option('--path', dest='xml_path', metavar='XML_PATH',
                          help='path and file name of xml file')
        parser.add_option('--display-xml', dest='display_xml', action='store_true',
                          help='display the parsed xml file contents')
        parser.add_option('--pretty-print-xml', dest='pprint_xml', action='store_true',
                          help='pretty print the parsed xml file contents')
        (opts, args) = parser.parse_args()

        # if --debug raise our log level
        if opts.debug > 0:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
            weewx.debug = opts.debug

        # display driver version number
        if opts.version:
            print "%s driver version: %s" % (DRIVER_NAME, DRIVER_VERSION)
            exit(0)

        # get config_dict to use
        config_path, config_dict = weecfg.read_config(opts.config_path, args)
        # inform the user of the config file being used
        print "Using configuration file %s" % config_path
        # extract the XML driver stanza as a config dict
        xml_config_dict = config_dict.get('XML', {})

        # run the driver
        if opts.run_driver:
            run_driver(xml_config_dict)

        # pretty print the xml data
        if opts.pprint_xml:
            # get the path and file name to use as our source, it can be
            # specified by a command line parameter or obtained from a WeeWX
            # config file
            _xml_path = opts.xml_path if opts.xml_path else xml_config_dict.get('path')
            # pretty print the XML data
            pprint_xml_data(_xml_path)
            exit(0)

        # display the xml data
        if opts.display_xml:
            # get the path and file name to use as our source, it can be
            # specified by a command line parameter or obtained from a WeeWX
            # config file
            _xml_path = opts.xml_path if opts.xml_path else xml_config_dict.get('path')
            # display the XML data
            display_xml_data(_xml_path)
            exit(0)

        # if we reached here then display our usage info
        parser.print_help()

    def display_xml_data(xml_path):
        """Display the raw parsed xml data."""

        # get an XmlObject
        xml = XmlObject(xml_path)
        # now display the data
        # first a blank line for aesthetics
        print
        # now the data
        print xml.tostring

    def pprint_xml_data(xml_path):
        """Pretty print the raw parsed xml data."""

        from xml.dom import minidom

        # get an XmlObject
        xml = XmlObject(xml_path)
        # now display the data
        # first a blank line for aesthetics
        print
        # now the data
        print minidom.parseString(xml.tostring).toprettyxml(indent="   ", newl='')

    def run_driver(xml_config_dict):
        """Run the xmlparse driver.

        Runs the XML driver as it would be run with WeeWX but without the
        overheads of WeeWX. Loop data only is emitted direct to the console in
        much the same way as wehn running WeeWX directly.
        """

        # obtain and XmlParseDriver object
        driver = XmlParseDriver(xml_config_dict)
        # generate and display loop packets indefinitely
        for packet in driver.genLoopPackets():
            print weeutil.weeutil.timestamp_to_string(packet['dateTime']), packet

    main()
