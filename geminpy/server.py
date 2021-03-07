import socket
import ssl
import select
import time
from threading import Thread
from pathlib import Path

from .parser import parse_request
from .route import Route
import geminpy.response as response


class GeminiServer:

    def __init__(self, cert_file_path, cert_key_path, address='0.0.0.0', port=1965):
        self.address = address
        self.port = port

        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(Path(cert_file_path), Path(cert_key_path))

        self.routes = []

    def add_route(self, path, func):
        self.routes.append(Route(path, func))

    def remove_route(self, path):
        for r in self.routes:
            if r.path_matches(path):
                self.routes.remove(r)
                break

    def _route(self, req_path):
        for r in self.routes:
            if r.path_matches(req_path):
                return r
        return None

    def _serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setblocking(False)
            sock.bind((self.address, self.port))
            sock.listen(5)
            with self.ssl_context.wrap_socket(sock, server_side=True) as secure_socket:
                inputs = [secure_socket]
                outputs = []
                messages = {}

                while inputs:
                    readable, writable, exceptional = select.select(
                        inputs, outputs, inputs)
                    for s in readable:
                        if s is secure_socket:
                            connection, client_address = s.accept()
                            connection.setblocking(0)
                            inputs.append(connection)
                            messages[connection] = None
                        else:
                            data = s.recv(1026)
                            if data:
                                req = parse_request(data)
                                route = self._route(req.path)
                                if route:
                                    res = route.func(req)
                                else:
                                    res = response.Response(response.ResponseCodes.PERMANENT_FAILURE, "Not Found")
                                messages[s] = res.encode()
                                print(res.encode())
                                if s not in outputs:
                                    outputs.append(s)

                    for s in writable:
                        s.sendall(messages[s])
                        outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del messages[s]

                    for s in exceptional:
                        inputs.remove(s)
                        if s in outputs:
                            outputs.remove(s)
                        s.close()
                        del messages[s]

    def listen(self, block=True):
        t = Thread(target=self._serve, daemon=True)
        t.start()
        print(f"Geminpy listening on {self.address}:{self.port}")
        if block:
            while True:
                try:
                    time.sleep(2)
                except KeyboardInterrupt:
                    exit(0)
