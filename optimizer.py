# Tool to optimize Ceramic Dagger builds that make use of Arcane Doughty. 
# The user can set fixed mods, faction bonuses, warframe arcanes, etc.
# Should be easy to change the stats to another weapon.

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Iterator
from itertools import combinations

# Global constants. Edit them as your setup changes.
AVENGER = True
FURY = True
FACTION_MOD = True
AVENGER_BONUS = 0.45
FURY_CRIT_MUL = 2.8
MAX_SLOTS = 8
FACTION_BONUS = 1.5

@dataclass
class StatModifier:
    """Represents a stat modifier with a name and value"""
    name: str
    value: float

@dataclass
class Build:
    """Represents a build with fixed and variable mods, and stats"""
    fixed_mods: List[str]
    variable_mods: List[str]
    stats: Dict[str, Any]

@dataclass
class StatDisplay:
    """Represents a stat display with a label, value, and optional base value"""
    label: str
    value: float
    base_value: float = 0.0
    contributions: List[StatModifier] = field(default_factory=list)
    suffix: str = "%"
    special_notes: List[str] = field(default_factory=list)

    def format_value(self, value: float) -> str:
        """
        Formats the value of the stat.

        If the suffix is "%", multiplies the value by 100 and appends the suffix.
        Otherwise, simply formats the value.

        Args:
            value (float): The value to be formatted.

        Returns:
            str: The formatted value.
        """
        return f"{value * 100:.2f}{self.suffix}" if self.suffix == "%" else f"{value:.2f}"

    def format_contributions(self) -> str:
        """
        Formats the contributions to the stat.

        If the base value is not zero, adds a "Base" string with the formatted value.
        If the contributions list is not empty, joins the contributions with the format "X% from Y".
        Finally, adds any special notes.

        Returns:
            str: The formatted contributions.
        """
        parts = []
        if self.base_value:
            parts.append(f"Base {self.format_value(self.base_value)}")
        
        if self.contributions:
            contrib_str = " + ".join(f"{mod.value * 100:.2f}% from {mod.name}" 
                                   for mod in self.contributions)
            parts.append(f"({contrib_str})")
        
        parts.extend(filter(None, self.special_notes))
        return " * ".join(filter(None, parts))

    def __str__(self) -> str:
        """
        Returns a string representation of the stat display.

        Includes the label, formatted value, and formatted contributions.

        Returns:
            str: The string representation of the stat display.
        """
        return (f"  {self.label}: {self.format_value(self.value)} "
                f"{self.format_contributions()}")

