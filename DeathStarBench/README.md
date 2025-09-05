
# DeathStarBench - Energy Experiments ⚡️

Repo for deploying and benchmarking **DeathStarBench**, focusing on the **HotelReservation** microservice on a Kubernetes cluster.  
Goal: measure **energy consumption** using **Ecofloc**.

---

## 1. Prerequisites

- Kubernetes cluster ready (recommended: 3 nodes → 1 master + 2 workers, same LAN).
- Docker + Docker Compose installed.
- Ubuntu 22.04 recommended.

### Docker

- **Option 1 (Docker Desktop):** [Install Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)  
- **Option 2 (Docker CLI + Compose, recommended):** [Guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)

### Kubernetes

Install `kubeadm` per [official docs](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm).

Verify nodes:

```bash
kubectl get nodes
````

---
Then you have to deploy the DB Architecture, following the tutorial of Death Star Bench.

## 2. Ecofloc Setup

Use a **specific fork/version** of Ecofloc (LUIS HUACHACA version) (https://github.com/Luis-Huachaca-HV/ecofloc-microservices/tree/energy-experiments).
Install on all nodes, configure `features.conf` and `settings.conf` per node.

---

## 3. Hosts & Node Communication

Edit `/etc/hosts` on each node to map hostnames → IPs.

Example master node:

```bash
127.0.0.1       localhost
127.0.1.1       luish-Nitro-AN515-57
192.168.18.35   luish-Nitro-AN515-57
192.168.18.30   luish-Aspire-A315-55G
192.168.18.29   luish-HP-Laptop-14-dq0xxx
```

Test SSH connectivity:

```bash
ssh user@hostname
```

---

## 4. Deploy HotelReservation

Follow DeathStarBench docs: [Kubernetes Deployment](https://github.com/delimitrou/DeathStarBench/tree/master/hotelReservation/kubernetes)

```bash
kubectl apply -Rf /path/to/DeathStarBench/hotelReservation/kubernetes/
kubectl get pods
```

Stop to collect PIDs:

```bash
kubectl delete -Rf /path/to/DeathStarBench/hotelReservation/kubernetes/
```

---

## 5. Collect Cluster PIDs for Ecofloc

`gepidsh.sh` gathers **PIDs per node** for Ecofloc.

Edit script with your paths:

```bash
YAML_DIR="/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes"
remote_computers_list=("luish@luish-Aspire-A315-55G" "luish@luish-HP-Laptop-14-dq0xxx")
sudo_password="238244758"

declare -A remote_computers_map
remote_computers_map["luish@luish-Aspire-A315-55G"]="/home/luish/Documents/p3/ecofloc"
remote_computers_map["luish@luish-HP-Laptop-14-dq0xxx"]="/home/luish/Documents/p3/ecofloc"
```

Run:

```bash
./gepidsh.sh
```

Check that `pids.txt` is updated on each node.

---

## 6. Run Experiment

1. Deploy cluster:

```bash
kubectl apply -Rf /path/to/DeathStarBench/hotelReservation/kubernetes/
```

2. Open 3 terminals:

* **Terminal 1 – Jaeger:**

```bash
kubectl port-forward svc/jaeger 16686:16686 -n default
```

* **Terminal 2 – Frontend:**

```bash
kubectl port-forward svc/frontend 5000:5000 -n default
```

* **Terminal 3 – Load Generation (`wrk`):**

```bash
wrk -t2 -c2 -d30 -L -s ./mixed-workload_type_1.lua http://localhost:5000 -R2
```

> Ensure `wrk` is installed: [Guide](https://nitikagarw.medium.com/getting-started-with-wrk-and-wrk2-benchmarking-6e3cdc76555f)

3. Run measurement script:

```bash
./deploycomp.sh
```

> `wrk` should run longer than `deploycomp.sh` to capture full metrics.

---

## 7. Results

Generated `.txt` files on the main node contain energy readings:

```
Experiment: CPU Request 1, CPU Limit 100m on 1 Nodes and Control Plane
Local Machine (luish-Nitro-AN515-57)
Average Power : 0.14 W
Total Energy : 2.77 J

Remote Machine (luish@luish-Aspire-A315-55G)
Average Power : 0.23 W
Total Energy : 4.34 J

Remote Machine (luish@luish-HP-Laptop-14-dq0xxx)
Average Power : 2.27 W
Total Energy : 45.44 J
```

Clean manually if extra chars appear.

---

## 8. Analysis & Graphs

Python scripts under `figures/scripts/` generate plots:

```bash
cd DeathStarBench/hotelReservation/kubernetes/figures/scripts/
python3 analisis.py
python3 comp.py
python3 graphics.py
python3 merge.py
python3 score.py
```

---

## 9. TL;DR Flow

1. Install Docker + Kubernetes
2. Setup 3-node cluster
3. Compile specific Ecofloc version
4. Configure `features.conf` & `settings.conf`
5. Update `/etc/hosts` for SSH
6. Run `gepidsh.sh` to collect PIDs
7. Deploy **HotelReservation**
8. Launch Jaeger, Frontend, `wrk`
9. Execute `deploycomp.sh`
10. Review results & generate plots

---

## Credits

* **Benchmark:** DeathStarBench
* **Profiler:** Ecofloc
* **Experiments by:** Luis Huachaca Vargas




---





# DeathStarBench

Open-source benchmark suite for cloud microservices. DeathStarBench includes five end-to-end services, four for cloud systems, and one for cloud-edge systems running on drone swarms. 

## End-to-end Services <img src="microservices_bundle4.png" alt="suite-icon" width="40"/>

* Social Network (released)
* Media Service (released)
* Hotel Reservation (released)
* E-commerce site (in progress)
* Banking System (in progress)
* Drone coordination system (in progress)

## License & Copyright 

DeathStarBench is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 2.

DeathStarBench is being developed by the [SAIL group](http://sail.ece.cornell.edu/) at Cornell University. 

## Publications

More details on the applications and a characterization of their behavior can be found at ["An Open-Source Benchmark Suite for Microservices and Their Hardware-Software Implications for Cloud and Edge Systems"](http://www.csl.cornell.edu/~delimitrou/papers/2019.asplos.microservices.pdf), Y. Gan et al., ASPLOS 2019. 

If you use this benchmark suite in your work, we ask that you please cite the paper above. 


## Beta-testing

If you are interested in joining the beta-testing group for DeathStarBench, send us an email at: <microservices-bench-L@list.cornell.edu>
