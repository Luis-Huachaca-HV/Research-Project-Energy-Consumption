Research Project: Energy Consumption ⚡️🖥️

This repo is a lab playground for energy consumption experiments across multiple distributed systems and benchmarks.
Think of it as a zoo of workloads + tools wired up to measure CPU, RAM, and power usage with Ecofloc
 (our main energy profiler).

Repo Map 🗺️
Research-Project-Energy-Consumption/
│
├── ecofloc/             # Ecofloc profiler (energy measurements)
├── DeathStarBench/      # Social network microservices benchmark
├── mubench/             # Benchmarking framework (reference project)
├── teastore/            # Java EE microservice benchmark (TeaStore)
├── scheduler-plugins/   # Kubernetes scheduler extensions
└── README.md            # This file


Each subproject comes with its own quirks (and usually its own README).
Some benchmarks are CPU/memory intensive, others are I/O heavy. Ecofloc lets us track actual energy per container, which is the whole point of this playground.

Setup 🔧
Prerequisites

Docker + Docker Compose

Kubernetes (for scheduler-plugins)

Python ≥ 3.10 (for Ecofloc tools)

A machine with RAPL or similar energy counters (otherwise Ecofloc is blind ⚡️👀)

Install Ecofloc

Clone and build Ecofloc (inside this repo):

cd ecofloc
make build


Check it runs:

./ecofloc -h

How Energy Is Measured 🔋

First, we collect the PID(s) of running containers.

Then, Ecofloc attaches to those PIDs and tracks energy counters.

There are two main ways to launch Ecofloc:

Threaded mode (manual attach) – you grab container PIDs and run Ecofloc per PID.

Namespace mode (-n) – Ecofloc auto-attaches to the container namespace (easier for batch experiments).

👉 In this repo, we use the -n mode most of the time (see examples in ecofloc/README.md).

Running Benchmarks ⚙️
DeathStarBench
cd DeathStarBench
./run.sh


Monitor with Ecofloc in namespace mode:

./ecofloc -n <container_name_or_ns> -o results.json

TeaStore
cd teastore
docker-compose up -d


Track CPU/RAM + energy:

./ecofloc -n teastore_webui -o teastore_energy.json

CPU + RAM Metrics 📊

Besides energy, we log CPU and memory stats via:

docker stats --no-stream > resource_usage.log


Or, for more reproducible runs:

./ecofloc -n <container> --track-cpu --track-ram -o combined_metrics.json


This way, we can correlate power ↔ CPU ↔ memory usage per workload.

References 📚

Ecofloc
 – Energy profiler.

DeathStarBench
 – Social network microservices benchmark.

mubench
 – Generic benchmarking project.

TeaStore
 – Microservice demo app.

👉 With this structure:

You’ve got one global README (this one) with the overview.

Each benchmark/tool keeps its own README.md with deployment quirks.

No local machine paths (~/Documents/...) are exposed.