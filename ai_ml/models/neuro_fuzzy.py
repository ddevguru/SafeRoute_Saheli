"""
SafeRoute Saheli — Neuro-Fuzzy Inference System (ANFIS / Takagi-Sugeno)
Evaluates dynamic women safety risk score S in [0, 100] based on multi-factor sensory & contextual inputs:
1. Lighting Level (0.0 to 1.0)
2. Crowd Density (0.0 to 1.0)
3. Police Proximity Distance in km (0.0 to 10.0)
4. Time-of-Day Risk (0.0 to 1.0)
5. Historical Crime Index (0.0 to 1.0)
6. User Vulnerability Index (0.0 to 1.0)
"""

import math
import numpy as np
import torch
import torch.nn as nn

class GaussianMembership(nn.Module):
    """Layer 1: Fuzzification using learnable Gaussian membership functions"""
    def __init__(self, num_inputs, num_rules):
        super().__init__()
        # Initialize centers (mu) and spreads (sigma)
        self.mu = nn.Parameter(torch.rand(num_inputs, num_rules))
        self.sigma = nn.Parameter(torch.ones(num_inputs, num_rules) * 0.3)

    def forward(self, x):
        # x shape: (batch_size, num_inputs) -> expand to (batch_size, num_inputs, num_rules)
        x_exp = x.unsqueeze(2)
        diff = x_exp - self.mu.unsqueeze(0)
        membership = torch.exp(-0.5 * (diff / (self.sigma.unsqueeze(0) + 1e-6)) ** 2)
        return membership


