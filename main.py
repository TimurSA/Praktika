import socket
import threading

# Конфигурация прокси-сервера
HOST = '127.0.0.1'  # Локальный хост
PORT = 8888  # Порт для прокси-сервера


# Функция для обработки клиентских соединений
def handle_client(client_socket):
    # Получение данных от клиента
    request = client_socket.recv(4096)

    # Парсинг первого строки HTTP-запроса
    first_line = request.split(b'\n')[0]
    url = first_line.split(b' ')[1]

    # Извлечение хоста из URL
    http_pos = url.find(b'://')
    if http_pos == -1:
        temp = url
    else:
        temp = url[(http_pos + 3):]

    port_pos = temp.find(b':')

    webserver_pos = temp.find(b'/')
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ''
    port = -1
    if port_pos == -1 or webserver_pos < port_pos:
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int(temp[(port_pos + 1):][:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]

    # Соединение с целевым сервером
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((webserver, port))
    proxy_socket.send(request)

    while True:
        # Получение данных от веб-сервера
        data = proxy_socket.recv(4096)

        if len(data) > 0:
            # Отправка данных клиенту
            client_socket.send(data)
        else:
            break

    # Закрытие сокетов
    proxy_socket.close()
    client_socket.close()


def main():
    # Создание сокета прокси-сервера
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f'[*] Proxy server running on {HOST}:{PORT}')

    while True:
        # Принятие нового соединения от клиента
        client_socket, addr = server_socket.accept()

        print(f'[*] Received connection from {addr[0]}:{addr[1]}')

        # Создание нового потока для обработки клиента
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == '__main__':
    main()
