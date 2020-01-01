# ABOS Loader Changelog


## [ 1.4.0 ] - 31/12/2019

### Added
- Update the CPU info request for new abos bootloader firmware version, now shows the cpu model.

## [ 1.3.0 ] - 05/10/2019

### Added
- Add Makefile targets to support installation on MacOS: 
    make python-osx 
    make python2-osx 
    make python3-osx 
    make install-osx

## [ 1.3.0 ] - 19/08/2019

### Added
- Add standalong executable for windows.
- Add makefile target for default python version installed in the operating system (works on windows).

## [ 1.3.0 ] - 20/03/2019

### Added
- Add support for python>=3.6.
- Add AbosLoader class for better integration.
- Add a message callback and progress callback to the bootloader class.

### Changed
- The progress callback function is managed by the main program.

## [ 1.0.0 ] - 10/11/2018

Add first version of ABOS Loader


[1.3.0]: https://github.com/alfreedom/ABOS-Loader/releases/tag/v1.3.0
[1.0.0]: https://github.com/alfreedom/ABOS-Loader/releases/tag/v1.0.0