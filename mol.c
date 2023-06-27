/*
CIS2750
Assignment 3
Cooper MacGregor
March 21,2023
*/

#include "mol.h"
#include <math.h>

//copies the values pointed to by element, x, y, and z into the atom stored at atom.
void atomset(atom *atom, char element[3], double *x, double *y, double *z) {
    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

//copies the values in the atom stored at atom to the locations pointed to by element, x, y, and z.
void atomget(atom *atom, char element[3], double *x, double *y, double *z) {
    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

//copies the values a1, a2 and epairs into the corresponding structure attributes in bond.
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
        bond->a1 = *a1;
        bond->a2 = *a2;
        bond->atoms = *atoms;
        bond->epairs = *epairs;
        compute_coords(bond);
}

//copies the structure attributes in bond to their corresponding arguments: a1, a2 and epairs.
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
        *a1 = bond->a1;
        *a2 = bond->a2;
        *atoms = bond->atoms;
        *epairs = bond->epairs;
}

//returns the address of a malloced area of memory, large enough to hold a molecule.
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max) {
    //malloc area large enough to hold a molecule
    molecule *mol = malloc(sizeof(molecule));
        if(mol == NULL) {
            return NULL;
        }
    mol->atom_max = atom_max;
    mol->atom_no = 0;
    //mallocs enough memory to hold atom_max atoms
    mol->atoms = malloc(sizeof(atom) * atom_max);
        if(mol->atoms == NULL) {
            return NULL;
        }
    //mallocs enough memory to hold the pointer to atom_max atoms
    mol->atom_ptrs = malloc(sizeof(atom*) * atom_max);
        if(mol->atom_ptrs == NULL) {
            return NULL;
        }
    
    mol->bond_max = bond_max;
    mol->bond_no = 0;
    //mallocs enough memory to hold bond_max bonds
    mol->bonds = malloc(sizeof(bond) * bond_max);
        if(mol->bonds == NULL) {
            return NULL;
        }
    //mallocs enough memory to hold the pointer to bond_max bonds
    mol->bond_ptrs = malloc(sizeof(bond*) * bond_max);
        if(mol->bond_ptrs == NULL) {
            return NULL;
        }
    return mol;
}

/*copies the data pointed to by atom to the first “empty” atom in atoms in 
the molecule pointed to by molecule, and set the first “empty” pointer 
in atom_ptrs to the same atom in the atoms array incrementing the value of atom_no.*/
void molappend_atom(molecule *molecule, atom *atom) {
    int i;
    //find first empty spot in the atom_ptrs array
    for (i = 0; i < molecule->atom_no; i++) {
        if (molecule->atom_ptrs[i] == NULL) {
            break;
        }
    }
    //if there is no empty spots in the array
    if(molecule->atom_no >= molecule->atom_max) {
        if(molecule->atom_max == 0)
            molecule->atom_max++;
        else {
            molecule->atom_max *= 2;
        }
        //reallocate memory for the increased size of the atoms and atom_ptrs array
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
            if(molecule->atoms == NULL) {
                printf("There was an error reallocating space for atoms.");
                exit(0);
            }
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom *) * molecule->atom_max);
            if(molecule->atom_ptrs == NULL) {
                printf("There was an error reallocating space for atom_ptrs.");
                exit(0);
            }
    }
    molecule->atoms[molecule->atom_no] = *atom;
    //point the pointers to the newly allocated addresses
    for(int i = 0; i < molecule->atom_max; i++) {
        molecule->atom_ptrs[i] = &(molecule->atoms[i]);
    }
    molecule->atom_no++;
}

//operates like that molappend_atom function, except for bonds.
void molappend_bond(molecule *molecule, bond *bond) {
    int i;
    //find first empty spot in the atom_ptrs array
    for (i = 0; i < molecule->bond_no; i++) {
        if (molecule->bond_ptrs[i] == NULL) {
            break;
        }
    }
    //if there is no empty spots in the array
    if(molecule->bond_no >= molecule->bond_max) {
        if(molecule->bond_max == 0)
            molecule->bond_max++;
        else {
            molecule->bond_max *= 2;
        }
        //reallocate memory for the increased size of the bonds and bond_ptrs array
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
            if(molecule->bonds == NULL) {
                printf("There was an error reallocating space for bonds.");
                exit(0);
            }
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond *) * molecule->bond_max);
        if(molecule->bond_ptrs == NULL) {
                printf("There was an error reallocating space for bond_ptrs.");
                exit(0);
            }
    }
    molecule->bonds[molecule->bond_no] = *bond;
    //point the pointers to the newly allocated addresses
    for(int i = 0; i < molecule->bond_max; i++) {
        molecule->bond_ptrs[i] = &(molecule->bonds[i]);
    }
    molecule->bond_no++;
}

//frees the memory associated with the molecule pointed to by ptr.
void molfree(molecule *ptr) {
    free(ptr->atom_ptrs);
    free(ptr->atoms);
    free(ptr->bond_ptrs);
    free(ptr->bonds);
    free(ptr);
}

molecule *molcopy(molecule *src) {
    // allocate memory for the new molecule using the src values
    molecule *mol_copy = molmalloc(src->atom_max, src->bond_max);
        if(mol_copy == NULL) {
            return NULL;
        }
    //copy atoms into the new molecule copy
    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom(mol_copy, &src->atoms[i]);
    }
    //copy bonds into the new molecule copy
    for (int i = 0; i < src->bond_no; i++) {
        molappend_bond(mol_copy, &src->bonds[i]);
    }
    //return the pointer to the copy
    return mol_copy;
}

