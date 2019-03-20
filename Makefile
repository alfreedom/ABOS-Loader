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



install:  abosl abosl.pyc abosloader.pyc
	mkdir -p /opt/abosloader
	cp abosl /opt/abosloader
	cp abosl.pyc /opt/abosloader
	cp abosloader.pyc /opt/abosloader
	ln -sf /opt/abosloader/abosl /usr/local/bin/abosl

uninstall: 
	rm -Rf /opt/abosloader
	
clean:
	rm -rf __pycache__/
	rm -Rf abosl abosl.pyc abosloader.pyc

python2: clean abosl.py, abosliader.py
	python2 -m compileall abosloader.py abosl.py 
	rm -rf __pycache__/
	echo 'python2 /opt/abosloader/abosl.pyc "$$@"' > abosl
	chmod +x abosl
	pip2 install intelhex pyserial

python3: clean abosl.py abosloader.py
	python3 -m compileall abosloader.py abosl.py 
	mv __pycache__/abosl.cpython* ./abosl.pyc
	mv __pycache__/abosloader.cpython* ./abosloader.pyc
	rm -rf __pycache__/
	echo 'python3 /opt/abosloader/abosl.pyc "$$@"' > abosl
	chmod +x abosl
	pip3 install intelhex pyserial
