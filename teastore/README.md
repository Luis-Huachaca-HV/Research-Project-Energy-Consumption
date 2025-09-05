TeaStore Energy Experiments ☕⚡

This folder contains scripts, results, and configs for our energy consumption experiments using the TeaStore microservice application
.

Structure 📂

comptea.py – Python script for processing results.

energy_experimet.sh – Shell script to run the energy consumption experiments.

energy_results_teastore.csv – Collected energy measurements.

timestamps.csv – Raw experiment timestamps.

httploadgenerator.jar – Load generator used to stress TeaStore services.

examples/httploadgenerator/ – Folder with detailed CSV results from load tests.

PNG files – Plots of average power and total energy usage during experiments.

How to Reproduce 🧪

Clone the official TeaStore repo and deploy services:

git clone https://github.com/DescartesResearch/TeaStore.git


Follow the installation guide there, then copy these experiment files into the repo folder and run as needed.

Running the Experiment 🚀

Follow the TeaStore docs to deploy the experiment setup:
👉 https://github.com/DescartesResearch/TeaStore/blob/master/GET_STARTED.md#13-run-the-teastore-on-a-kubernetes-cluster

Run the incremental request load generator.

Execute the script:

./gepids.sh
