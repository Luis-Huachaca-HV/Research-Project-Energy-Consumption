
# Research Project: Energy Consumption ⚡️🖥️  


This repo is a **lab playground** for energy consumption experiments across multiple distributed systems and benchmarks.  
Think of it as a **zoo of workloads + tools** wired up to measure CPU, RAM, and power usage with **Ecofloc** (our main energy profiler).


## Repo Map 🗺️  

```

Research-Project-Energy-Consumption/
│
├── ecofloc/             # Ecofloc profiler (energy measurements)
├── DeathStarBench/      # Social network microservices benchmark
├── mubench/             # Benchmarking framework (reference project)
├── teastore/            # Java EE microservice benchmark (TeaStore)
├── scheduler-plugins/   # Kubernetes scheduler extensions
└── README.md            # This file

````

Each subproject comes with its own quirks (and usually its own README).  
Some benchmarks are CPU/memory intensive, others are I/O heavy.  
Ecofloc lets us **track actual energy per container**, which is the whole point of this playground.  

---

## Setup 🔧  

### Prerequisites  

- Docker + Docker Compose  
- Kubernetes (for `scheduler-plugins`)  
- Python ≥ 3.10 (for Ecofloc tools)  
- A machine with RAPL or similar energy counters (otherwise Ecofloc is blind ⚡️👀)  

### Install Ecofloc  

Go here and install on every machine:
https://github.com/Luis-Huachaca-HV/ecofloc-microservices/tree/energy-experiments


---


## References 📚

* [Ecofloc](https://github.com/bsc-dom/eco-floc) – Energy profiler.
* [DeathStarBench](https://github.com/delimitrou/DeathStarBench) – Social network microservices benchmark.
* [mubench](https://github.com/mubench/mubench) – Generic benchmarking project.
* [TeaStore](https://github.com/DescartesResearch/TeaStore) – Microservice demo app.

---

