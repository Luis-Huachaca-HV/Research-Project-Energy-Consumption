Scheduler-Plugins with EnergyScore ⚡️

This directory ships the EnergyScore plugin and the patches required to integrate it into the official Kubernetes Scheduler-Plugins project.

Usage 🛠️

Clone the official repo:

git clone https://github.com/kubernetes-sigs/scheduler-plugins.git
cd scheduler-plugins


Copy the EnergyScore plugin into the new pkg:

cp -r ../Research-Project-Energy-Consumption/scheduler-plugins/pkg/energyscore pkg/


Apply the patches:

git apply ../Research-Project-Energy-Consumption/scheduler-plugins/patches/*.patch


Copy configs:

cp ../Research-Project-Energy-Consumption/scheduler-plugins/configs/*.yaml ./config/

1. Install Go (latest version recommended)
sudo apt update
sudo apt install golang-go -y


Or grab the latest tarball from https://go.dev/dl/
.

2. Clean deps & fetch modules

From the root of scheduler-plugins:

go mod tidy

3. Build the scheduler
make build


This will generate the scheduler binary at:

_bin/kube-scheduler

4. Run your patched scheduler

Test it in your cluster (kind, minikube, whatever):

_bin/kube-scheduler --config energy-score-config.yaml --v=4

⚡ Notes

Changes in apis/config/v1/... and pkg/energyscore/ add new types + plugin logic → make sure your energy-score-config.yaml points to pkg/energyscore/.

If make build fails due to missing generated code (deepcopy, conversion, defaults), regenerate with:

make update


This runs hack/update-codegen.sh and refreshes the zz_generated.*.go files.

Quick & Dirty Re-run 🚀

Build your patched scheduler again:

cd scheduler-plugins
make build


→ Binary lands in _bin/kube-scheduler.

Launch it with your config (separate terminal):

_bin/kube-scheduler --config /path/to/energy-score-config.yaml --v=4


--config → must point to your YAML.

--v=4 → debug-level logs (handy to confirm EnergyScore is actually loaded).

This scheduler will run on your host, connected to the cluster, under the name energy-scheduler.

Use EnergyScore in Pods 🧪

Create a test pod (e.g. energy_test.yaml) with:

kubectl apply -f energy_test.yaml


And watch your pod get scheduled using the EnergyScore logic.