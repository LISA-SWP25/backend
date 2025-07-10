#  ![telegram-cloud-photo-size-2-5431661620049868588-m](https://github.com/user-attachments/assets/e29ca5cb-c40c-4da0-8b8d-b63a37749c04) LISA: Backend 

# LISA Backend API

**Legitimate Infrastructure Simulation Agent - Management API**

A FastAPI-based backend system for managing and monitoring software agents that simulate legitimate user activity on target systems.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg)

##  Features

- **Agent Management**: Create, configure, and deploy software agents
- **Real-time Monitoring**: WebSocket-based live agent monitoring
- **Role-based Configuration**: Define user roles and behaviors
- **Template System**: Reusable behavior and application templates
- **CI/CD Integration**: Automated agent building and deployment
- **Heartbeat Monitoring**: Real-time agent health and activity tracking
- **PostgreSQL/SQLite Support**: Flexible database backend

##  Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Docker Setup](#docker-setup)
- [Development](#development)
- [Agent Integration](#agent-integration)

##  Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd lisa/backend

# Start with Docker Compose
docker-compose up -d

# Access the API documentation
open http://localhost:8000/docs
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload

# API available at http://localhost:8000
```

### Core Components

- **Agent Manager**: Handles agent lifecycle and configuration
- **Heartbeat System**: Monitors agent health and activity
- **Template Engine**: Manages behavior and application templates
- **Build Pipeline**: Compiles agents for deployment
- **Monitoring Dashboard**: Real-time system overview

##  Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (SQLite fallback available)
- Docker & Docker Compose 

### Backend Setup

1. **Clone and Install**
   ```bash
   git clone <your-repo-url>
   cd lisa/backend
   pip install -r requirements.txt
   ```

2. **Database Configuration**
   ```python
   # app/database.py
   DATABASE_URL = 'postgresql://lisa:pass@localhost:5432/lisa_dev'
   ```

3. **Environment Variables**
   ```bash
   export DATABASE_URL="postgresql://lisa:pass@localhost:5432/lisa_dev"
   export CORS_ORIGINS="http://localhost:3000"
   ```

4. **Run the Server**
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

##  API Documentation

### Core Endpoints

#### Agent Management
```http
POST   /api/agents/generate              # Create agent configuration
GET    /api/agents                       # List all agents
GET    /api/agents/{agent_id}/status     # Get agent status
POST   /api/agents/{agent_id}/deploy     # Deploy agent
GET    /api/agents/{agent_id}/config     # Download agent config
```

#### Heartbeat & Monitoring
```http
POST   /api/agents/heartbeat             # Agent heartbeat (main endpoint)
GET    /api/agents/active                # List active agents
GET    /api/agents/statistics/summary    # System statistics
GET    /api/monitoring/overview          # Monitoring dashboard
```

#### Templates & Roles
```http
POST   /api/roles                        # Create user role
GET    /api/roles                        # List roles
POST   /api/behavior-templates           # Create behavior template
GET    /api/behavior-templates           # List templates
POST   /api/application-templates        # Create app template
```

#### System & Health
```http
GET    /api/health                       # System health check
GET    /api/stats                        # System statistics
WS     /api/ws/agents/{agent_id}         # WebSocket monitoring
```

### Agent Heartbeat Format

```json
POST /api/agents/heartbeat
{
  "timestamp": "2025-01-15T14:30:45.123456",
  "agent_id": "USR0012345",
  "username": "john_doe",
  "role": "Junior Developer",
  "department": "Development",
  "location": "Headquarters",
  "system_info": {
    "hostname": "workstation-01",
    "platform": "Linux-5.15.0-56-generic-x86_64",
    "python_version": "3.10.6",
    "cpu_count": 8,
    "agent_version": "1.0.0"
  },
  "status": "active",
  "statistics": {
    "agent_uptime": 3600.5,
    "current_app": "Visual Studio Code",
    "plugin_mode": true,
    "total_plugins": 5,
    "available_apps": 7
  },
  "current_activity": {
    "application": "Visual Studio Code",
    "is_plugin": true
  }
}
```

##  Database Schema

### Core Tables

```sql
-- Agents table
agents (
  id SERIAL PRIMARY KEY,
  agent_id VARCHAR(50) UNIQUE,
  name VARCHAR(100),
  status VARCHAR(20),
  os_type VARCHAR(20),
  last_seen TIMESTAMP,
  config JSON
)

-- Agent Activities (heartbeats, logs)
agent_activities (
  id SERIAL PRIMARY KEY,
  agent_id INTEGER REFERENCES agents(id),
  activity_type VARCHAR(50),
  activity_data JSON,
  timestamp TIMESTAMP
)

-- Roles and Templates
roles (id, name, description, category)
behavior_templates (id, name, description, template_data)
application_templates (id, name, template_config)
```

##  Docker Setup

### Full Stack Deployment

```yaml
# docker-compose.yml
services:
  # PostgreSQL 
  lisa_postgres_quick:
    image: postgres:15-alpine
    container_name: lisa_postgres_quick
    environment:
      POSTGRES_DB: lisa_dev
      POSTGRES_USER: lisa
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - lisa_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lisa -d lisa_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend 
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.fast 
    container_name: lisa_backend
    environment:
      - DATABASE_URL=postgresql://lisa:pass@lisa_postgres_quick:5432/lisa_dev
      - CORS_ORIGINS=http://localhost:3000
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    networks:
      - lisa_network
    depends_on:
      lisa_postgres_quick:
        condition: service_healthy

  # Frontend 
  frontend:
    image: nginx:alpine
    container_name: lisa_frontend
    ports:
      - "3000:80"
    volumes:
      - ./frontend-static:/usr/share/nginx/html:ro
    networks:
      - lisa_network
    depends_on:
      - backend

# Agent Deployer 
agent-deployer:
  image: python:3.11-slim
  container_name: lisa_agent_deployer
  working_dir: /app
  command: >
    sh -c "pip install fastapi uvicorn --no-cache-dir && 
           python -c 'from fastapi import FastAPI; import uvicorn; app = FastAPI(); app.add_api_route(\"/\", lambda: {\"status\": \"running\", \"service\": \"agent-deployer\"}); app.add_api_route(\"/health\", lambda: {\"status\": \"healthy\"}); uvicorn.run(app, host=\"0.0.0.0\", port=8001)'"
  ports:
    - "8001:8001"
  networks:
    - lisa_network

networks:
  lisa_network:
    driver: bridge

volumes:
  postgres_data:
```

### Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Adding New Endpoints

1. Create endpoint in `app/api/endpoints/`
2. Add route to `app/main.py`
3. Define schemas in `app/schemas.py`
4. Update database models if needed

##  Agent Integration

### Agent Heartbeat Integration

```python
import requests
import time

def send_heartbeat(agent_data):
    response = requests.post(
        "http://localhost:8000/api/agents/heartbeat",
        json=agent_data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Example usage
while True:
    heartbeat_data = {
        "agent_id": "USR0012345",
        "username": "john_doe",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        # ... other fields
    }
    
    result = send_heartbeat(heartbeat_data)
    time.sleep(60)  # Send every minute
```

### Agent Configuration Download

```bash
# Download agent configuration
curl -o agent_config.json \
  "http://localhost:8000/api/agents/USR0012345/config"

# Deploy agent with configuration
python agent_deployer.py --config agent_config.json
```

##  Configuration

### Environment Variables

```bash
DATABASE_URL="postgresql://user:pass@host:port/database"
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
API_KEY="your-api-key-here"
LOG_LEVEL="INFO"
```

### Database Configuration

```python
# For PostgreSQL
DATABASE_URL = 'postgresql://lisa:pass@localhost:5432/lisa_dev'

# For SQLite (fallback)
DATABASE_URL = 'sqlite:///./fallback.db'
```

##  Monitoring & Observability

### Health Check

```bash
curl http://localhost:8000/api/health
```

### System Statistics

```bash
curl http://localhost:8000/api/stats
```

### WebSocket Monitoring

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/agents/USR0012345');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Agent update:', data);
};
```

##  Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL is running
   docker ps | grep postgres
   
   # Check connection
   psql -h localhost -U lisa -d lisa_dev
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

3. **Agent Not Receiving Config**
   ```bash
   # Check agent endpoint
   curl http://localhost:8000/api/agents/USR0012345/status
   
   # Verify agent is registered
   curl http://localhost:8000/api/agents
   ```

##  API Response Examples

### Successful Heartbeat Response
```json
{
  "status": "received",
  "agent_id": "USR0012345",
  "timestamp": "2025-01-15T14:30:45.123456",
  "message": "Heartbeat processed successfully",
  "next_heartbeat_in": 86400
}
```

### Agent Status Response
```json
{
  "agent": {
    "agent_id": "USR0012345",
    "name": "john_doe",
    "status": "active",
    "last_seen": "2025-01-15T14:30:45.123456",
    "role": "Junior Developer"
  },
  "recent_activities": [...]
}
```

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
