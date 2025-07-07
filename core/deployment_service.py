import asyncio
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Optional

import paramiko
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Agent, AgentActivity
from app.core.config import settings

class DeploymentService:
    """Service for deploying agents to remote hosts"""
    
    def __init__(self):
        self.ssh_client = None
        self.sftp_client = None
    
    async def deploy_agent(
        self,
        agent: Agent,
        target_host: str,
        username: str,
        password: Optional[str] = None,
        ssh_key_path: Optional[str] = None,
        db: Session = None
    ) -> Dict:
        """Deploy agent to target host via SSH"""
        
        try:
            # Connect to host
            self._connect_ssh(target_host, username, password, ssh_key_path)
            
            # Generate agent configuration
            agent_config = self._generate_agent_config(agent)
            
            # Create remote directories
            self._create_remote_directories()
            
            # Deploy agent files
            self._deploy_agent_files(agent_config, agent.os_type)
            
            # Install and start agent service
            self._install_agent_service()
            
            # Update agent status in database
            if db:
                agent.status = "deployed"
                agent.injection_target = target_host
                agent.last_seen = datetime.utcnow()
                db.commit()
                
                # Log deployment
                activity = AgentActivity(
                    agent_id=agent.id,
                    activity_type="deployment_success",
                    activity_data={
                        "host": target_host,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                db.add(activity)
                db.commit()
            
            return {
                "status": "success",
                "message": f"Agent {agent.agent_id} deployed to {target_host}"
            }
            
        except Exception as e:
            if db:
                agent.status = "deployment_failed"
                db.commit()
                
                activity = AgentActivity(
                    agent_id=agent.id,
                    activity_type="deployment_error",
                    activity_data={
                        "error": str(e),
                        "host": target_host,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                db.add(activity)
                db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=f"Deployment failed: {str(e)}"
            )
        finally:
            self._disconnect_ssh()
    
    def _connect_ssh(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None
    ):
        """Establish SSH connection"""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if key_path and os.path.exists(key_path):
            # Use SSH key authentication
            self.ssh_client.connect(
                hostname=host,
                username=username,
                key_filename=key_path,
                timeout=30
            )
        elif password:
            # Use password authentication
            self.ssh_client.connect(
                hostname=host,
                username=username,
                password=password,
                timeout=30
            )
        else:
            raise ValueError("Either password or SSH key must be provided")
        
        self.sftp_client = self.ssh_client.open_sftp()
    
    def _disconnect_ssh(self):
        """Close SSH connections"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
    
    def _generate_agent_config(self, agent: Agent) -> Dict:
        """Generate agent configuration"""
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "role": {
                "name": agent.role.name,
                "description": agent.role.description,
                "category": agent.role.category
            },
            "behavior_template": agent.template.template_data,
            "server_url": settings.LISA_SERVER_URL,
            "check_in_interval": 60,
            "stealth_level": agent.stealth_level,
            "work_schedule": {
                "start_time": "09:00",
                "end_time": "18:00",
                "breaks": [
                    {"start": "13:00", "duration_minutes": 60}
                ]
            },
            "applications_used": [
                "Visual Studio Code",
                "Google Chrome",
                "Slack",
                "Terminal"
            ]
        }
    
    def _create_remote_directories(self):
        """Create necessary directories on remote host"""
        directories = [
            "/opt/lisa_agent",
            "/opt/lisa_agent/logs",
            "/opt/lisa_agent/plugins",
            "/var/log/lisa"
        ]
        
        for directory in directories:
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"sudo mkdir -p {directory}"
            )
            stdout.channel.recv_exit_status()
    
    def _deploy_agent_files(self, config: Dict, os_type: str):
        """Deploy agent binary and configuration"""
        # Transfer agent binary
        local_binary = f"agents/binaries/lisa_agent_{os_type.lower()}"
        remote_binary = "/opt/lisa_agent/lisa_agent"
        
        if os.path.exists(local_binary):
            self.sftp_client.put(local_binary, "/tmp/lisa_agent")
            self.ssh_client.exec_command(
                f"sudo mv /tmp/lisa_agent {remote_binary} && sudo chmod +x {remote_binary}"
            )
        else:
            # Create a simple Python agent as fallback
            self._create_python_agent()
        
        # Transfer configuration
        config_content = json.dumps(config, indent=2)
        with self.sftp_client.open("/tmp/agent_config.json", "w") as f:
            f.write(config_content)
        
        self.ssh_client.exec_command(
            "sudo mv /tmp/agent_config.json /opt/lisa_agent/config.json"
        )
    
    def _create_python_agent(self):
        """Create a simple Python-based agent"""
        agent_script = '''#!/usr/bin/env python3
import json
import time
import random
import requests
import subprocess
import platform
from datetime import datetime

def load_config():
    with open('/opt/lisa_agent/config.json', 'r') as f:
        return json.load(f)

def send_heartbeat(config):
    try:
        data = {
            "agent_id": config["agent_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "status": "active",
            "system_info": {
                "platform": platform.system(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            }
        }
        
        response = requests.post(
            f"{config['server_url']}/api/agents/{config['agent_id']}/heartbeat",
            json=data,
            timeout=10
        )
    except Exception as e:
        print(f"Heartbeat failed: {e}")

def simulate_activity(config):
    applications = config.get("applications_used", [])
    if applications:
        app = random.choice(applications)
        print(f"Simulating activity: Opening {app}")
        
        # Log activity
        with open('/var/log/lisa/agent.log', 'a') as f:
            f.write(f"{datetime.now()} - Activity: {app}\\n")

def main():
    config = load_config()
    print(f"LISA Agent {config['agent_id']} started")
    
    while True:
        # Send heartbeat
        send_heartbeat(config)
        
        # Simulate activity based on work schedule
        current_time = datetime.now().strftime("%H:%M")
        start_time = config["work_schedule"]["start_time"]
        end_time = config["work_schedule"]["end_time"]
        
        if start_time <= current_time <= end_time:
            simulate_activity(config)
        
        # Sleep with some randomness
        sleep_time = config.get("check_in_interval", 60) + random.randint(-10, 10)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
'''
        
        with self.sftp_client.open("/tmp/lisa_agent.py", "w") as f:
            f.write(agent_script)
        
        self.ssh_client.exec_command(
            "sudo mv /tmp/lisa_agent.py /opt/lisa_agent/lisa_agent && "
            "sudo chmod +x /opt/lisa_agent/lisa_agent"
        )
    
    def _install_agent_service(self):
        """Install agent as systemd service"""
        service_content = '''[Unit]
Description=LISA Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/lisa_agent
ExecStart=/usr/bin/python3 /opt/lisa_agent/lisa_agent
Restart=always
RestartSec=10
StandardOutput=append:/var/log/lisa/agent.log
StandardError=append:/var/log/lisa/agent.error.log

[Install]
WantedBy=multi-user.target
'''
        
        with self.sftp_client.open("/tmp/lisa-agent.service", "w") as f:
            f.write(service_content)
        
        # Install and start service
        commands = [
            "sudo mv /tmp/lisa-agent.service /etc/systemd/system/",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable lisa-agent",
            "sudo systemctl start lisa-agent"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode()
                raise Exception(f"Command failed: {cmd}, Error: {error}")
