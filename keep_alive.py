import threading
import time
import requests
import os

def keep_alive():
    port = os.environ.get('PORT', '8080')
    url = 'http://0.0.0.0:' + port
    while True:
        time.sleep(280)
        try:
            requests.get(url, timeout=10)
            print("Ping enviado - servidor ativo!")
        except:
            pass

t = threading.Thread(target=keep_alive, daemon=True)
t.start()

