import json
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from starter.runtime import Ollama

class RuntimeTest(unittest.TestCase):
    def test_http_contract_and_json_validation(self):
        received=[]
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received.append((self.path,json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                self.send_response(200); self.end_headers()
                self.wfile.write(json.dumps({'message':{'content':'{"answer":"hello"}'}}).encode())
            def log_message(self,*args): pass
        with HTTPServer(('127.0.0.1',0),Handler) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            try: self.assertEqual(Ollama('sample',port=server.server_port)([{'role':'user','content':'hi'}],2),{'answer':'hello'})
            finally: server.shutdown(); thread.join()
        self.assertEqual(received[0][0],'/api/chat')
        self.assertFalse(received[0][1]['stream'])
        self.assertEqual(received[0][1]['format'],'json')

    def test_cli_offline_agent_and_qa(self):
        for command in [('agent','--question','stock notebook'),('qa','--question','returns')]:
            run=subprocess.run([sys.executable,'-m','starter',*command,'--offline','--lang','en'],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertIn('OFFLINE FIXTURE',run.stderr)
            self.assertIn('12' if command[0]=='agent' else '[policy.txt]',run.stdout)

class DeadlineTest(unittest.TestCase):
    def assert_trickle_times_out(self, phase):
        import time
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                try:
                    if phase=='headers':
                        self.wfile.write(b'HTTP/1.1 200 OK\r\nX-Slow: ')
                        self.wfile.flush()
                        for _ in range(12):
                            self.wfile.write(b'x'); self.wfile.flush(); time.sleep(.03)
                        self.wfile.write(b'\r\nConnection: close\r\n\r\n{}')
                    else:
                        time.sleep(.09)
                        self.wfile.write(b'HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n')
                        for char in b'{"message": {"content": "{}"}}':
                            self.wfile.write(bytes([char])); self.wfile.flush(); time.sleep(.09)
                except (BrokenPipeError, ConnectionResetError): pass
            def log_message(self,*args): pass
        with HTTPServer(('127.0.0.1',0),Handler) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            try:
                started=time.monotonic()
                with self.assertRaises(TimeoutError): Ollama('sample',port=server.server_port)([],.1)
                self.assertLess(time.monotonic()-started,.15 if phase=='body' else .25)
            finally: server.shutdown(); thread.join()

    def test_trickled_headers_cannot_extend_total_deadline(self):
        self.assert_trickle_times_out('headers')

    def test_connection_close_body_cannot_extend_total_deadline(self):
        self.assert_trickle_times_out('body')
