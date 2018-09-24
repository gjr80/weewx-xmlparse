# XML parse driver #

A [WeeWX](http://weewx.com/ "WeeWX - Open source software for your weather station") driver to read data from an XML file.

## Description ##

The *XML parse driver* extension allows WeeWX to poll an XML format file for data. The driver maps data from XML elements and attributes to WeeWX loop packet fields and emits loop packets at a user configurable rate.

## Pre-Requisites ##

The *XML parse driver* extension requires:

-   WeeWX v3.0.0 or greater

## Installation ##

The *XML parse driver* extension can be installed manually or automatically using the [*wee_extension* utility](http://weewx.com/docs/utilities.htm#wee_extension_utility). The preferred method of installation is through the use of *wee_extension*.

**Note:** Symbolic names are used below to refer to some file location on the WeeWX system. These symbolic names allow a common name to be used to refer to a directory that may be different from system to system. The following symbolic names are used below:

-   *$DOWNLOAD_ROOT*. The path to the directory containing the downloaded *XML parse driver* extension.
-   *$BIN_ROOT*. The path to the directory where WeeWX executables are located. This directory varies depending on WeeWX installation method. Refer to [where to find things](http://weewx.com/docs/usersguide.htm#Where_to_find_things "where to find things") in the [WeeWX User's Guide](http://weewx.com/docs/usersguide.htm "User's Guide to the WeeWX Weather System") for further information.

### Installation using the wee_extension utility ###

1.  Download the latest *XML parse driver* extension from the *XML parse driver* extension [releases page](https://github.com/gjr80/weewx-xmlparse/releases) into a directory accessible from the WeeWX machine.

        $ wget -P $DOWNLOAD_ROOT https://github.com/gjr80/weewx-xmlparse/releases/download/v0.1.0/xmlparse-0.1.0.tar.gz

    where *$DOWNLOAD_ROOT* is the path to the directory where the *XML parse driver* extension is to be downloaded.

1.  Stop WeeWX:

        $ sudo /etc/init.d/weewx stop

    or

        $ sudo service weewx stop

    or

        $ sudo systemctl stop weewx

3.  Install the *XML parse driver* extension downloaded at step 1 using the *wee_extension* utility:

        $ wee_extension --install=$DOWNLOAD_ROOT/xmlparse-0.1.0.tar.gz

    This will result in output similar to the following:

        Request to install '/var/tmp/xmlparse-0.1.0.tar.gz'
        Extracting from tar archive /var/tmp/xmlparse-0.1.0.tar.gz
        Saving installer file to /home/weewx/bin/user/installer/xmlparse
        Saved configuration dictionary. Backup copy at /home/weewx/weewx.conf.20180828124410
        Finished installing extension '/var/tmp/xmlparse-0.1.0.tar.gz'

1.  Select the *XML parse driver* and do a basic driver configuration:

        $ sudo /home/weewx/bin/wee_config --reconfigure

    or

        $ sudo /usr/share/weewx/wee_config --reconfigure

1.  Edit *weewx.conf* and complete the required mappings in *[XML]* *[[sensor_map]]* section. Refer to [Sensor maps]() in the *XML parse driver* wiki for details on how to enter sensor and unit maps. In additon, there are short form notes on the sensor and unit maps in the comments at the start of the *xmlparse.py* file.

1.  [Run WeeWX directly](http://weewx.com/docs/usersguide.htm#Running_directly) and confirm that loop packets and archive records are being generated and the data is appears valid:

        $ sudo /home/weewx/bin/weewxd /home/weewx/weewx.conf

    or

        $ sudo /usr/share/weewx/weewxd /etc/weewx/weewx.conf

    **Note:** The above commands include the appropriate paths for a default *setup.py* and package WeeWX installs accordingly. If you have modified the WeeWX install locations it may be necessary to prefix *weewxd* and *weewx.conf* with different paths.

    You should now see something like below with a series of loop packets (indicated by *LOOP:* preceding each line) every *poll_interval* seconds and archive records (indicated by *REC:* preceding each line) every archive interval seconds:

        Some sample LOOP: and REC: output

    The above indicates that the XML file is being read, valid data is being extracted, loop packets are being emitted by the driver and WeeWX is constructing archive records from the accumulated loop data.

1.  If all appears correct when run directly you can stop WeeWX by entering *Ctl-Z* in the terminal and you can now start WeeWX as a daemon:

        $ sudo /etc/init.d/weewx start

    or

        $ sudo service weewx start

    or

        $ sudo systemctl start weewx

1.  The WeeWX log should be monitored to verify archive records are being saved.

### Manual installation ###

1.  Download the latest *XML parse driver* extension from the *XML parse driver* extension [releases page](https://github.com/gjr80/weewx-xmlparse/releases) into a directory accessible from the WeeWX machine.

        $ wget -P $DOWNLOAD_ROOT https://github.com/gjr80/weewx-xmlparse/releases/download/v0.1.0/xmlparse-0.1.0.tar.gz

    where *$DOWNLOAD_ROOT* is the path to the directory where the *XML parse driver* extension is to be downloaded.

1.  Stop WeeWX:

        $ sudo /etc/init.d/weewx stop

    or

        $ sudo service weewx stop

    or

        $ sudo systemctl stop weewx

1.  Unpack the extension as follows:

        $ tar xvfz xmlparse-0.1.0.tar.gz

1.  Copy files from within the resulting directory as follows:

        $ cp xmlparse/bin/user/xmlparse.py /home/weewx/bin/user

    or

        $ cp xmlparse/bin/user/xmlparse.py /usr/share/weewx/user

1.  Select the *XML parse driver* and do a basic driver configuration:

        $ sudo /home/weewx/bin/wee_config --reconfigure

    or

        $ sudo /usr/share/weewx/wee_config --reconfigure

1.  Edit *weewx.conf* and complete the required mappings in *[XML]* *[[sensor_map]]* section. Refer to [Sensor maps]() in the *XML parse driver* wiki for details on how to enter sensor and unit maps. In additon, there are short form notes on the sensor and unit maps in the comments at the start of the *xmlparse.py* file.

1.  [Run WeeWX directly](http://weewx.com/docs/usersguide.htm#Running_directly) and confirm that loop packets and archive records are being generated and the data is appears valid:

        $ sudo /home/weewx/bin/weewxd /home/weewx/weewx.conf

    or

        $ sudo /usr/share/weewx/weewxd /etc/weewx/weewx.conf

    **Note:** The above commands include the appropriate paths for a default *setup.py* and package WeeWX installs accordingly. If you have modified the WeeWX install locations it may be necessary to prefix *weewxd* and *weewx.conf* with different paths.

    You should now see something like below with a series of loop packets (indicated by *LOOP:* preceding each line) every *poll_interval* seconds and archive records (indicated by *REC:* preceding each line) every archive interval seconds:

        Some sample LOOP: and REC: output

    The above indicates that the XML file is being read, valid data is being extracted, loop packets are being emitted by the driver and WeeWX is constructing archive records from the accumulated loop data.

1.  If all appears correct when run directly you can stop WeeWX by entering *Ctl-Z* in the terminal and you can now start WeeWX as a daemon:

        $ sudo /etc/init.d/weewx start

    or

        $ sudo service weewx start

    or

        $ sudo systemctl start weewx

1.  The WeeWX log should be monitored to verify archive records are being saved.

## Support ##

General support issues may be raised in the Google Groups [weewx-user forum](https://groups.google.com/group/weewx-user) . Specific bugs in the *XML parse driver* extension code should be the subject of a new issue raised via the [*XML parse driver* extension issues page](https://github.com/gjr80/weewx-xmlparse/issues).

## Licensing ##

The *XML parse driver* extension is licensed under the [GNU Public License v3](https://github.com/gjr80/weewx-xmlparse/blob/master/LICENSE).
