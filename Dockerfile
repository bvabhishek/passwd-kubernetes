# File: Dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    sudo \
    passwd \
    python3 \
    vim \
    libpam-modules \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m attacker && echo "attacker:attacker" | chpasswd

# Dangerous permissions
RUN chmod 666 /etc/passwd && chmod 666 /etc/shadow

USER attacker
WORKDIR /home/attacker

COPY passwd.py .

CMD ["/bin/bash"]
