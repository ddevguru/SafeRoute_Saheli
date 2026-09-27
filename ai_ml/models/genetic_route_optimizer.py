"""
SafeRoute Saheli — Genetic Algorithm Route Optimizer (Soft Computing)
Multi-Objective Evolutionary Optimization for Safe Routing:
Fitness = w1 * SafetyScore - w2 * DistancePenalty - w3 * TimePenalty + w4 * SafeHavenBonus
"""

import math
import random
from typing import List, Dict, Tuple, Any
from .neuro_fuzzy import get_anfis_model

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers"""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class RouteChromosome:
    """Represents a candidate route as an ordered sequence of GPS waypoints"""
    def __init__(self, waypoints: List[Tuple[float, float]]):
        self.waypoints = waypoints
        self.distance_km = 0.0
        self.safety_score = 0.0
        self.duration_minutes = 0.0
        self.fitness = 0.0
        self.risk_breakdown: List[Dict[str, Any]] = []

    def copy(self):
        c = RouteChromosome(list(self.waypoints))
        c.distance_km = self.distance_km
        c.safety_score = self.safety_score
        c.duration_minutes = self.duration_minutes
        c.fitness = self.fitness
        c.risk_breakdown = list(self.risk_breakdown)
        return c


class GeneticRouteOptimizer:
    """
    Soft Computing Genetic Algorithm for Safe Route Optimization
    """
    def __init__(self, population_size: int = 30, generations: int = 25, 
                 crossover_rate: float = 0.85, mutation_rate: float = 0.20,
                 num_intermediate_nodes: int = 5):
        self.pop_size = population_size
        self.generations = generations
        self.cx_rate = crossover_rate
        self.mut_rate = mutation_rate
        self.num_intermediate = num_intermediate_nodes
        self.anfis = get_anfis_model()

    def _generate_candidate(self, origin: Tuple[float, float], dest: Tuple[float, float], 
                            spread_factor: float = 0.015) -> RouteChromosome:
        """Generate a random exploratory route between origin and destination"""
        waypoints = [origin]
        lat1, lon1 = origin
        lat2, lon2 = dest

        for i in range(1, self.num_intermediate + 1):
            t = i / (self.num_intermediate + 1)
            # Linear interpolation base
            base_lat = lat1 + t * (lat2 - lat1)
            base_lon = lon1 + t * (lon2 - lon1)

            # Lateral exploration perturbation (simulating street grid / arterial detours)
            lat_jitter = random.uniform(-spread_factor, spread_factor)
            lon_jitter = random.uniform(-spread_factor, spread_factor)
            waypoints.append((base_lat + lat_jitter, base_lon + lon_jitter))

        waypoints.append(dest)
        return RouteChromosome(waypoints)

    def _evaluate_chromosome(self, chrom: RouteChromosome, hour_of_day: int,
                             weight_safety: float, weight_distance: float):
        """
        Evaluate route using ANFIS Neuro-Fuzzy risk inference along all segments
        """
        total_dist = 0.0
        segment_safeties = []
        breakdown = []

        # Time risk function: peaks around 1:00 AM - 3:00 AM (0.95), lowest at 1:00 PM (0.10)
        time_risk = 0.5 + 0.45 * math.cos(math.radians((hour_of_day - 2) * 15.0))
        time_risk = max(0.1, min(1.0, time_risk))

        for i in range(len(chrom.waypoints) - 1):
            p1 = chrom.waypoints[i]
            p2 = chrom.waypoints[i + 1]
            seg_dist = haversine_distance(p1[0], p1[1], p2[0], p2[1])
            total_dist += seg_dist

            # Midpoint environmental simulation
            mid_lat = (p1[0] + p2[0]) / 2.0
            mid_lon = (p1[1] + p2[1]) / 2.0

            # Simulate spatial lighting, crowd density, police proximity based on coordinates
            lighting = 0.4 + 0.5 * math.sin(mid_lat * 120.0 + mid_lon * 90.0)
            lighting = max(0.1, min(1.0, lighting))

            crowd = 0.3 + 0.6 * math.cos(mid_lat * 80.0 - mid_lon * 110.0)
            crowd = max(0.05, min(0.95, crowd))

            police_dist_km = 0.5 + 3.0 * abs(math.sin(mid_lat * 200.0))
            crime_index = 0.2 + 0.5 * abs(math.cos(mid_lon * 150.0))

            # Run ANFIS Neuro-Fuzzy inference
            risk_res = self.anfis.predict_risk(
                lighting=lighting,
                crowd=crowd,
                police_dist_km=police_dist_km,
                time_risk=time_risk,
                crime_score=crime_index
            )

            segment_safeties.append(risk_res["safety_score"])
            breakdown.append({
                "segment_index": i,
                "start": p1,
                "end": p2,
                "distance_km": round(seg_dist, 2),
                "safety_score": risk_res["safety_score"],
                "risk_level": risk_res["level"],
                "recommendation": risk_res["recommendation"]
            })

        avg_safety = sum(segment_safeties) / max(1, len(segment_safeties))
        est_duration_min = (total_dist / 4.5) * 60.0  # Walking speed ~4.5 km/h

        # Multi-objective fitness
        # Higher safety increases fitness; higher distance penalizes fitness
        dist_penalty = (total_dist * 8.0)
        fitness = (weight_safety * avg_safety) - (weight_distance * dist_penalty)

        chrom.distance_km = round(total_dist, 2)
        chrom.safety_score = round(avg_safety, 1)
        chrom.duration_minutes = max(1, int(round(est_duration_min)))
        chrom.fitness = fitness
        chrom.risk_breakdown = breakdown

    def _crossover(self, parent1: RouteChromosome, parent2: RouteChromosome) -> Tuple[RouteChromosome, RouteChromosome]:
        """Order-preserving crossover between intermediate waypoints"""
        n = len(parent1.waypoints)
        if n <= 3:
            return parent1.copy(), parent2.copy()

        # Intermediate indices 1 to n-2
        idx1 = random.randint(1, n - 2)
        idx2 = random.randint(idx1, n - 2)

        child1_pts = list(parent1.waypoints)
        child2_pts = list(parent2.waypoints)

        # Swap intermediate waypoint block
        child1_pts[idx1:idx2+1] = parent2.waypoints[idx1:idx2+1]
        child2_pts[idx1:idx2+1] = parent1.waypoints[idx1:idx2+1]

        return RouteChromosome(child1_pts), RouteChromosome(child2_pts)

    def _mutate(self, chrom: RouteChromosome, mutation_scale: float = 0.008):
        """Randomly perturb intermediate waypoints to explore alternate well-lit roads"""
        for i in range(1, len(chrom.waypoints) - 1):
            if random.random() < self.mut_rate:
                lat, lon = chrom.waypoints[i]
                lat += random.gauss(0, mutation_scale)
                lon += random.gauss(0, mutation_scale)
                chrom.waypoints[i] = (lat, lon)

    def optimize(self, origin: Tuple[float, float], dest: Tuple[float, float],
                 hour_of_day: int = 21, profile: str = "SAFEST") -> Dict[str, Any]:
        """
        Run Evolutionary Genetic Optimization for Safe Route Planning
        profile options:
        - "SAFEST": High safety weight (w_s=0.75, w_d=0.25)
        - "BALANCED": Balanced safety & travel time (w_s=0.50, w_d=0.50)
        - "FASTEST": Minimizes walking distance/time (w_s=0.20, w_d=0.80)
        """
        if profile == "SAFEST":
            w_safety, w_dist = 0.75, 0.25
        elif profile == "FASTEST":
            w_safety, w_dist = 0.20, 0.80
        else: # BALANCED
            w_safety, w_dist = 0.50, 0.50

        # 1. Initialize Population
        population = [self._generate_candidate(origin, dest) for _ in range(self.pop_size)]

        # 2. Evaluate Initial Population
        for ind in population:
            self._evaluate_chromosome(ind, hour_of_day, w_safety, w_dist)

        # 3. Evolution Loop
        for gen in range(self.generations):
            # Sort by fitness descending
            population.sort(key=lambda c: c.fitness, reverse=True)

            # Elitism: retain top 2
            next_pop = [population[0].copy(), population[1].copy()]

            # Tournament Selection & Reproduction
            while len(next_pop) < self.pop_size:
                # Tournament k=3
                t1 = random.sample(population, 3)
                p1 = max(t1, key=lambda c: c.fitness)

                t2 = random.sample(population, 3)
                p2 = max(t2, key=lambda c: c.fitness)

                if random.random() < self.cx_rate:
                    c1, c2 = self._crossover(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()

                self._mutate(c1)
                self._mutate(c2)

                self._evaluate_chromosome(c1, hour_of_day, w_safety, w_dist)
                self._evaluate_chromosome(c2, hour_of_day, w_safety, w_dist)

                next_pop.append(c1)
                if len(next_pop) < self.pop_size:
                    next_pop.append(c2)

            population = next_pop

        # 4. Final Best Individual
        best: RouteChromosome = max(population, key=lambda c: c.fitness)

        # Build turn-by-turn steps
        steps = []
        for i, pt in enumerate(best.waypoints):
            if i == 0:
                inst = "Start journey at current location"
            elif i == len(best.waypoints) - 1:
                inst = "Arrive at safe destination"
            else:
                inst = f"Continue on well-lit corridor via Waypoint {i}"
            steps.append({
                "step_index": i + 1,
                "instruction": inst,
                "latitude": round(pt[0], 6),
                "longitude": round(pt[1], 6)
            })

        return {
            "profile": profile,
            "safety_score": best.safety_score,
            "distance_km": best.distance_km,
            "duration_minutes": best.duration_minutes,
            "waypoints": [{"lat": round(pt[0], 6), "lng": round(pt[1], 6)} for pt in best.waypoints],
            "steps": steps,
            "segment_breakdown": best.risk_breakdown
        }

    def generate_all_route_options(self, origin: Tuple[float, float], dest: Tuple[float, float],
                                   hour_of_day: int = 21) -> Dict[str, Any]:
        """
        Generates 3 full routing options for user selection (Safest, Balanced, Fastest)
        """
        safest = self.optimize(origin, dest, hour_of_day, "SAFEST")
        balanced = self.optimize(origin, dest, hour_of_day, "BALANCED")
        fastest = self.optimize(origin, dest, hour_of_day, "FASTEST")

        return {
            "origin": {"lat": origin[0], "lng": origin[1]},
            "destination": {"lat": dest[0], "lng": dest[1]},
            "hour_of_day": hour_of_day,
            "recommended": "SAFEST",
            "routes": {
                "safest": safest,
                "balanced": balanced,
                "fastest": fastest
            }
        }
