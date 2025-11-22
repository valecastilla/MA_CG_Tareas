from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Cell


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None): # Constructor
        """Create a new playing area of (width, height) cells."""
        super().__init__(seed=seed) # Call parent constructor, seed for random generator

        """Grid where cells are connected to their 8 neighbors.

        Example for two dimensions:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        """
        self.grid = OrthogonalMooreGrid((width, height), capacity=1, torus=True) # Create grid, capacity 1 agent per cell, torus takes edges as connected

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        for cell in self.grid.all_cells: # For each cell in the grid create a Cell agent
            if cell.coordinate[1] == 49: # Solo la fila superior puede tener células vivas al inicio
                Cell(
                self, # Model
                cell,
                init_state=(
                    Cell.ALIVE
                    if self.random.random() < initial_fraction_alive # initial_fraction_alive probability to be alive
                    else Cell.DEAD
                ),
            )
            else:
                Cell(
                self, 
                cell, 
                init_state=Cell.DEAD)

        self.running = True


    def step(self):
        """Perform the model step in two stages:

        - First, all cells assume their next state (whether they will be dead or alive)
        - Then, all cells change state to their next state.
        """
        self.agents.do("determine_state")

        self.agents.do("assume_state")
