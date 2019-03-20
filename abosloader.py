# -*- coding: utf-8 -*-

"""
 ******************************************************************************
 *   file: abosloader.py                                                      *
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
import sys
import intelhex 
import serial
import time


SYNC_COMMAND				= 0x16
ENTER_BOOTLOADER_COMMAND	= 0x0F
END_TRANSMISSION_COMMAND	= 0x04
ACK_COMMAND					= 0x06
NACK_COMMAND				= 0x15
CANCEL_BOOTLOADER_COMMAND	= 0x1B
PAGE_WRITE_COMMAND			= 0x02
CANCELATION_COMMAND			= 0x18

'''
	Ejecuta la rutina de carga del programa
'''
def Run(hexfile, port, baud, verbose, progress_func):
  
  ihex = intelhex.IntelHex()
  tries = 0
  maxtries = 5
  err_code = 0

  # Intenta leer e interpretar el archivo .hex
  if verbose:
    print 'Reading hex file "'+hexfile+'"...'
  try:
      ihex.fromfile(hexfile,format='hex')
  except (IOError, intelhex.IntelHexError):
      e = sys.exc_info()[1]
      return 1, ('Error 1: reading hex file: %s\n' % e)

  # Calcula el tamaño del archivo .hex
  program_size = len(ihex.tobinarray())
  if verbose:
    print '\r\nHex file size: %d bytes\r\n' % program_size

  if verbose:
    print 'Opening serial port...'

  # Intenta abrir el puerto serie.
  try:
    ser_port = serial.Serial(port, baud, timeout=.3)
  except serial.SerialException as e:
    return 2, ('Error 2: opening port %s\n' % port)

  if verbose:
    print('Restarting AVR via DTR pin...\r\n')

  # Reinicia el AVR conectado al puerto
  RestartAVR(ser_port)

  if verbose:
    print('Requesting MCU info...')
  # Envía el caracter de sincronización
  response = SendSync(ser_port, SYNC_COMMAND)

  # Si no responde con 8 bytes muestra error
  if len(response) != 8:
    return 3, ('Error 3: Communication error with the ABOS bootloader, responds with %d \n' % len(response))

  # Si no responde con ACK muestra error
  if response[0] != ACK_COMMAND:
    return 4, ('Error 4: The AVR bootloader not responds\n')

  # Guarda el tamaño de página de la respuesta en bytes
  page_size = response[2] << 8
  page_size |= response[1]

  # Guarda el espacio de memoria disponible para el programa en bytes
  flash_size = response[4] << 8
  flash_size |= response [3]
  flash_size *= 1024

  # Guarda la versión del Bootloader grabada en el micro
  abos_version = '%d.%d.%d' % (response[5], response[6], response[7])

  # Calcula el número de paginas a escribir.
  pages_to_write = program_size / page_size + (1 if program_size % page_size != 0 else 0)

  print('ABOS Version in microcontroller: %s' % abos_version)
  if verbose:
    print('Flash memory size: %d bytes (%d KB)' % (flash_size, flash_size/1024))
    print('Page size: %d bytes' % page_size)
    print('Pages to write: %d\r\n' % pages_to_write)
  
  cancel = False;
  if program_size > flash_size:
    exit = False
    print('The program is larger than the space available in the microcontroller.')
    while not exit:
      try:
        print('Do you want to load it anyway?')
        op = raw_input('[Yes/no]: ')
        if op == '':
          op = 'Y'
        op = op.upper();
        if op == 'Y' or op == 'YES':
          cancel = False;
          exit=True
        elif op == 'N' or op == 'NO':
          cancel = True
          exit=True
      except:
        cancel = True
        exit=True

  if cancel:
    # Envia comando ESC para cancelar la carga
    if verbose:
      print("\r\nSendig Cancel Bootloader Command...")
    cmd = bytearray([CANCEL_BOOTLOADER_COMMAND])
  else:
    # Envia comando ACK para entrar al modo bootlaoder.
    if verbose:
      print("\r\nSendig Enter Bootlader Command...")
    cmd = bytearray([ENTER_BOOTLOADER_COMMAND])

  try:
	ser_port.write(cmd)
	# Lee la respuesta de un byte = ACK
	response = bytearray(ser_port.read(1))
	if len(response) != 1 and response[0] != ACK_COMMAND:
  		return 5, ('\r\n\r\nError 5: The AVR bootloader not responds to Enter Bootloader command\r\n')
  except Exception as e:
  	return 6, ('\r\n\r\nError 6: The communication with the AVR was interrumped\r\n')

  if cancel:
    return;

  current_page = 0
  exit = False

  print('\r\nWriting %d bytes...' % program_size)

  # Obtiene el tiempo inicial para la carga del programa
  start = time.time()
  while not exit:

  	# Envía código STX para inicio de escritura de página
    if verbose:
      print("\r\nSendig Page Write Command...")

    cmd = bytearray([PAGE_WRITE_COMMAND])
    try:
    	ser_port.write(cmd)
    	# Lee la respuesta de un byte = ACK
    	esponse = bytearray(ser_port.read(1))
    	if len(response) != 1 and response[0] != ACK_COMMAND:
    		return 7, ('Error 7: The AVR bootloader not responds to start write page command\n')
    except Exception as e:
		return 8, ('\r\n\r\nError 8: The communication with the AVR was interrumped\n')
		return 1

    if verbose:
      print("Writing page %d of %d...\r\n" %(current_page+1, pages_to_write))
    
    # Actualiza el progreso de carga
    progress_func(((current_page+1)*1.0)/pages_to_write, verbose);

    # Obtiene la página a enviar
    data_to_send = bytearray(ihex.tobinarray(start = (current_page*page_size), size=page_size))
    
    try:
	    # Envía la página
	    ser_port.write(data_to_send)
    	# Lee la respuesta de un byte = ACK
	    response = bytearray(ser_port.read(1))
	    if len(response) != 1 and response[0] != ACK_COMMAND:
	      return 9, ('Error 9: The AVR bootloader not responds to end write page command\n')
    except Exception as e:
    	return 10, ('\r\n\r\nError 10: The communication with the AVR was interrumped\r\n')

    # Avanza a la siguiente página
    current_page += 1

    # Si ya envió todas las paginas sale del ciclo.
    if current_page == pages_to_write:
      exit = 1

  # Calcula el tiempo transcurrido de la carga
  elapsed = time.time() - start

  # Envia comando para finalizar escritura
  if verbose:
    print("\r\nSending End Transmission Command...")
  cmd = bytearray([END_TRANSMISSION_COMMAND])

  try:
    ser_port.write(cmd)
    # Lee la respuesta de un byte = ACK
    response = bytearray(ser_port.read(1))
    if len(response) != 1 and response[0] != ACK_COMMAND:
        return 11, ('\r\n\r\nError 11: The AVR bootloader not responds to finish program command\r\n')
  except Exception as e:
    return 12, ('\r\n\r\nError 12: The communication with the AVR was interrumped\r\n')

  # Muestra el tiempo de carga del programa
  return 0, ("\r\n\r\n¡Done! Program loaded in %.2f seconds\n" % elapsed)


'''
	Reinicia el micro mediante el pin DTR del puerto serie
'''
def RestartAVR(serial_port):
  serial_port.setDTR(False)
  serial_port.setDTR(True)
  serial_port.setDTR(False)

'''
	Envía el caracter de sincronización y devuelve la respuesta del bootloader.
'''
def SendSync(serial_port, cmd):
  maxtries = 5
  # Envía el caracter de sincronización maxtries veces
  cmd = bytearray([cmd])
  for item in range(maxtries):  
    serial_port.write(cmd)
    response = bytearray(serial_port.read(8))
    if len(response) == 8:
      break;

  return response