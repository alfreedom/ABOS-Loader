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

ABOS_LOADER_VERSION = '1.4.0'

baud = 38400    # Default value defined in the avr abos bootloader

abos_loader = AbosLoader()

def main(argv):
  hexfile = ''
  port = ''
  cpu_model = ''
  verbose = False # Default verbose is to False
  baud = 38400    # Default value defined in the avr abos bootloader

  # Parsea las opciones de la linea de comandos
  try:
    opts, args = getopt.getopt(argv,"v?hp:b:c:",["port=", "baudrate=","cpu=", "version", "verbose","help"])
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
    elif opt in ("-c", "--cpu"):
      cpu_model = arg
    elif opt in ("-b", "--baudrate"):
      try:
        baud = int(arg)
      except:
        abosloader_msg(0, 'Invalid baudrate "%s".\nRun abosl -? to see help.' % arg, True)
        sys.exit()
    elif opt in ("--verbose"):
      verbose = True

  if not args:
    abosloader_msg(0, '###  ABOS LOADER  ###\n', verbose=True)
    abosloader_msg(0, 'ERROR: hex file is not specified.\nRun abosl -? to see help.', verbose=True)
    sys.exit()

  # Si se especificó algo distinto envía el error
  if len(args) > 1:
    abosloader_msg(0, '###  ABOS LOADER  ###\n', verbose=True)
    abosloader_msg(0, 'Too many arguments', verbose=True)
    sys.exit()


  # Verifica que se hayan especificado el nombre del puerto serial
  if port == '':
    abosloader_msg(0, '###  ABOS LOADER  ###\n', verbose=True)
    abosloader_msg(0, 'ERROR: serial port is not specified.\nRun abosl -? to see help.', verbose=True)
    sys.exit()

  # Guarda el nombre del archivo .hex
  hexfile = args[0]
  showVersion();
  abosloader_msg(0, '', verbose=True)
  abosloader_msg(0, 'Loading "%s" file into AVR microcontroller\r\n' %(hexfile), verbose=True)

  # Ejecuta el programa cargador
  error = abos_loader.run(cpu_model, hexfile, port, baud, verbose, update_progress, abosloader_msg)

  if error != 0:
  	print('¡Woops! D:\n')
  else:
  	print('\n\n¡Done! ;)\n')

  return 0

def abosloader_msg(code, message, verbose):
	if code != 0:
		print('{}\n'.format(message))
	elif verbose:
		print('{}'.format(message))


def update_progress(progress):
    barLength = 60
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
  showVersion()
  print('\nUsage:')
  print('      abosl -c <CPU_MODEL> -p <SERIAL_PORT> [options] HEXFILE\n')
  print('Options:')
  print('    -b, --baudrate=BAUDRATE      Specify the serial baudrate (default %s)' % baud)
  print('    -p, --port=SERIAL_PORT       Specify the serial port name')
  print('    -h, -?, --help               Show this help message')
  print('    -v, --version                Show the abosloader version')
  print('    -c, --cpu=CPU_MODEL          Specify the CPU model.')
  print('')
  print('        Supported Models:')
  print('           - atmega128')
  print('           - atmega16')
  print('           - atmega32')
  print('')
  print('    --verbose                    Show output verbose\n')
  print('Arguments:')
  print('    HEXFILE    Path to the hex file to load into AVR microcontroller\n\n')
  print('Written by Alfredo Orozco  <alfredoopa@gmail.com>')

'''
	Muestra la versión del programa
'''
def showVersion():
  print('ABOS LOADER v{}'.format(ABOS_LOADER_VERSION))
  print('Opensource Loader for the ABOS Bootloader in AVR microcontrollers')



'''
	Función main principal
'''
if __name__ == "__main__":
   main(sys.argv[1:])
