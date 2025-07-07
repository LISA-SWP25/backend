import paramiko
import json
import os
from typing import Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SSHDeploymentManager:
    """Manages SSH connections and agent deployments"""
    
    def __init__(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def connect(self, host: str, username: str, password: Optional[str] = None, 
                key_path: Optional[str] = None, port: int = 22):
        """Establish SSH connection to target host"""
        try:
            if key_path:
                self.ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    key_filename=key_path,
                    timeout=30
                )
            else:
                self.ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30
                )
            logger.info(f"Successfully connected to {host}")
            return True
        except Exception as e:
            logger.error(f"SSH connection failed: {str(e)}")
            raise
    
    def deploy_agent(self, agent_config: Dict, agent_binary_path: str):
        """Deploy agent to remote host"""
        try:
            # Create remote directory
            stdin, stdout, stderr = self.ssh_client.exec_command(
                "mkdir -p /opt/lisa_agent"
            )
            stdout.channel.recv_exit_status()
            
            # Transfer agent binary
            sftp = self.ssh_client.open_sftp()
            remote_agent_path = "/opt/lisa_agent/agent"
            sftp.put(agent_binary_path, remote_agent_path)
            sftp.chmod(remote_agent_path, 0o755)
            
            # Transfer config
            config_json = json.dumps(agent_config, indent=2)
            with sftp.open("/opt/lisa_agent/config.json", "w") as f:
                f.write(config_json)
            
            # Create systemd service
            service_content = self._generate_systemd_service()
            with sftp.open("/tmp/lisa-agent.service", "w") as f:
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
            
            logger.info("Agent deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise
    
    def _generate_systemd_service(self) -> str:
        """Generate systemd service file content"""
        return """[Unit]
Description=LISA Agent Service
After=network.target

[Service]
Type=simple
User=lisa
WorkingDirectory=/opt/lisa_agent
ExecStart=/opt/lisa_agent/agent
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    def check_agent_status(self) -> Dict:
        """Check if agent is running on remote host"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(
                "sudo systemctl status lisa-agent"
            )
            output = stdout.read().decode()
            exit_status = stdout.channel.recv_exit_status()
            
            return {
                "running": exit_status == 0,
                "output": output
            }
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {"running": False, "error": str(e)}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
