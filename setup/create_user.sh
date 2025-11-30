sudo cat > /home/ubuntu/create_user.sh << 'EOF'
#!/bin/bash

# User creation script for SSH access with sudo privileges
# Run as: sudo ./create_user.sh username "public-key"

if [ $# -ne 2 ]; then
    echo "Usage: sudo $0 username \"ssh-public-key\""
    echo "Example: sudo $0 john \"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... user@email\""
    exit 1
fi

USERNAME="$1"
PUBLIC_KEY="$2"
DEFAULT_PASSWORD="1234"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run with sudo"
    exit 1
fi

echo "Creating sudo user: $USERNAME"

# Check if user exists
if id "$USERNAME" &>/dev/null; then
    echo "User $USERNAME already exists. Reconfiguring..."
    # Remove existing home directory to start fresh
    rm -rf /home/"$USERNAME"
    # Delete and recreate user
    userdel -r "$USERNAME" 2>/dev/null
fi

# Create new user with home directory and bash shell
useradd -m -s /bin/bash "$USERNAME"

# Add user to sudo group
usermod -aG sudo "$USERNAME"

# Set default password
echo "$USERNAME:$DEFAULT_PASSWORD" | chpasswd

# Create SSH directory
mkdir -p /home/"$USERNAME"/.ssh

# Add public key to authorized_keys
echo "$PUBLIC_KEY" > /home/"$USERNAME"/.ssh/authorized_keys

# Set proper permissions
chmod 700 /home/"$USERNAME"/.ssh
chmod 600 /home/"$USERNAME"/.ssh/authorized_keys
chown -R "$USERNAME":"$USERNAME" /home/"$USERNAME"/.ssh

echo "=== User $USERNAME created successfully ==="
echo "Username: $USERNAME"
echo "Password: $DEFAULT_PASSWORD"
echo "SSH Key: Configured"
echo "Sudo privileges: Enabled"
echo ""
echo "SSH access:"
echo "  ssh $USERNAME@154.114.52.192"
echo ""
echo "User can change password with: passwd"
echo "Home directory: /home/$USERNAME"
EOF
