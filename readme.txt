XML parse driver

A WeeWX driver to read data from an XML file.

Description

The XML parse driver allows WeeWX to poll an XML format file for data at a user
configurable rate. The driver maps data from XML elements and attributes emits
this data in a WeeWX loop packet format.

Pre-Requisites

The XML parse driver requires:

-   WeeWX v3.0.0 or greater

Installation

The XML parse driver can be installed manually or automatically using the
wee_extension utility (http://weewx.com/docs/utilities.htm#wee_extension_utility).
The preferred method of installation is through the use of wee_extension.

Installation using the wee_extension utility

Note:   Symbolic names are used below to refer to some file location on the
weeWX system. These symbolic names allow a common name to be used to refer to
a directory that may be different from system to system. The following symbolic
names are used below:

-   $DOWNLOAD_ROOT. The path to the directory containing the downloaded
    XML parse driver extension package.

-   $BIN_ROOT. The path to the directory where weeWX executables are located.
    This directory varies depending on weeWX installation method. Refer to
    'where to find things' in the weeWX User's Guide:
    http://weewx.com/docs/usersguide.htm#Where_to_find_things for further
    information.

Installation using the wee_extension utility

1.  Download the latest XML parse driver extension package from the XML parse
driver releases page (https://github.com/gjr80/weewx-xmlparse/releases) into a
directory accessible from the WeeWX machine.

    $ wget -P $DOWNLOAD_ROOT https://github.com/gjr80/weewx-xmlparse/releases/download/v0.1.0/xmlparse-0.1.0.tar.gz

    where *$DOWNLOAD_ROOT* is the path to the directory where the XML parse
    driver extension package is to be downloaded.

2.  Stop WeeWX:

    $ sudo /etc/init.d/weewx stop

    or

    $ sudo service weewx stop

    or

    $ sudo systemctl stop weewx

3.  Install the XML parse driver downloaded at step 1 using the wee_extension
utility:

    $ wee_extension --install=$DOWNLOAD_ROOT/xmlparse-0.1.0.tar.gz

    This will result in output similar to the following:

        Request to install '/var/tmp/xmlparse-0.1.0.tar.gz'
        Extracting from tar archive /var/tmp/xmlparse-0.1.0.tar.gz
        Saving installer file to /home/weewx/bin/user/installer/xmlparse
        Saved configuration dictionary. Backup copy at /home/weewx/weewx.conf.20180828124410
        Finished installing extension '/var/tmp/xmlparse-0.1.0.tar.gz'

4.  Select the XML parse driver and do a basic driver configuration:

    $ sudo /home/weewx/bin/wee_config --reconfigure

    or

    $ sudo /usr/share/weewx/wee_config --reconfigure

5.  Edit weewx.conf and complete the required mappings in [XML] [[sensor_map]]
section. Refer to [Sensor maps] in the XML parse driver wiki for details on how
to enter sensor and unit maps. In additon, there are short form notes on the
sensor and unit maps in the comments at the start of the xmlparse.py file.

6.  Run WeeWX directly (http://weewx.com/docs/usersguide.htm#Running_directly)
and confirm that loop packets and archive records are being generated and the
data appears valid:

    $ sudo /home/weewx/bin/weewxd /home/weewx/weewx.conf

    or

    $ sudo /usr/share/weewx/weewxd /etc/weewx/weewx.conf

    Note: The above commands include the appropriate paths for default setup.py
          and package installs accordingly. If you have modified the WeeWX
          install locations it may be necessary to prefix weewxd and weewx.conf
          with different paths.

    You should now see something like below with a series of loop packets
    (indicated by LOOP: preceding each line) every poll_interval seconds and
    archive records (indicated by REC: preceding each line) every archive
    interval seconds:

        Some sample LOOP: and REC: output

    The above indicates that the XML file is being read, valid data is being
    extracted, loop packets are being emitted by the driver and WeeWX is
    constructing archive records from the accumulated loop data.

7.  If all appears correct when run directly you can stop WeeWX by entering
Ctl-Z in the terminal and you can now start WeeWX as a daemon:

    $ sudo /etc/init.d/weewx start

    or

    $ sudo service weewx start

    or

    $ sudo systemctl start weewx

8.  The WeeWX log should be monitored to verify archive records are being saved.

Manual installation

1.  Download the latest XML parse driver extension package from the XML parse
driver releases page (https://github.com/gjr80/weewx-xmlparse/releases) into a
directory accessible from the WeeWX machine.

    $ wget -P $DOWNLOAD_ROOT https://github.com/gjr80/weewx-xmlparse/releases/download/v0.1.0/xmlparse-0.1.0.tar.gz

    where *$DOWNLOAD_ROOT* is the path to the directory where the XML parse
    driver extension package is to be downloaded.

2.  Stop WeeWX:

    $ sudo /etc/init.d/weewx stop

    or

    $ sudo service weewx stop

    or

    $ sudo systemctl stop weewx

3.  Unpack the extension as follows:

    $ tar xvfz xmlparse-0.1.0.tar.gz

4.  Copy files from within the resulting directory as follows:

    $ cp xmlparse/bin/user/xmlparse.py /home/weewx/bin/user

    or

    $ cp xmlparse/bin/user/xmlparse.py /usr/share/weewx/user

5.  Select the XML parse driver and do a basic driver configuration:

    $ sudo /home/weewx/bin/wee_config --reconfigure

    or

    $ sudo /usr/share/weewx/wee_config --reconfigure

6.  Edit weewx.conf and complete the required mappings in [XML] [[sensor_map]]
section. Refer to [Sensor maps] in the XML parse driver wiki for details on how
to enter sensor and unit maps. In additon, there are short form notes on the
sensor and unit maps in the comments at the start of the xmlparse.py file.

7.  Run WeeWX directly (http://weewx.com/docs/usersguide.htm#Running_directly)
and confirm that loop packets and archive records are being generated and the
data appears valid:

    $ sudo /home/weewx/bin/weewxd /home/weewx/weewx.conf

    or

    $ sudo /usr/share/weewx/weewxd /etc/weewx/weewx.conf

    Note: The above commands include the appropriate paths for default setup.py
          and package installs accordingly. If you have modified the WeeWX
          install locations it may be necessary to prefix weewxd and weewx.conf
          with different paths.

    You should now see something like below with a series of loop packets
    (indicated by LOOP: preceding each line) every poll_interval seconds and
    archive records (indicated by REC: preceding each line) every archive
    interval seconds:

        Some sample LOOP: and REC: output

    The above indicates that the XML file is being read, valid data is being
    extracted, loop packets are being emitted by the driver and WeeWX is
    constructing archive records from the accumulated loop data.

8.  If all appears correct when run directly you can stop WeeWX by entering
Ctl-Z in the terminal and you can now start WeeWX as a daemon:

    $ sudo /etc/init.d/weewx start

    or

    $ sudo service weewx start

    or

    $ sudo systemctl start weewx

9.  The WeeWX log should be monitored to verify archive records are being saved.

Support

General support issues may be raised in the Google Groups weewx-user forum
(https://groups.google.com/group/weewx-user). Specific bugs in the XML parse
driver code should be the subject of a new issue raised via the XML parse
driver issues page (https://github.com/gjr80/weewx-xmlparse/issues).

Licensing

The XML parse driver is licensed under the GNU Public License v3
(https://github.com/gjr80/weewx-xmlparse/blob/master/LICENSE).







The Realtime gauge-data extension provides for near realtime updating of the
SteelSeries Weather Gauges by weeWX. The extension consists of a weeWX service
that generates the file gauge-data.txt used to update the SteelSeries Weather
Gauges.

Pre-Requisites

The Realtime gauge-data extension requires weeWX v3.4.0 or greater.

Installation Instructions

Installation using the wee_extension utility

Note:   Symbolic names are used below to refer to some file location on the
weeWX system. These symbolic names allow a common name to be used to refer to
a directory that may be different from system to system. The following symbolic
names are used below:

-   $DOWNLOAD_ROOT. The path to the directory containing the downloaded
    Realtime gauge-data extension.

-   $HTML_ROOT. The path to the directory where weeWX generated reports are
    saved. This directory is normally set in the [StdReport] section of
    weewx.conf. Refer to 'where to find things' in the weeWX User's Guide:
    http://weewx.com/docs/usersguide.htm#Where_to_find_things for further
    information.

-   $BIN_ROOT. The path to the directory where weeWX executables are located.
    This directory varies depending on weeWX installation method. Refer to
    'where to find things' in the weeWX User's Guide:
    http://weewx.com/docs/usersguide.htm#Where_to_find_things for further
    information.

-   $SKIN_ROOT. The path to the directory where weeWX skin folders are located.
    This directory is normally set in the [StdReport] section of
    weewx.conf. Refer to 'where to find things' in the weeWX User's Guide:
    http://weewx.com/docs/usersguide.htm#Where_to_find_things for further
    information.

1.  Download the latest Realtime gauge-data extension from the Realtime
gauge-data releases page (https://github.com/gjr80/weewx-realtime_gauge-data
/releases) into
a directory accessible from the weeWX machine.

    wget -P $DOWNLOAD_ROOT https://github.com/gjr80/weewx-realtime_gauge-data
/releases/download/v0.3.5/rtgd-0.3.5.tar.gz

	where $DOWNLOAD_ROOT is the path to the directory where the Realtime
    gauge-data extension is to be downloaded.

2.  Stop weeWX:

    sudo /etc/init.d/weewx stop

	or

    sudo service weewx stop

3.  Install the Realtime gauge-data extension downloaded at step 1 using the
wee_extension utility:

    wee_extension --install=$DOWNLOAD_ROOT/rtgd-0.3.5.tar.gz

    This will result in output similar to the following:

        Request to install '/var/tmp/rtgd-0.3.5.tar.gz'
        Extracting from tar archive /var/tmp/rtgd-0.3.5.tar.gz
        Saving installer file to /home/weewx/bin/user/installer/Rtgd
        Saved configuration dictionary. Backup copy at /home/weewx/weewx.conf.20161123124410
        Finished installing extension '/var/tmp/rtgd-0.3.5.tar.gz'

4. Start weeWX:

    sudo /etc/init.d/weewx start

	or

    sudo service weewx start

This will result in the gauge-data.txt file being generated on receipt of each
loop packet. A default installation will result in the generated gauge-data.txt
file being placed in the $HTML_ROOT directory. The Realtime gauge-data
extension installation can be further customized (eg file locations, frequency
of generation etc) by referring to the Realtime gauge-data extension wiki.

Manual installation

1.  Download the latest Realtime gauge-data extension from the Realtime
gauge-data releases page (https://github.com/gjr80/weewx-realtime_gauge-data
/releases) into
a directory accessible from the weeWX machine.

    wget -P $DOWNLOAD_ROOT https://github.com/gjr80/weewx-realtime_gauge-data
/releases/download/v0.3.5/rtgd-0.3.5.tar.gz

	where $DOWNLOAD_ROOT is the path to the directory where the Realtime
    gauge-data extension is to be downloaded.

2.  Unpack the extension as follows:

    tar xvfz rtgd-0.3.5.tar.gz

3.  Copy files from within the resulting folder as follows:

    cp rtgd/bin/user/rtgd.py $BIN_ROOT/user

	replacing the symbolic name $BIN_ROOT with the nominal locations for your
    installation.

4.  Edit weewx.conf:

    vi weewx.conf

5.  In weewx.conf, add a [RealtimeGaugeData] stanza as per the abbreviated
instructions for use in the comments at the start of $BIN_ROOT/user/rtgd.py.

6.  In weewx.conf, modify the [Engine] [[Services]] section by adding the
RealtimeGaugeData service to the list of process services to be run:

    [Engine]
        [[Services]]

            report_services = weewx.engine.StdPrint, weewx.engine.StdReport, user.rtgd.RealtimeGaugeData

7. Start weeWX:

    sudo /etc/init.d/weewx start

	or

    sudo service weewx start

This will result in the gauge-data.txt file being generated on receipt of each
loop packet. A default installation will result in the generated gauge-data.txt
file being placed in the $HTML_ROOT directory. The Realtime gauge-data
extension installation can be further customized (eg file locations, frequency
of generation etc) by referring to the Realtime gauge-data extension wiki.