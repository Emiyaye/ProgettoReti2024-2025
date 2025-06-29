Cognome e nome: Bao Botti
Matricola: 0001080230

Traccia 1 – Web Server + Sito Web Statico (livello base/intermedio)

1. Tecnologie Utilizzate

    Python 3.x: Il linguaggio di programmazione principale per lo sviluppo del server HTTP.

    Socket (modulo Python): Utilizzato per la comunicazione TCP/IP tra client (browser) e server.

    HTML5/CSS3

    Modulo os e logging (Python): per la registrazione delle attività del server.

2. Struttura del Progetto

progetto/
│
├── server.py             # Web server HTTP
├── server.log            # File di log generato dal server (attività e errori)
└── www/                  # Cartella radice del sito web statico
    ├── index.html        # Home
    ├── pag2.html         # Template
    ├── pag3.html         # Template
    ├── styles.css        # Foglio di stile CSS per tutto il sito
    └── images/           
        └── logo.jpg      # Immagine test

3. Funzionalità del Server (server.py)

Il server implementato offre le seguenti funzionalità principali:

    Ascolto sulla porta localhost:8080: Il server si lega all'indirizzo 127.0.0.1 (localhost) e ascolta le connessioni in entrata sulla porta 8080. 

    Gestione richieste HTTP di tipo GET: Il server è configurato per processare esclusivamente le richieste HTTP con metodo GET, restituendo un codice 501 Not Implemented per tutti gli altri metodi.

    La richiesta alla root (/) viene automaticamente reindirizzata a index.html.
    Le richieste per le directory che non contengono un index.html vengono gestite con un 403 Forbidden.

    Restituzione di codici HTTP standard:

        200 OK: Per i file richiesti che esistono e sono correttamente serviti.
        404 Not Found: Per le risorse (file) non trovate sul server
        403 Forbidden: Per i tentativi di accedere a directory senza un file index.html
        500 Internal Server Error: In caso di errori interni imprevisti
        501 Not Implemented: per metodi HTTP diversi da GET.

    Supporto ai MIME types: Il server riconosce e imposta correttamente l'header Content-Type per diversi tipi di file (es. text/html, text/css, image/jpg)
    Logging dettagliato: Ogni richiesta ricevuta, insieme al suo esito (successo, errore 404, ...), viene registrata in un file server.log

Flusso di Esecuzione del Server

    Init:

        Viene creato un socket TCP/IP.
        Il socket viene configurato per riutilizzare l'indirizzo.
        Il socket viene legato a localhost:8080 e messo in ascolto per le connessioni.
        Viene configurato il sistema di logging per scrivere su server.log.
        Viene verificata l'esistenza della directory www/.

    Ciclo:

        Il server entra in un ciclo while True per accettare continuamente nuove connessioni.
        Quando un client si connette, server_socket.accept() crea un nuovo socket per la comunicazione con quel client.

    Gestione della Richiesta (handle_request):

        Ricezione Richiesta: Il server riceve i dati della richiesta HTTP dal client_socket.
        Parsing Richiesta: La prima riga della richiesta viene analizzata per estrarre il metodo HTTP, il percorso della risorsa richiesta e la versione HTTP.
        Logging: La richiesta viene registrata nel server.log.
        Validazione Metodo: Se il metodo non è GET, invia 501 Not Implemented.
        Sicurezza: Se rileva un tentativo di accedere a un file fuori da WEB_ROOT (www), invia 403 Forbidden.

        Ricerca File:

            Controlla se il requested_file_path esiste.
            Se è un file, determina il Content-Type (MIME type), legge il contenuto del file (in modalità binaria) e invia una risposta 200 OK 
            Se è una directory, cerca un index.html al suo interno. Se trovato, lo serve con 200 OK. Altrimenti, invia 403 Forbidden.

        File non Trovato: invia una risposta 404 Not Found.

        Gestione Eccezioni: invia un 500 Internal Server Error e logga i dettagli dell'errore.

        Chiusura Socket Client: Il client_socket viene chiuso nel blocco finally .

    Chiusura Server:

        Il ciclo di ascolto può essere interrotto da Ctrl+C (KeyboardInterrupt).

        Il server_socket principale viene chiuso, e un messaggio di spegnimento viene loggato.

4.  Sito Statico (Cartella www/)

    Navigazione: Una barra di navigazione in alto.
    File CSS: Tutti gli stili sono gestiti da styles.css.
    Layout Responsive: Il CSS include media queries (@media) con un break point di 768px

5. Estensioni Opzionali Implementate

    Supporto a MIME types parziali: Il server gestisce correttamente alcuni tipi MIME .html, .css, .jpg
    Logging delle richieste (su file): Tutte le interazioni del client con il server sono registrate in server.log
    Layout responsive: Il sito statico è stato progettato con un CSS che include media queries.
    Gestione degli errori HTTP: Implementazione di risposte 403 Forbidden, 500 Internal Server Error, e 501 Not Implemented oltre a 200 OK e 404 Not Found.
    Prevenzione accessi anomali a directory: Il server verifica che le richieste non tentino di accedere a file al di fuori della directory www.

6. Test Effettuati

Sono stati eseguiti i seguenti test per verificare la corretta funzionalità del server:

    Richieste valide con browser (http://localhost:8080/):
        Tutte le pagine (index.html, about.html, contact.html) e le risorse (styles.css, logo.jpg) sono state caricate correttamente con risposte 200 OK

    Richieste a file inesistenti (http://localhost:8080/pagina_sconosciuta.html):
        Il server ha restituito correttamente una pagina 404 Not Found personalizzata

    Richieste a directory senza index.html (http://localhost:8080/images/):
        Risultato: Il server ha restituito una pagina 403 Forbidden

    Test CSS e responsive su schermi di varie dimensioni:
        Il layout del sito si è adattato correttamente a diverse larghezze dello schermo del browser

    Test MIME:
        Le risorse come .html, .css, e .jpg sono state servite con il Content-Type corretto