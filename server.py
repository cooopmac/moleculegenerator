import sys
import molsql
from urllib.parse import parse_qs
from urllib import parse
import MolDisplay
import cgi
import pprint
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class InvalidMoleculeError(Exception):
    pass

db = molsql.Database()
db.create_tables()
tables = db.cursor.fetchall()
num_tables = len(tables)
if num_tables == 0:
    db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
    db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
    db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
    db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );
public_files = ['/index.html', '/style.css', '/script.js']

class myServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in public_files:
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html", )

            fp = open(self.path[1:])
            webpage = fp.read()
            fp.close()

            self.send_header( "Content-length", len(webpage))
            self.end_headers()
            self.wfile.write(bytes(webpage, "utf-8"))

        elif self.path == '/get_element_table':
            db.cursor.execute('SELECT ELEMENT_NAME, ELEMENT_CODE, ELEMENT_ID FROM Elements')
            elements = [{'name': row[0], 'code': row[1], 'id': row[2]} for row in db.cursor.fetchall()]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(elements).encode())
        
        elif self.path == '/get_molecule':
            db.cursor.execute("SELECT NAME, MOLECULE_ID FROM Molecules")
            molecule_data = [{'name': record[0], 'id': record[1]} for record in db.cursor.fetchall()]
            
            for molecule in molecule_data:
                db.cursor.execute("SELECT COUNT(*) FROM MoleculeAtom WHERE MOLECULE_ID=?", (molecule['id'],))
                molecule['num_atoms'] = db.cursor.fetchone()[0]
                db.cursor.execute("SELECT COUNT(*) FROM MoleculeBond WHERE MOLECULE_ID=?", (molecule['id'],))
                molecule['num_bonds'] = db.cursor.fetchone()[0]

            response = {'molecules': molecule_data}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/display_molecule'):
            query_params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            print(query_params)
            molecule_name = query_params['name']

            print(molecule_name)

            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients()

            mol = db.load_mol(molecule_name)
            svg = mol.svg()
            print(svg)

            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            self.wfile.write(bytes(svg, "utf-8"))

        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) )
    
    def do_POST(self):
        if self.path == '/add_element':
          content_length = int(self.headers['Content-Length'])
          post_data = self.rfile.read(content_length).decode('utf-8')
          print(post_data)
          element_data = parse_qs(post_data)
          print(element_data)

          # Extract the element data from the POST request
          db['Elements'] = (element_data['element-number'][0],
                            element_data['element-code'][0],
                            element_data['element-name'][0],
                            element_data['element-color1'][0],
                            element_data['element-color2'][0],
                            element_data['element-color3'][0],
                            element_data['element-radius'][0])
          db.conn.commit()
          print_element = db.element_name()
          print(print_element)
          print_element_str = str(print_element)
          print(print_element_str)

          # Send a success response
          self.send_response(200)
          self.send_header('Content-type', 'text/plain')
          self.send_header('Refresh', '5;url=/index.html')
          self.end_headers()
          self.wfile.write(b'Element added successfully. Returning to home in 5 seconds...')
        
        elif self.path == '/remove_element':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            element_data = parse_qs(post_data)

            element_number = element_data['element-number-remove'][0]
            print(element_number)
            db.cursor.execute("DELETE FROM Elements WHERE ELEMENT_ID=?", (element_number,))
            db.conn.commit()

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Refresh', '5;url=/index.html')
            self.end_headers()
            self.wfile.write(b'Element removed successfully. Returning to home in 5 seconds...')

            print(db.element_name())
        
        elif self.path == '/upload_sdf':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            sdf_file = form['sdf_file'].file.read().decode('utf-8').split('\n')
            mol_name = form['mol_name'].value

            db.add_molecule(mol_name, sdf_file)
            db.conn.commit()

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Refresh', '5;url=/index.html')
            self.end_headers()
            self.wfile.write(f'SDF Uploaded successfully, {mol_name} added! Returning to home in 5 seconds...'.encode('utf-8'))

httpd = HTTPServer(('localhost', int(sys.argv[1])), myServer)
httpd.serve_forever()


