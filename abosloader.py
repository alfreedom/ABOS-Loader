# -*- coding: utf-8 -*-

"""
 ******************************************************************************
 *   file: abosloader.py                                                      *
 *                                                                            *
 *   ABOS Loader                                                                     *
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


SYNC_COMMAND                = 0x16
ENTER_BOOTLOADER_COMMAND    = 0x0F
END_TRANSMISSION_COMMAND    = 0x04
ACK_COMMAND                 = 0x06
NACK_COMMAND                = 0x15
CANCEL_BOOTLOADER_COMMAND   = 0x1B
PAGE_WRITE_COMMAND          = 0x02
CANCELATION_COMMAND         = 0x18

class AbosLoader:
    '''
        Clase para manejar el cargador Abos Loader para el bootloader ABOS
        de los microcontroladores AVR.
    '''
    def __init__(self):
        self.hexfile = intelhex.IntelHex()
        pass

    # Algoritmo principal para manejar la lógica de carga de un programa con el bootloader ABOS
    def run(self, hexfile, port, baud, verbose, progress_func=None, messages_func=None):
        self.filename = hexfile
        self.progress_func = progress_func
        self.messages_func = messages_func

        # Lee el archivo hexadecimal
        self.__send_message(code=0, message = 'Reading hex file {}...'.format(self.filename))
        error = self.__read_hexfile()
        if error:
            return 1 
         # Calcula el tamaño del archivo .hex
        program_size = len(self.hexfile.tobinarray())

        # Abre el puerto serial
        self.__send_message(code=0, message='Opening Serial Port...')
        error = self.__open_serial_port(port=port, baudrate=baud)
        if error:
            return 1

        # Reinicia el micro AVR con el pin DTR
        self.__send_message(code=0, message='Restarting AVR via DTR pin...')
        self.__restart_avr()

        # Envía caracter de sincronización y obtiene la respuesta desde el micro AVR
        self.__send_message(code=0, message='Requesting MCU info...')
        response, error = self.__send_sync()
        if error:
            return 1

        # Calcula el número de paginas a escribir.
        self.pages_to_write = program_size // response['page_size'] + (1 if program_size % response['page_size'] != 0 else 0)
        self.page_size = response['page_size']
        self.__send_message(code=0, message='Hex file size: %d bytes' % program_size)
        self.__send_message(code=0, message='ABOS Version in AVR: %s' % response['abos_version'])
        self.__send_message(code=0, message='AVR memory size: %d bytes (%d KB)' % (response['flash_size'], response['flash_size']/1024))
        self.__send_message(code=0, message='AVR Page size: %d bytes' % response['page_size'])
        self.__send_message(code=0, message='Pages to write: %d' % self.pages_to_write)

        # Verifica que el tamaño del programa no sea mayor que el espacio disponible en el micro
        if program_size > response['flash_size']:
            self.__send_message(code=5, message='Error 5: The program is larger than the space available in the microcontroller.')
            self.__cancel_bootloader_mode()
            return 1

        # Envía comando para entrar en modo bootloader
        self.__send_message(code=0, message="Sendig Enter Bootlader Command...")
        error = self.__enter_bootloader_mode()
        if error:
            return;

        # Envía los datos del programa al bootloader
        self.__send_message(code=0, message='Writing %d bytes...' % program_size)
        start = time.time()
        error = self.__write_program()
        if error:
            return 1
        # Calcula el tiempo transcurrido de la carga
        elapsed = time.time() - start

        # Envia comando para finalizar escritura
        self.__send_message(code=0, message="Sending End Transmission Command...")
        error = self.__send_end_transmission_command()
        if error:
            return 1

        # Muestra el tiempo de carga del programa
        self.__send_message(code=0, message="¡Done! Program loaded in %.2f seconds" % elapsed)

        return 0


    def __send_message(self, code=0, message=''):
        if self.messages_func is not None:
            self.messages_func(code=code, message=message)


    def __read_hexfile(self):
        
        # Intenta leer e interpretar el archivo .hex
        try:
                self.hexfile.fromfile(self.filename,format='hex')
        except (IOError, intelhex.IntelHexError):
                e = sys.exc_info()[1]
                self.__send_message(code=1, message='Error 1: reading hex file: "%s"' % e)
                return None, True

        return False


    def __open_serial_port(self, port, baudrate):
        # Intenta abrir el puerto serie.
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=.3)
        except serial.SerialException as e:
            self.__send_message(code=2, message='Error 2: opening port %s' % self.port)
            return True

        return False


    def __restart_avr(self):
        self.serial_port.setDTR(False)
        time.sleep(.3)
        self.serial_port.setDTR(True)
        self.serial_port.setDTR(False)


    def __send_sync(self):
        maxtries = 5
        # Envía el caracter de sincronización maxtries veces
        cmd = bytearray([SYNC_COMMAND])
        for item in range(maxtries):  
            self.serial_port.write(cmd)
            response = bytearray(self.serial_port.read(8))
            if len(response) == 8:
                break;

        # Si no responde con 8 bytes muestra error
        if len(response) != 8:
            self.__send_message(code=3, message='Error 3: Communication error with the ABOS bootloader, responds with %d' % len(response))
            return None, True

        # Si no responde con ACK muestra error
        if response[0] != ACK_COMMAND:
            self.__send_message(code=4, message='Error 4: The AVR bootloader not responds')
            return None, True

        # Guarda el tamaño de página de la respuesta en bytes
        ret = {}
        ret['page_size'] = response[2] << 8
        ret['page_size'] |= response[1]

        # Guarda el espacio de memoria disponible para el programa en bytes
        ret['flash_size'] = response[4] << 8
        ret['flash_size'] |= response [3]
        ret['flash_size'] *= 1024

        # Guarda la versión del Bootloader grabada en el micro
        ret['abos_version'] = '%d.%d.%d' % (response[5], response[6], response[7])

        return ret, False


    def __enter_bootloader_mode(self):
        cmd = bytearray([ENTER_BOOTLOADER_COMMAND])

        try:
            self.serial_port.write(cmd)
            # Lee la respuesta de un byte = ACK
            response = bytearray(self.serial_port.read(1))
            if len(response) != 1 and response[0] != ACK_COMMAND:
                self.__send_message(code=6, message='Error 6: The AVR bootloader not responds to Enter Bootloader command')
                return True
        except Exception as e:
            self.__send_message(code=7, message='Error 7: The communication with the AVR was interrumped')
            return True

        return False


    def __cancel_bootloader_mode(self):
        cmd = bytearray([CANCEL_BOOTLOADER_COMMAND])

        try:
            self.serial_port.write(cmd)
            # Lee la respuesta de un byte = ACK
            response = bytearray(self.serial_port.read(1))
            if len(response) != 1 and response[0] != ACK_COMMAND:
                self.__send_message(code=6, message='Error 8: The AVR bootloader not responds to Cancel Bootloader command')
                return True
        except Exception as e:
            self.__send_message(code=7, message='Error 9: The communication with the AVR was interrumped')
            return True

        return False


    def __write_program(self):
        current_page = 0
        exit = False

        # Obtiene el tiempo inicial para la carga del programa
        while not exit:

            # Envía código STX para inicio de escritura de página
            self.__send_message(code=0, message="Sendig Page Write Command...")

            error = self.__send_page_write_command()
            if error:
                return True

            self.__send_message(code=0, message="Writing page %d of %d..." %(current_page+1, self.pages_to_write))
            
            # Actualiza el progreso de carga
            if self.progress_func is not None:
                self.progress_func(((current_page+1)*1.0)/self.pages_to_write);

            # Obtiene la página a enviar
            data_to_send = bytearray(self.hexfile.tobinarray(start = (current_page*self.page_size), size=self.page_size))
            
            try:
                # Envía la página
                self.serial_port.write(data_to_send)
                # Lee la respuesta de un byte = ACK
                response = bytearray(self.serial_port.read(1))
                if len(response) != 1 and response[0] != ACK_COMMAND:
                    self.__send_message(code=12, message='Error 12: The AVR bootloader not responds to end write page command')
                    return True
            except Exception as e:
                self.__send_message(code=13, message='Error 13: The communication with the AVR was interrumped')
                return True

            # Avanza a la siguiente página
            current_page += 1
            # Si ya envió todas las paginas sale del ciclo.
            if current_page == self.pages_to_write:
                exit = True

        return False


    def __send_page_write_command(self):
        cmd = bytearray([PAGE_WRITE_COMMAND])
        try:
            self.serial_port.write(cmd)
            # Lee la respuesta de un byte = ACK
            response = bytearray(self.serial_port.read(1))
            if len(response) != 1 and response[0] != ACK_COMMAND:
                self.__send_message(code=10, message='Error 10: The AVR bootloader not responds to start write page command')
                return True
        except Exception as e:
            self.__send_message(code=11, message='Error 11: The communication with the AVR was interrumped')
            return True

        return False


    def __send_end_transmission_command(self):
        
        cmd = bytearray([END_TRANSMISSION_COMMAND])

        try:
            self.serial_port.write(cmd)
            # Lee la respuesta de un byte = ACK
            response = bytearray(self.serial_port.read(1))
            if len(response) != 1 and response[0] != ACK_COMMAND:
                self.__send_message(code=14, message='Error 14: The AVR bootloader not responds to finish program command')
                return True
        except Exception as e:
            self.__send_message(code=15, message='Error 15: The communication with the AVR was interrumped')
            return True

        return False
