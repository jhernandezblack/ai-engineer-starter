"""Bounded loopback-only Ollama transport. No credentials or SDK required."""
import http.client
import json
import socket
import time

class DeadlineSocket(socket.socket):
    """Keep the same deadline even when HTTPResponse owns the socket file.

    socket.makefile() uses recv_into, including while parsing HTTP headers.
    Updating this socket itself avoids relying on HTTPConnection.sock, which
    becomes None for Connection: close responses.
    """
    def __init__(self, deadline):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.deadline=deadline

    def remaining(self):
        remaining=self.deadline-time.monotonic()
        if remaining<=0: raise TimeoutError('Model deadline exceeded')
        self.settimeout(remaining)

    def connect(self, address):
        self.remaining()
        return super().connect(address)

    def sendall(self, data, flags=0):
        self.remaining()
        return super().sendall(data, flags)

    def recv_into(self, buffer, nbytes=0, flags=0):
        self.remaining()
        return super().recv_into(buffer, nbytes, flags)

class Ollama:
    def __init__(self, model='qwen3:4b', port=11434):
        self.model=model
        self.port=port

    def __call__(self, messages, timeout):
        deadline=time.monotonic()+timeout
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=timeout)
        body=json.dumps({'model':self.model,'messages':messages,'format':'json','stream':False,'think':False,'options':{'temperature':0,'num_predict':512,'num_ctx':4096}})
        response=None
        sock=DeadlineSocket(deadline)
        conn.sock=sock
        try:
            sock.connect(('127.0.0.1',self.port))
            conn.request('POST','/api/chat',body,{'Content-Type':'application/json'})
            response=conn.getresponse()
            if response.status!=200: raise ValueError('Ollama HTTP error: '+str(response.status))
            chunks=[]; size=0
            while True:
                remaining=deadline-time.monotonic()
                if remaining<=0: raise TimeoutError('Model deadline exceeded')
                chunk=response.read1(min(4096,65537-size))
                if not chunk: break
                size+=len(chunk)
                if size>65536: raise ValueError('Model response too large')
                chunks.append(chunk)
            result=json.loads(b''.join(chunks))
            return json.loads(result['message']['content'])
        finally:
            if response is not None: response.close()
            conn.close()
            sock.close()
