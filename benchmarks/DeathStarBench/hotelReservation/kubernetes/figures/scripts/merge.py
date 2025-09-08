import matplotlib.pyplot as plt
import numpy as np

# File containing the parsed energy results
input_file = "parsed_energy_resultsnic.txt"

# Initialize data structures
experiment_names = []  # Names of experiments (e.g., nic 2000, nic 4000)
global_experiments = []  # Global list of experiment labels
machine_data = {}  # Dictionary to store energy data for each machine across experiments

# Parse the input file
with open(input_file, "r") as file:
    current_experiment_name = None
    current_machine = None
    for line in file:
        line = line.strip()
        if line.startswith("Parsed Energy Results"):
            # Extract the experiment name (e.g., nic 2000, nic 4000)
            current_experiment_name = line.replace("Parsed Energy Results", "").strip()
            experiment_names.append(current_experiment_name)
            if current_experiment_name not in machine_data:
                machine_data[current_experiment_name] = {}
        elif line.startswith("Experiments:"):
            # Extract the experiment labels (e.g., "1 CPU Configuration", etc.)
            experiments = [exp.strip() for exp in line.replace("Experiments:", "").split(",")]
            if not global_experiments:
                global_experiments = experiments
            elif experiments != global_experiments:
                raise ValueError("Mismatch in experiment labels across sections.")
        elif line.endswith(":") and not line.startswith("Experiments"):
            # Extract the machine name (e.g., luish-Nitro-AN515-57)
            current_machine = line.replace(":", "").strip()
            if current_machine not in machine_data[current_experiment_name]:
                machine_data[current_experiment_name][current_machine] = [None] * len(global_experiments)
        elif "Joules" in line and current_machine:
            # Extract the energy value and associate it with the current machine
            energy_value = float(line.split(":")[-1].strip().replace("Joules", ""))
            # Find the index of the experiment and store the energy value
            for i, exp in enumerate(global_experiments):
                if exp in line:
                    machine_data[current_experiment_name][current_machine][i] = energy_value
                    break

# Ensure all machines have the same number of energy values as the global experiments
for experiment_name, machines in machine_data.items():
    for machine in machines:
        while len(machine_data[experiment_name][machine]) < len(global_experiments):
            machine_data[experiment_name][machine].append(None)

# Plot the data
x = np.arange(len(global_experiments))  # X-axis positions for experiments
fig, ax = plt.subplots(figsize=(14, 8))

# Plot lines for each machine across all experiments
for experiment_name, machines in machine_data.items():
    for machine, energy_values in machines.items():
        # Replace None with 0 for plotting
        energy_values = [val if val is not None else 0 for val in energy_values]
        ax.plot(x, energy_values, marker='o', label=f"{machine} ({experiment_name})")

# Add labels, title, and legend
ax.set_xlabel("Experiments")
ax.set_ylabel("Total Energy (Joules)")
ax.set_title("Energy Consumption Comparison Across Machines and Experiments")
ax.set_xticks(x)
ax.set_xticklabels(global_experiments, rotation=45, ha="right")
ax.legend(title="Machines and Experiments", bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout and save the plot
plt.tight_layout()
plt.savefig("2merge.png")  # Save the plot as an image
plt.show()