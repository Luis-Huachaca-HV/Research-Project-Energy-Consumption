#!/bin/bash

YAML_DIR="/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes"
# List of remote computers (replace with actual hostnames or IP addresses)
#kubectl apply -Rf "/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes"

remote_computers_list=("luish@luish-Aspire-A315-55G" "luish@luish-HP-Laptop-14-dq0xxx")

# Sudo password for remote machines
sudo_password="238244758"

# List of remote computers with their respective usernames and save paths
declare -A remote_computers_map
remote_computers_map["luish@luish-Aspire-A315-55G"]="/home/luish/Documents/p3/ecofloc2/ecofloc"
remote_computers_map["luish-HP-Laptop-14-dq0xxx"]="/home/luish/Documents/p3/ecofloc"

retrieve_pids() {
  local remote=$1
  local save_path=$2

  sshpass -p "$sudo_password" ssh -t $remote << EOF
    # Define keywords to search in /proc
    keywords=("kworker/R-inet_" "dockerd" "containerd" "containerd-shim" "docker-init" "buildkitd" "goa-daemon" "goa-identity-se" "code" "mongod" "mongo")

    # Initialize an array to store PIDs
    pids=()

    # Search in /proc
    for pid in \$(ls /proc | grep -E '^[0-9]+$'); do
      if [[ -f /proc/\$pid/comm ]]; then
        process_name=\$(cat /proc/\$pid/comm)
        for keyword in "\${keywords[@]}"; do
          if [[ "\$process_name" == *"\$keyword"* ]]; then
            pids+=("\$pid")
          fi
        done
      fi
    done

    # Get the PIDs of Kubernetes components
    k8s_components=("kube-apiserver" "kube-scheduler" "kube-controller-manager" "kubelet" "etcd")
    for component in "\${k8s_components[@]}"; do
      component_pids=\$(pgrep -f "\$component")
      if [ -n "\$component_pids" ]; then
        pids+=("\$component_pids")
      fi
    done

    # Get the PIDs of containerd
    containerd_pids=\$(pgrep -f "containerd")
    if [ -n "\$containerd_pids" ]; then
      pids+=("\$containerd_pids")
    fi

    # Get the PIDs of running containers in containerd
    container_pids=\$(echo "$sudo_password" | sudo -S ctr -n k8s.io tasks ls -q | xargs -I {} sudo ctr -n k8s.io tasks ps {} | awk 'NR>1 {print \$2}')
    if [ -n "\$container_pids" ]; then
      pids+=("\$container_pids")
    fi

    # Remove duplicates and filter out non-numeric entries
    unique_pids=\$(echo "\${pids[@]}" | tr ' ' '\\n' | grep -E '^[0-9]+$' | sort -u)

    # Save the PIDs to a file
    echo "\$unique_pids" > "$save_path/pids.txt"
EOF
}

retrieve_pids_local() {
  local save_path=$1

  # Define keywords to search in /proc
  keywords=("kworker/R-inet_" "dockerd" "containerd" "containerd-shim" "docker-init" "buildkitd" "goa-daemon" "goa-identity-se" "code" "mongod" "mongo")

  # Initialize an array to store PIDs
  pids=()

  # Search in /proc
  for pid in $(ls /proc | grep -E '^[0-9]+$'); do
    if [[ -f /proc/$pid/comm ]]; then
      process_name=$(cat /proc/$pid/comm)
      for keyword in "${keywords[@]}"; do
        if [[ "$process_name" == *"$keyword"* ]]; then
          pids+=("$pid")
        fi
      done
    fi
  done

  # Get the PIDs of Kubernetes components
  k8s_components=("kube-apiserver" "kube-scheduler" "kube-controller-manager" "kubelet" "etcd")
  for component in "${k8s_components[@]}"; do
    component_pids=$(pgrep -f $component)
    if [ -n "$component_pids" ]; then
      pids+=($component_pids)
    fi
  done

  # Get the PIDs of containerd
  containerd_pids=$(pgrep -f containerd)
  if [ -n "$containerd_pids" ]; then
    pids+=($containerd_pids)
  fi

  # Get the PIDs of running containers in containerd
  container_pids=$(echo "$sudo_password" | sudo -S ctr -n k8s.io tasks ls -q | xargs -I {} sudo ctr -n k8s.io tasks ps {} | awk 'NR>1 {print $2}')
  if [ -n "$container_pids" ]; then
    pids+=($container_pids)
  fi

  # Remove duplicates and filter out non-numeric entries
  unique_pids=($(echo "${pids[@]}" | tr ' ' '\n' | grep -E '^[0-9]+$' | sort -u))

  # Print all unique PIDs to pids.txt
  echo "${unique_pids[@]}" > $save_path/pids.txt
}

# Retrieve PIDs on local and remote computers
retrieve_pids_local "/home/luish/Documents/p3/ecofloc2/ecofloc"
for remote in "${!remote_computers_map[@]}"; do
  retrieve_pids $remote "${remote_computers_map[$remote]}"
done