import socket
import os
import hashlib

#criar uma chave de cache baseada na URL
def generate_cache_key(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()

#armazenar conteúdo no cache
def cache_content(key, content):
    with open(f'cache/{key}', 'wb') as cache_file:
        cache_file.write(content)

#recuperar conteúdo do cache
def get_cached_content(key):
    cache_path = f'cache/{key}'
    if os.path.isfile(cache_path):
        with open(cache_path, 'rb') as cache_file:
            return cache_file.read()
    return None

#lidar com solicitações do cliente
def handle_request(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    print(f"Requisição recebida:\n{request}")

    lines = request.splitlines()
    if len(lines) == 0:
        client_socket.close()
        return
    
    first_line = lines[0]
    method, url, _ = first_line.split()
    if method != 'GET':
        response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()
        return

    # Extrai o host e o caminho do URL
    if "://" in url:
        protocol, url = url.split("://", 1)
    if "/" in url:
        host, path = url.split("/", 1)
        path = "/" + path
    else:
        host = url
        path = "/"

    cache_key = generate_cache_key(url)

    # Verifica se a resposta está no cache
    cached_response = get_cached_content(cache_key)
    if cached_response:
        print("Servindo do cache.")
        client_socket.sendall(cached_response)
        client_socket.close()
        return

    # Encaminha a solicitação para o servidor remoto
    try:
        print(f"Conectando-se ao servidor remoto: {host}")
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((host, 80))
        remote_socket.sendall(f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode('utf-8'))
        
        response = b""
        while True:
            data = remote_socket.recv(4096)
            if not data:
                break
            response += data
        remote_socket.close()

        cache_content(cache_key, response)

        client_socket.sendall(response)

    except Exception as e:
        print(f"Erro ao encaminhar a solicitação: {e}")
        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
        client_socket.sendall(response.encode('utf-8'))
    finally:
        client_socket.close()

# Configuração do servidor proxy
def start_proxy(host='127.0.0.1', port=8080):
    os.makedirs('cache', exist_ok=True)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor proxy rodando em http://{host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Conexão recebida de {client_address}")
            handle_request(client_socket)
    except KeyboardInterrupt:
        print("\nEncerrando o servidor proxy.")
    finally:
        server_socket.close()

start_proxy()