MECHMEMORY LIVE-CONNECTED DASHBOARD
===================================

WHAT THIS DOES
- Serves the dashboard at http://127.0.0.1:5000
- Embeds your Wokwi project:
  https://wokwi.com/projects/477576199813596161
- Receives ESP32 JSON readings at POST /api/readings
- Stores readings and maintenance records in SQLite
- Refreshes dashboard data every 2 seconds

PART A — RUN THE DASHBOARD LOCALLY (Windows)
1. Extract this ZIP to a folder such as Desktop\MechMemory_Live_Connected.
2. Open Command Prompt in that folder.
3. Run:
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
4. Open http://127.0.0.1:5000 in Chrome.
5. Leave the terminal running.

PART B — MAKE THE API REACHABLE FROM WOKWI
Wokwi cloud simulation cannot normally reach your computer's 127.0.0.1 directly.
For a student demo, create a temporary HTTPS tunnel to port 5000 using a tunnel provider
such as ngrok (install and sign in using the provider's official instructions).
Then run the tunnel command, typically:
   ngrok http 5000
Copy the HTTPS forwarding URL shown by the tunnel, e.g. https://YOUR-SUBDOMAIN.ngrok-free.app
Do not include /api/readings in the base URL variable below; the sketch appends it.
Keep both Flask and the tunnel running. A temporary tunnel URL may change when restarted.
Do not expose private or sensitive data through a public tunnel.

PART C — UPDATE THE WOKWI SKETCH
In your Wokwi project, replace sketch.ino with the code in wokwi_sketch.ino.
Before starting simulation, replace YOUR_NGROK_HTTPS_URL with the actual HTTPS URL from
your tunnel provider, e.g. https://example.ngrok-free.app (no trailing slash).
Keep the circuit pins consistent:
- Potentiometer SIG: GPIO 34 and GPIO 35
- Green LED: GPIO 18 through resistor
- Red LED: GPIO 19 through resistor
- Potentiometers VCC: 3V3; GNDs and LED cathodes: common GND

PART D — TEST
1. Start Flask and the HTTPS tunnel.
2. Open dashboard at http://127.0.0.1:5000.
3. In Wokwi, start the simulation.
4. Turn a potentiometer so temperature > 70 or vibration > 7.
5. Dashboard should update within about 2 seconds. Check the Flask terminal for lines such as:
   MCH-001: T=..., V=..., ANOMALY

TROUBLESHOOTING
- Dashboard says API NOT CONNECTED: make sure Flask is running and open the dashboard through
  http://127.0.0.1:5000, not by double-clicking the HTML file.
- Wokwi data does not arrive: verify the tunnel URL in the sketch, that it is HTTPS, and that
  the tunnel and Flask are running.
- Check the Wokwi Serial Monitor for HTTP response codes. 201 means a reading was accepted.
- If your tunnel provider displays a browser warning/interstitial for requests, use a provider/
  configuration that supports direct HTTPS API requests.
- Do not paste your tunnel URL into public posts if you do not want others to access the demo.

NOTE
The dashboard and SQLite DB are local. The public tunnel only forwards requests from Wokwi to
your local Flask server. This is a prototype, not a production-secure industrial monitoring system.
