
# ABOS Loader

The ABOS Loader is a python script that communicates with a serial port and send a 
program in hex format to an AVR microcontroller with ABOS Bootloader.

## Installation

To install ABOS loader run the next commands in a terminal.

    git clone https://github.com/alfreedom/abosloader
    cd abosloader
    make
    sudo make install

The default installatin path is "/opt/abosloader/".
The installation creates a symbolic link in "/usr/local/bin" with **_abosl_**.

## Usage

    abosl [options] HEXFILE

### Options:
    -b, --baudrate=BAUDRATE      Specify the serial baudrate (default 38400)
    -p, --port=SERIAL_PORT       Specify the serial port name
    -h, -?, --help               Show help
    -v, --version                Show the abosloader version
    --verbose                    Show output verbose

### Arguments:
    HEXFILE Name of the hex file to load

### Example
With default baudrate (**_38400_**):

    abosl -p /dev/ttyUSB0 myProgram.hex

Specifying other baudrate:

    abosl --port=/dev/ttyUSB0 --baudrate=19200 myProgram.hex
or

    abosl -p /dev/ttyUSB0 -b 19200 myProgram.hex
## Installation
ABOS Loader require python2, between pyserial and intelhex libraries.
Be shure that you have python2 and pip2 in the system path.

    pip2 install pyserial intelhex
    cd abosloader
    make all
    sudo make install

This will generate the abos.pyc, abosloader.pyc and abosl files, also install
the program in **_/opt/abosloader/_** path.

To tes the istallation run:

    abosl -?

## Supported Platforms
  * Linux
  * MacOS
---