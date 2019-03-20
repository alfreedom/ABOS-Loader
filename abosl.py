# -*- coding: utf-8 -*-
"""
 ******************************************************************************
 *   file: abosl.py                                                           *
 *                                                                            *
 *	 ABOS Loader                                                                     *
 *                                                                            *
 *   This program is free software: you can redistribute it and/or modify     *
 *   it under the terms of the GNU General Public License as published by     *
 *   the Free Software Foundation, either version 3 of the License, or        *
 *   (at your option) any later version.                                      *
 *                                                                            *
 *   This program is distributed in the hope that it will be useful,          *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of           *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            *
 *   GNU General Public License for more details.                             *
 *                                                                            *
 *   You should have received a copy of the GNU General Public License        *
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>     *
 *                                                                            *
 *   Written by Alfredo Orozco <alfredoopa@gmail.com>                         *
 ******************************************************************************
"""
import sys, getopt
from abosloader import AbosLoader

ABOS_LOADER_VERSION = '1.3.0'

baud = 38400    # Default value defined in the avr abos bootloader

abos_loader = AbosLoader()

def main(argv):
  hexfile = ''
  port = ''
  verbose = False # Default verbose is to False
  baud = 38400    # Default value defined in the avr abos bootloader

  # Parsea las opciones de la linea de comandos
  try:
    opts, args = getopt.getopt(argv,"v?hp:b:",["port=", "baudrate=", "version", "verbose","help"])
  except getopt.GetoptError:
    showHelp()
    sys.exit(2)
   #############################################

  # Procesa los argumentos pasados a la aplicación.
  for opt, arg in opts:
    if opt in ("-?", "--help"):
      showHelp()
      sys.exit()
    elif opt in ("-v", "--version"):
      showVersion();
      sys.exit()
    elif opt in ("-p", "--port"):
      port = arg
    elif opt in ("-b", "--baudrate"):
      try:
        baud = int(arg)
      except:
        abosloader_msg(0, 'Invalid baudrate "%s".\nRun abosl -? to see help.' % arg)
        sys.exit()
    elif opt in ("--verbose"):
      verbose = True

  # Verifica que se hayan pasado el nombre del archivo hex y el puerto serial
  if port == '':
    abosloader_msg(0, '###  ABOS LOADER  ###\n')
    abosloader_msg(0, 'ERROR: serial port is not specified.\nRun abosl -? to see help.')
    sys.exit()

  if not args:
    abosloader_msg(0, '###  ABOS LOADER  ###\n')
    abosloader_msg(0, 'ERROR: hex file is not specified.\nRun abosl -? to see help.')
    sys.exit()

  # Si se especificó algo distinto envía el error
  if len(args) > 1:
    abosloader_msg(0, '###  ABOS LOADER  ###\n')
    abosloader_msg(0, 'Too many arguments')
    sys.exit()

  # Guarda el nombre del archivo .hex
  hexfile = args[0]
  showVersion();
  abosloader_msg(0, '')
  abosloader_msg(0, 'Loading "%s" file into AVR microcontroller\r\n' %(hexfile))

  msg_func = None
  if verbose:
  	msg_func = abosloader_msg

  # Ejecuta el programa cargador
  error = abos_loader.run(hexfile, port, baud, verbose, update_progress, msg_func)

  if error != 0:
  	print('¡Woops! :(\n')
  else:
  	print('\n¡Bye! :D\n')

  return 0

def abosloader_msg(code, message):
	if code != 0:
		print('{}\n'.format(message))
	else:
		print('{}'.format(message))


def update_progress(progress):
    barLength = 50 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "\r\n\r\nHalt...\r\n"
    if progress >= 1:
        progress = 1
    block = int(round(barLength*progress))
    text = "\rProgress: [{0}] {1}% {2}".format( "="*block + ">"+" "*(barLength-block), int(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()

''' 
	Muestra la ayuda del programa
'''
def showHelp():
  print('###  ABOS LOADER  ###\n')
  print('Opensource Loader for the ABOS Bootloader in AVR microcontrollers\n')
  print('Usage:')
  print('      abosl [options] HEXFILE\n')
  print('Options:')
  print('    -b, --baudrate=BAUDRATE      specify the serial baudrate (default %s)' % baud)
  print('    -p, --port=SERIAL_PORT       specify the serial port name')
  print('    -h, -?, --help               show this help message')
  print('    -v, --version                show the abosloader version')
  print('    --verbose                    show output verbose\n')
  print('Arguments:')
  print('    HEXFILE    Name of the hex file to load into AVR microcontroller\n\n')
  print('Written by Alfredo Orozco  <alfredoopa@gmail.com>')

'''
	Muestra la versión del programa
'''
def showVersion():
  print('###  ABOS LOADER  ###\n')
  print('Opensource Loader for the ABOS Bootloader in AVR microcontrollers')
  print('version: ' + ABOS_LOADER_VERSION)


'''
	Función main principal
'''
if __name__ == "__main__":
   main(sys.argv[1:])
