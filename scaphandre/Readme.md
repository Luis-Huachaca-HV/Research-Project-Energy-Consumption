# Measuring Energy Consumption with Scaphandre ⚡

To measure **energy consumption** in our experiments, we use [Scaphandre](https://github.com/hubblo-org/scaphandre).

📚 Documentation: [Scaphandre Docs](https://hubblo-org.github.io/scaphandre-documentation/)

---

## 1. Installation

First, download and install Scaphandre for Linux.

- Repository: [https://github.com/hubblo-org/scaphandre](https://github.com/hubblo-org/scaphandre)  
- Compilation guide: [Compilation for Linux](https://hubblo-org.github.io/scaphandre-documentation/tutorials/compilation-linux.html)

You need to install **Cargo** and **Rust** to compile Scaphandre into an executable.  
Once compiled, you can either Make it globally (to execute from anywhere), or  Run it directly inside its directory.  

---

## 2. Running Scaphandre with Prometheus Exporter

After you have the `scaphandre` executable, use the **Prometheus exporter**:

```bash
sudo scaphandre prometheus
````

Expected output:

```
scaphandre::sensors: Sysinfo sees 16
Scaphandre prometheus exporter
Sending ⚡ metrics
Press CTRL-C to stop scaphandre
scaphandre::sensors: Not enough records for socket
```

---

## 3. Using a Custom Script

We created our own script (`scaphscript.sh`) to measure consumption for specific process names.

### Step 1 — Give execution permissions

```bash
chmod +x scaphscript.sh
```

### Step 2 — Run the script

```bash
./scaphscript.sh
```

Example output:

```
Fetching power consumption for Kubernetes-related processes...
Total filtered Power Consumption (µW): 0
Total filtered Power Consumption (µW): 0
Total filtered Power Consumption (µW): 2752.62
Total filtered Power Consumption (µW): 1519.49
Total filtered Power Consumption (µW): 3566.57
Script finished after 37 seconds.
Total Energy Consumption for PostgreSQL-Related Processes (J): .04703208000000000000
```

---

## 4. Customizing the Script

You can **modify the script** to gather more keynames and filter processes related to your experiment.
The script relies on the **Prometheus exporter** to collect and filter energy consumption data.

---

 With this setup, you can monitor and analyze the energy usage of specific processes in your Kubernetes experiments.

```
