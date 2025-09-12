#!/bin/bash

echo "Fetching power consumption for Kubernetes-related processes..."

duration=36
start_time=$(date +%s)
sampling_interval=6
energy=0

while true; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [[ $elapsed_time -ge $duration ]]; then
        echo "Script finished after $elapsed_time seconds."
        break
    fi
    #change kubernetes - docker to put your names for your experiment related processes
    postgres_power=$(curl -s http://localhost:8080/metrics | awk '
    /scaph_process_power_consumption_microwatts/ {
        # Extraer cmdline y exe directamente
        if ($0 ~ /cmdline="[^"]*kubernetes[^"]*"/ || $0 ~ /exe="[^"]*docker[^"]*"/) {
            n = split($0, parts, "} ")
            power = parts[2] + 0
            if (power > 0) {
                total += power
            }
        }
    }
    END {
        print total
    }
')


    postgres_power=${postgres_power:-0}
    echo "Total filtered Power Consumption (µW): $postgres_power"

    # Calcular energía (J = W * s)
    power_in_watts=$(echo "$postgres_power / 1000000" | bc -l)
    energy_for_interval=$(echo "$power_in_watts * $sampling_interval" | bc -l)
    energy=$(echo "$energy + $energy_for_interval" | bc -l)

    sleep 2
done

echo "Total Energy Consumption for PostgreSQL-Related Processes (J): $energy"