//sorts the array of pointers to atoms based on the z-value
int cmp_atoms(const void *a, const void *b) {
    //create two pointers to pointers of atoms
    struct atom **a_ptr, **b_ptr;

    a_ptr = (struct atom **)a;
    b_ptr = (struct atom **)b;

    //compare the z values and return, if a>b return +, if a<b return -, if a=b return 0
    return (int)((*a_ptr)->z - (*b_ptr)->z);
}

//sorts the array of pointers to bonds, calculates the z value by taking the average z value from the 2 atoms within the bond
int cmp_bonds(const void *a, const void *b) {
    //create two pointers to pointers of bonds
    struct bond **a_ptr, **b_ptr;

    a_ptr = (struct bond **)a;
    b_ptr = (struct bond **)b;

    //compare the z values and return, if a>b return +, if a<b return -, if a=b return 0
    return (int)(*a_ptr)->z - (*b_ptr)->z;
}

/*sorts the atom_ptrs array in place in order of increasing z value.  
It should also sort the bond_ptrs array in place in order of increasing “z value”. 
Since bonds don’t have a z attribute, their z value is assumed to be the average 
z value of their two atoms.*/
void molsort(molecule *molecule) {
    //use qsort to sort the pointers, use the cmp_atoms and cmp_bonds to do that
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *), cmp_atoms);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *), cmp_bonds);
}

//returns an affine transformation matrix corresponding to a rotation of deg degrees around the x-axis.
void xrotation(xform_matrix xform_matrix, unsigned short deg) {
    //converts degrees to radians
    double radians = deg * PI / 180;

    //computes sin and cos of the angle
    double sin_x = sin(radians);
    double cos_x = cos(radians);

    //assigns the z rotation to the matrix
    xform_matrix[0][0] = 1; xform_matrix[0][1] = 0;     xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0; xform_matrix[1][1] = cos_x; xform_matrix[1][2] = -sin_x;
    xform_matrix[2][0] = 0; xform_matrix[2][1] = sin_x; xform_matrix[2][2] = cos_x;
}

//returns an affine transformation matrix corresponding to a rotation of deg degrees around the y-axis.
void yrotation(xform_matrix xform_matrix, unsigned short deg) {
    //converts degrees to radians
    double radians = deg * PI / 180;

    //computes sin and cos of the angle
    double sin_y = sin(radians);
    double cos_y = cos(radians);

    //assigns the z rotation to the matrix
    xform_matrix[0][0] = cos_y;  xform_matrix[0][1] = 0; xform_matrix[0][2] = sin_y;
    xform_matrix[1][0] = 0;      xform_matrix[1][1] = 1; xform_matrix[1][2] = 0;
    xform_matrix[2][0] = -sin_y; xform_matrix[2][1] = 0; xform_matrix[2][2] = cos_y;
}

//returns an affine transformation matrix corresponding to a rotation of deg degrees around the z-axis.
void zrotation(xform_matrix xform_matrix, unsigned short deg) {
    //converts degrees to radians
    double radians = deg * PI / 180;

    //computes sin and cos of the angle
    double sin_z = sin(radians);
    double cos_z = cos(radians);

    //assigns the z rotation to the matrix
    xform_matrix[0][0] = cos_z; xform_matrix[0][1] = -sin_z; xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin_z; xform_matrix[1][1] = cos_z;  xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;     xform_matrix[2][1] = 0;      xform_matrix[2][2] = 1;
}

////applies the transformation matrix to all the atoms of the molecule by performing a vector matrix multiplication on the x, y, z coordinates.
void mol_xform(molecule *molecule, xform_matrix matrix) {
    double x, y, z;
    //go through each atom in the molecule and apply the transformation matrix
    for (int i = 0; i < molecule->atom_no; i++) {
        x = matrix[0][0] * molecule->atoms[i].x + matrix[0][1] * molecule->atoms[i].y + matrix[0][2] * molecule->atoms[i].z;
        y = matrix[1][0] * molecule->atoms[i].x + matrix[1][1] * molecule->atoms[i].y + matrix[1][2] * molecule->atoms[i].z;
        z = matrix[2][0] * molecule->atoms[i].x + matrix[2][1] * molecule->atoms[i].y + matrix[2][2] * molecule->atoms[i].z;

        //update the current atom's x, y, and z coordinates
        molecule->atoms[i].x = x;
        molecule->atoms[i].y = y;
        molecule->atoms[i].z = z;
    }

    //apply compute_coords to each bond
    for (int i = 0; i < molecule->bond_no; i++) {
        compute_coords(&molecule->bonds[i]);
    }
}

void compute_coords(bond *bond) {
    double x1 = bond->atoms[bond->a1].x;
    bond->x1 = x1;
    double x2 = bond->atoms[bond->a2].x;
    bond->x2 = x2;
    double y1 = bond->atoms[bond->a1].y;
    bond->y1 = y1;
    double y2 = bond->atoms[bond->a2].y;
    bond->y2 = y2;
    double z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;
    bond->z = z;
    double len = sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1));
    bond->len = len;
    double dx = ((x2 - x1) / len);
    bond->dx = dx;
    double dy = ((y2 - y1) / len);
    bond->dy = dy;
}
