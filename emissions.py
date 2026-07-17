"""Carbon footprint calculations and benchmark comparisons for a single client."""
from recommendations import ENERGY_RECOMMENDATIONS, WASTE_RECOMMENDATIONS, TRAVEL_RECOMMENDATIONS


class CarbonFootprint:
    def __init__(self, client_id):
        self.client_id = client_id
        self.energy_emission = None
        self.waste_emission = None
        self.travel_emission = None

    def calculate_energy_emission(self, electricity, gas, fuel):
        self.energy_emission = electricity * 12 * 0.0005 + gas * 12 * 0.0053 + fuel * 12 * 2.23
        return self.energy_emission

    def calculate_waste_emission(self, waste_generate, waste_recycle):
        # Accept waste_recycle as either a percentage (e.g. 30) or a fraction (e.g. 0.3)
        waste_recycle = waste_recycle / 100 if waste_recycle > 1 else waste_recycle
        self.waste_emission = waste_generate * 12 * (0.57 - waste_recycle)
        return self.waste_emission

    def calculate_travel_emission(self, travel_km, fuel_efficiency):
        self.travel_emission = travel_km * (1 / fuel_efficiency) * 2.31
        return self.travel_emission

    def calculate_total_emission(self):
        if self.energy_emission is not None and self.waste_emission is not None and self.travel_emission is not None:
            return self.energy_emission + self.waste_emission + self.travel_emission
        return None

    def get_energy_recommendations(self):
        return ENERGY_RECOMMENDATIONS

    def get_waste_recommendations(self):
        return WASTE_RECOMMENDATIONS

    def get_travel_recommendations(self):
        return TRAVEL_RECOMMENDATIONS

    def compare_to_benchmark(self, emission_type, emission_value, benchmark):
        exceeds_benchmark = emission_value > benchmark
        if exceeds_benchmark:
            message = f"Your {emission_type} emission exceeds the benchmark of {benchmark} kgCO2/year."
            recommendations = None if emission_type == "total" else getattr(self, f"get_{emission_type}_recommendations")()
        else:
            message = f"Your {emission_type} emission is within the benchmark of {benchmark} kgCO2/year."
            recommendations = None
        return message, recommendations, exceeds_benchmark
