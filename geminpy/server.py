import ssl
from pathlib import Path
import asyncio

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

    def __route(self, req_path):
        for r in self.routes:
            if r.path_matches(req_path):
                return r
        return None

    async def __handle_client(self, reader, writer):
        data = await reader.read(1026)
        req = parse_request(data)

        route = self.__route(req.path)
        if isinstance(route, Route):
            res = route.func(req)
        else:
            res = response.Response(response.ResponseCodes.PERMANENT_FAILURE, "Not Found")

        writer.write(res.encode())
        await writer.drain()
        writer.close()

    def listen(self):
        loop = asyncio.get_event_loop()
        co_ro = asyncio.start_server(self.__handle_client, self.address, self.port, loop=loop, ssl=self.ssl_context)
        server = loop.run_until_complete(co_ro)
        print(f"Geminpy listening on {server.sockets[0].getsockname()}")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
