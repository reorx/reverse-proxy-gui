#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import sys
import requests
import threading


hostname = '127.0.0.1:32767'


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def set_header():
    headers = {
        'Host': hostname
    }

    return headers


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        sent = False
        try:

            url = 'http://{}{}'.format(hostname, self.path)
            req_header = self.parse_headers()

            print(req_header)
            print(url)
            resp = requests.get(url, headers=merge_two_dicts(req_header, set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            self.finish()
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def do_POST(self, body=True):
        sent = False
        try:
            url = 'https://{}{}'.format(hostname, self.path)
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            req_header = self.parse_headers()

            resp = requests.post(url, data=post_body, headers=merge_two_dicts(req_header, set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            self.finish()
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def parse_headers(self):
        req_header = {}
        for line in self.headers:
            line_parts = [o.strip() for o in line.split(':', 1)]
            if len(line_parts) == 2:
                req_header[line_parts[0]] = line_parts[1]
        return req_header

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        print('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                print(key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(resp.content))
        self.end_headers()


def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Proxy HTTP requests')
    parser.add_argument('--port', dest='port', type=int, default=9999,
                        help='serve HTTP requests on specified port (default: random)')
    args = parser.parse_args(argv)
    return args


class ServerProcess:
    def __init__(self, address):
        self.address = address

    def run(self):
        self.server = HTTPServer(self.address, ProxyHTTPRequestHandler)
        print(f'http server is running as reverse proxy {self.address}')
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            pass
        finally:
            # Clean-up server (close socket, etc.)
            print('server.server_close()')
            self.server.server_close()

    def start(self):
        self.p = threading.Thread(name='http server', target=self.run)
        self.p.start()

    def stop(self):
        print('server.shutdown')
        self.server.shutdown()
        print('p.join')
        self.p.join()


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    server = ServerProcess(('0.0.0.0', args.port))
    server.run()


if __name__ == '__main__':
    main()
