package energyscore

import (
	"context"
	"fmt"
	"math"
	"strconv"
	"strings"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/klog/v2"
	fwk "k8s.io/kubernetes/pkg/scheduler/framework"
	"sigs.k8s.io/scheduler-plugins/apis/config"
)

const Name = "EnergyScore"

// Per-component energy label keys set by the external scoring tool (main2.py).
const (
	labelCPU = "energy-score-cpu"
	labelRAM = "energy-score-ram"
	labelNIC = "energy-score-nic"
	labelSD  = "energy-score-sd"
)

// hwComponent identifies a hardware component tracked by Ecofloc.
type hwComponent int

const (
	hwCPU hwComponent = iota
	hwRAM
	hwNIC
	hwSD
)

// loadThresholds are the dynamic scheduling limits (percent, 0-100).
// The algorithm tries them in order from lowest to highest, skipping those
// already exceeded by the hottest node in the cluster.
var loadThresholds = []float64{0, 25, 50, 75, 100}

// componentWeights maps priority rank (0=primary … 3=least) to score weight.
// Primary component gets 50 % of the energy score, last gets 5 %.
var componentWeights = [4]float64{0.50, 0.30, 0.15, 0.05}

// rawServiceEnergy holds per-microservice component energy averages.
// Values are normalized per service before scoring.
var rawServiceEnergy = map[string]map[hwComponent]float64{
	"auth": {
		hwCPU: 47.9225333333,
		hwRAM: 33.4647666667,
		hwNIC: 0.0,
		hwSD:  4.9939666667,
	},
	"db": {
		hwCPU: 2.5029666667,
		hwRAM: 1.7891,
		hwNIC: 0.0,
		hwSD:  148.0105666667,
	},
	"persistence": {
		hwCPU: 66.11125,
		hwRAM: 27.4251,
		hwNIC: 0.0,
		hwSD:  0.51335,
	},
	"recommender": {
		hwCPU: 27.2603,
		hwRAM: 16.4238666667,
		hwNIC: 0.0,
		hwSD:  0.4012666667,
	},
	"webui": {
		hwCPU: 127.0389,
		hwRAM: 94.2190333333,
		hwNIC: 0.0,
		hwSD:  1.9492333333,
	},
	"image": {
		hwCPU: 29.3875,
		hwRAM: 32.85185,
		hwNIC: 0.0,
		hwSD:  64.3662,
	},
	"registry": {
		hwCPU: 5.66165,
		hwRAM: 4.69335,
		hwNIC: 0.0,
		hwSD:  0.5975,
	},
}

var normalizedServiceEnergy = normalizeServiceEnergy(rawServiceEnergy)

// servicePriority maps known TeaStore service name fragments to their
// hardware component priority (most power-draining first).
//
// Source: measured workload profiles:
//
//	webui        → cpu, ram, sd, nic
//	teastore-image → sd, cpu, ram, nic
//	persistence  → cpu, ram, sd, nic
//	auth         → cpu, ram, sd, nic
//	db           → cpu, sd, ram, nic
//	registry     → cpu, ram, sd, nic
//	recommender  → cpu, ram, sd, nic
var servicePriority = map[string][]hwComponent{
	"webui":       {hwCPU, hwRAM, hwSD, hwNIC},
	"image":       {hwSD, hwCPU, hwRAM, hwNIC},
	"persistence": {hwCPU, hwRAM, hwSD, hwNIC},
	"auth":        {hwCPU, hwRAM, hwSD, hwNIC},
	"db":          {hwCPU, hwSD, hwRAM, hwNIC},
	"registry":    {hwCPU, hwRAM, hwSD, hwNIC},
	"recommender": {hwCPU, hwRAM, hwSD, hwNIC},
}

var defaultPriority = []hwComponent{hwCPU, hwRAM, hwSD, hwNIC}

