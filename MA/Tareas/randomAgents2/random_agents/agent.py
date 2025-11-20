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
        # vertical zigzag direction: -1 moves up, +1 moves down
        self.zig_vertical = -1
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

        # If agent marked for initial zigzag upward, perform prioritized moves
        if self.agentMap.get('InitialZig'):
            curr_x, curr_y = self.cell.coordinate
            # If already at top row, clear flag
            if curr_y == 0:
                self.agentMap.pop('InitialZig', None)
            else:
                # Try move horizontally first (makes progress), else move up one
                nx = curr_x + self.direction
                if 0 <= nx < self.model.width:
                    dest = self.model.grid[nx, curr_y]
                    if is_safe(dest):
                        self.cell = dest
                        self.batteryLevel -= 1
                        return
                # If horizontal blocked/out-of-bounds, reverse direction and try move up one
                self.direction = -self.direction
                up_y = max(0, curr_y - 1)
                dest = self.model.grid[curr_x, up_y]
                if is_safe(dest):
                    self.cell = dest
                    self.batteryLevel -= 1
                    # If reached top, clear flag
                    if self.cell.coordinate[1] == 0:
                        self.agentMap.pop('InitialZig', None)
                    return
                # fallback: pick any safe neighbor that reduces row (closer to top)
                safe_neighbors = [
                    c for c in self.cell.neighborhood.select(lambda cell: True) if is_safe(c)
                ]
                if safe_neighbors:
                    safe_neighbors.sort(key=lambda c: c.coordinate[1])  # prefer smaller y (towards top)
                    self.cell = safe_neighbors[0]
                    self.batteryLevel -= 1
                    if self.cell.coordinate[1] == 0:
                        self.agentMap.pop('InitialZig', None)
                    return

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
                # Reverse direction if top or bottom are reached
                if next_x < 2 or next_x >= self.model.width - 2:
                    self.direction = -self.direction
                    newX = self.cell.coordinate[0]
                    newY = self.cell.coordinate[1] + (2 * self.zig_vertical)
                    # If we hit the top, switch to going down, if bottom, switch to going up
                    if newY <= 0:
                        newY = 0
                        self.zig_vertical = 1
                    elif newY >= self.model.height - 1:
                        newY = self.model.height - 1
                        self.zig_vertical = -1

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
                                    self.cell = dest
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
        curr_x, curr_y = self.cell.coordinate

        # Sign funcrion to determine direction
        def sign(v): 
            return 0 if v == 0 else (1 if v > 0 else -1)

        # Check if coordinates are in grid bounds
        def in_bounds(x, y):
            return 0 <= x < self.model.width and 0 <= y < self.model.height

        # Check if no obstacles in cell
        def is_safe(cell):
            return not any(isinstance(a, ObstacleAgent) for a in getattr(cell, 'agents', []))

        dx = sign(point[0] - curr_x)
        dy = sign(point[1] - curr_y)

        # Build prioritized candidate moves, to optimize getting to point
        candidates = []
        primary = (curr_x + dx, curr_y + dy)
        candidates.append(primary)

        # Depending on which axis needs movement add preference
        if dx != 0:
            candidates.append((curr_x + dx, curr_y))
        if dy != 0:
            candidates.append((curr_x, curr_y + dy))

        # Depending on vertical direction prefer top ot bottom cells
        if dy != 0:
            candidates.extend([
                (curr_x - 1, curr_y + dy),
                (curr_x + 1, curr_y + dy),
            ])

        # Depending on horizontal direction prefer left or right cells
        if dx != 0:
            candidates.extend([
                (curr_x + dx, curr_y - 1),
                (curr_x + dx, curr_y + 1),
            ])

        # Remove duplicate candidates
        seen = set() # set is ude to keep track of visited coordinates
        uniq_candidates = [] # Avoid duplicates 
        for x, y in candidates:
            if (x, y) not in seen: 
                seen.add((x, y))
                uniq_candidates.append((x, y))

        # Pick the first safe candidate
        for x, y in uniq_candidates:
            if not in_bounds(x, y):
                continue
            cell = self.model.grid[x, y]
            if is_safe(cell):
                self.cell = cell
                return

        # If no candidates are safe, just choose a random safe neighbor
        safe_neighbors = [
            c for c in self.cell.neighborhood.select(lambda cell: True) if is_safe(c)
        ]
        if safe_neighbors:
            # Prefer neighbors that move closer to the target, witgh Manhattan distance
            def manh(c):
                x, y = c.coordinate
                return abs(x - point[0]) + abs(y - point[1]) # Manhattan distance

            safe_neighbors.sort(key=manh)
            self.cell = safe_neighbors[0]
            return

        # If no safe neighbors, do nothing
        return

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
        # If the agent already has a charging station assigned, keep it.
        if 'ChargingStation' in self.agentMap:
            return

        # Prefer a charging station in the agent's current cell
        for a in getattr(self.cell, 'agents', []):
            if isinstance(a, ChargingStationAgent):
                self.agentMap['ChargingStation'] = a.cell.coordinate
                return

        # Fallback: search the grid for any charging station (legacy behavior)
        for cell in getattr(self.model, 'grid').all_cells:
            for a in getattr(cell, 'agents', []):
                if isinstance(a, ChargingStationAgent):
                    self.agentMap['ChargingStation'] = a.cell.coordinate
                    return
                
    def noBattery(self):
        print("No battery state")
        self.remove() # Remove the agent from the model

    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        self.saveInfo()
        # Longest path it would take to reach charging station
        if self.batteryLevel <= 0:
            self.noBattery()
        elif self.batteryLevel <= self.model.width + self.model.height and not self.needToCharge: # Max amount needed to reach charging station from any point
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

    def collected(self):
        # Remove the trash agent safely: only remove if it's still present in its cell
        if hasattr(self, 'cell') and self in getattr(self.cell, 'agents', []):
            self.remove()

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
