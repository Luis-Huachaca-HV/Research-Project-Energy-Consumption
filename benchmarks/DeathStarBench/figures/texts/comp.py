import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Archivos de entrada
file_with_plugin = "energia_con_plugin.txt"
file_without_plugin = "energia_sin_plugin.txt"

# Función para parsear logs
def parse_energy_log(filepath):
    data = defaultdict(lambda: defaultdict(lambda: {"Average Power": [], "Total Energy": []}))
    current_experiment = ""
    current_machine = ""

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("Experiment:"):
                current_experiment = line.replace("Experiment:", "").strip()
            elif "Local Machine" in line or "Remote Machine" in line:
                current_machine = line.strip()
            elif "Average Power" in line:
                match = re.search(r"([\d\.]+)", line)
                if match:
                    value = float(match.group(1))
                    data[current_experiment][current_machine]["Average Power"].append(value)
            elif "Total Energy" in line:
                match = re.search(r"([\d\.]+)", line)
                if match:
                    value = float(match.group(1))
                    data[current_experiment][current_machine]["Total Energy"].append(value)
    return data

# Cargar datos
data_with = parse_energy_log(file_with_plugin)
data_without = parse_energy_log(file_without_plugin)

# Experimentos y máquinas únicas
experiments = sorted(set(data_with.keys()) | set(data_without.keys()))
machines = sorted(set(
    m for e in experiments for m in (data_with.get(e, {}) | data_without.get(e, {}))
))

# Función para calcular totales e imprimir resumen
def print_totals(data, tag):
    print(f"\n===== Totales para: {tag} =====")
    total_global = 0.0
    for machine in machines:
        total_machine = 0.0
        for exp in experiments:
            total_machine += sum(data.get(exp, {}).get(machine, {}).get("Total Energy", []))
        print(f"{machine} -> Total Energy: {total_machine:.2f} J")
        total_global += total_machine
    print(f"TOTAL ACUMULADO ({tag}): {total_global:.2f} J\n")

print_totals(data_with, "Con Plugin")
print_totals(data_without, "Sin Plugin")

# Plot de energía total y promedio
for metric in ["Total Energy", "Average Power"]:
    fig, ax = plt.subplots(figsize=(16, 8))
    x = range(len(experiments))

    # Acumuladores por experimento
    sums_with = []
    sums_without = []

    for machine in machines:
        y_with = []
        y_without = []

        for idx, exp in enumerate(experiments):
            val_with = sum(data_with.get(exp, {}).get(machine, {}).get(metric, []))
            val_without = sum(data_without.get(exp, {}).get(machine, {}).get(metric, []))
            y_with.append(val_with)
            y_without.append(val_without)

        # Dibujar curvas
        ax.plot(x, y_with, marker='o', label=f"{machine} (con plugin) - {metric}")
        ax.plot(x, y_without, marker='x', linestyle='--', label=f"{machine} (sin plugin) - {metric}")

    # Calcular y mostrar sumas por experimento
    for idx, exp in enumerate(experiments):
        total_with = sum(
            sum(data_with.get(exp, {}).get(machine, {}).get(metric, [])) for machine in machines
        )
        total_without = sum(
            sum(data_without.get(exp, {}).get(machine, {}).get(metric, [])) for machine in machines
        )
        sums_with.append(total_with)
        sums_without.append(total_without)

        # Anotar en gráfico
        ax.annotate(f"{total_with:.1f}", (idx, total_with), textcoords="offset points", xytext=(0, 5),
                    ha='center', fontsize=9, color='green')
        ax.annotate(f"{total_without:.1f}", (idx, total_without), textcoords="offset points", xytext=(0, -15),
                    ha='center', fontsize=9, color='red')

    # Etiquetas y leyenda
    ax.set_title(f"Comparación de '{metric}' con y sin plugin")
    ax.set_xlabel("Experimentos")
    ax.set_ylabel(f"{metric} (Watts o Joules)")
    ax.set_xticks(x)
    ax.set_xticklabels(experiments, rotation=45, ha="right")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()

    # Guardar imagen
    plt.savefig(f"comparacion_{metric.replace(' ', '_').lower()}.png")
    plt.show()
