import re
import json

# Archivo de entrada
log_file = "/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes/parsed_energy_resultsnic.txt"

# Pesos para cada métrica
weights = {
    "nic": 0.25,
    "cpu": 0.35,
    "sd": 0.25,
    "ram": 0.15
}

# Función para normalizar valores
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value) * 100

# Leer y procesar el archivo
def process_log(file_path):
    data = {}
    current_experiment = None
    current_node = None

    with open(file_path, "r") as file:
        for line in file:
            # Detectar el inicio de un experimento
            if "Parsed Energy Results" in line:
                current_experiment = line.strip()
                data[current_experiment] = {}
            # Detectar el nodo
            elif re.match(r"^\s*\w+@", line) or re.match(r"^\s*\w+-", line):
                current_node = line.strip().replace(":", "")
                data[current_experiment][current_node] = {}
            # Detectar métricas
            elif ":" in line and current_node:
                metric, value = line.split(":")
                metric = metric.strip()
                value = float(value.strip().split()[0])  # Extraer el valor numérico
                data[current_experiment][current_node][metric] = value

    return data

# Calcular puntajes
def calculate_scores(data):
    scores = {}

    for experiment, nodes in data.items():
        scores[experiment] = {}
        for node, metrics in nodes.items():
            # Normalizar métricas
            normalized_metrics = {}
            for metric, value in metrics.items():
                min_value = min(metrics.values())
                max_value = max(metrics.values())
                normalized_metrics[metric] = normalize(value, min_value, max_value)

            # Calcular puntaje total
            total_score = sum(
                weights.get(metric.lower(), 0) * normalized_metrics[metric]
                for metric in normalized_metrics
            )
            scores[experiment][node] = round(total_score, 2)

    return scores

# Exportar resultados a JSON
def export_to_json(data, output_file):
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)

# Procesar el log y calcular puntajes
data = process_log(log_file)
scores = calculate_scores(data)

# Exportar los puntajes
output_file = "/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes/energy_scores.json"
export_to_json(scores, output_file)

print(f"Puntajes calculados y exportados a {output_file}")