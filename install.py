#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
#                       Installer for XML parse driver
#
# Version: 0.1.0                                        Date: 6 October 2018
#
# Revision History
#   3 October 2018      v0.1.0
#       - initial implementation
#

import weewx

from distutils.version import StrictVersion
from setup import ExtensionInstaller

REQUIRED_VERSION = "3.0.0"
XMLPARSE_VERSION = "0.1.0"


def loader():
    return XmlParseDriverInstaller()


class XmlParseDriverInstaller(ExtensionInstaller):
    def __init__(self):
        if StrictVersion(weewx.__version__) < StrictVersion(REQUIRED_VERSION):
            _dv = ' '.join(('XML parse', XMLPARSE_VERSION))
            msg = "%s requires WeeWX %s or greater, found %s" % (_dv,
                                                                 REQUIRED_VERSION,
                                                                 weewx.__version__)
            raise weewx.UnsupportedFeature(msg)
        super(XmlParseDriverInstaller, self).__init__(
            version=XMLPARSE_VERSION,
            name='XmlParse',
            description='A WeeWX driver to read data from an XML file.',
            author="Gary Roderick",
            author_email="gjroderick<@>gmail.com",
            files=[('bin/user', ['bin/user/xmlparse.py'])]
        )
