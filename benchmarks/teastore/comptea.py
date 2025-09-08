import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Datos en texto plano
energy_data = """
==== Inicio de medición de energía sin plugin stand by====
Hora: mar. 08 juil. 2025 16:59:07 -05
Local Machine (luish-Nitro-AN515-57)
Average Power : 2.32 Watts
Total Energy : 30.13 Joules
Remote Machine (luish@luish-Aspire-A315-55G)
Average Power : 0.21 Watts
Total Energy : 3.01 Joules
Remote Machine (luish@luish-HP-Laptop-14-dq0xxx)
Average Power : 0.56 Watts
Total Energy : 6.77 Joules

==== Inicio de medición de energía con plugin stand by====
Hora: mar. 08 juil. 2025 17:33:54 -05
Local Machine (luish-Nitro-AN515-57)
Average Power : 0.91 Watts
Total Energy : 10.93 Joules
Remote Machine (luish@luish-Aspire-A315-55G)
Average Power : 0.20 Watts
Total Energy : 2.76 Joules
Remote Machine (luish@luish-HP-Laptop-14-dq0xxx)
Average Power : 0.47 Watts
Total Energy : 6.12 Joules

==== Inicio de medición de energía con plugin sobrecarga====
Hora: mar. 08 juil. 2025 18:09:43 -05
Local Machine (luish-Nitro-AN515-57)
Average Power : 0.98 Watts
Total Energy : 12.72 Joules
Remote Machine (luish@luish-Aspire-A315-55G)
Average Power : 0.19 Watts
Total Energy : 2.59 Joules
Remote Machine (luish@luish-HP-Laptop-14-dq0xxx)
Average Power : 0.29 Watts
Total Energy : 4.57 Joules

==== Inicio de medición de energía sin plugin sobrecarga====
Hora: mar. 08 juil. 2025 18:17:17 -05
Local Machine (luish-Nitro-AN515-57)
Average Power : 0.89 Watts
Total Energy : 11.61 Joules
Remote Machine (luish@luish-Aspire-A315-55G)
Average Power : 0.22 Watts
Total Energy : 2.58 Joules
Remote Machine (luish@luish-HP-Laptop-14-dq0xxx)
Average Power : 0.34 Watts
Total Energy : 5.39 Joules
"""

# Parsear el texto
def parse_energy_text(text):
    data = defaultdict(lambda: defaultdict(dict))
    current_exp = ""
    current_machine = ""

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("==== Inicio de medición"):
            match = re.search(r"energía (.*?)====", line)
            if match:
                current_exp = match.group(1).strip()
        elif line.startswith("Local Machine") or line.startswith("Remote Machine"):
            current_machine = line.strip()
        elif "Average Power" in line:
            value = float(re.search(r"([\d.]+)", line).group(1))
            data[current_exp][current_machine]["Average Power"] = value
        elif "Total Energy" in line:
            value = float(re.search(r"([\d.]+)", line).group(1))
            data[current_exp][current_machine]["Total Energy"] = value
    return data

data = parse_energy_text(energy_data)

# Clasificar experimentos
standby_exp = ["sin plugin stand by", "con plugin stand by"]
overload_exp = ["sin plugin sobrecarga", "con plugin sobrecarga"]
metrics = ["Total Energy", "Average Power"]
machines = sorted({m for e in data for m in data[e]})

# Función para graficar
def plot_comparison(title, exp_names, filename_prefix):
    for metric in metrics:
        fig, ax = plt.subplots(figsize=(10, 6))
        width = 0.35
        x = range(len(machines))

        for i, exp in enumerate(exp_names):
            values = [data[exp].get(machine, {}).get(metric, 0) for machine in machines]
            offset = (-width/2 if i == 0 else width/2)
            ax.bar([p + offset for p in x], values, width=width, label=exp, alpha=0.7)

        ax.set_title(f"{title} - {metric}")
        ax.set_ylabel(metric + (" (Joules)" if "Energy" in metric else " (Watts)"))
        ax.set_xticks(x)
        ax.set_xticklabels(machines, rotation=30, ha="right")
        ax.legend()
        plt.tight_layout()
        plt.savefig(f"{filename_prefix}_{metric.replace(' ', '_').lower()}.png")
        plt.show()

# Mostrar comparaciones
plot_comparison("Comparación Standby", standby_exp, "standby")
plot_comparison("Comparación Sobrecarga", overload_exp, "sobrecarga")
