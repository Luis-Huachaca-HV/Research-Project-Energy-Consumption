import matplotlib.pyplot as plt
import numpy as np

# File containing the energy results
input_file = "energy_results.txt"
output_file = "parsed_energy_resultsnic.txt"  # File to save the parsed results

# Initialize data structures
experiments = []
machine_data = {
    "luish-Nitro-AN515-57": [],
    "luish@luish-Aspire-A315-55G": [],
    "luish@luish-HP-Laptop-14-dq0xxx": []
}

# Parse the energy results file
with open(input_file, "r") as file:
    current_experiment = None
    current_machine = None
    for line in file:
        line = line.strip()
        if line.startswith("Experiment:"):
            # Extract the experiment name
            current_experiment = line.replace("Experiment: ", "")
            if current_experiment not in experiments:
                experiments.append(current_experiment)
        elif line.startswith("Local Machine"):
            current_machine = "luish-Nitro-AN515-57"
        elif line.startswith("Remote Machine (luish@luish-Aspire-A315-55G)"):
            current_machine = "luish@luish-Aspire-A315-55G"
        elif line.startswith("Remote Machine (luish@luish-HP-Laptop-14-dq0xxx)"):
            current_machine = "luish@luish-HP-Laptop-14-dq0xxx"
        elif "Total Energy" in line and current_machine:
            # Extract the energy value and associate it with the current machine
            energy_value = float(line.split(":")[-1].strip().replace("Joules", ""))
            machine_data[current_machine].append(energy_value)

# Ensure all machines have data for all experiments
for machine in machine_data:
    while len(machine_data[machine]) < len(experiments):
        machine_data[machine].append(0.0)

# Save the parsed data to a text file (append mode)
with open(output_file, "a") as file:
    file.write("Parsed Energy Results\n")
    file.write("=====================\n")
    file.write(f"Experiments: {', '.join(experiments)}\n\n")
    for machine, values in machine_data.items():
        file.write(f"{machine}:\n")
        for experiment, value in zip(experiments, values):
            file.write(f"  {experiment}: {value} Joules\n")
        file.write("\n")

# Debugging: Print parsed data
print("Parsed data appended to", output_file)

# Plot the data
x = np.arange(len(experiments))  # X-axis positions for experiments
width = 0.25  # Width of each bar
spacing = 0.1  # Additional spacing between experiment groups

fig, ax = plt.subplots(figsize=(12, 6))

# Plot bars for each machine
offset = -(width + spacing) * (len(machine_data) - 1) / 2  # Center the bars for each experiment
for machine, energy_values in machine_data.items():
    ax.bar(x + offset, energy_values, width, label=machine)
    offset += width + spacing

# Add labels, title, and legend
ax.set_xlabel("Experiments")
ax.set_ylabel("Total Energy (Joules)")
ax.set_title("Energy Consumption per Machine Across Experiments")
ax.set_xticks(x)
ax.set_xticklabels(experiments, rotation=45, ha="right")
ax.legend(title="Machines")

# Adjust layout and save the plot
plt.tight_layout()
plt.savefig("figures/sd6min15009nenergy_consumption.png")  # Save the plot as an image
plt.show()