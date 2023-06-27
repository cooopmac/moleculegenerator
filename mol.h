/*
CIS2750
Assignment 3
Cooper MacGregor
March 21,2023
*/

#ifndef _mol_h
#define _mol_h
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define PI 3.14159265359

//atom defines a structure that describes an atom and its position in 3-dimensional space.
//element is a null-terminated string representing the element name of the atom.
//x, y, and z are double precision floating point numbers describing the position in Angstroms (Å) of the atom relative to a common origin for a molecule.
typedef struct atom
{
  char element[3];
  double x, y, z;
} atom;

//bond defines a structure that represents a co-valent bond between two atoms.
//a1 and a2 are pointers to the two atoms in the co-valent bond.
//epairs is the number of electron pairs in the bond
typedef struct bond
{
  unsigned short a1, a2;
  unsigned char epairs;
  atom *atoms;
  double x1, x2, y1, y2, z, len, dx, dy; 
} bond;

//molecule represents a molecule which consists of zero or more atoms, and zero or more bonds.
//atom_max is a non-negative integer that records the dimensionality of an array pointed to by atoms.
//atom_no is the number of atoms currently stored in the array atoms.
//bond_max is a non-negative integer that records the dimensionality of an array pointed to by bonds
//bond_no is the number of bonds currently stored in the array bonds.
//atom_ptrs and bond_ptrs are arrays of pointers. Their dimensionalities will correspond to the atoms and bonds arrays, respectively.
typedef struct molecule
{
    unsigned short atom_max, atom_no; 
    atom *atoms, **atom_ptrs; 
    unsigned short bond_max, bond_no; 
    bond *bonds, **bond_ptrs;
} molecule;

//xform_matrix reprents a 3-d affine transformation matrix (an extension of the 2-d affine transformation you saw in the first lab).
typedef double xform_matrix[3][3];

typedef struct mx_wrapper
{
  xform_matrix xform_matrix;
} mx_wrapper;

//copies the values pointed to by element, x, y, and z into the atom stored at atom.
void atomset( atom *atom, char element[3], double *x, double *y, double *z);

//copies the values in the atom stored at atom to the locations pointed to by element, x, y, and z.
void atomget( atom *atom, char element[3], double *x, double *y, double *z);

//copies the values a1, a2 and epairs into the corresponding structure attributes in bond.
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs);

//copies the structure attributes in bond to their corresponding arguments: a1, a2 and epairs.
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs);

//returns the address of a malloced area of memory, large enough to hold a molecule.
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max );

//returns the address of a malloced area of memory, large enough to hold a molecule.
molecule *molcopy( molecule *src );

//frees the memory associated with the molecule pointed to by ptr.
void molfree( molecule *ptr );

/*copies the data pointed to by atom to the first “empty” atom in atoms in 
the molecule pointed to by molecule, and set the first “empty” pointer 
in atom_ptrs to the same atom in the atoms array incrementing the value of atom_no.*/
void molappend_atom( molecule *molecule, atom *atom );

//operates like that molappend_atom function, except for bonds.
void molappend_bond( molecule *molecule, bond *bond );

/*sorts the atom_ptrs array in place in order of increasing z value.  
It should also sort the bond_ptrs array in place in order of increasing “z value”. 
Since bonds don’t havea z attribute, their z value is assumed to be the average 
z value of their two atoms.*/
void molsort( molecule *molecule );

//allocates, computes, and returns an affine transformation matrix corresponding to a rotation of deg degrees around the x-axis.
void xrotation( xform_matrix xform_matrix, unsigned short deg );

//allocates, computes, and returns an affine transformation matrix corresponding to a rotation of deg degrees around the y-axis.
void yrotation( xform_matrix xform_matrix, unsigned short deg );

//allocates, computes, and returns an affine transformation matrix corresponding to a rotation of deg degrees around the z-axis.
void zrotation( xform_matrix xform_matrix, unsigned short deg );

//applies the transformation matrix to all the atoms of the molecule by performing a vector matrix multiplication on the x, y, z coordinates.
void mol_xform( molecule *molecule, xform_matrix matrix );

void compute_coords(bond *bond);

#endif
