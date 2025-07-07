# Setup SSH keys for LISA agent deployment
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "LISA SSH Key Setup"
echo "===================="

# Create SSH directory
SSH_DIR="./ssh-keys"
mkdir -p "$SSH_DIR"

# Generate SSH key pair for LISA
log_info "Generating SSH key pair for LISA..."

if [ ! -f "$SSH_DIR/lisa_deployment_key" ]; then
    ssh-keygen -t rsa -b 4096 -f "$SSH_DIR/lisa_deployment_key" -N "" -C "lisa-deployment@lisa-system"
    log_success "SSH key pair generated"
else
    log_warn "SSH key already exists, skipping generation"
fi

# Set proper permissions
chmod 600 "$SSH_DIR/lisa_deployment_key"
chmod 644 "$SSH_DIR/lisa_deployment_key.pub"

# Create SSH config for LISA
log_info "Creating SSH config..."

cat > "$SSH_DIR/ssh_config" << 'EOF'
# LISA SSH Configuration

# Default settings
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    PasswordAuthentication no
    PubkeyAuthentication yes
    IdentityFile /app/ssh-keys/lisa_deployment_key
    ConnectTimeout 10
    ServerAliveInterval 60
    ServerAliveCountMax 3

# Example target configurations
# Uncomment and modify as needed

# Host target-server-1
#     HostName 192.168.1.100
#     User deployer
#     Port 22
#     IdentityFile /app/ssh-keys/lisa_deployment_key

# Host target-server-2
#     HostName 10.0.0.50
#     User admin
#     Port 2222
#     IdentityFile /app/ssh-keys/lisa_deployment_key

# Host *.production.com
#     User deploy
#     Port 22
#     ProxyJump bastion.production.com
EOF

log_success "SSH config created"

# Create known_hosts file
touch "$SSH_DIR/known_hosts"

# Create authorized_keys template
log_info "Creating deployment instructions..."

cat > "$SSH_DIR/README.md" << EOF
# LISA SSH Key Deployment Guide

## Generated SSH Key

