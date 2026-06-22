# 🚀 SocialHub — Full-Stack Social Media Platform

A production-grade **Facebook + Instagram hybrid** built with Django, featuring real-time chat, stories, posts, likes, comments, follows, and push notifications. Designed as a **3-tier monolithic architecture** optimized for high traffic.

![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

---

## 📋 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Prerequisites](#-prerequisites)
3. [Quick Start (Docker)](#-quick-start-docker-recommended)
4. [Local Development Setup](#-local-development-setup)
5. [Component Setup Details](#-component-setup-details)
6. [Running the Application](#-running-the-application)
7. [API Reference](#-api-reference)
8. [WebSocket Events](#-websocket-events)
9. [Scaling Guide](#-scaling-guide)
10. [Troubleshooting](#-troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  PRESENTATION TIER                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Nginx     │  │ CloudFlare  │  │  React/Vue Frontend │  │
│  │  (Static)   │  │   CDN       │  │  (WebSocket Client) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  APPLICATION TIER                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Django REST │  │  Django     │  │  Celery Workers     │  │
│  │   API       │  │  Channels   │  │  (Background Jobs)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  DATA TIER                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ PostgreSQL  │  │   Redis     │  │  MinIO/S3           │  │
│  │ (Primary DB)│  │ (Cache/WS)  │  │  (Media Storage)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### Required Software

| Software | Version | Purpose | Install Link |
|----------|---------|---------|-------------|
| **Python** | 3.12+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| **PostgreSQL** | 16+ | Primary database | [postgresql.org](https://www.postgresql.org/download/) |
| **Redis** | 7+ | Cache, queue, WebSocket pub/sub | [redis.io](https://redis.io/docs/latest/operate/oss_and_stack/install/) |
| **Docker** | 24+ | Containerization (recommended) | [docker.com](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.20+ | Multi-container orchestration | Included with Docker Desktop |

### Optional Software

| Software | Purpose | Install Link |
|----------|---------|-------------|
| **MinIO** | Object storage (S3-compatible) | [min.io](https://min.io/download) |
| **Node.js** | Frontend development | [nodejs.org](https://nodejs.org/) |
| **Postman** | API testing | [postman.com](https://www.postman.com/downloads/) |
| **pgAdmin** | PostgreSQL GUI | [pgadmin.org](https://www.pgadmin.org/download/) |

### System Requirements

- **RAM**: 4GB minimum (8GB recommended for Docker)
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows (WSL2 recommended for Windows)
- **Ports**: 8000, 5432, 6379, 9000, 9001 must be available

---

## 🐳 Quick Start (Docker — Recommended)

The fastest way to get everything running. All services start with a single command.

### Step 1: Extract the Project

```bash
# Unzip the project
unzip social-app.zip
cd social-app
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional for local dev)
nano .env
```

Default `.env` for Docker:
```bash
DEBUG=False
SECRET_KEY=change-this-to-a-random-string-in-production
DB_NAME=socialdb
DB_USER=socialuser
DB_PASSWORD=socialpass
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=social-media
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Step 3: Deploy with Docker

```bash
# Make the deploy script executable
chmod +x scripts/deploy.sh

# Run the deployment
./scripts/deploy.sh
```

This script will:
1. Build the Docker image
2. Start PostgreSQL, Redis, MinIO, Nginx, Django, and Celery
3. Run database migrations
4. Collect static files
5. Create cache tables

### Step 4: Verify Everything is Running

```bash
# Check all containers
docker-compose -f docker/docker-compose.yml ps

# Expected output:
# NAME                STATUS          PORTS
# social-app-db-1     Up 10 seconds   0.0.0.0:5432->5432/tcp
# social-app-redis-1  Up 10 seconds   0.0.0.0:6379->6379/tcp
# social-app-minio-1  Up 10 seconds   0.0.0.0:9000-9001->9000-9001/tcp
# social-app-web-1    Up 10 seconds   0.0.0.0:8000->8000/tcp
# social-app-nginx-1  Up 10 seconds   0.0.0.0:80->80/tcp
```

### Step 5: Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost/api/ | — |
| **Admin Panel** | http://localhost/admin/ | Create superuser first |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **API Docs** | http://localhost/api/ | Browse endpoints |

### Step 6: Create a Superuser

```bash
docker-compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

### Step 7: Stop the Application

```bash
docker-compose -f docker/docker-compose.yml down

# To remove all data (volumes):
docker-compose -f docker/docker-compose.yml down -v
```

---

## 💻 Local Development Setup

For active development where you need hot-reload and direct code access.

### Step 1: Install System Dependencies

#### On Ubuntu/Debian:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and build tools
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Install Redis
sudo apt install -y redis-server

# Install other dependencies
sudo apt install -y build-essential libpq-dev gcc curl
```

#### On macOS:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.12 postgresql@16 redis
brew services start postgresql@16
brew services start redis
```

#### On Windows (WSL2):
```bash
# Follow Ubuntu instructions inside WSL2
# Or use Docker Desktop with WSL2 backend
```

### Step 2: Set Up PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE socialdb;
CREATE USER socialuser WITH PASSWORD 'socialpass';
GRANT ALL PRIVILEGES ON DATABASE socialdb TO socialuser;
ALTER USER socialuser CREATEDB;

# Exit
\q

# Verify connection
psql -h localhost -U socialuser -d socialdb
```

### Step 3: Set Up Redis

```bash
# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Expected output: PONG

# Check Redis info
redis-cli info server
```

### Step 4: Set Up MinIO (Optional — for file storage)

```bash
# Download MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# Create data directory
mkdir -p ~/minio-data

# Start MinIO server
export MINIO_ROOT_USER=minioadmin
export MINIO_ROOT_PASSWORD=minioadmin
minio server ~/minio-data --console-address :9001

# Access at http://localhost:9001
```

### Step 5: Create Python Virtual Environment

```bash
# Navigate to project
cd social-app

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify Python version
python --version
# Expected: Python 3.12.x
```

### Step 6: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install base requirements
pip install -r requirements/base.txt

# For production-like local testing:
pip install -r requirements/production.txt

# Verify Django installation
python -m django --version
```

### Step 7: Configure Environment Variables

```bash
# Create .env file
cp .env.example .env

# Edit with your local settings
nano .env
```

Local development `.env`:
```bash
DEBUG=True
SECRET_KEY=your-dev-secret-key-here-min-50-chars-long-for-security
DB_NAME=socialdb
DB_USER=socialuser
DB_PASSWORD=socialpass
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=social-media
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Step 8: Run Database Migrations

```bash
python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: accounts, admin, auth, chat, contenttypes, notifications, posts, sessions, stories, token_blacklist
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...
```

### Step 9: Create Cache Table

```bash
python manage.py createcachetable
```

### Step 10: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 11: Create Superuser

```bash
python manage.py createsuperuser

# Enter:
# Email: admin@example.com
# Username: admin
# Password: (choose strong password)
```

### Step 12: Verify Setup

```bash
# Run Django checks
python manage.py check

# Expected: System check identified no issues (0 silenced).
```

---

## 🚀 Running the Application

### Local Development Mode

You need **4 terminal windows** running simultaneously:

#### Terminal 1: Django Development Server
```bash
cd social-app
source venv/bin/activate
python manage.py runserver

# Or with ASGI for WebSocket support:
# uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000
```
Access: http://localhost:8000

#### Terminal 2: Celery Worker
```bash
cd social-app
source venv/bin/activate
celery -A config worker -l info --concurrency=4

# For Windows (use solo pool):
# celery -A config worker -l info -P solo
```

#### Terminal 3: Celery Beat (Scheduler)
```bash
cd social-app
source venv/bin/activate
celery -A config beat -l info
```

#### Terminal 4: MinIO (if not using Docker)
```bash
export MINIO_ROOT_USER=minioadmin
export MINIO_ROOT_PASSWORD=minioadmin
minio server ~/minio-data --console-address :9001
```

### Production Mode (Local)

```bash
# Use production settings
export DJANGO_SETTINGS_MODULE=config.settings.production

# Run with Gunicorn (HTTP only)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Or with Uvicorn (HTTP + WebSocket)
uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🔧 Component Setup Details

### PostgreSQL Configuration

```bash
# Edit PostgreSQL config for performance
sudo nano /etc/postgresql/16/main/postgresql.conf

# Recommended settings for social app:
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
wal_buffers = 16MB
checkpoint_completion_target = 0.9
random_page_cost = 1.1
effective_io_concurrency = 200
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Redis Configuration

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Recommended settings:
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

Restart Redis:
```bash
sudo systemctl restart redis-server
```

### MinIO Bucket Setup

```bash
# Install MinIO client (mc)
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# Configure MinIO client
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create bucket
mc mb local/social-media

# Set bucket policy (public read for avatars/posts)
mc anonymous set download local/social-media
```

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login/` | Get JWT access & refresh tokens | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |
| POST | `/api/auth/logout/` | Blacklist refresh token | Yes |

**Login Example:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "yourpassword"
  }'

# Response:
# {
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
# }
```

### Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/register/` | Register new user |
| GET/PATCH | `/api/accounts/me/` | Get/update profile |
| GET | `/api/accounts/<username>/` | View user profile |
| POST | `/api/accounts/<username>/follow/` | Follow/unfollow |
| GET | `/api/accounts/<username>/followers/` | List followers |
| GET | `/api/accounts/<username>/following/` | List following |
| GET | `/api/accounts/search/?q=john` | Search users |
| GET | `/api/accounts/suggested/` | Suggested users |

### Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/feed/` | Personalized feed |
| GET | `/api/posts/trending/` | Trending posts |
| GET/POST | `/api/posts/` | List/create posts |
| GET/PUT/DELETE | `/api/posts/<id>/` | Get/update/delete post |
| POST | `/api/posts/<id>/like/` | Like/unlike post |
| POST | `/api/posts/<id>/save/` | Save/unsave post |
| GET/POST | `/api/posts/<id>/comments/` | List/add comments |
| POST | `/api/posts/comments/<id>/like/` | Like comment |
| GET | `/api/posts/tag/<tagname>/` | Posts by tag |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/chat/conversations/` | List/create conversations |
| GET | `/api/chat/conversations/<id>/` | Conversation detail |
| GET | `/api/chat/conversations/<id>/messages/` | List messages |
| POST | `/api/chat/conversations/<id>/read/` | Mark as read |
| POST | `/api/chat/dm/<username>/` | Start direct message |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/` | List notifications |
| GET | `/api/notifications/unread-count/` | Unread count |
| POST | `/api/notifications/mark-all-read/` | Mark all read |
| POST | `/api/notifications/<id>/read/` | Mark one read |

### Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stories/feed/` | Active stories from followed |
| GET/POST | `/api/stories/my/` | My stories |
| POST | `/api/stories/<id>/view/` | View story |

---

## 🔌 WebSocket Events

Connect to: `ws://localhost:8000/ws/chat/`

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `join_conversation` | `{"conversation_id": 1}` | Join a chat room |
| `send_message` | `{"conversation_id": 1, "content": "Hello", "message_type": "text"}` | Send message |
| `typing` | `{"conversation_id": 1, "is_typing": true}` | Typing indicator |
| `read_message` | `{"message_id": 123}` | Mark as read |
| `reaction` | `{"message_id": 123, "emoji": "❤️"}` | Add reaction |
| `ping` | `{}` | Keep connection alive |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `connection_established` | `{"message": "Connected as username"}` | Connection confirmed |
| `conversation_joined` | `{"conversation_id": 1, "messages": [...]}` | Joined room |
| `new_message` | `{"message": {...}}` | New message received |
| `typing` | `{"user_id": 1, "username": "john", "is_typing": true}` | Typing indicator |
| `read_receipt` | `{"message_id": 123, "read_by": 2}` | Message read |
| `reaction` | `{"message_id": 123, "emoji": "❤️", "user_id": 2}` | Reaction added |
| `notification` | `{"type": "new_message", "data": {...}}` | Push notification |

---

## 📈 Scaling Guide

### Traffic Level: 1,000 Users
```bash
# Single server, minimal config
uvicorn config.asgi:application --workers 2
```

### Traffic Level: 10,000 Users
```bash
# Add read replica, increase workers
uvicorn config.asgi:application --workers 4

# Add PgBouncer for connection pooling
# Scale Celery workers: celery -A config worker -c 8
```

### Traffic Level: 100,000+ Users
```bash
# Horizontal scaling with Docker Compose
# Scale web containers:
docker-compose up -d --scale web=4

# Add Redis Cluster
# Add PostgreSQL read replicas
# Use CDN for media (CloudFlare + S3)
# Separate WebSocket servers
```

### Traffic Level: 1,000,000+ Users
- **Kubernetes** deployment with auto-scaling
- **Database sharding** by user ID
- **Edge WebSocket servers** (CloudFlare Workers)
- **Elasticsearch** for search
- **Kafka** for event streaming
- **Multi-region** deployment

---

## 🧪 Testing

### Run Load Test
```bash
# Install aiohttp
pip install aiohttp

# Run the load test
python scripts/load_test.py

# Simulates 100 concurrent users creating posts and viewing feeds
```

### Run Django Tests
```bash
python manage.py test apps.accounts apps.posts apps.chat
```

### API Testing with cURL
```bash
# Register
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}' \
  | jq -r '.access')

# Create post
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello World!","post_type":"text"}'

# Get feed
curl http://localhost:8000/api/posts/feed/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'config'`
**Solution:** Make sure you're in the project root directory and virtual environment is activated.
```bash
cd social-app
source venv/bin/activate
export PYTHONPATH=/path/to/social-app:$PYTHONPATH
```

### Issue: `connection refused` to PostgreSQL
**Solution:** Check PostgreSQL is running and credentials are correct.
```bash
sudo systemctl status postgresql
psql -h localhost -U socialuser -d socialdb
```

### Issue: Redis connection errors
**Solution:** Verify Redis is running.
```bash
redis-cli ping
sudo systemctl restart redis-server
```

### Issue: WebSocket not connecting
**Solution:** Use ASGI server (uvicorn/daphne), not WSGI.
```bash
# Wrong:
python manage.py runserver  # WSGI only

# Correct:
uvicorn config.asgi:application --reload
```

### Issue: Static files not loading
**Solution:** Run collectstatic and check WhiteNoise.
```bash
python manage.py collectstatic --noinput
# Verify STATIC_ROOT and STATICFILES_STORAGE in settings
```

### Issue: Media uploads failing
**Solution:** Check MinIO is running and bucket exists.
```bash
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb local/social-media
mc anonymous set download local/social-media
```

### Issue: Celery tasks not running
**Solution:** Verify Redis URL and start worker.
```bash
celery -A config worker -l info --concurrency=2
# Check CELERY_BROKER_URL in settings
```

---

## 📁 Project Structure

```
social-app/
│
├── apps/
│   ├── accounts/          # User auth, profiles, follows
│   ├── posts/             # Posts, comments, likes, feed
│   ├── chat/              # Real-time messaging (WebSocket)
│   ├── notifications/     # Push notifications
│   └── stories/           # 24-hour ephemeral stories
│
├── config/                # Django settings, ASGI, WSGI, Celery
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── development.py # Dev settings
│   │   └── production.py  # Prod settings
│   ├── asgi.py            # ASGI with WebSocket
│   ├── wsgi.py            # WSGI fallback
│   ├── urls.py            # URL routing
│   └── celery.py          # Celery config
│
├── docker/
│   ├── Dockerfile         # Multi-stage build
│   ├── docker-compose.yml # Full stack orchestration
│   └── nginx.conf         # Reverse proxy config
│
├── scripts/
│   ├── setup.sh           # One-command local setup
│   ├── deploy.sh          # Production deployment
│   └── load_test.py       # Traffic simulation
│
├── requirements/
│   ├── base.txt           # Core dependencies
│   └── production.txt     # Production extras
│
├── static/                # CSS, JS, images
├── media/                 # User uploads
├── templates/             # HTML templates
├── manage.py              # Django CLI
└── .env.example           # Environment template
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Credits

- **Django** — Web framework
- **Django REST Framework** — API toolkit
- **Django Channels** — WebSocket support
- **Celery** — Distributed task queue
- **PostgreSQL** — Primary database
- **Redis** — Cache, queue, pub/sub
- **MinIO** — Object storage
- **Nginx** — Reverse proxy

---

**Built with ❤️ for high-traffic social platforms.**
