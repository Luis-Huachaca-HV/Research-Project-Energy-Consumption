
---

# TeaStore Energy Experiments ☕⚡

This folder contains scripts, results, and configs for our energy consumption experiments using the [TeaStore microservice application](https://github.com/DescartesResearch/TeaStore).

---

## Structure 📂

* `comptea.py` – Python script for processing results.
* `energy_experimet.sh` – Shell script to run the energy consumption experiments.
* `energy_results_teastore.csv` – Collected energy measurements.
* `timestamps.csv` – Raw experiment timestamps.
* `httploadgenerator.jar` – Load generator used to stress TeaStore services.
* `examples/httploadgenerator/` – Folder with detailed CSV results from load tests.
* PNG files – Plots of average power and total energy usage during experiments.

---

## How to Reproduce 🧪

1. Clone the official TeaStore repo and deploy services:

   ```bash
   git clone https://github.com/DescartesResearch/TeaStore.git
   ```

2. Follow the installation guide there, then copy these experiment files into the repo folder and run as needed.

---

## Running the Experiment 🚀

1. Follow the TeaStore docs to deploy the experiment setup:
   👉 [https://github.com/DescartesResearch/TeaStore/blob/master/GET\_STARTED.md#13-run-the-teastore-on-a-kubernetes-cluster](https://github.com/DescartesResearch/TeaStore/blob/master/GET_STARTED.md#13-run-the-teastore-on-a-kubernetes-cluster)

2. Run the incremental request load generator in teastore.

3. Execute the script:

   ```bash
   ./gepids.sh
   ```

---