**Private Key**: \`lisa_deployment_key\`
**Public Key**: \`lisa_deployment_key.pub\`

## Public Key Content:
\`\`\`
$(cat "$SSH_DIR/lisa_deployment_key.pub")
\`\`\`

## Setup Instructions

### 1. Copy Public Key to Target Servers

For each target server where you want to deploy agents:

\`\`\`bash
# Method 1: Using ssh-copy-id (if available)
ssh-copy-id -i ./ssh-keys/lisa_deployment_key.pub user@target-server

# Method 2: Manual copy
cat ./ssh-keys/lisa_deployment_key.pub | ssh user@target-server "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"

# Method 3: Direct file copy
scp ./ssh-keys/lisa_deployment_key.pub user@target-server:~/.ssh/authorized_keys
\`\`\`

### 2. Test SSH Connection

\`\`\`bash
# Test connection using LISA's private key
ssh -i ./ssh-keys/lisa_deployment_key user@target-server

# Should connect without password
\`\`\`

### 3. Configure Target Hosts

Edit \`./ssh-keys/ssh_config\` to add your target servers:

\`\`\`
Host my-target-server
    HostName 192.168.1.100
    User deployer
    Port 22
    IdentityFile /app/ssh-keys/lisa_deployment_key
\`\`\`

### 4. Deploy Agent via LISA

\`\`\`bash
# Deploy agent to configured host
curl -X POST "http://localhost:8001/api/deploy" \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent_id": "USR1234567",
    "target_host": "my-target-server",
    "deployment_method": "ssh",
    "credentials": {
      "username": "deployer",
      "use_ssh_key": true
    },
    "install_location": "/opt/agents/",
    "auto_start": true
  }'
\`\`\`

## Security Best Practices

1. **Restrict SSH Key Usage**:
   - Use dedicated deployment user on target servers
   - Limit sudo/root access for deployment user
   - Consider using SSH certificates instead of keys

2. **Network Security**:
   - Use SSH jump hosts/bastions for production
   - Implement IP restrictions if possible
   - Monitor SSH access logs

3. **Key Rotation**:
   - Rotate SSH keys regularly (quarterly/annually)
   - Keep backup of old keys during transition
   - Update all target servers when rotating

## Troubleshooting

### Permission Issues
\`\`\`bash
# Fix SSH key permissions
chmod 600 ./ssh-keys/lisa_deployment_key
chmod 644 ./ssh-keys/lisa_deployment_key.pub

# Fix target server permissions
ssh user@target "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
\`\`\`

### Connection Testing
\`\`\`bash
# Verbose SSH connection test
ssh -v -i ./ssh-keys/lisa_deployment_key user@target-server

# Test from LISA dropper container
docker exec -it lisa_dropper ssh -i /app/ssh-keys/lisa_deployment_key user@target-server
\`\`\`
EOF

log_success "Deployment instructions created"

# Create SSH key management script
log_info "Creating SSH key management script..."

cat > "$SSH_DIR/manage-keys.sh" << 'EOF'
#!/bin/bash

# LISA SSH Key Management

case "$1" in
    "generate")
        echo "Generating new SSH key pair..."
        ssh-keygen -t rsa -b 4096 -f lisa_deployment_key_new -C "lisa-deployment@lisa-system"
        echo "New key generated: lisa_deployment_key_new"
        ;;
    "rotate")
        echo "Rotating SSH keys..."
        if [ -f "lisa_deployment_key_new" ]; then
            mv lisa_deployment_key lisa_deployment_key_backup_$(date +%Y%m%d)
            mv lisa_deployment_key.pub lisa_deployment_key.pub_backup_$(date +%Y%m%d)
            mv lisa_deployment_key_new lisa_deployment_key
            mv lisa_deployment_key_new.pub lisa_deployment_key.pub
            chmod 600 lisa_deployment_key
            chmod 644 lisa_deployment_key.pub
            echo "Key rotation completed. Update target servers with new public key."
        else
            echo "No new key found. Run 'generate' first."
        fi
        ;;
    "test")
        if [ -z "$2" ]; then
            echo "Usage: $0 test user@hostname"
            exit 1
        fi
        echo "Testing SSH connection to $2..."
        ssh -i lisa_deployment_key -o ConnectTimeout=5 "$2" "echo 'SSH connection successful'"
        ;;
    "copy")
        if [ -z "$2" ]; then
            echo "Usage: $0 copy user@hostname"
            exit 1
        fi
        echo "Copying public key to $2..."
        ssh-copy-id -i lisa_deployment_key.pub "$2"
        ;;
    "show-public")
        echo "LISA Public Key:"
        cat lisa_deployment_key.pub
        ;;
    *)
        echo "LISA SSH Key Management"
        echo "Usage: $0 {generate|rotate|test|copy|show-public}"
        echo ""
        echo "Commands:"
        echo "  generate     Generate new SSH key pair"
        echo "  rotate       Rotate to new key (requires generate first)"
        echo "  test HOST    Test SSH connection to host"
        echo "  copy HOST    Copy public key to host"
        echo "  show-public  Display public key"
        ;;
esac
EOF

chmod +x "$SSH_DIR/manage-keys.sh"

log_success "SSH key management script created"

# Display summary
echo ""
log_success "SSH key setup completed!"
echo ""
echo "Files created in $SSH_DIR/:"
echo "  • lisa_deployment_key       (Private key - keep secure!)"
echo "  • lisa_deployment_key.pub   (Public key - deploy to target servers)"
echo "  • ssh_config                (SSH configuration)"
echo "  • known_hosts               (Known hosts file)"
echo "  • README.md                 (Deployment instructions)"
echo "  • manage-keys.sh            (Key management script)"
echo ""
echo "Public Key (copy to target servers):"
echo "$(cat "$SSH_DIR/lisa_deployment_key.pub")"
echo ""
echo "Next Steps:"
echo "1. Copy public key to target servers:"
echo "   ssh-copy-id -i $SSH_DIR/lisa_deployment_key.pub user@target-server"
echo ""
echo "2. Test SSH connection:"
echo "   ssh -i $SSH_DIR/lisa_deployment_key user@target-server"
echo ""
echo "3. Configure target hosts in $SSH_DIR/ssh_config"
echo ""
echo "4. Restart LISA dropper to load SSH keys:"
echo "   docker-compose restart dropper"
echo ""
echo "Security Note: Keep the private key secure and never share it!"