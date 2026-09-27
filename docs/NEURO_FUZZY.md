# SafeRoute Saheli — ANFIS Neuro-Fuzzy Inference System

This document outlines the mathematical and architectural formulation of the **Adaptive Neuro-Fuzzy Inference System (ANFIS / Takagi-Sugeno)** powering the dynamic women safety risk engine in SafeRoute Saheli.

---

## 1. System Overview & Inputs

The system models complex, non-linear relationships between multi-sensor environmental telemetry, temporal vulnerability, and spatial crime history to output a continuous Risk Score $S \in [0, 100]$:

$$\text{Inputs: } \mathbf{x} = [x_1, x_2, x_3, x_4, x_5, x_6]^T$$

1. **$x_1$ (Lighting Level):** $x_1 \in [0.0, 1.0]$ ($0.0$ = dark unlit alley, $1.0$ = floodlit daylight)
2. **$x_2$ (Crowd Density):** $x_2 \in [0.0, 1.0]$ ($0.0$ = completely deserted, $1.0$ = active thoroughfare/market)
3. **$x_3$ (Police Proximity Distance):** Normalized distance to nearest verified police station $x_3 = \min(d / 5.0, 1.0)$
4. **$x_4$ (Time-of-Day Risk):** Diurnal risk function peaking during late night hours (22:00 to 04:00)
5. **$x_5$ (Historical Crime Index):** Spatial crime density coefficient $x_5 \in [0.0, 1.0]$
6. **$x_6$ (User Vulnerability):** User alert level or solo travel indicator $x_6 \in [0.0, 1.0]$

---

## 2. 5-Layer ANFIS Architecture

```
Layer 1: Fuzzification (Gaussian Membership Functions)
Layer 2: Rule Firing Strength (T-norm Product)
Layer 3: Normalization of Firing Strengths
Layer 4: Takagi-Sugeno Consequents (First-Order Polynomial)
Layer 5: Defuzzification (Weighted Sum Output)
```

### Layer 1: Fuzzification
Every input node evaluates membership degrees using Gaussian functions parameterized by center $\mu_{ij}$ and spread $\sigma_{ij}$:

$$\mu_{A_{ij}}(x_i) = \exp\left( -\frac{1}{2} \left( \frac{x_i - \mu_{ij}}{\sigma_{ij}} \right)^2 \right)$$

### Layer 2: Rule Firing Strength
Every rule node multiplies the incoming signals to determine rule activation strength:

$$w_k = \prod_{i=1}^{n} \mu_{A_{ik}}(x_i)$$

### Layer 3: Normalized Firing Strength
Computes the ratio of the $k$-th rule's firing strength to the sum of all firing strengths:

$$\bar{w}_k = \frac{w_k}{\sum_{m=1}^{M} w_m}$$

### Layer 4: Takagi-Sugeno Consequent Layer
Computes linear first-order polynomial functions for each rule:

$$f_k = \sum_{i=1}^{n} p_{ki} x_i + r_k$$

where $p_{ki}$ are learnable consequent coefficients and $r_k$ are rule bias terms.

### Layer 5: Overall Defuzzification Output
The final overall safety risk score is computed as the normalized weighted sum:

$$S = \sum_{k=1}^{M} \bar{w}_k f_k, \quad S \in [0.0, 100.0]$$

---

## 3. Safety Score & Classification

The SafeRoute Saheli Safety Score is defined as the complement:

$$\text{Safety Score} = 100.0 - S$$

| Risk Score Range | Safety Level | Actionable Dispatch Recommendation |
| :--- | :--- | :--- |
| **0.0 – 24.9** | **VERY_SAFE** | Well-lit, populated arterial route. Normal travel. |
| **25.0 – 44.9** | **LOW_RISK** | Normal vigilance recommended. |
| **45.0 – 69.9** | **MODERATE_RISK** | Stay on main roads. Inform guardians via Active Companion mode. |
| **70.0 – 100.0** | **HIGH_DANGER** | Avoid corridor. Genetic routing automatically seeks safe detour. |
