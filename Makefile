##############################################################################
#   file: Makefile                                                           #
#                                                                            #
#	  ABOS Loader                                                          #
#                                                                            #
#   This program is free software: you can redistribute it and/or modify     #
#   it under the terms of the GNU General Public License as published by     #
#   the Free Software Foundation, either version 3 of the License, or        #
#   (at your option) any later version.                                      #
#                                                                            #
#   This program is distributed in the hope that it will be useful,          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#   GNU General Public License for more details.                             #
#                                                                            #
#   You should have received a copy of the GNU General Public License        #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>     #
#                                                                            #
#   Written by Alfredo Orozco <alfredoopa@gmail.com>                         #
##############################################################################

all: abosl.py abosloader.py
	python2 -m compileall abosloader.py abosl.py
	echo 'python2 /opt/abosloader/abosl.pyc "$$@"' > abosl
	chmod +x abosl

install: all abosl abosloader.pyc
	pip2 install intelhex pyserial
	mkdir -p /opt/abosloader
	cp abosl /opt/abosloader
	cp abosl.pyc /opt/abosloader
	cp abosloader.pyc /opt/abosloader
	ln -sf /opt/abosloader/abosl /usr/local/bin/abosl

uninstall: 
	rm -Rf /opt/abosloader
	
clean:
	rm -Rf abosl abosl.pyc abosloader.pyc
