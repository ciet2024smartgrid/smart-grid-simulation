import sys
from energy_grid import EnergyGrid
from resolver import resolve_energy_grid

def main():
    grid_file = sys.argv[1]

    energy_grid = EnergyGrid.load_energy_grid(grid_file)

    solution = resolve_energy_grid(energy_grid)

    solution.print()


if __name__ == "__main__":
    main()
