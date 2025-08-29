# TeaStore Energy Experiments

This folder contains scripts, results, and configurations related to our energy consumption experiments using the [TeaStore microservice application](https://github.com/DescartesResearch/TeaStore).

## Structure

- `comptea.py` – Python script for processing results.
- `energy_experimet.sh` – Shell script used to run the energy consumption experiments.
- `energy_results_teastore.csv` – Collected energy measurements.
- `timestamps.csv` – Raw timestamps from experiments.
- `httploadgenerator.jar` – Load generator used to stress the TeaStore services.
- `examples/httploadgenerator/` – Folder containing detailed CSV results from load tests.
- PNG files – Graphs of average power and total energy consumption during experiments.

## How to Reproduce

1. Clone the official TeaStore repository and deploy the services:
   ```bash
   git clone https://github.com/DescartesResearch/TeaStore.git```

2. Follow the installation there and copy these files in the folder, then exe


## Ejecucion del Experimento

   Seguir la documentacion para desplegar la experimentacion: https://github.com/DescartesResearch/TeaStore/blob/master/GET_STARTED.md#13-run-the-teastore-on-a-kubernetes-cluster
   

   Ejecutar el experimento de generador de cargas de request incrementales.

   Ejecutar gepids.sh

