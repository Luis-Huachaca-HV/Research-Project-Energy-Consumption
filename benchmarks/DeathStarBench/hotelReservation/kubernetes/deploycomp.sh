#!/bin/bash

YAML_DIR="/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes"
# List of remote computers (replace with actual hostnames or IP addresses)
WRK_DIR="/home/luish/Documents/death/DeathStarBench/hotelReservation/wrk2/scripts/hotel-reservation"



remote_computers_list=("luish@luish-Aspire-A315-55G" "luish@luish-HP-Laptop-14-dq0xxx")

# Sudo password for remote machines
sudo_password="238244758"

# Function to measure energy consumption
measure_energy() {
  local interval=1000
  local duration=20
  local output_file="energy_results.txt"

  echo "Measuring energy consumption with interval $interval ms and duration $duration s"


  #/home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-sd/ecofloc-sd.out -n text -i $interval -t $duration 
  #sudo /home/luish/Documents/p3/ecofloc/ecofloc-nic/ecofloc-nic.out -n text -i $interval -t $duration -d -f
  #sudo /home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-ram/ecofloc-ram.out -n text -i $interval -t $duration 
  echo "Local Machine ($(hostname))" >> $output_file

  sudo /home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-cpu/ecofloc-cpu.out -n text -i $interval -t $duration | grep -E "Average Power|Total Energy" >> $output_file

  # Run the same commands on remote computers
    for remote in "${remote_computers_list[@]}"; do
    if [[ $remote == "luish@luish-HP-Laptop-14-dq0xxx" ]]; then
      #ssh -t $remote "/home/luish/Documents/p3/ecofloc/ecofloc-sd/ecofloc-sd.out -n text -i $interval -t $duration "
      #ssh -t $remote "echo $sudo_password | sudo -S /home/luish/Documents/p3/ecofloc/ecofloc-nic/ecofloc-nic.out -n text -i $interval -t $duration "
      #ssh -t $remote "echo $sudo_password | sudo -S /home/luish/Documents/p3/ecofloc/ecofloc-ram/ecofloc-ram.out -n text -i $interval -t $duration "
      echo "Remote Machine ($remote)" >> $output_file

      remote_output=$(ssh -tt $remote "echo 238244758 | sudo -S /home/luish/Documents/p3/ecofloc/ecofloc-cpu/ecofloc-cpu.out -n text -i $interval -t $duration | grep -E 'Average Power|Total Energy'")
      echo "$remote_output" >> $output_file
    else
      #ssh -t $remote " /home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-sd/ecofloc-sd.out -n text -i $interval -t $duration "
      #ssh -t $remote "echo $sudo_password | sudo -S /home/luish/Documents/p3/ecofloc/ecofloc-nic/ecofloc-nic.out -n text -i $interval -t $duration "
      #ssh -t $remote "echo $sudo_password | sudo -S /home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-ram/ecofloc-ram.out -n text -i $interval -t $duration "
      echo "Remote Machine ($remote)" >> $output_file

      remote_output=$(ssh -tt $remote "echo 238244758 | sudo -S /home/luish/Documents/p3/ecofloc2/ecofloc/ecofloc-cpu/ecofloc-cpu.out -n text -i $interval -t $duration | grep -E 'Average Power|Total Energy'") 
      echo "$remote_output" >> $output_file
    fi
  done
}
# Function to update CPU resources in the deployment YAML files
update_cpu_resources_in_yaml() {
  local yaml_file=$1
  local cpu_request=$2
  local cpu_limit=$3

  echo "Updating CPU resources in $yaml_file: requests=$cpu_request, limits=$cpu_limit"
  sed -i "/resources:/,/limits:/s/cpu: .*/cpu: \"$cpu_request\"/" $yaml_file
  sed -i "/limits:/,/requests:/s/cpu: .*/cpu: \"$cpu_limit\"/" $yaml_file
}



# Start port-forwarding
start_port_forwarding() {
  echo "Starting port-forwarding for frontend service..."
  kubectl port-forward svc/frontend 5000:5000 -n default &
  PORT_FORWARD_PID=$!
  sleep 5  # Give it time to establish
}

# Run workload using wrk2
run_workload() {
  echo "Running workload using wrk2..."
  cd "$WRK_DIR"
  wrk -t 8 -c 8 -d 1600 -L -s mixed-workload_type_1.lua http://localhost:5000 -R 1500
  cd - > /dev/null
}


# Stop workload
stop_workload() {
  echo "Stopping workload..."
  kill $WORKLOAD_PID
}
# Cleanup port-forwarding
cleanup_port_forwarding() {
  echo "Stopping port-forwarding..."
  kill $PORT_FORWARD_PID
}

kubectl apply -Rf "$YAML_DIR"

sleep 15
echo "Entering experiments"
# Start port-forwarding
#start_port_forwarding

# Start workload
#run_workload



# Function to update memory resources in the deployment YAML files
# Function to update memory resources in the deployment YAML files

# Function to cordon and uncordon nodes
scale_nodes() {
  local node=$1
  local action=$2

  if [ "$action" == "cordon" ]; then
    echo "Cordoning node $node"
    kubectl cordon $node
  elif [ "$action" == "uncordon" ]; then
    echo "Uncordoning node $node"
    kubectl uncordon $node
  fi
}

# Function to update replicas in the deployment YAML files
update_replicas_in_yaml() {
  local yaml_file=$1
  local replicas=$2

  echo "Updating replicas in $yaml_file: replicas=$replicas"
  sed -i "s/replicas: [0-9]*/replicas: $replicas/" $yaml_file
}

/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes/gepidsh.sh



# Experiment: CPU Configurations on Specific Nodes and Control Plane
for cpu_request in "1" "2"; do
  for cpu_limit in "100m" "200m"; do
    for num_nodes in 1 2; do
      echo "Experiment: CPU Request $cpu_request, CPU Limit $cpu_limit on $num_nodes Nodes and Control Plane" >> energy_results.txt
      
      # Cordon all nodes first
      for node in $(kubectl get nodes -o name); do
        kubectl cordon $node
      done

      # Uncordon the control plane
      kubectl uncordon "luish-nitro-an515-57"

      # Uncordon the required number of worker nodes
      active_nodes=0
      for node in $(kubectl get nodes -o name | grep -v "luish-nitro-an515-57"); do
        if [ $active_nodes -lt $num_nodes ]; then
          kubectl uncordon $node
          active_nodes=$((active_nodes + 1))
        fi
      done

      # Update CPU resources in YAML files
      for yaml_file in $YAML_DIR/*.yaml; do
        update_cpu_resources_in_yaml $yaml_file "$cpu_request" "$cpu_limit"
      done

      # Apply the updated YAML files
      kubectl apply -Rf $YAML_DIR
      sleep 15

      # Measure energy consumption
      measure_energy
    done
  done
done



# Experiment: Varying Deployment Replicas
for replicas in 1 3 5; do
  echo "Experiment: $replicas Replicas" >> energy_results.txt
  for yaml_file in $YAML_DIR/*.yaml; do
    update_replicas_in_yaml $yaml_file "$replicas"
  done
  kubectl apply -Rf $YAML_DIR
  sleep 15
  measure_energy
done




# Stop workload
#stop_workload

# Cleanup port-forwarding
#cleanup_port_forwarding

# Cleanup Kubernetes resources
kubectl delete -Rf "$YAML_DIR"



