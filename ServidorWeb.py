import socket
import os

# Função para lidar com solicitações HTTP
def handle_request(client_socket):

    requisicao = client_socket.recv(1024).decode('utf-8')
    print(f"Requisição recebida:\n{requisicao}")
    
    # Divide a requisição em linhas e obtém o caminho do arquivo
    requisicao_linhas = requisicao.splitlines()
    if len(requisicao_linhas) > 0:
        primeira_linha = requisicao_linhas[0]
        method, path, _ = primeira_linha.split()

        if path == "/":
            path = "HelloWord.html"  
        else:
            path = path.lstrip("/")
        
        # Verifica se o arquivo solicitado existe
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                content = file.read()
            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
            )
            client_socket.sendall(response.encode('utf-8') + content)
        else:
            # Resposta HTTP 404 Não Encontrado
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                "<html><body><h1>404 Not Found</h1></body></html>"
            )
            client_socket.sendall(response.encode('utf-8'))

    # Fecha a conexão com o cliente
    client_socket.close()

# Configuração do servidor
def start_server(host='127.0.0.1', port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Servidor rodando em http://{host}:{port}")
    
    try:
        while True:

            client_socket, client_address = server_socket.accept()
            print(f"Conexão recebida de {client_address}")
    
            handle_request(client_socket)
    except KeyboardInterrupt:
        print("\nEncerrando o servidor.")
    finally:
        server_socket.close()


start_server()