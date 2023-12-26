FROM python:3.10-bullseye

# Install SSH server
# Create an SSH user
# Allow SSH access
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      sudo \
      openssh-server \
    && useradd -rm -d /home/sshuser -s /bin/bash -g root -G sudo -u 1000 sshuser \
    && mkdir '/var/run/sshd' \
    && echo 'sshuser:password' | chpasswd    # Set the SSH user's password
# Expose the SSH port
EXPOSE 22
# Start SSH server on container startup
CMD ["/usr/sbin/sshd", "-D"]