class WeaponBuildOptimizer:
    """
    A class to optimize weapon builds based on various stats and mods.
    """

    # Mapping of stat names to their corresponding internal representation
    STAT_MAPPINGS = {
        "base_damage": "dmg_mul",
        "puncture_multiplier": "puncture_multipliers",
        "status_chance": "status_chance_mul",
        "crit_chance": "crit_chance_mul",
        "crit_damage": "crit_dmg_mul",
        "new_element_damage": "new_element_damage"
    }

    # Mapping of stat names to their corresponding contribution types
    CONTRIBUTION_MAPPINGS = {
        "base_damage": "base_damage",
        "puncture_multiplier": "puncture",
        "status_chance": "status_chance",
        "crit_chance": "crit_chance",
        "crit_damage": "crit_dmg",
        "new_element_damage": "new_element"
    }

    def __init__(self, base_stats: Dict[str, float], fixed_mods: Dict[str, Dict], 
                 available_mods: Dict[str, Dict]):
        """
        Initializes the optimizer with the base stats, fixed mods, and available mods.

        Args:
            base_stats (Dict[str, float]): The base stats of the weapon.
            fixed_mods (Dict[str, Dict]): The fixed mods applied to the weapon.
            available_mods (Dict[str, Dict]): The available mods that can be applied to the weapon.
        """
        self.base_stats = base_stats
        self.fixed_mods = fixed_mods
        self.available_mods = available_mods

    def _initialize_stat_trackers(self) -> Tuple[Dict[str, float], Dict[str, List[StatModifier]]]:
        """
        Initializes the stat trackers with default values.

        Returns:
            Tuple[Dict[str, float], Dict[str, List[StatModifier]]]: A tuple containing the stat trackers and contribution trackers.
        """
        # Initialize the stat trackers with default values
        stats = {
            "dmg_mul": 1.0,
            "puncture_multipliers": [],
            "new_element_damage": 0.0,
            "status_chance_mul": 1.0,
            "crit_chance_mul": 1.0,
            "crit_dmg_mul": 1.0
        }
        
        # Initialize the contribution trackers with empty lists
        contributions = {
            "status_chance": [],
            "crit_chance": [],
            "crit_dmg": [],
            "puncture": [],
            "new_element": [],
            "base_damage": []
        }
        
        return stats, contributions

    def _process_mod(self, mod_name: str, mod: Dict[str, float], stats: Dict[str, Any], 
                        contributions: Dict[str, List[StatModifier]]) -> None:
        """
        Processes a mod and updates the stats and contributions accordingly.
    
        Args:
            mod_name (str): The name of the mod.
            mod (Dict[str, float]): The stats of the mod.
            stats (Dict[str, Any]): The current stats of the weapon.
            contributions (Dict[str, List[StatModifier]]): The contributions of the mods.
    
        Returns:
            None
        """
        for stat_type, value in mod.items():
            # Check if the stat type is in the STAT_MAPPINGS
            if stat_type in self.STAT_MAPPINGS:
                # Get the corresponding stat key and contribution key
                stat_key = self.STAT_MAPPINGS[stat_type]
                contrib_key = self.CONTRIBUTION_MAPPINGS[stat_type]
                
                # Update the stats
                if isinstance(stats[stat_key], list):
                    # If the stat is a list, append the value
                    stats[stat_key].append(value)
                else:
                    # If the stat is not a list, add the value
                    stats[stat_key] += value
                
                # Update the contributions
                contributions[contrib_key].append(StatModifier(mod_name, value))
    
    def calculate_total_damage(self, mods: List[Dict]) -> Dict:
        """
        Calculates the total damage of the weapon based on the mods.
    
        Args:
            mods (List[Dict]): The mods to be applied to the weapon.
    
        Returns:
            Dict: The total damage of the weapon.
        """
        # Initialize the stat trackers
        stats, contributions = self._initialize_stat_trackers()
        
        # Process the fixed mods
        for mod_name, mod_stats in self.fixed_mods.items():
            self._process_mod(mod_name, mod_stats, stats, contributions)
    
        # Process the variable mods
        for mod in mods:
            mod_name = mod['name']
            mod_stats = {k: v for k, v in mod.items() if k != 'name'}
            self._process_mod(mod_name, mod_stats, stats, contributions)
    
        # Calculate the damage components
        base = self.base_stats
        weapon_stats = self._calculate_weapon_stats(base, stats)
        crit_stats = self._calculate_crit_stats(base, stats, weapon_stats)
        
        # Calculate the final damage
        total_damage = self._calculate_final_damage(base, weapon_stats, crit_stats)
        
        # Prepare the output
        return self._prepare_stats_output(stats, contributions, weapon_stats, crit_stats, total_damage)
    
    def _calculate_weapon_stats(self, base: Dict, stats: Dict) -> Dict:
        """
        Calculates the weapon stats based on the base stats and the mods.
    
        Args:
            base (Dict): The base stats of the weapon.
            stats (Dict): The current stats of the weapon.
    
        Returns:
            Dict: The calculated weapon stats.
        """
        # Calculate the elemental bonus
        elemental_bonus = stats["new_element_damage"]
        
        # Calculate the puncture bonus
        puncture_bonus = 1.0 + sum(stats["puncture_multipliers"])
        
        # Calculate the damage bonus
        damage_bonus = stats["dmg_mul"] - 1.0
        
        # Calculate the puncture damage
        puncture_damage = base["base_puncture"] * puncture_bonus
        
        # Calculate the weapon damage
        weapon_damage = (base["base_damage"] + puncture_damage + 
                        stats["new_element_damage"] * base["base_damage"])
        
        # Return the calculated weapon stats
        return {
            "elemental_bonus": elemental_bonus,
            "puncture_bonus": puncture_bonus,
            "damage_bonus": damage_bonus,
            "puncture_damage": puncture_damage,
            "weapon_damage": weapon_damage
        }

    def _calculate_crit_stats(self, base: Dict, stats: Dict, weapon_stats: Dict) -> Dict:
        """
        Calculates the critical hit stats based on the base stats, mods, and weapon stats.
    
        Args:
            base (Dict): The base stats of the weapon.
            stats (Dict): The current stats of the weapon.
            weapon_stats (Dict): The calculated weapon stats.
    
        Returns:
            Dict: The calculated critical hit stats.
        """
        # Calculate the status chance
        status_chance = base["base_status_chance"] * stats["status_chance_mul"]
        
        # Calculate the puncture chance
        puncture_chance = weapon_stats["puncture_damage"] / weapon_stats["weapon_damage"]
        
        # Calculate the critical hit chance
        crit_chance = (base["base_crit_chance"] * 
                      (stats["crit_chance_mul"] * (FURY_CRIT_MUL if FURY else 1.0)) + 
                      (AVENGER_BONUS if AVENGER else 0.0))
        
        # Calculate the final critical hit damage bonus
        final_crit_dmg_bonus = puncture_chance * status_chance * 10
        
        # Calculate the critical hit damage
        crit_dmg = base["base_crit_dmg"] * stats["crit_dmg_mul"] + final_crit_dmg_bonus
        
        return {
            "status_chance": status_chance,
            "puncture_chance": puncture_chance,
            "crit_chance": crit_chance,
            "crit_dmg": crit_dmg,
            "final_crit_dmg_bonus": final_crit_dmg_bonus
        }
    
    def _calculate_final_damage(self, base: Dict, weapon_stats: Dict, crit_stats: Dict) -> float:
        """
        Calculates the final damage of the weapon based on the base stats, weapon stats, and critical hit stats.
    
        Args:
            base (Dict): The base stats of the weapon.
            weapon_stats (Dict): The calculated weapon stats.
            crit_stats (Dict): The calculated critical hit stats.
    
        Returns:
            float: The final damage of the weapon.
        """
        # Calculate the faction bonus
        faction_bonus = FACTION_BONUS if len(self.fixed_mods) > 1 else 1.0
        
        # Calculate the final damage
        return ((base["base_damage"] * 
                (1 + weapon_stats["elemental_bonus"] + weapon_stats["puncture_bonus"]) *
                (1 + weapon_stats["damage_bonus"]) + 144) *
                (1 + crit_stats["crit_chance"] * (crit_stats["crit_dmg"] - 1) + 
                 max(0, crit_stats["crit_chance"] - 1) * 0.5)) * faction_bonus
    
    def _prepare_stats_output(self, stats: Dict, contributions: Dict, 
                            weapon_stats: Dict, crit_stats: Dict, total_damage: float) -> Dict:
        """
        Prepares the output stats dictionary.
    
        Args:
            stats (Dict): The current stats of the weapon.
            contributions (Dict): The contributions of the mods.
            weapon_stats (Dict): The calculated weapon stats.
            crit_stats (Dict): The calculated critical hit stats.
            total_damage (float): The final damage of the weapon.
    
        Returns:
            Dict: The output stats dictionary.
        """
        return {
            "total_damage": round(total_damage, 2),
            "total_weapon_damage": round(weapon_stats["weapon_damage"], 2),
            "crit_chance": crit_stats["crit_chance"],
            "crit_dmg": crit_stats["crit_dmg"],
            "status_chance": crit_stats["status_chance"],
            "puncture_chance": crit_stats["puncture_chance"],
            "final_crit_dmg_bonus_value": crit_stats["final_crit_dmg_bonus"],
            "damage_multipliers": {
                "impact": round(self.base_stats["base_impact"], 2),
                "puncture": round(weapon_stats["puncture_damage"], 2),
                "new_element": stats["new_element_damage"]
            },
            "damage_type_bonus_against_faction": FACTION_BONUS if len(contributions["new_element"]) > 1 else 1.0,
            "contributions": contributions
        }
    
    def optimize_builds(self, top_n: int = 3) -> List[Build]:
        num_slots = MAX_SLOTS - len(self.fixed_mods)
        if num_slots < 0:
            raise ValueError("Too many fixed mods")

        def generate_builds() -> Iterator[Build]:
            fixed_mods_list = list(self.fixed_mods.keys())
            for mods in combinations(self.available_mods.keys(), num_slots):
                mod_list = [
                    {
                        'name': mod,
                        **self.available_mods[mod]
                    } 
                    for mod in mods
                ]
                stats = self.calculate_total_damage(mod_list)
                yield Build(fixed_mods_list, list(mods), stats)

        return sorted(generate_builds(), 
                     key=lambda x: x.stats["total_damage"], 
                     reverse=True)[:top_n]
    
    def display_build(self, build: Build) -> None:
        """
        Displays the details of a build.
    
        Args:
            build (Build): The build to display.
        """
        # Get the stats of the build
        stats = build.stats
        
        # Get the base stats of the weapon
        base = self.base_stats
        
        # Print the build details
        print(f"Build: {', '.join(build.fixed_mods + build.variable_mods)}")
        print(f"Total Damage: {stats['total_damage']:.2f}")
        print("Details:")
        
        # Create a list of stat displays
        displays = [
            StatDisplay(
                "Weapon Damage",
                stats['total_weapon_damage'],
                contributions=stats['contributions']['base_damage'],
                suffix=""
            ),
            StatDisplay(
                "Critical Chance",
                stats['crit_chance'],
                base['base_crit_chance'],
                stats['contributions']['crit_chance'],
                special_notes=[
                    "180% from Arcane Fury" if FURY else "",
                    "45% flat from Arcane Avenger" if AVENGER else ""
                ]
            ),
            StatDisplay(
                "Critical Damage",
                stats['crit_dmg'],
                base['base_crit_dmg'],
                stats['contributions']['crit_dmg'],
                special_notes=[f"Doughty Bonus {stats['final_crit_dmg_bonus_value']:.2f}"]
            ),
            StatDisplay(
                "Status Chance",
                stats['status_chance'],
                base['base_status_chance'],
                stats['contributions']['status_chance']
            ),
            StatDisplay(
                "Puncture Chance",
                stats['puncture_chance'],
                base['base_puncture'] / base['base_damage'],
                stats['contributions']['puncture']
            )
        ]
        
        # Print each stat display
        for display in displays:
            print(display)
        
        # Display additional info
        self._display_additional_info(stats)

    def _display_additional_info(self, stats: Dict[str, Any]) -> None:
        """
        Displays additional information about the build.
    
        Args:
            stats (Dict[str, Any]): The stats of the build.
        """
        # Print the Doughty Bonus
        print(f"  Doughty Bonus: {stats['final_crit_dmg_bonus_value']:.2f}")
        
        # Calculate the faction bonus
        faction_bonus = stats['damage_type_bonus_against_faction']
        
        # Print the damage type bonus against faction
        print(f"  Damage Type Bonus Against Faction: {faction_bonus} "
              f"({'applied' if faction_bonus == FACTION_BONUS else 'inactive'})")
    
        # Print the damage multipliers
        print("  Damage Multipliers:")
        multipliers = stats['damage_multipliers']
        print(f"    Impact: {multipliers['impact']:.2f}")
        print(f"    Puncture: {multipliers['puncture']:.2f}")
        
        # Print the additional element type if it exists
        new_element = multipliers['new_element']
        if new_element:
            print(f"    Additional Element Type: {new_element * self.base_stats['base_damage']:.2f}")
        
        # Print a newline
        print()
    

