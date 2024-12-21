# Arcane-Doughty-Optimizer

A Python-based tool for optimizing stat stick builds that make use of Arcane Doughty in Warframe. Currently configured for the Ceramic Dagger, but easily adaptable to other weapons.

## Overview

This tool helps players optimize their stat stick builds by:
- Calculating total damage output considering various mod combinations
- Accounting for Arcane Doughty's unique critical damage bonus mechanics
- Supporting various game mechanics including:
  - Arcane Avenger
  - Arcane Fury
  - Faction damage bonuses
  - Status chance calculations
  - Critical hit mechanics

## Features

- **Flexible Mod System**: Supports both fixed and variable mods in your builds
- **Comprehensive Calculations**: 
  - Weapon base damage
  - Critical chance and damage
  - Status chance
  - Puncture damage
  - Element damage
  - Faction bonuses
- **Detailed Output**: Provides comprehensive breakdowns of:
  - Damage contributions from each mod
  - Critical hit calculations
  - Status chance effects
  - Arcane interactions
- **Build Comparison**: Automatically compares and ranks different mod combinations

## Usage

1. Configure your conditions in the global flags (Arcane Fury, Avenger, modding for an specific faction)
2. Set up your fixed mods (if any) in the `fixed_mods` dictionary.
3. Define available mods in the `available_mods` dictionary:
4. It is possible to change the weapon data for another one (i.e. Magistar)
5. Just run the file and it will print the 3 best builds for your current setup.

## Requirements

- Python 3.10+

## Notes

- This tool is specifically optimized for stat stick weapons that utilize Arcane Doughty mechanics
- The calculations assume perfect conditions (full combo counter, all arcanes triggered, etc.)
- Modify the weapon stats and available mods as needed for different weapons

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.