// EnergyScore scores nodes using per-component energy efficiency labels and a
// dynamic load-threshold algorithm.
//
// For each pod the plugin:
//  1. Finds the hottest node in the cluster (max combined load).
//  2. Determines which hardware components the pod stresses most (by service name).
//  3. Iterates load thresholds [0 % → 25 % → 50 % → 75 % → 100 %], skipping
//     thresholds already exceeded by the hottest node.
//  4. At the first threshold where this node can accept the pod (projected load
//     ≤ threshold), assigns a score = 60 % × threshold-headroom + 40 % × weighted
//     component energy score.
//
// NormalizeScore then applies soft damping so EnergyScore acts as a tie-breaker
// and does not override NodeResourcesFit / BalancedAllocation.
type EnergyScore struct {
	handle           fwk.Handle
	weightMultiplier float64
}

var _ fwk.ScorePlugin = &EnergyScore{}

func (es *EnergyScore) Name() string { return Name }

// ── Score ─────────────────────────────────────────────────────────────────────

func (es *EnergyScore) Score(
	ctx context.Context,
	state *fwk.CycleState,
	pod *corev1.Pod,
	nodeName string,
) (int64, *fwk.Status) {

	nodeInfo, err := es.handle.SnapshotSharedLister().NodeInfos().Get(nodeName)
	if err != nil {
		return 0, fwk.NewStatus(fwk.Error, err.Error())
	}
	node := nodeInfo.Node()
	if node == nil {
		return 0, fwk.NewStatus(fwk.Error, "node info has nil node")
	}

	// 1. Find the load of the hottest node in the cluster.
	hotLoad := clusterHotLoad(es.handle)

	// 2. Compute this node's current and projected load (after hypothetically
	//    adding the pod).
	currentLoad := computeNodeLoad(nodeInfo)
	delta := podLoadDelta(pod, nodeInfo)
	projectedLoad := clamp01(currentLoad + delta)

	// 3. Per-component energy preferences from per-service normalized profiles.
	serviceName := podServiceName(pod)
	servicePrefs := serviceComponentScores(serviceName)

	// 4. Node's actual efficiency labels (cpu, ram, etc.)
	nodeEfficiencies := readComponentScores(node)

	// 5. Pod's component priority based on service name.
	priority := podComponentPriority(pod)

	// 6. Weighted energy score: Combined efficiency of the node for the pod's specific needs.
	// We multiply the node's efficiency by the pod's component preference.
	weightedEnergy := 0.0
	for rank, hw := range priority {
		// A high weightedEnergy means the node is efficient in the components the pod needs most.
		weightedEnergy += componentWeights[rank] * (nodeEfficiencies[hw] * servicePrefs[hw] / 100.0)
	}

	// 6. Dynamic threshold pass (pseudocode translation).
	//    Find the lowest threshold this node fits in, skipping those already
	//    exceeded by the hottest node.
	bestThresholdScore := -1.0
	for _, limitPct := range loadThresholds {
		limit := limitPct / 100.0

		// Skip thresholds already exceeded by the hottest node — no point
		// trying to fill a band the cluster has already blown past.
		if limit < hotLoad {
			continue
		}

		if projectedLoad <= limit {
			// Lower threshold = more headroom = higher priority.
			// 0 % → 100 pts, 25 % → 75 pts, 50 % → 50 pts, 75 % → 25 pts, 100 % → 0 pts.
			bestThresholdScore = 100.0 - limitPct
			break
		}
	}

	var rawScore float64
	if bestThresholdScore < 0 {
		// Cannot accommodate the pod at any threshold level.
		rawScore = 0
	} else {
		// 60 % load-headroom awareness + 40 % energy efficiency for the pod's
		// primary components.
		rawScore = 0.60*bestThresholdScore + 0.40*weightedEnergy
	}

	score := int64(math.Round(clamp(rawScore, 0, float64(fwk.MaxNodeScore))))

	klog.V(5).InfoS("EnergyScore: score calculated",
		"pod", pod.Name,
		"node", nodeName,
		"hotLoad", fmt.Sprintf("%.3f", hotLoad),
		"currentLoad", fmt.Sprintf("%.3f", currentLoad),
		"projectedLoad", fmt.Sprintf("%.3f", projectedLoad),
		"thresholdScore", fmt.Sprintf("%.1f", bestThresholdScore),
		"weightedEnergy", fmt.Sprintf("%.2f", weightedEnergy),
		"finalScore", score,
	)

	return score, fwk.NewStatus(fwk.Success)
}

