
TISKOVÝ PANEL – NASTAVENÍ A SPUŠTĚNÍ
====================================

Tento projekt umožňuje odesílat G-code soubory na tiskárnu přes webové rozhraní.
Tisk probíhá po schválení požadavku přes administrátorský panel.

POŽADAVKY:
----------
- Python 3.8+
- Flask (web server)
- PrusaSlicer nainstalovaný na PC
- Připojená tiskárna (USB / síť)
- Windows (cesty ve skriptu odpovídají Windows)

CO JE POTŘEBA NASTAVIT:
------------------------
1. CESTA K PRUSASLICERU:
   - Otevři main.py a uprav:
     SLICER_PATH = r'C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe'

2. SLOŽKA PRO UKLÁDÁNÍ G-CODE:
   - Otevři main.py a uprav:
     UPLOAD_FOLDER = r'C:\cesta\kam\se\ukladaji\soubory'

3. COM PORT TISKÁRNY:
   - Např. SERIAL_PORT = "COM3" (přizpůsob svému systému)

4. AKTIVACE ODESLÁNÍ DO TISKÁRNY:
   - V PrusaSliceru: Nastavení tiskárny > Obecné > Upload G-code do tiskárny

SPUŠTĚNÍ SERVERU:
-----------------
1. Spusť:
   python main.py

2. Otevři v prohlížeči:
   http://localhost:5000

FUNKCE:
-------
- Uživatel nahraje .gcode soubor
- Požadavek čeká na schválení
- Admin může potvrdit (soubor se odešle na tiskárnu) nebo zrušit
- Pokud selže připojení k tiskárně, zobrazí se upozornění a požadavek zůstává čekající

STRUKTURA PROJEKTU:
--------------------
projekt/
├── main.py
├── templates/
│   └── Main.html
├── static/
│   └── styles.css
├── gcode/
└── readme.txt (tento soubor)

TIPY:
-----
- Pokud se Slicer nespouští → zkontroluj správnost cesty
- Pokud tiskárna nepřijímá soubor → otestuj ručně přes Slicer
- Flask nainstaluj pomocí: pip install flask
