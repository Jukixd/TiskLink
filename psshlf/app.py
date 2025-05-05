import os
import subprocess
import serial
from flask import Flask, request, render_template, jsonify, redirect

app = Flask(__name__)

UPLOAD_FOLDER = r'C:\Users\tmadz\OneDrive\Plocha\psshlf\gcode'
SLICER_PATH = r'C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe'
SERIAL_PORT = "COM3"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


print_queue = []

def is_printer_connected():
    try:
        ser = serial.Serial(SERIAL_PORT, timeout=1)
        ser.close()
        return True
    except serial.SerialException:
        print(f"Tiskarna není připojená")
        return False

def run_prusa_slicer(filepath):
    try:
        print(f"Spouštím PrusaSlicer s G-code: {filepath}")
        process = subprocess.Popen([SLICER_PATH, filepath])
        process.communicate() 
        if process.returncode != 0:
            raise Exception(f"PrusaSlicer se nepodařilo spustit (kód chyby: {process.returncode})")
    except Exception as e:
        raise Exception(f'Error while running slicer: {e}')

def send_gcode_to_printer(filepath):
    try:
        print(f"Odesílám G-code {filepath} na tiskárnu...")
        process = subprocess.run([SLICER_PATH, '--send-to-printer', filepath], check=True)
        if process.returncode != 0:
            raise Exception(f"Chyba při odesílání G-code na tiskárnu")
        print("G-code byl úspěšně odeslán na tiskárnu.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Selhalo odeslání G-code na tiskárnu")

@app.route('/')
def index():
    return render_template('Main.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.gcode'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        
        print_queue.append({
            'filename': file.filename,
            'filepath': filepath,
            'status': 'waiting'  
        })

        return jsonify({'message': 'File uploaded and added to the queue.'}), 200

    return jsonify({'error': 'Invalid file type. Only .gcode files are allowed.'}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            return redirect('/panel')
        else:
            return render_template('login.html', error='Špatné přihlašovací údaje.')
    return render_template('login.html')

@app.route('/panel')
def panel():
    return render_template('panel.html', print_queue=print_queue)

@app.route('/confirm_print/<int:index>', methods=['POST'])
def confirm_print(index):
    try:
        job = print_queue[index]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], job['filename'])

        if not is_printer_connected():
            run_prusa_slicer(filepath)
            return jsonify({'error': 'Tiskárna není připojena. G-code byl otevřen v PrusaSliceru, požadavek zůstává čekající.'}), 400

        send_gcode_to_printer(filepath)
        job['status'] = 'confirmed'
        return jsonify({'message': 'Tisk byl potvrzen a G-code byl odeslán na tiskárnu.'})

    except IndexError:
        return jsonify({'error': 'Neplatný index požadavku'}), 404
    except Exception as e:
        return jsonify({'error': f'Chyba: {str(e)}'}), 500

@app.route('/cancel_print/<int:job_index>', methods=['POST'])
def cancel_print(job_index):
    job = print_queue[job_index]
    if job['status'] == 'waiting':
        job['status'] = 'cancelled'
        return jsonify({'message': 'Požadavek byl zrušen.'})
    return jsonify({'error': 'Požadavek již byl zpracován.'}), 400


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
