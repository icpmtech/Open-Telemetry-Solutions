#!/bin/bash

# Criar pasta e permissões corretas
mkdir -p tempo-data
sudo chown -R 10001:10001 tempo-data

# Subir os serviços
docker-compose up -d