// ── NormalizeScore ────────────────────────────────────────────────────────────

// NormalizeScore applies soft damping so EnergyScore functions as a tie-breaker.
// With default weightMultiplier=1.0 and dampingFactor=0.20 the max spread between
// best and worst node is ~20 points out of 100, leaving primary scheduling decisions
// to NodeResourcesFit and BalancedAllocation.
func (es *EnergyScore) NormalizeScore(
	ctx context.Context,
	state *fwk.CycleState,
	pod *corev1.Pod,
	scores fwk.NodeScoreList,
) *fwk.Status {
	if len(scores) == 0 {
		return fwk.NewStatus(fwk.Success)
	}

	var maxScore int64
	minScore := int64(math.MaxInt64)
	for i := range scores {
		if scores[i].Score > maxScore {
			maxScore = scores[i].Score
		}
		if scores[i].Score < minScore {
			minScore = scores[i].Score
		}
	}

	midPoint := fwk.MaxNodeScore / 2

	if maxScore == minScore {
		for i := range scores {
			scores[i].Score = midPoint
		}
		return fwk.NewStatus(fwk.Success)
	}

	const dampingFactor = 0.20
	effectiveDamping := clamp(dampingFactor*es.weightMultiplier, 0, 1)

	for i := range scores {
		normalized := int64(math.Round(float64(scores[i].Score-minScore) * float64(fwk.MaxNodeScore) / float64(maxScore-minScore)))
		scores[i].Score = midPoint + int64(float64(normalized-midPoint)*effectiveDamping)
		klog.V(5).InfoS("EnergyScore: normalized+damped",
			"pod", pod.Name,
			"node", scores[i].Name,
			"rawNormalized", normalized,
			"effectiveDamping", fmt.Sprintf("%.3f", effectiveDamping),
			"dampedScore", scores[i].Score,
		)
	}

	return fwk.NewStatus(fwk.Success)
}

func (es *EnergyScore) ScoreExtensions() fwk.ScoreExtensions { return es }

// ── New ───────────────────────────────────────────────────────────────────────

func New(_ context.Context, obj runtime.Object, handle fwk.Handle) (fwk.Plugin, error) {
	args, ok := obj.(*config.EnergyScoreArgs)
	if !ok {
		return nil, fmt.Errorf("expected EnergyScoreArgs, got %T", obj)
	}
	wm := args.WeightMultiplier
	if wm <= 0 {
		wm = 1.0
	}
	return &EnergyScore{handle: handle, weightMultiplier: wm}, nil
}

// ── Internal helpers ──────────────────────────────────────────────────────────

// clusterHotLoad returns the combined load ratio of the most-loaded node.
func clusterHotLoad(handle fwk.Handle) float64 {
	allNodes, err := handle.SnapshotSharedLister().NodeInfos().List()
	if err != nil {
		return 0
	}
	hot := 0.0
	for _, ni := range allNodes {
		if l := computeNodeLoad(ni); l > hot {
			hot = l
		}
	}
	return hot
}

