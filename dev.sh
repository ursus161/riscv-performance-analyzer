#!/bin/bash

COMPOSE="sudo docker compose -f docker/docker-compose.yml"
#salvez comanda de baza sa nu o rescriu de fiecare data


rebuild=false
[ "$1" = "--build" ] && rebuild=true #nu fac rebulid decat daca e flagul setat 

echo "Stopping Snap Docker..."
sudo snap stop docker 2>/dev/null || true # aici aveam conflict de dependinte snap cu apt care mi tinea portul 80 blocat


echo "Stopping containers..."
$COMPOSE down --remove-orphans 2>/dev/null || {
    echo "Stop failed, restarting Docker daemon..."
    sudo systemctl stop docker.socket docker
    sudo systemctl start docker
    sleep 2
}

echo "Freeing port 80..."
sudo fuser -k 80/tcp 2>/dev/null || true  #tot ce tine de portul 80 e curatat luna
sleep 1

echo "Starting..."
if $rebuild; then
    $COMPOSE up --build --force-recreate # primul flag recompileaza imaginile de docker si al doilea le reface de la zero 
else
    $COMPOSE up --force-recreate
fi
