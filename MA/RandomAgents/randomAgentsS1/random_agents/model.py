from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid

from .agent import ChargingStationAgent, RandomAgent, ObstacleAgent, TrashAgent

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
        num_obstacles: Number of obstacle agents in the simulation
    """
    def __init__(self, num_obstacles=10, num_trash=10, width=8, height=8, seed=42):

        super().__init__(seed=seed)
        self.num_agents = 1
        self.num_obstacles = num_obstacles
        self.num_trash = num_trash
        # Track how many trash items have been collected so far
        self.num_collected = 0
        self.seed = seed
        self.width = width
        self.height = height

        self.grid = OrthogonalMooreGrid([width, height], torus=False)

        # Set up data collection: report counts of agent types each step
        model_reporters = {
            "RandomAgent": lambda m: sum(1 for a in m.agents if isinstance(a, RandomAgent)),
            "TrashAgent": lambda m: sum(1 for a in m.agents if isinstance(a, TrashAgent)),
            # Steps left until forced stop
            "StepsLeft": lambda m: max(0, getattr(m, 'max_steps', 0) - getattr(m, 'steps', 0)),
        }

        self.datacollector = DataCollector(model_reporters)

        # Identify the coordinates of the border of the grid
        border = [(x,y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height-1] or x in [0, width - 1]]

        # Create the border cells
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                ObstacleAgent(self, cell=cell)
            

        RandomAgent.create_agents(
            self,
            self.num_agents,
            # Agent starting position at 1,1
            cell=self.grid[1,1]
        )

        ObstacleAgent.create_agents(
            self,
            self.num_obstacles,
            cell=self.random.choices(self.grid.empties.cells, k=self.num_obstacles)
        )

        TrashAgent.create_agents(
            self,
            self.num_trash,
            cell=self.random.choices(self.grid.empties.cells, k=self.num_trash)
        )

        # Find the cell where the agent spawns to create the charging station there
        charging_cell = None
        for c in self.grid.all_cells:
            contents = c.agents  # Get agents in the cell
            for a in contents:
                if isinstance(a, RandomAgent): # If there is a RandomAgent in the cell
                    charging_cell = c # Assign that cell
                    break
            if charging_cell is not None: # If we have found the cell, break out of the loop, just one agent in S1
                break

        ChargingStationAgent.create_agents(
            self,
            1,
            cell=charging_cell,
        )

        self.steps = 0
        self.max_steps = 1000
        
        self.running = True # Indicate that the model is running

    def step(self):
        '''Advance the model by one step.'''
        # Stop if no trash remains
        if sum(1 for a in self.agents if isinstance(a, TrashAgent)) == 0:
            self.running = False
            return

        self.agents.shuffle_do("step")

        # Collect data
        try:
            self.datacollector.collect(self)
        except Exception:
            pass

        # Increment step counter and stop if reached max
        self.steps += 1
        if self.steps >= getattr(self, 'max_steps', 1000):
            self.running = False

    @staticmethod
    def count_type(model, typeAgent):
        """Helper method to count trees in a given condition in a given model."""
        return sum(1 for a in model.agents if a.__class__.__name__ == typeAgent)
