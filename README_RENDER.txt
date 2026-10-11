MECHMEMORY — RENDER DEPLOYMENT

1. Upload these project files to a GitHub repository (keep app.py, requirements.txt, render.yaml, templates/ and wokwi_sketch.ino).
2. On https://render.com, create a new Web Service and connect that GitHub repository.
3. Render should detect render.yaml. If configuring manually: Runtime Python; Build Command: pip install -r requirements.txt; Start Command: gunicorn app:app.
4. Deploy. Open the Render service URL and confirm the dashboard loads. Test https://YOUR-RENDER-SERVICE.onrender.com/api/latest in the browser; it should return JSON saying no readings received yet until Wokwi sends data.
5. In Wokwi sketch.ino, set API_BASE_URL to your exact Render HTTPS URL, without a trailing slash. Save and run the simulation. Check Serial Monitor for HTTP 201.

NOTE: The included SQLite database is suitable for a demo, but on a typical Render free web service local files may not persist across restarts/redeploys. For a lasting deployment, use a managed database or persistent disk.
