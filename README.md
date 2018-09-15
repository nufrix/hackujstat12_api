# Zeď hanby API
## Instalace
Vytoříme si virtuální environment:

```[nufrix@nufrix-thinkpad-t470p ~/Workspace/hackujstat12_api] ⑂master $ virtualenv -p python2.7 venv```
 
Napojíme se do něj:

```[nufrix@nufrix-thinkpad-t470p ~/Workspace/hackujstat12_api] ⑂master $ source venv/bin/activate```

A nainstalujeme si requirements:

```[nufrix@nufrix-thinkpad-t470p ~/Workspace/hackujstat12_api] (venv) ⑂master $ pip install -r requirements.txt```

Pak už jen stačí spustit API:

```
[nufrix@nufrix-thinkpad-t470p ~/Workspace/hackujstat12_api] (venv) ⑂master $ python app.py 
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 222-051-826
 ...
```