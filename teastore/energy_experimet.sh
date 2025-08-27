#!/bin/bash

# -------------------- CONFIGURACIÓN --------------------

# IP o hostname donde se ejecuta el LIMBO loadgenerator
LOADGENERATOR_HOST="192.168.18.30"

# Ruta al directorio base del TeaStore
TEASTORE_DIR="/home/luish/Documents/death/teastore/TeaStore/examples/httploadgenerator"

# Archivos de carga
JAR_FILE="$TEASTORE_DIR/httploadgenerator.jar"
LUA_SCRIPT="$TEASTORE_DIR/teastore_browse.lua"
CSV_PROFILE="$TEASTORE_DIR/increasingLowIntensity.csv"

# ecofloc CPU local
ECOFLOC_CPU_LOCAL="/home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-cpu/ecofloc-cpu.out"
DURATION=20        # en segundos (por el CSV)
INTERVAL=1000       # intervalo de muestreo en ms
SUDO_PASS="238244758"

# Asociación nodo -> ruta ecofloc-cpu
declare -A REMOTE_ECOFLOC_PATHS
REMOTE_ECOFLOC_PATHS["luish@luish-Aspire-A315-55G"]="/home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-cpu/ecofloc-cpu.out"
REMOTE_ECOFLOC_PATHS["luish@luish-HP-Laptop-14-dq0xxx"]="/home/luish/Documents/p3/ecofloc/ecofloc-cpu/ecofloc-cpu.out"

# Lista de nodos
REMOTE_NODES=("luish@luish-Aspire-A315-55G" "luish@luish-HP-Laptop-14-dq0xxx")

# Archivos de salida
ENERGY_OUTPUT="energy_results_teastore.csv"
LOAD_OUTPUT="limbo_results_teastore.csv"

/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes/gepidsh.sh

# -------------------- EJECUCIÓN ------------------------


# -------------------- MEDICIÓN DE ENERGÍA --------------------

echo "==== Inicio de medición de energía ====" >> "$ENERGY_OUTPUT"
echo "Hora: $(date)" >> "$ENERGY_OUTPUT"

# Medición en máquina local
echo "Local Machine ($(hostname))" >> "$ENERGY_OUTPUT"
echo "$SUDO_PASS" | sudo -S "$ECOFLOC_CPU_LOCAL" -n text -i $INTERVAL -t $DURATION | grep -E "Average Power|Total Energy" >> "$ENERGY_OUTPUT"

# Medición en máquinas remotas con sus rutas específicas
for NODE in "${REMOTE_NODES[@]}"; do
  ECOFLOC_REMOTE=${REMOTE_ECOFLOC_PATHS[$NODE]}
  echo "Remote Machine ($NODE)" >> "$ENERGY_OUTPUT"
  ssh -tt "$NODE" "echo $SUDO_PASS | sudo -S $ECOFLOC_REMOTE -n text -i $INTERVAL -t $DURATION | grep -E 'Average Power|Total Energy'" >> "$ENERGY_OUTPUT"
done

# Esperar a que LIMBO termine

# -------------------- FIN -----------------------------

echo "=== Fin del experimento ==="
echo "Resultados:"
echo "  - Carga HTTP: $LOAD_OUTPUT"
echo "  - Energía CPU: $ENERGY_OUTPUT"
