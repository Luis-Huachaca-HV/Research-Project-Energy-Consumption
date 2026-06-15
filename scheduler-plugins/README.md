# EnergyScore Scheduler Artifact

This directory contains the scheduler-side artifact for LLAPA: a Kubernetes `ScorePlugin` called `EnergyScore`, the patch set required to register it in `scheduler-plugins`, and the configuration used to run it as `energy-scheduler`.

![Scheduler evolution](../assets/scheduler-evolution.svg)

## What is implemented here

The code currently stored in [pkg/energyscore/energyscore.go](/home/luish/Documents/repoluispro/Research-Project-Energy-Consumption/scheduler-plugins/pkg/energyscore/energyscore.go) is the first working scheduler version:

- it reads one node label, `energy-score`;
- it multiplies that value by `weightMultiplier`;
- it returns the result during the scheduler scoring phase.

This is the minimal scheduler artifact that proves the full integration path:

- plugin registration through the `cmd/scheduler/main.go` patch;
- scheduler configuration through `configs/energy-score-config.yaml`;
- pod-level usage through `schedulerName: energy-scheduler`.

## Why version 1 still matters

`v1` is intentionally simple. It does not yet consume the full LLAPA profile, but it verifies the hard part first: running a custom Kubernetes scheduler that can bias placement with an external energy signal.

In other words, `v1` established the scheduling hook before the multi-device model was ready.

## Version 2 direction

The follow-up scheduler notes from the active development workspace define `v2` as the LLAPA-aligned refinement:

- replace the single label with per-device labels;
- combine device-level energy with current node load;
- normalize and damp the score so energy influences scheduling without overwhelming standard Kubernetes placement logic.

The four labels proposed for `v2` are:

- `energy.cpu.j`
- `energy.ram.j`
- `energy.nic.j`
- `energy.sd.j`

The conceptual improvement is straightforward: `v1` says “this node is globally efficient,” while `v2` says “this node is efficient for the devices this microservice actually stresses.”

## How it connects to the paper

Section 5 of the paper introduced an initial energy-aware scheduler driven by LLAPA profiles. This directory is the implementation artifact for that line of work:

- `v1` maps to the first pluginized scheduler integration.
- `v2` maps to the next multi-component scoring model that better matches the paper’s device-aware motivation.

## Evaluation & Results

For a complete performance and energy consumption analysis comparing `v2` vs `v1` and the baseline (including throughput, request execution success, and per-microservice profile graphs), please see the **[V2 vs V1 Evaluation & Comparison Report](COMPARISON.md)**.

## Files

- [pkg/energyscore/energyscore.go](/home/luish/Documents/repoluispro/Research-Project-Energy-Consumption/scheduler-plugins/pkg/energyscore/energyscore.go): current `v1` plugin implementation.
- [configs/energy-score-config.yaml](/home/luish/Documents/repoluispro/Research-Project-Energy-Consumption/scheduler-plugins/configs/energy-score-config.yaml): scheduler config for `energy-scheduler`.
- [configs/podep.yaml](/home/luish/Documents/repoluispro/Research-Project-Energy-Consumption/scheduler-plugins/configs/podep.yaml): sample pod/deployment manifest.
- [configs/test-pod.yaml](/home/luish/Documents/repoluispro/Research-Project-Energy-Consumption/scheduler-plugins/configs/test-pod.yaml): simple test pod.
- `patches/*.patch`: changes required to register the plugin inside the upstream `scheduler-plugins` project.

## Build and run

1. Clone upstream `scheduler-plugins`.
2. Copy `pkg/energyscore`.
3. Apply the patches from this repo.
4. Copy the YAML config files.
5. Run `make build`.
6. Start the binary with `--config energy-score-config.yaml`.

Example:

```bash
git clone https://github.com/kubernetes-sigs/scheduler-plugins.git
cd scheduler-plugins
cp -r ../Research-Project-Energy-Consumption/scheduler-plugins/pkg/energyscore pkg/
git apply ../Research-Project-Energy-Consumption/scheduler-plugins/patches/*.patch
cp ../Research-Project-Energy-Consumption/scheduler-plugins/configs/*.yaml ./config/
make build
_bin/kube-scheduler --config ./config/energy-score-config.yaml --v=4
```

## Present limitation

The repository code is still `v1`. If you want the scheduler to consume the same four-device view that LLAPA produces for TeaStore and µBench, the next implementation step is to encode those device-level values as per-node labels or another scheduler-visible input and extend `EnergyScore` accordingly.