class ANFISRiskModel(nn.Module):
    """
    5-Layer Adaptive Neuro-Fuzzy Inference System (Takagi-Sugeno Model)
    """
    def __init__(self, num_inputs=6, num_rules=8):
        super().__init__()
        self.num_inputs = num_inputs
        self.num_rules = num_rules

        # Layer 1: Gaussian Membership Functions
        self.fuzzification = GaussianMembership(num_inputs, num_rules)

        # Layer 4: Takagi-Sugeno Consequent Parameters: f_i = p_i1 * x_1 + ... + p_in * x_n + r_i
        self.consequent_weights = nn.Parameter(torch.randn(num_rules, num_inputs) * 0.1)
        self.consequent_biases = nn.Parameter(torch.zeros(num_rules))

        self._initialize_expert_rules()

    def _initialize_expert_rules(self):
        """Seed initial weights with domain expert knowledge for women safety"""
        with torch.no_grad():
            # Input order: [lighting, crowd, police_dist_norm, time_risk, crime_score, vulnerability]
            # Rule 0: Safe conditions (High light, high crowd, near police, day time, low crime) -> Very Low Risk
            # Rule 1: High danger (Dark, isolated, far police, late night, high crime) -> Very High Risk
            # Rule 2: Night isolation with low lighting -> High Risk
            # Rule 3: Crowded daytime market -> Low Risk
            # Rule 4: Moderate lighting, moderate crowd, night -> Moderate Risk
            # Rule 5: User distressed/vulnerable -> Escalated Risk
            
            # Calibrate centers (mu)
            # Lighting
            self.fuzzification.mu.data[0] = torch.tensor([0.9, 0.1, 0.1, 0.8, 0.5, 0.4, 0.7, 0.3])
            # Crowd
            self.fuzzification.mu.data[1] = torch.tensor([0.9, 0.05, 0.1, 0.8, 0.4, 0.2, 0.6, 0.1])
            # Police dist norm (0 = adjacent, 1 = >5km)
            self.fuzzification.mu.data[2] = torch.tensor([0.1, 0.9, 0.8, 0.2, 0.5, 0.6, 0.3, 0.7])
            # Time risk (0 = noon, 1 = 2 AM)
            self.fuzzification.mu.data[3] = torch.tensor([0.1, 0.95, 0.9, 0.2, 0.7, 0.8, 0.3, 0.85])
            # Crime score
            self.fuzzification.mu.data[4] = torch.tensor([0.05, 0.95, 0.7, 0.1, 0.5, 0.6, 0.2, 0.8])
            # Vulnerability
            self.fuzzification.mu.data[5] = torch.tensor([0.1, 0.9, 0.6, 0.1, 0.4, 0.95, 0.2, 0.7])

            # Calibrate spreads (sigma)
            self.fuzzification.sigma.data.fill_(0.25)

            # Consequent biases (Base risk score output per rule: 0 to 100)
            self.consequent_biases.data = torch.tensor([5.0, 95.0, 80.0, 12.0, 48.0, 88.0, 20.0, 75.0])

    def forward(self, x):
        """
        x: Tensor of shape (batch_size, 6)
        Returns: Tensor of risk scores in [0, 100] of shape (batch_size, 1)
        """
        batch_size = x.shape[0]

        # Layer 1: Membership values (batch_size, num_inputs, num_rules)
        mu = self.fuzzification(x)

        # Layer 2: Rule Firing Strengths (T-norm product across inputs)
        # Shape: (batch_size, num_rules)
        w = torch.prod(mu, dim=1) + 1e-7

        # Layer 3: Normalized Firing Strengths
        w_sum = torch.sum(w, dim=1, keepdim=True)
        w_norm = w / w_sum  # Shape: (batch_size, num_rules)

        # Layer 4: Consequent evaluation (Takagi-Sugeno linear function)
        # f_i = sum_j(p_ij * x_j) + r_i
        # Shape: (batch_size, num_rules)
        linear_terms = torch.matmul(x, self.consequent_weights.t())  # (batch_size, num_rules)
        consequents = linear_terms + self.consequent_biases.unsqueeze(0)

        # Layer 5: Defuzzification (Weighted sum)
        # Risk Score = sum_i (w_norm_i * consequent_i)
        risk_score = torch.sum(w_norm * consequents, dim=1, keepdim=True)

        # Clamp output strictly in [0.0, 100.0]
        risk_score = torch.clamp(risk_score, 0.0, 100.0)
        return risk_score

    def predict_risk(self, lighting: float, crowd: float, police_dist_km: float, 
                     time_risk: float, crime_score: float, vulnerability: float = 0.5) -> dict:
        """
        Convenience inference method returning structured risk analysis.
        """
        self.eval()
        with torch.no_grad():
            police_dist_norm = min(max(police_dist_km / 5.0, 0.0), 1.0)
            inp = torch.tensor([[
                float(lighting),
                float(crowd),
                float(police_dist_norm),
                float(time_risk),
                float(crime_score),
                float(vulnerability)
            ]], dtype=torch.float32)

            score = self.forward(inp).item()
            score = round(max(0.0, min(100.0, score)), 1)

            # Categorize risk level
            if score < 25.0:
                level = "VERY_SAFE"
                color = "#10B981"
                recommendation = "Path is well-lit, populated, and close to emergency help."
            elif score < 45.0:
                level = "LOW_RISK"
                color = "#3B82F6"
                recommendation = "Normal caution advised. Route is generally safe."
            elif score < 70.0:
                level = "MODERATE_RISK"
                color = "#F59E0B"
                recommendation = "Exercise vigilance. Stay on primary roads and inform guardian."
            else:
                level = "HIGH_DANGER"
                color = "#EF4444"
                recommendation = "Avoid this route if possible! Take alternative well-lit arterial roads or enable Active Companion mode."

            return {
                "risk_score": score,
                "safety_score": round(100.0 - score, 1),
                "level": level,
                "color": color,
                "recommendation": recommendation,
                "factors": {
                    "lighting": lighting,
                    "crowd_density": crowd,
                    "police_distance_km": police_dist_km,
                    "time_risk": time_risk,
                    "historical_crime": crime_score,
                    "user_vulnerability": vulnerability
                }
            }


# Singleton model instance
_anfis_instance = None

def get_anfis_model() -> ANFISRiskModel:
    global _anfis_instance
    if _anfis_instance is None:
        _anfis_instance = ANFISRiskModel()
        _anfis_instance.eval()
    return _anfis_instance
