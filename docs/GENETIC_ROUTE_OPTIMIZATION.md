# SafeRoute Saheli — Genetic Algorithm Route Optimizer

This document explains the soft computing **Multi-Objective Genetic Algorithm (GA)** utilized by SafeRoute Saheli to plan safe travel corridors for women.

---

## 1. Problem Formulation & Multi-Objective Objective Function

Finding an optimal path for women's safety is not simply finding the shortest geodesic distance. It requires balancing:
1. **Safety Score Maximization** (evaluated along all path segments by the ANFIS Neuro-Fuzzy engine).
2. **Distance & Travel Time Minimization** (avoiding unnecessarily long or exhausting detours).
3. **Safe Haven Proximity** (maximizing proximity to verified 24x7 police booths, hospitals, and open commercial sanctuaries).

### Multi-Objective Fitness Function:
For a candidate chromosome route $C$ consisting of waypoints $W = (w_1, w_2, \dots, w_K)$:

$$\text{Fitness}(C) = w_{\text{safety}} \cdot \bar{S}(C) - w_{\text{dist}} \cdot D(C) - w_{\text{time}} \cdot T(C) + w_{\text{haven}} \cdot H(C)$$

Where:
- $\bar{S}(C) = \frac{1}{K-1} \sum_{i=1}^{K-1} S_{\text{segment}}(w_i, w_{i+1})$ is the average ANFIS safety score.
- $D(C) = \sum_{i=1}^{K-1} \text{Haversine}(w_i, w_{i+1})$ is the total route distance in kilometers.
- $T(C)$ is estimated walking duration in minutes ($T = \frac{D}{4.5 \text{ km/h}} \times 60$).
- $H(C)$ is a bonus awarded for passing within 200m of verified safe points.

---

## 2. Genetic Algorithm Architecture

### Chromosome Representation
Each individual route chromosome is represented as an ordered sequence of GPS coordinates:
$$C = \left[ (lat_1, lon_1), (lat_2, lon_2), \dots, (lat_K, lon_K) \right]$$
with $w_1 = \text{Origin}$ and $w_K = \text{Destination}$.

### 1. Initialization
A population of $N=30$ candidate routes is initialized:
- Direct geodesic path with intermediate nodes.
- Randomized lateral corridor perturbations generating exploratory alternate thoroughfares.

### 2. Selection Operator
- **Tournament Selection ($k=3$):** 3 candidate routes are sampled randomly from the population, and the individual with the highest fitness is chosen as a parent.

### 3. Crossover Operator (Sub-tour Preservation)
- Two random intermediate waypoint indices $[i, j]$ are selected.
- Sub-tour waypoints between $i$ and $j$ are exchanged between Parent 1 and Parent 2 to produce two valid offspring routes while maintaining topological origin-destination continuity.

### 4. Mutation Operator (Corridor Divergence)
- With mutation probability $p_m = 0.20$, intermediate waypoints are perturbed by a Gaussian displacement vector $\mathcal{N}(0, \sigma^2)$ representing diversion into adjacent parallel avenues.

### 5. Elitism
- The top 2 fittest routes in each generation are preserved unchanged into the subsequent generation to prevent regression.

---

## 3. Tri-Profile Route Output

The genetic optimizer executes 25-50 generations in under 60 milliseconds on the backend, generating 3 distinct routes:
1. **Safest Route:** High safety weight ($w_{\text{safety}} = 0.75, w_{\text{dist}} = 0.25$). Avoids all high-crime or unlit pockets.
2. **Balanced Route:** Equal weighting ($w_{\text{safety}} = 0.50, w_{\text{dist}} = 0.50$). Optimal everyday commuter route.
3. **Fastest Route:** Distance minimized ($w_{\text{dist}} = 0.80, w_{\text{safety}} = 0.20$). Shortest path with real-time hazard warnings.