// computeNodeLoad returns the combined load ratio [0,1] for a node.
// 70 % weight on the dominant CPU/mem ratio, 30 % on pod density.
func computeNodeLoad(nodeInfo *fwk.NodeInfo) float64 {
	node := nodeInfo.Node()
	if node == nil {
		return 0
	}

	var usedCPU, usedMem int64
	for _, pi := range nodeInfo.Pods {
		if pi == nil || pi.Pod == nil {
			continue
		}
		c, m := podRequests(pi.Pod)
		usedCPU += c
		usedMem += m
	}

	var capCPU, capMem, capPods int64
	if qty, ok := node.Status.Allocatable[corev1.ResourceCPU]; ok {
		capCPU = qty.MilliValue()
	}
	if qty, ok := node.Status.Allocatable[corev1.ResourceMemory]; ok {
		capMem = qty.Value()
	}
	if qty, ok := node.Status.Allocatable[corev1.ResourcePods]; ok {
		capPods = qty.Value()
	}
	if capPods <= 0 {
		capPods = 110
	}

	cpuRatio := ratio(usedCPU, capCPU)
	memRatio := ratio(usedMem, capMem)
	dominant := maxFloat64(cpuRatio, memRatio)
	podDensity := float64(len(nodeInfo.Pods)) / float64(capPods)

	return 0.7*clamp01(dominant) + 0.3*clamp01(podDensity)
}

// podLoadDelta estimates the fractional load the pod would add to the node.
// Uses the same 70/30 weights as computeNodeLoad so that projectedLoad = currentLoad + delta
// stays on the same scale and threshold comparisons are correct.
func podLoadDelta(pod *corev1.Pod, nodeInfo *fwk.NodeInfo) float64 {
	node := nodeInfo.Node()
	if node == nil {
		return 0
	}
	podCPU, podMem := podRequests(pod)

	var capCPU, capMem, capPods int64
	if qty, ok := node.Status.Allocatable[corev1.ResourceCPU]; ok {
		capCPU = qty.MilliValue()
	}
	if qty, ok := node.Status.Allocatable[corev1.ResourceMemory]; ok {
		capMem = qty.Value()
	}
	if qty, ok := node.Status.Allocatable[corev1.ResourcePods]; ok {
		capPods = qty.Value()
	}
	if capPods <= 0 {
		capPods = 110
	}

	dominant := maxFloat64(ratio(podCPU, capCPU), ratio(podMem, capMem))
	podDensityDelta := 1.0 / float64(capPods)
	return 0.7*clamp01(dominant) + 0.3*clamp01(podDensityDelta)
}

// readComponentScores reads the four per-component energy labels from a node.
// Returns 50.0 (neutral) for any label that is absent or unparseable.
// Labels with value 0 are treated as missing (node has no data for that component).
func readComponentScores(node *corev1.Node) map[hwComponent]float64 {
	scores := map[hwComponent]float64{
		hwCPU: 50.0,
		hwRAM: 50.0,
		hwNIC: 50.0,
		hwSD:  50.0,
	}
	labelKeys := map[hwComponent]string{
		hwCPU: labelCPU,
		hwRAM: labelRAM,
		hwNIC: labelNIC,
		hwSD:  labelSD,
	}
	for hw, key := range labelKeys {
		if val, ok := node.Labels[key]; ok {
			if parsed, err := strconv.ParseFloat(val, 64); err == nil && parsed > 0 {
				scores[hw] = clamp(parsed, 0, 100)
			}
			// parsed == 0 → missing data, keep neutral 50
		}
	}
	return scores
}

// podComponentPriority returns the hardware component order for the pod's
// service type, detected from the pod's app labels or name.
func podComponentPriority(pod *corev1.Pod) []hwComponent {
	for _, key := range []string{
		"app",
		"app.kubernetes.io/name",
		"app.kubernetes.io/component",
	} {
		if name, ok := pod.Labels[key]; ok {
			if prio, found := matchService(strings.ToLower(name)); found {
				return prio
			}
		}
	}
	if prio, found := matchService(strings.ToLower(pod.Name)); found {
		return prio
	}
	return defaultPriority
}

func matchService(s string) ([]hwComponent, bool) {
	for svc, prio := range servicePriority {
		if strings.Contains(s, svc) {
			return prio, true
		}
	}
	return nil, false
}

