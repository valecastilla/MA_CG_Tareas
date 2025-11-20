from mesa.discrete_space import CellAgent, FixedAgent

class RandomAgent(CellAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, model, cell):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
        """
        super().__init__(model)
        self.cell = cell
        self.agentMap = {}
        self.direction = 1
        self.needToCharge = False
        self.needToReturn = False
        self.cleaning = False
        self.batteryLevel = 100  # Battery level starts at 100%

    def move(self):
        """
        Determines the next empty cell in its neighborhood, and moves to it
        """
        """ if self.random.random() < 0.5: # 50% chance to move or stay
            # Checks which grid cells are empty
            next_moves = self.cell.neighborhood.select(lambda cell: cell.is_empty) # next_moves are the empty neighboring cells
            self.cell = next_moves.select_random_cell() # Selects one cell from next_moves randomly and moves to it """
        
        newX = self.cell.coordinate[0] 
        newY = self.cell.coordinate[1]

        # Find cells with no obstacles
        def is_safe(cell):
            return not any(isinstance(a, ObstacleAgent) for a in getattr(cell, 'agents', []))

        # If currently at (1,1) try to move to (2,2) unless blocked
        if self.cell.coordinate == (1, 1):
            dest = self.model.grid[2, 2]
            if is_safe(dest):
                self.cell = dest  # Move to (2,2), to optimize collection of trash
                print("Moved to (2,2) from (1,1)")
                self.batteryLevel -= 1
            else:
                # pick a safe neighboring cell if (2,2) blocked
                safe_neighbors = [
                    c for c in self.cell.neighborhood.select(lambda cell: True) if is_safe(c)
                ]
                if safe_neighbors:
                    dest = self.model.grid[self.cell.coordinate[0] + 1, self.cell.coordinate[1]]
                    if (dest) in safe_neighbors: 
                        self.cell = dest
                        self.batteryLevel -= 1
                    else:
                        dest = self.model.grid[self.cell.coordinate[0], self.cell.coordinate[1] + 1]
                        if (dest) in safe_neighbors:
                            self.cell = dest
                            self.batteryLevel -= 1
                        else: 
                            self.cell = self.random.choice(safe_neighbors)
                            self.batteryLevel -= 1
                        
        else:
            curr_x, curr_y = self.cell.coordinate
            # If we were blocked when trying to reach (2,2), try to reach row 2
            if self.agentMap.get('TargetRow2'):
                if curr_y != 2:
                    step_y = 1 if 2 > curr_y else -1 # If current row is smaller that target go up, else down
                    dest = self.model.grid[curr_x, curr_y + step_y]
                    if is_safe(dest):
                        self.cell = dest
                        self.batteryLevel -= 1
                        return
                else:
                    # Reached row 2
                    self.agentMap.pop('TargetRow2', None)

            # If we need to return to a previous row after avoidance
            if self.agentMap.get('ReturnRow') is not None:
                target_row = self.agentMap['ReturnRow']
                if curr_y != target_row:
                    step_y = 1 if target_row > curr_y else -1 # If current row is smaller that target go up, else down
                    # Depending on direction choose optimal cell
                    #if self.direction > 0:
                     #   step_x = 
                    dest = self.model.grid[curr_x, curr_y + step_y]
                    if is_safe(dest):
                        self.cell = dest
                        self.batteryLevel -= 1
                        # If we've returned to the row
                        if self.cell.coordinate[1] == target_row:
                            self.agentMap.pop('ReturnRow', None)
                        return

            # Find neighboring cells that contain any TrashAgent and are safe
            trash_neighbors = [
                c for c in self.cell.neighborhood.select(
                    lambda cell: any(isinstance(agent, TrashAgent) for agent in getattr(cell, 'agents', []))
                ) if is_safe(c)
            ]

            if self.cleaning:
                # Move towards the last position before cleaning
                last_position = self.agentMap.get('LastPosition')
                if last_position:
                    dest = self.model.grid[last_position]
                    if is_safe(dest):
                        self.cell = dest
                        print(f"Moved to {self.cell.coordinate} while returning to last position before cleaning")
                        self.batteryLevel -= 1
                    else:
                        # if last position is now blocked, pick another safe neighbor
                        safe_neighbors = [
                            c for c in self.cell.neighborhood.select(lambda cell: cell.is_empty) if is_safe(c)
                        ]
                        if safe_neighbors:
                            self.cell = self.random.choice(safe_neighbors)
                            print(f"Moved to {self.cell.coordinate} while returning to last position before cleaning (alternate)")
                            self.batteryLevel -= 1
                    # Check if reached the last position
                    if self.cell.coordinate == last_position:
                        self.cleaning = False  # Stop cleaning mode once back to last position

            elif trash_neighbors:
                # Save last position before changing to cell with trash
                self.agentMap['LastPosition'] = self.cell.coordinate
                self.cleaning = True
                # Move to the first safe neighbor that has trash
                self.cell = trash_neighbors[0]
                print(f"Moved to {self.cell.coordinate} while moving to trash")
                self.batteryLevel -= 1

            else:
                next_x = self.cell.coordinate[0] + self.direction
                if next_x < 2 or next_x >= self.model.width - 2:
                    self.direction = -self.direction
                    newX = self.cell.coordinate[0]
                    newY = self.cell.coordinate[1] + 2
                    # Handle top and bottom borders
                    newY = max(0, min(self.model.height - 1, newY))
                    dest = self.model.grid[newX, newY]
                    if is_safe(dest):
                        self.cell = dest
                        self.batteryLevel -= 1
                    else:
                        safe_neighbors = [
                            c for c in self.cell.neighborhood.select(lambda cell: cell.is_empty or any(isinstance(a, TrashAgent) for a in getattr(cell, 'agents', []))) if is_safe(c)
                        ]
                        if safe_neighbors:
                            # Store return row so we can go back after avoiding
                            self.agentMap['ReturnRow'] = self.cell.coordinate[1]
                            self.cell = self.random.choice(safe_neighbors)
                            self.batteryLevel -= 1
                else:
                    dest = self.model.grid[next_x, self.cell.coordinate[1]]
                    if is_safe(dest):
                        self.cell = dest
                        self.batteryLevel -= 1
                    else:
                        # If obstacle remember current row and pick a safe neighbor to avoid
                        self.agentMap['ReturnRow'] = self.cell.coordinate[1]
                        safe_neighbors = [
                            c for c in self.cell.neighborhood.select(lambda cell: True) if is_safe(c)
                        ]
                        if safe_neighbors:
                            dest = self.model.grid[self.cell.coordinate[0] + self.direction, self.cell.coordinate[1] - 1]  # Try avoiding from bottom
                            if is_safe(dest):
                                self.cell = dest
                                self.batteryLevel -= 1
                            else:
                                dest = self.model.grid[self.cell.coordinate[0] + self.direction, self.cell.coordinate[1] + 1]
                                if is_safe(dest):
                                    self.cell == dest
                                    self.batteryLevel -= 1
                                else:
                                    self.cell = self.random.choice(safe_neighbors)
                                    self.batteryLevel -= 1   

        print(f"Battery level: {self.batteryLevel}%")

        pass

    def charging(self):
        # Move towards the charging station
        print("Charging state")
        charging_station_pos = self.agentMap.get('ChargingStation')
        if charging_station_pos:
            if self.cell.coordinate != charging_station_pos:
                self.moveToPoint(charging_station_pos)
            else:
                # At charging station, recharge
                self.batteryLevel = self.batteryLevel + 5
                if self.batteryLevel >= 100:
                    self.batteryLevel = 100
                    self.needToCharge = False
                    self.needToReturn = True
                    self.returning()

    def cleaning(self):
        print("Cleaning state")
    

    # Use chevysev distance to move to a specific point
    # Add obstacles avoidance
    def moveToPoint(self, point): # point is a tuple (x,y)
        print("Moving to point state")
        newX = self.cell.coordinate[0]
        newY = self.cell.coordinate[1]
        if newX < point[0]:
            newX = newX + 1
        elif newX > point[0]:
            newX = newX - 1
        if newY < point[1]:
            newY = newY + 1
        elif newY > point[1]:
            newY = newY - 1
        self.cell = self.model.grid[newX, newY]

    def returning(self):
        print("Returning state")
        # Move back to last position before charging
        last_position = self.agentMap.get('LastPositionCharge')
        if last_position:
            if self.cell.coordinate != last_position:
                self.moveToPoint(last_position)
            else:
                # Reached last position, resume normal operation
                self.needToReturn = False
                self.move()      

    def saveInfo(self):
        # Save the agent's current position in the agentMap
        # Look through all grid cells to find the charging station's position.
        for cell in getattr(self.model, 'grid').all_cells:
            for a in getattr(cell, 'agents', []):
                if isinstance(a, ChargingStationAgent):
                    self.agentMap['ChargingStation'] = a.cell.coordinate
                    return

    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        self.saveInfo()
        # Longest path it would take to reach charging station
        if self.batteryLevel <= self.model.width + self.model.height and not self.needToCharge: # Max amount needed to reach charging station from any point
            self.agentMap['LastPositionCharge'] = self.cell.coordinate
            print(self.agentMap["LastPositionCharge"])
            self.needToCharge = True
            self.charging()
        elif self.needToCharge:
            self.charging()
        elif self.needToReturn:
            self.returning()
        else:
            self.move()

        


class ObstacleAgent(FixedAgent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass # Obstacle agents do not move

class TrashAgent(FixedAgent):
    """
    Trash agent. Just to add trash to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell
        self.num_collected = 0

    def collected(self):
        # Remove the trash from the grid/schedule, then notify the model
        # so the global collected count increments once.
        self.remove()
        # Increment model-level collected counter (initialize if missing)
        if not hasattr(self.model, 'num_collected'):
            self.model.num_collected = 0
        self.model.num_collected += 1
        # If we've collected all trash items, stop the simulation
        if getattr(self.model, 'num_collected', 0) >= getattr(self.model, 'num_trash', 0):
            self.model.running = False

    def step(self):
        # Define condition for being collected
        content = self.cell.agents  # Get agents in the cell
        for a in content:
            if isinstance(a, RandomAgent):
                self.collected()
            else:
                pass # Trash agents do not move

class ChargingStationAgent(FixedAgent):
    """
    Charging Station agent. Just to add charging stations to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass # Charging Station agents do not move
