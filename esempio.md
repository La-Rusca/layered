# Docker compose - esempio

Il seguente docker compose contiene molti dei concetti visti in classe
- port mapping
- volumi
    - nominati
    - configurati in Portainer / docker volume create nomecontainer
- variabili d'ambiente
- build

## Struttura del progetto

```
compose/
├── esempio.md               # questo file (readme)
├── docker-compose.yml       # definizione dei servizi
├── Dockerfile               # immagine Flask (usata da build)
├── nginx.conf               # reverse proxy verso il backend
└── app/
    ├── app.py               # endpoint "/" e "/db"
    └── requirements.txt     # dipendenze Python
```

## Il file docker-compose.yml

```yaml
services:
  db:
    image: mysql:8.0
    container_name: esempio-db
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: segreta
      MYSQL_DATABASE: esempio
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-psegreta"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build: .
    container_name: esempio-flask
    environment:
      DB_HOST: db
      DB_PASSWORD: segreta
      DB_NAME: esempio
    volumes:
      - uploads:/app/uploads
    depends_on:
      db:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    container_name: esempio-nginx
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend

volumes:
  uploads:
  mysql-data:
    external: true
```

## Concetti spiegati

### 1. Port mapping (`ports`)

Con `"host:container"` si espone la porta del container all'esterno.

- `"3306:3306"` sul servizio `db` → il client MySQL locale può collegarsi al database.
- `"8080:80"` sul servizio `nginx` → basta aprire http://localhost:8080 nel browser per raggiungere il container.

### 2. Volumi

I volumi servono per rendere persistenti i dati, che altrimenti verrebbero persi quando il container viene rimosso.

- **Volume nominato** `uploads`: dichiarato nella sezione `volumes:` in basso e montato in `/app/uploads`. Viene gestito da Docker stesso.
- **Volume esterno** `mysql-data`: dichiarato con `external: true`, quindi deve esistere già. Si crea in due modi:
  - da terminale: `docker volume create mysql-data`
  - da Portainer: sezione *Volumes* → *Add volume*
- **Volume bind (solo lettura)**: `./nginx.conf:/etc/nginx/conf.d/default.conf:ro` monta un file locale direttamente nel container, senza copiarlo.

### 3. Variabili d'ambiente (`environment`)

Ogni servizio riceve coppie `NOME: valore`:

- `db`: `MYSQL_ROOT_PASSWORD` e `MYSQL_DATABASE` (usate da MySQL al primo avvio).
- `backend`: `DB_HOST`, `DB_PASSWORD`, `DB_NAME`, che Flask legge in `app.py` con `os.environ.get(...)`.

Le variabili d'ambiente permettono di configurare l'app senza modificare il codice.

### 4. Build (`build`)

Il servizio `backend` usa `build: .` invece di `image:`: Docker esegue il `Dockerfile` nella cartella del compose per creare un'immagine personalizzata (installazione delle dipendenze Flask e copia del codice di `app/`).

### Extra: dipendenze tra servizi

- `depends_on` con `condition: service_healthy` → il backend parte solo quando il database risulta sano.
- `healthcheck` → Docker esegue `mysqladmin ping` per verificare che MySQL sia pronto.

## Comandi utili

```bash
# 1) creare il volume esterno (obbligatorio, è external: true)
docker volume create mysql-data

# 2) avviare i servizi (la prima volta compila l'immagine Flask)
docker compose up --build

# 3) aprire il browser
#   root: http://localhost:8080
#   verifica DB: http://localhost:8080/db

# fermare i servizi (senza eliminare i volumi)
docker compose down

# fermare ed eliminare anche i container/volumi/reti
docker compose down -v

# vedere lo stato dei servizi
docker compose ps

# vedere i log in tempo reale
docker compose logs -f

# mostrare un singolo servizio
docker compose up db

# ricostruire dopo una modifica al codice
docker compose up --build
```