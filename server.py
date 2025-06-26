import socket
import os
import logging


# Impostazioni del Server 
HOST = '127.0.0.1' 
PORT = 8080        
WEB_ROOT = 'www'   

# Configurazione del Logging
# Il logging ora scriverà su un file 'server.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log")
    ]
)

# Dizionario dei MIME Types
MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.jpg': 'image/jpeg',
}

def get_mime_type(file_path):
    """
    Determina il MIME type di un file basandosi sulla sua estensione.
    Restituisce 'application/octet-stream' se l'estensione non è riconosciuta.
    """
    _, ext = os.path.splitext(file_path)
    return MIME_TYPES.get(ext.lower(), 'application/octet-stream')

def handle_request(client_socket, client_address):
    """
    Gestisce una singola richiesta HTTP da un client connesso, cerca il file richiesto e invia la risposta.
    """
    client_ip, client_port = client_address
    
    try:
        # Riceve la richiesta HTTP dal browser
        request_data = client_socket.recv(4096).decode('utf-8')
        
        # Se la richiesta è vuota
        if not request_data:
            logging.info(f"[{client_ip}:{client_port}] Richiesta vuota, chiudo connessione.")
            return

        request_lines = request_data.split('\n')
        first_line = request_lines[0].strip()

        # Verifica che la prima riga della richiesta sia valida
        if not first_line:
            logging.warning(f"[{client_ip}:{client_port}] Richiesta malformata: prima riga vuota.")
            return

        parts = first_line.split(' ')
        if len(parts) < 3: # Deve essere almeno "METODO, percorso, HTTP/VERS"
            logging.warning(f"[{client_ip}:{client_port}] Richiesta malformata: '{first_line}'.")
            return
            
        method, path, http_version = parts[0], parts[1], parts[2]
        
        # Log data
        logging.info(f"[{client_ip}:{client_port}] {method} {path} {http_version}")

        # Gestione del metodo HTTP !=GET
        if method != 'GET':
            response_content = "<h1>501 Not Implemented</h1><p>The requested method is not supported.</p>"
            response_header = (
                f"HTTP/1.1 501 Not Implemented\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode('utf-8')
            client_socket.sendall(response_header + response_content.encode('utf-8'))
            logging.warning(f"[{client_ip}:{client_port}] 501 Not Implemented - Method: {method}")
            return


        if path == '/':
            requested_file_path = os.path.join(WEB_ROOT, 'index.html')
        else:
            requested_file_path = os.path.join(WEB_ROOT, path[1:])

        
        # Assicura che il percorso risolto sia all'interno di WEB_ROOT
        absolute_requested_path = os.path.abspath(requested_file_path)
        absolute_web_root = os.path.abspath(WEB_ROOT)

        if not absolute_requested_path.startswith(absolute_web_root):
            # Tentativo di accesso fuori dalla WEB_ROOT del server
            response_content = "<h1>403 Forbidden</h1><p>Access to this resource is forbidden.</p>"
            response_header = (
                f"HTTP/1.1 403 Forbidden\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode('utf-8')
            client_socket.sendall(response_header + response_content.encode('utf-8'))
            logging.warning(f"[{client_ip}:{client_port}] 403 Forbidden - Path: {path} (Directory Traversal attempt?)")
            return


        if os.path.exists(requested_file_path):
            if os.path.isfile(requested_file_path):
                # File trovato e accessibile
                mime_type = get_mime_type(requested_file_path)
                
                with open(requested_file_path, 'rb') as f:
                    content_body = f.read()
                
                response_header = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {mime_type}\r\n"
                    f"Content-Length: {len(content_body)}\r\n"
                    f"Connection: close\r\n\r\n" # Chiusura della connessione dopo la risposta
                ).encode('utf-8')
                
                client_socket.sendall(response_header + content_body)
                logging.info(f"[{client_ip}:{client_port}] 200 OK - File: {path} ({len(content_body)} bytes, Type: {mime_type})")

            elif os.path.isdir(requested_file_path):
                # Richiesta di una directory
                index_in_dir_path = os.path.join(requested_file_path, 'index.html')
                if os.path.isfile(index_in_dir_path):
                    # Trovato index.html all'interno della directory
                    mime_type = get_mime_type(index_in_dir_path)
                    with open(index_in_dir_path, 'rb') as f:
                        content_body = f.read()
                    
                    response_header = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: {mime_type}\r\n"
                        f"Content-Length: {len(content_body)}\r\n"
                        f"Connection: close\r\n\r\n"
                    ).encode('utf-8')
                    client_socket.sendall(response_header + content_body)
                    logging.info(f"[{client_ip}:{client_port}] 200 OK - Directory Index: {path} (served {index_in_dir_path})")
                else:
                    # No index.html
                    response_content = "<h1>403 Forbidden</h1><p>Access to this directory is forbidden.</p>"
                    response_header = (
                        f"HTTP/1.1 403 Forbidden\r\n"
                        f"Content-Type: text/html\r\n"
                        f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
                        f"Connection: close\r\n\r\n"
                    ).encode('utf-8')
                    client_socket.sendall(response_header + response_content.encode('utf-8'))
                    logging.warning(f"[{client_ip}:{client_port}] 403 Forbidden - Directory: {path}")
        else:
            # File non trovato, 404 Not Found
            response_content = "<h1>404 Not Found</h1><p>The requested resource was not found on this server.</p>"
            response_header = (
                f"HTTP/1.1 404 Not Found\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode('utf-8')
            client_socket.sendall(response_header + response_content.encode('utf-8'))
            logging.warning(f"[{client_ip}:{client_port}] 404 Not Found - File: {path}")

    except Exception as e:
        # Gestione eccezioni
        logging.error(f"[{client_ip}:{client_port}] Errore durante la gestione della richiesta: {e}", exc_info=True)
        try:
            response_content = "<h1>500 Internal Server Error</h1><p>An unexpected error occurred on the server.</p>"
            response_header = (
                f"HTTP/1.1 500 Internal Server Error\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode('utf-8')
            client_socket.sendall(response_header + response_content.encode('utf-8'))
        except Exception as e_inner:
            logging.critical(f"[{client_ip}:{client_port}] Errore critico inviando 500: {e_inner}")
    finally:
        # Assicurati che il socket del client sia sempre chiuso
        client_socket.close()

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

        logging.info(f"Server in ascolto su http://{HOST}:{PORT}")
        logging.info(f"Servendo i file dalla cartella: {os.path.abspath(WEB_ROOT)}")

        # Verifica che la cartella WEB_ROOT esista
        if not os.path.exists(WEB_ROOT):
            logging.error(f"Errore: La cartella '{WEB_ROOT}' non esiste. Creala e aggiungi i tuoi file statici.")
            exit(1)

        while True:
            client_conn, client_addr = server_socket.accept()
            logging.info(f"Connessione accettata da {client_addr[0]}:{client_addr[1]}")
            handle_request(client_conn, client_addr)
            
    except KeyboardInterrupt:
        logging.info("Server interrotto dall'utente (Ctrl+C). Chiusura del server.")
    except Exception as e:
        logging.critical(f"Errore inatteso nel server principale: {e}", exc_info=True)
    finally:
        server_socket.close()
        logging.info("Server spento.")