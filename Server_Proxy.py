# Abdulrahman Abu Alhussein 
import socket
import threading
import os
import hashlib

from urllib.parse import urlparse #need this to seperate the urls
from datetime import datetime #for time stamps

class ProxyServer:
    def __init__(self, host='localhost', port=8888):
        # Initializing server and cache direct
        self.host = host
        self.port = port
        self.cache_dir = './cache'
        self.cache_index = {}
        self.setup_cache()

    def setup_cache(self):
        # Makes sure vache folder is there if not creates one
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()

    def cache_path(self, cache_key):
        return os.path.join(self.cache_dir, cache_key)

    def cache_response(self, url, response):
      # this will save the respone 
        cache_key = self.cache_key(url)
        cache_path = self.cache_path(cache_key)
        try:
            with open(cache_path, 'wb') as f:
                f.write(response)
            self.cache_index[url] = {
                'key': cache_key,
                'timestamp': datetime.now(),
                'size': len(response)
            }
        except Exception:
            pass

    def get_cached_response(self, url):
        # retrives the saved response from earlier 
        if url in self.cache_index:
            cache_key = self.cache_index[url]['key']
            cache_path = self.cache_path(cache_key)
            try:
                with open(cache_path, 'rb') as f:
                    return f.read()
            except Exception:
                del self.cache_index[url] #fail safe just incase 
        return None

    def split_http(self, request):
        #seperates the link from the http (Readme.txt for why i decided to go this route)
        try:
            lines = request.split('\r\n')
            method, url = lines[0].split()[:2]
            hostname, path = None, "/"

            if url.startswith('http://'):
                parsed = urlparse(url)
                hostname, path = parsed.hostname, parsed.path or '/'
            else:
                # puts back the url and finds the hostname
                url = url.lstrip('/')
                hostname, path = url.split('/')[0], '/' + '/'.join(url.split('/')[1:])
                url = f"http://{url}"

            headers = {}
            for line in lines[1:]:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    headers[key.lower()] = value
            return method, url, hostname, path, headers
        except Exception:
            return None, None, None, None, None

    def forward_request(self, hostname, path, headers):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.settimeout(10)
                server_socket.connect((hostname, 80))
                request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n"
                request += ''.join(f"{k}: {v}\r\n" for k, v in headers.items() if k not in ['host', 'connection'])
                request += "\r\n"
                server_socket.sendall(request.encode())
                response = b""
                while (data := server_socket.recv(8192)):
                    response += data
                return response
        except Exception:
            return None

    def handle_client(self, client_socket, client_address):
        # handles the clients request 
        try:
            request_data = client_socket.recv(8192).decode()
            method, url, hostname, path, headers = self.split_http(request_data)

            if not all([method, url, hostname, path]) or method != 'GET':
                client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
                return
                 # Show what the proxy is connecting to
            print(f"Connecting to {hostname}")
            cached_response = self.get_cached_response(url)
            if cached_response:
                client_socket.sendall(cached_response)
            else:
                response = self.forward_request(hostname, path, headers)
                if response:
                    self.cache_response(url, response)
                    client_socket.sendall(response)
                else:
                    client_socket.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
        finally:
            client_socket.close()

    def start(self):
        #listens for any incoming connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            #shows what the proxy is listening on 
            print(f"Proxy server listening on {self.host}:{self.port}")
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()

if __name__ == "__main__":
    proxy = ProxyServer()
    proxy.start()
