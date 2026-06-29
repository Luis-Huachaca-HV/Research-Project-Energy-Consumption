import re
from collections import defaultdict

def parse_energy_results(file_path):
    """Parse the energy results file and extract data."""
    experiments = []
    current_experiment = None
    current_machine = None

    with open(file_path, 'r') as file:
        for line in file:
            # Match experiment headers
            experiment_match = re.match(r"Parsed Energy Results (.+) (\d+) (\d+) seconds", line)
            if experiment_match:
                if current_experiment:
                    experiments.append(current_experiment)
                current_experiment = {
                    "type": experiment_match.group(1).strip(),
                    "requests": int(experiment_match.group(2)),
                    "time": int(experiment_match.group(3)),
                    "machines": {}
                }
                continue

            # Match machine names
            machine_match = re.match(r"(\S+):", line)
            if machine_match:
                current_machine = machine_match.group(1).strip()
                current_experiment["machines"][current_machine] = {}
                continue

            # Match energy consumption records
            energy_match = re.match(r"\s+(.+):\s+([\d.]+) Joules", line)
            if energy_match and current_machine:
                metric = energy_match.group(1).strip()
                energy = float(energy_match.group(2))
                current_experiment["machines"][current_machine][metric] = energy

    if current_experiment:
        experiments.append(current_experiment)

    return experiments

def calculate_efficiency_scores(experiments):
    """Calculate efficiency scores for each machine based on energy consumption."""
    scores = defaultdict(float)

    for experiment in experiments:
        # Extract experiment details
        experiment_type = experiment["type"]
        requests = experiment["requests"]
        time = experiment["time"]
        machines = experiment["machines"]

        # Calculate a constant based on time and requests
        constant = requests / time

        # Normalize energy consumption for each metric
        for metric in set(metric for machine in machines.values() for metric in machine):
            max_energy = max(machine.get(metric, 0) for machine in machines.values())
            min_energy = min(machine.get(metric, 0) for machine in machines.values())

            for machine, metrics in machines.items():
                energy = metrics.get(metric, 0)
                if max_energy != min_energy:  # Avoid division by zero
                    normalized_energy = (energy - min_energy) / (max_energy - min_energy)
                else:
                    normalized_energy = 0  # All machines have the same energy for this metric

                # Assign scores: less energy gets more points
                scores[machine] += (1 - normalized_energy) * constant

    return scores

def rank_machines(scores):
    """Rank machines based on their efficiency scores."""
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# Example usage
file_path = "/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes/parsed_energy_resultsnic.txt"
experiments = parse_energy_results(file_path)
scores = calculate_efficiency_scores(experiments)
ranked_machines = rank_machines(scores)

# Print the rankings
print("Machine Rankings (Higher Score = More Efficient):")
for rank, (machine, score) in enumerate(ranked_machines, start=1):
    print(f"{rank}. {machine}: {score:.2f}")