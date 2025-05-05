import os
import subprocess
import serial
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = r'C:\Users\tmadz\OneDrive\Plocha\psshlf\gcode'
SLICER_PATH = r'C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe'

SERIAL_PORT = "COM3" 


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            raise Exception(f"Chyba při odesílání G-code na tiskárnu)")
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

        try:
            run_prusa_slicer(filepath)
        except Exception as e:
            return jsonify({'error': 'Failed to run PrusaSlicer'}), 500

        if not is_printer_connected():
            return jsonify({'error': 'Printer is not connected or unavailable'}), 400

        try:
            send_gcode_to_printer(filepath)
            return jsonify({'message': 'G-code sent to printer successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to send G-code to printer: {str(e)}'}), 500
        

    return jsonify({'error': 'Invalid file type. Only .gcode files are allowed.'}), 400




if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
