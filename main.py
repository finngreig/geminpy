from geminpy.server import GeminiServer
import geminpy.response as response

if __name__ == '__main__':
    s = GeminiServer('./cert.pem', './key.pem', '127.0.0.1')
    s.add_route('/', lambda x: response.Response(response.ResponseCodes.SUCCESS, 'text/plain', 'Hello'))
    s.add_route('/world', lambda x: response.Response(response.ResponseCodes.SUCCESS, 'text/plain', 'World'))
    s.listen()
