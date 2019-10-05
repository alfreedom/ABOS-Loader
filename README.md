
# ABOS Loader

The ABOS Loader is a python script that communicates with a serial port and send a 
program in hex format to an AVR microcontroller with ABOS Bootloader.

## Installation

ABOS Loader require python >=2.6 or python>=3.6, together the pyserial and intelhex libraries.
Be shure that you have python2 and pip2 or python3 and pip3 in the system path.

To install ABOS loader run the next commands in a terminal:

    git clone https://github.com/alfreedom/abosloader
    cd abosloader

### Linux 

For python2:

    make python2
    sudo make install

For python3:

    make python3
    sudo make install


For default system python installation:

    make python
    sudo make install

### MacOS

For python2:

    make python2-osx
    sudo make install

For python3:

    make python3-osx
    sudo make install


For default system python installation:

    make python-osx
    sudo make install

### Windows

For windows (need python and gnu make executable in system path):

    make windows

This will generate the abos.pyc, abosloader.pyc and abosl files, also install
the program in the default installation path: **_/opt/abosloader/_**.
Also, the installation creates a symbolic link in "/usr/local/bin" with **_abosl_**.

If the windows target was run, generate a abosloader.exe into the windows folder, this is stand
alone executable, and it's recommended to add it to the system path.

To tes the istallation run:

    abosl -?

## Usage

    abosl [options] HEXFILE

### Options:
    -b, --baudrate=BAUDRATE      Specify the serial baudrate (default 38400)
    -p, --port=SERIAL_PORT       Specify the serial port name
    -h, -?, --help               Show help
    -v, --version                Show the abosloader version
    --verbose                    Show output verbose

### Arguments:
    HEXFILE: Path to the hex file to load into the avr

### Example
With default baudrate (**_38400_**):

    abosl -p /dev/ttyUSB0 myProgram.hex

Specifying other baudrate:

    abosl --port=/dev/ttyUSB0 --baudrate=19200 myProgram.hex
or

    abosl -p /dev/ttyUSB0 -b 19200 myProgram.hex


For windows, the serial por names become like COM3, COM4, COM5, and so.

## Supported Platforms

|  OS     | Supported |
|---------|:---------:|
|  Linux  | Yes       |
|  MacOS  | Yes       |
| Windows | Yes       |