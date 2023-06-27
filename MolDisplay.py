#CIS2750
#Assignment 3
#Cooper MacGregor
#March 21,2023


import molecule

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""
offsetx = 500
offsety = 500

class Atom:
    def __init__(self, c_atom):
        # Initialize an Atom object with a c_atom parameter
        self.c_atom = c_atom
        self.z = c_atom.z
    
    def __str__(self):
        # Return a string representation of the Atom object
        return f"Atom: element={self.c_atom.element}, x={self.c_atom.x}, y={self.c_atom.y}, z={self.c_atom.z}"

    def svg(self):
        # Calculate the coordinates and radius of the circle in SVG format
        cx = self.c_atom.x * 100.0 + offsetx
        cy = self.c_atom.y * 100.0 + offsety
        rad = radius[self.c_atom.element]
        fill = element_name[self.c_atom.element]
        # Return the SVG string for the circle
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (cx, cy, rad, fill)

class Bond:
    def __init__(self, c_bond):
        self.c_bond = c_bond
        self.z = c_bond.z

    def __str__(self):
        # Return a string representation of Bond instance.
        return f"Bond: z={self.z}, len={self.c_bond.len}, dx={self.c_bond.dx}, dy={self.c_bond.dy}, a1={self.c_bond.a1}, a2={self.c_bond.a2}, epairs={self.c_bond.epairs}"

    def svg(self):
        x1_center = self.c_bond.x1 * 100 + offsetx
        x2_center = self.c_bond.x2 * 100 + offsetx
        y1_center = self.c_bond.y1 * 100 + offsety
        y2_center = self.c_bond.y2 * 100 + offsety

        # Define the coordinates of the polygon using the bond's dx and dy attributes
        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (x1_center - self.c_bond.dy * 10, y1_center + self.c_bond.dx * 10, x1_center + self.c_bond.dy * 10,
        y1_center - self.c_bond.dx * 10, x2_center + self.c_bond.dy * 10, y2_center - self.c_bond.dx * 10, x2_center - self.c_bond.dy * 10, y2_center + self.c_bond.dx * 10)

class Molecule(molecule.molecule):
    # Return a string representation of Molecule instance.
    def __str__(self):
        atom_str = ""
        for i in range(self.atom_no):
            atom = self.get_atom(i)
            atom_str += f"Atom {i}: {atom.element}, {atom.x}, {atom.y}, {atom.z}\n"
        bond_str = ""
        for i in range(self.bond_no):
            bond = self.get_bond(i)
            bond_str += f"Bond {i}: {bond.a1} {bond.a2} {bond.epairs}\n"
        return f"{atom_str}\n{bond_str}"
    
    def svg(self):
        # Convert Molecule instance to an SVG image and return as a string.
        # Sort atoms and bonds by z coordinate.
        atoms = [Atom(self.get_atom(i)) for i in range(self.atom_no)]
        bonds = [Bond(self.get_bond(i)) for i in range(self.bond_no)]
        atoms.sort(key=lambda atom: atom.z) # Sort atoms by z coordinate
        bonds.sort(key=lambda bond: bond.z) # Sort atoms by z coordinate
        svg_coordinates = []
        while atoms and bonds:
            a1 = atoms[0]
            b1 = bonds[0]
            if a1.z < b1.z:
                svg_coordinates.append(a1.svg()) # Add atom to svg_coordinates
                atoms.pop(0)  # Remove atom from atoms
            else: # b1.z < a1.z
                svg_coordinates.append(b1.svg()) # Add bond to svg_coordinates
                bonds.pop(0)  # Remove bond from bonds
        svg_coordinates += [atom.svg() for atom in atoms] # Add remaining atoms to svg_coordinates
        svg_coordinates += [bond.svg() for bond in bonds]
        return header + "\n" + "".join(svg_coordinates) + footer # Return SVG string
    
    def parse(self, file):
        file_str = "\n".join(file) # Convert file list to string
        lines = file_str.split("\n") # Split file string into lines
        num_atoms, num_bonds = map(int, lines[3].strip().split()[:2])

        # Parse atoms from file and add to molecule
        for i in range(num_atoms):
            line = lines[i+4]
            x = float(line[:10].strip())
            y = float(line[10:20].strip())
            z = float(line[20:30].strip())
            element = line[31:33].strip()
            self.append_atom(element, x, y, z)
        
        # Parse bonds from file and add to molecule
        for i in range(4+num_atoms, 4+num_atoms+num_bonds):
            line = lines[i].strip()
            bond1 = int(line[:2].strip())
            bond2 = int(line[2:5].strip())  
            epairs = int(line[5:8].strip())
            self.append_bond(bond1-1, bond2-1, epairs)


        


        



    



        

    
        

