# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent): # Cell hereda de FixedAgent
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self): # Get coordinate x
        return self.cell.coordinate[0] 

    @property
    def y(self): # Get coordinate y
        return self.cell.coordinate[1]

    @property
    def is_alive(self): # Check if cell is alive
        return self.state == self.ALIVE

    @property
    def neighbors(self): # Get neighboring agents
        return self.cell.neighborhood.agents
    
    def __init__(self, model, cell, init_state=DEAD): # Constructor
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model) # Call parent constructor, in this case FixedAgent
        self.cell = cell # Cell where the agent is located
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self): # Just calculate next state based on neighbors
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """

        # # Discover top 3 cells position in the array returned by neighbors
        # if self.x == 1 and self.y == 1:  # Top-left corner
        #     print("1,1 neighbors:", [(n.x, n.y, n.state) for n in self.neighbors])
        # # In the neighbors list, the top 3 cells are at indices 2, 4, 7


        neighborStates = [neighbor.state for neighbor in self.neighbors]

        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state
    
        if self.y < 49:
            if neighborStates[2] == 1 and neighborStates[4] == 1 and neighborStates[7] == 1:
                self._next_state = self.DEAD
            elif neighborStates[2] == 1 and neighborStates[4] == 1 and neighborStates[7] == 0:
                self._next_state = self.ALIVE
            elif neighborStates[2] == 1 and neighborStates[4] == 0 and neighborStates[7] == 1:
                self._next_state = self.DEAD
            elif neighborStates[2] == 1 and neighborStates[4] == 0 and neighborStates[7] == 0:
                self._next_state = self.ALIVE
            elif neighborStates[2] == 0 and neighborStates[4] == 1 and neighborStates[7] == 1:
                self._next_state = self.ALIVE
            elif neighborStates[2] == 0 and neighborStates[4] == 1 and neighborStates[7] == 0:
                self._next_state = self.DEAD
            elif neighborStates[2] == 0 and neighborStates[4] == 0 and neighborStates[7] == 1:
                self._next_state = self.ALIVE
            elif neighborStates[2] == 0 and neighborStates[4] == 0 and neighborStates[7] == 0:
                self._next_state = self.DEAD

    def assume_state(self): # Update state to next state
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state