if __name__ == "__main__":
    # Define the base stats of the weapon
    base_stats = {
        "base_damage": 140,
        "base_impact": 14,
        "base_puncture": 126,
        "base_status_chance": 0.20,
        "base_crit_chance": 0.40,
        "base_crit_dmg": 1.5
    }

    # Define the fixed mods
    fixed_mods = {}

    # Define the available mods
    available_mods = {
        "Weeping Wounds": {"status_chance": 4.4},
        "Blood Rush": {"crit_chance": 4.4},
        "Jugulus Barbs": {"puncture_multiplier": 0.90, "status_chance": 0.60},
        "Auger Strike": {"puncture_multiplier": 1.20},
        "Primed Pressure Point": {"base_damage": 1.65},
        "Spoiled Strike": {"base_damage": 1.00},
        "60/60": {"new_element_damage": 0.60, "status_chance": 0.60},
        "60/60 2": {"new_element_damage": 0.60, "status_chance": 0.60},
        "Primed Fever Strike": {"new_element_damage": 1.65},
        "Shocking Touch": {"new_element_damage": 0.90},
        "Melee Prowess": {"status_chance": 0.90},
        "Sacrificial Steel": {"crit_chance": 2.20},
        "Organ Shatter": {"crit_damage": 0.90},
        "Gladiator Might": {"crit_damage": 0.60}
    }

    # Create a WeaponBuildOptimizer instance
    optimizer = WeaponBuildOptimizer(base_stats, fixed_mods, available_mods)
    
    # Optimize the builds
    best_builds = optimizer.optimize_builds(top_n=3)
    
    # Display the best builds
    for i, build in enumerate(best_builds, 1):
        print(f"Build {i}:")
        optimizer.display_build(build)
