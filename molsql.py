#CIS2750
#Assignment 3
#Cooper MacGregor
#March 21,2023

import molecule
import sqlite3
import os
from MolDisplay import Molecule, Atom, Bond
import MolDisplay

class Database:
    def __init__(self, reset=False):
        # If the database file already exists and reset is True, remove the file
        if os.path.exists("molecules.db") and reset:
            os.remove("molecules.db")

         # Create a connection to the database and a cursor object to execute SQL statements
        self.conn = sqlite3.connect("molecules.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # Create the Elements table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Elements (
            ELEMENT_ID INTEGER NOT NULL,
            ELEMENT_CODE VARCHAR(3) PRIMARY KEY NOT NULL,
            ELEMENT_NAME VARCHAR(32) NOT NULL,
            COLOUR1 CHAR(6) NOT NULL,
            COLOUR2 CHAR(6) NOT NULL,
            COLOUR3 CHAR(6) NOT NULL,
            RADIUS DECIMAL(3) NOT NULL
        )
    """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Atoms (
            ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ELEMENT_CODE VARCHAR(3) NOT NULL,
            X DECIMAL(7,4) NOT NULL,
            Y DECIMAL(7,4) NOT NULL,
            Z DECIMAL(7,4) NOT NULL,
            FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements (ELEMENT_CODE) 
        )
    """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Bonds (
            BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            A1 INTEGER NOT NULL,
            A2 INTEGER NOT NULL,
            EPAIRS INTEGER NOT NULL
        )
    """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Molecules (
            MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            NAME TEXT UNIQUE NOT NULL 
        )
    """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS MoleculeAtom (
            MOLECULE_ID INTEGER NOT NULL,
            ATOM_ID INTEGER NOT NULL,
            PRIMARY KEY (MOLECULE_ID, ATOM_ID),
            FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
            FOREIGN KEY (ATOM_ID) REFERENCES Atoms (ATOM_ID)
        )
    """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS MoleculeBond (
            MOLECULE_ID INTEGER NOT NULL,
            BOND_ID INTEGER NOT NULL,
            PRIMARY KEY (MOLECULE_ID, BOND_ID),
            FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
            FOREIGN KEY (BOND_ID) REFERENCES Bonds (ATOM_ID)
        )
    """)

    def __setitem__(self, table, values):
        # Insert values into the specified table
        placeholders = ",".join(["?"] * len(values))
        self.cursor.execute(f"INSERT INTO {table} VALUES ({placeholders})", values)
        self.conn.commit()

    def add_atom(self, molname, atom):
        # Insert a new atom into the Atoms table and link it to the specified molecule
        self.cursor.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)",
        (atom.element, atom.x, atom.y, atom.z))
        atom_id = self.cursor.lastrowid

        self.cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,))
        molecule_id = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)",
        (molecule_id, atom_id))

    def add_bond(self, molname, bond):
        self.cursor.execute("INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)", (bond.a1, bond.a2, bond.epairs))
        bond_id = self.cursor.lastrowid

        # Get the ID of the molecule with the given name
        self.cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,))
        molecule_id = self.cursor.fetchone()[0]

        # Associate the bond with the molecule by adding a row to the MoleculeBond table
        self.cursor.execute("INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?, ?)", (molecule_id, bond_id))

    def add_molecule(self, name, fp):
        molecule = Molecule()
        molecule.parse(fp)

        # Insert a new row into the Molecules table with the given name
        self.cursor.execute("INSERT INTO Molecules (NAME) VALUES (?)", (name,))

        # Add all of the atoms in the molecule to the database
        for i in range(molecule.atom_no):
            atom = molecule.get_atom(i)
            self.add_atom(name, atom)
        
        # Add all of the bonds in the molecule to the database
        for i in range(molecule.bond_no):
            bond = molecule.get_bond(i)
            self.add_bond(name, bond)
        
        # Commit the changes to the database
        self.conn.commit()

    def load_mol(self, name):
        # Fetch all of the atoms in the molecule with the given name, along with their associated element information
        db_query_atom = """
                    SELECT Atoms.*, Elements.*
                    FROM Molecules
                    JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                    JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
                    JOIN Elements ON Atoms.ELEMENT_CODE = Elements.ELEMENT_CODE
                    WHERE Molecules.NAME = ?
                    ORDER BY Atoms.ATOM_ID
                """
        atoms = self.cursor.execute(db_query_atom, (name,)).fetchall()
        molecule = Molecule()
        
        # Create an Atom object for each row in the result set and add it to the molecule
        for atom in atoms:
            element = (atom[1])
            x = (atom[2])
            y = (atom[3])
            z = (atom[4])
            molecule.append_atom(element, x, y, z)

        # Fetch all of the bonds in the molecule with the given name
        db_query_bond = """
                    SELECT Bonds.*
                    FROM Molecules
                    JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                    JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID
                    WHERE Molecules.NAME = ?
                    ORDER BY Bonds.BOND_ID
                """
        bonds = self.cursor.execute(db_query_bond, (name,)).fetchall()   
        
        # Create a Bond object for each row in the result set and add it to the molecule
        for bond in bonds:
            a1 = (bond[1])
            a2 = (bond[2])
            epairs = (bond[3])
            molecule.append_bond(a1, a2, epairs) 

        return molecule

    def radius(self):
        # select element code and radius from Elements table
        query = """
                SELECT ELEMENT_CODE, RADIUS FROM Elements
            """
        # execute query and fetch all results
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        
        # create a dictionary mapping element code to radius for each row in result
        return {row[0]: row[1] for row in result}

    def element_name(self):
        # select element code and element name from Elements table
        query = """
                SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements
            """
        # execute query and fetch all results
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        # create a dictionary mapping element code to element name for each row in result
        return {row[0]: row[1] for row in result}

    def radial_gradients(self):
        # select element name, color1, color2, and color3 from Elements table
        query = "SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements"

        # execute query and fetch all results
        results = self.cursor.execute(query).fetchall()
        radial_gradients = ""

        # iterate through each row in results and create an SVG radial gradient for each
        for result in results:
            radial_gradients += f"""
            <radialGradient id="{result[0]}" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">
                <stop offset="0%" stop-color="#{result[1]}"/> 
                <stop offset="50%" stop-color="#{result[2]}"/> 
                <stop offset="100%" stop-color="#{result[3]}"/>
            </radialGradient>
            """
        return radial_gradients
