CC = clang
CFLAGS = -Wall -std=c99 -pedantic 

INCLUDE_PATH = /usr/include/python3.7m
PYTHON_LIB_PATH = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

all: _molecule.so

clean:
	rm -f *.o *.so A2 molecule.py molecule_wrap.c molecule_wrap.o _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fpic -o mol.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) -shared molecule_wrap.o -L. -lmol -L$(PYTHON_LIB_PATH) -lpython3.7m -o _molecule.so

molecule_wrap.c: molecule.i mol.h
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c  -I$(INCLUDE_PATH) -fpic -o molecule_wrap.o
