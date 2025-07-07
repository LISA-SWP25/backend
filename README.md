#  ![telegram-cloud-photo-size-2-5431661620049868588-m](https://github.com/user-attachments/assets/e29ca5cb-c40c-4da0-8b8d-b63a37749c04) LISA: Backend 

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/your-org/lisa)
[![Python](https://img.shields.io/badge/python-3.11+-green)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-orange)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

##  Overview

LISA is a system for creating and managing agents that simulate legitimate user activity in cyber ranges and SOC training environments. The backend provides APIs for role management, behavior template creation, agent configuration generation, and CI/CD automation.


## Getting started

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/LISA-SWP25/backend.git
cd lisa/backend 
```
2. **Setup virtual environment**
```bash 
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```
3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL**
```bash 
createdb lisa_dev
createuser lisa --pwprompt
# Password: pass
```

5. **Start the server**
```bash 
uvicorn app.main:app --reload --port 8000
```

### Verify Installation
- API Health: http://localhost:8000/api/health
- API Documentation: http://localhost:8000/docs
- System Stats: http://localhost:8000/api/stats


## API Documentation

| Method |    Endpoint    |    Description    |
| ------ |     ------     |       ------      |
| POST   | /api/roles     | Create a new role |
| GET    | /api/roles     | List all roles    | 
| GET    | /api/roles/{id}| Get role details  | 
| PUT    | /api/roles/{id}| Update role       | 
| DELETE | /api/roles/{id}| Delete role       | 

## Behavior Templates

| Method |    Endpoint    |    Description    |
| ------ |     ------     |       ------      |
| POST   | /api/behavior-templates     | Create behavior template |
| GET    | /api/behavior-templates     | List templates   | 
| GET    | /api/behavior-templates/{id}| Get template details  | 

## Agent Management
| Method |    Endpoint    |    Description    |
| ------ |     ------     |       ------      |
| POST   | /api/agents/generate     | Generate agent configuration |
| GET    | /api/agents     | List all agents    | 
| GET    | /api/agents/{id}/status| Get agent status  | 
| GET    | /api/agents/{id}/config/download| Download config file       | 

## CI/CD Pipeline

| Method |    Endpoint    |    Description    |
| ------ |     ------     |       ------      |
| POST   | /api/builds    | Trigger agent build |
| GET    | /api/builds     | List builds    | 
| GET    | /api/builds/{id}| Get build status | 

## System

| Method |    Endpoint    |    Description    |
| ------ |     ------     |       ------      |
| GET    | /api/health     | System health check |
| GET    | /api/stats     | System statistics    | 
| GET    | /api/demo/workflow| Demo workflow  | 


## Usage Examples

### Create a Role
```bash
curl -X POST "http://localhost:8000/api/roles" \
-H "Content-Type: application/json" \
-d '{
  "name": "python_developer",
  "description": "Python developer working on web applications",
  "category": "developer"
}'
```

### Generate Agent Configuration
```bash
curl -X POST "http://localhost:8000/api/agents/generate" \
-H "Content-Type: application/json" \
-d '{
  "name": "Dev Agent 001",
  "role_id": 1,
  "template_id": 1,
  "os_type": "linux",
  "stealth_level": "medium"
}'
```