func podServiceName(pod *corev1.Pod) string {
	for _, key := range []string{
		"app",
		"app.kubernetes.io/name",
		"app.kubernetes.io/component",
	} {
		if name, ok := pod.Labels[key]; ok {
			if svc, found := matchServiceName(strings.ToLower(name)); found {
				return svc
			}
		}
	}
	if svc, found := matchServiceName(strings.ToLower(pod.Name)); found {
		return svc
	}
	return ""
}

func matchServiceName(s string) (string, bool) {
	for svc := range servicePriority {
		if strings.Contains(s, svc) {
			return svc, true
		}
	}
	return "", false
}

func serviceComponentScores(serviceName string) map[hwComponent]float64 {
	neutral := map[hwComponent]float64{
		hwCPU: 50.0,
		hwRAM: 50.0,
		hwNIC: 50.0,
		hwSD:  50.0,
	}
	if serviceName == "" {
		return neutral
	}
	if comps, ok := normalizedServiceEnergy[serviceName]; ok {
		return comps
	}
	return neutral
}

func normalizeServiceEnergy(raw map[string]map[hwComponent]float64) map[string]map[hwComponent]float64 {
	result := map[string]map[hwComponent]float64{}
	for serviceName, comps := range raw {
		minVal := math.MaxFloat64
		maxVal := -math.MaxFloat64
		for _, hw := range []hwComponent{hwCPU, hwRAM, hwNIC, hwSD} {
			val := comps[hw]
			if val < minVal {
				minVal = val
			}
			if val > maxVal {
				maxVal = val
			}
		}

		normComps := map[hwComponent]float64{}
		for _, hw := range []hwComponent{hwCPU, hwRAM, hwNIC, hwSD} {
			if maxVal == minVal {
				normComps[hw] = 50.0
				continue
			}
			normComps[hw] = clamp((comps[hw]-minVal)/(maxVal-minVal)*100.0, 0, 100)
		}
		result[serviceName] = normComps
	}
	return result
}

// ── Low-level helpers (unchanged from original) ───────────────────────────────

func clamp01(v float64) float64 { return clamp(v, 0, 1) }

func clamp(v, lo, hi float64) float64 {
	if v < lo {
		return lo
	}
	if v > hi {
		return hi
	}
	return v
}

func ratio(used, capacity int64) float64 {
	if capacity <= 0 || used <= 0 {
		return 0
	}
	return float64(used) / float64(capacity)
}

func maxFloat64(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}

func maxInt64(a, b int64) int64 {
	if a > b {
		return a
	}
	return b
}

func podRequests(pod *corev1.Pod) (int64, int64) {
	if pod == nil {
		return 0, 0
	}

	var appCPU, appMem int64
	for i := range pod.Spec.Containers {
		if qty, ok := pod.Spec.Containers[i].Resources.Requests[corev1.ResourceCPU]; ok {
			appCPU += qty.MilliValue()
		}
		if qty, ok := pod.Spec.Containers[i].Resources.Requests[corev1.ResourceMemory]; ok {
			appMem += qty.Value()
		}
	}

	var maxInitCPU, maxInitMem int64
	for i := range pod.Spec.InitContainers {
		var initCPU, initMem int64
		if qty, ok := pod.Spec.InitContainers[i].Resources.Requests[corev1.ResourceCPU]; ok {
			initCPU = qty.MilliValue()
		}
		if qty, ok := pod.Spec.InitContainers[i].Resources.Requests[corev1.ResourceMemory]; ok {
			initMem = qty.Value()
		}
		maxInitCPU = maxInt64(maxInitCPU, initCPU)
		maxInitMem = maxInt64(maxInitMem, initMem)
	}

	effectiveCPU := maxInt64(appCPU, maxInitCPU)
	effectiveMem := maxInt64(appMem, maxInitMem)

	if qty, ok := pod.Spec.Overhead[corev1.ResourceCPU]; ok {
		effectiveCPU += qty.MilliValue()
	}
	if qty, ok := pod.Spec.Overhead[corev1.ResourceMemory]; ok {
		effectiveMem += qty.Value()
	}

	return effectiveCPU, effectiveMem
}
