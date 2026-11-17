import json
import uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

storage = Path("problems")
storage.mkdir(exist_ok=True)
template = Path(__file__).resolve().parent.parent / "templates/init.cc"

class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        data = json.loads(
            self.rfile.read(int(self.headers["Content-Length"]))
        )

        def folder_name(number):
            name = ""
            while number:
                number, remainder = divmod(number - 1, 26)
                name = chr(65 + remainder) + name
            return name

        number = 1
        while (storage / folder_name(number)).exists():
            number += 1

        folder = storage / folder_name(number)
        folder.mkdir()

        (folder / f"{folder.name.lower()}.cc").write_bytes(
            template.read_bytes()
        )

        for i, test in enumerate(data.get("tests", []), start=1):
            (folder / f"{i}.in").write_text(test["input"], encoding="utf-8")
            (folder / f"{i}.out").write_text(test["output"], encoding="utf-8")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Saved")
        print(f"Saved {data['name']} to {folder}")

HTTPServer(("localhost", 10043), Receiver).serve_forever()