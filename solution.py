# I believe this records the sequence of updates made
# to the Sudoku puzzle during the solution
assignments = []

def cross(A, B):
    # Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

# /// Sudoku Board Setup Variables
rows = 'ABCDEFGHI'
cols = '123456789'

# variable to print intial grid layout:
initial_state = 'yes'

# Each square in the sudoku is a box
boxes = cross(rows, cols)

# all 9 square row units top left to right
row_units = [cross(r, cols) for r in rows]
# all 9 square column units left to right
column_units = [cross(rows, c) for c in cols]
# all 3x3 groupings of boxes
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Diagonal Units:
diag_down_units = [rows[i]+cols[i] for i in range(len(cols))]

diag_up_units = [rows[len(cols)-i-1]+cols[i] for i in range(len(cols)-1, -1, -1)]


# all the 9 square unit combinations
unitlist = (row_units + column_units + square_units 
        + [diag_down_units] + [diag_up_units])
# the 3 units every box is related to
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

# all the boxes that relate to a particular box
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

# all unique pairings of digits
digit_pairs = [cols[i]+cols[j] for i in range(len(cols)) for j in range (i+1,len(cols))]
# ///

def digit_pairs(digits):
    """
    Receive: string of digits
    Return: list of all unique pairings of digits
    """ 
    return [digits[i]+digits[j] for i in range(len(digits)) for j in range (i+1,len(digits))]

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Strategy:
    For pairs of boxes within the same unit that contain the same 2 digits,
    eliminate those digits from the other boxes within the unit

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # go through every unit
    for unit in unitlist:
        pair_list = {}
        twins = {}
        
        for box in unit: # for every box in the unit
            # if the box is not already in pair_list
            # add the box as a key value pair
            if values[box] not in pair_list.keys():
                # add the value as key with box ID as value
                pair_list[values[box]] = [box]
            elif len(values[box]) == 2:
                print('** Found box: ',box,'with matching twin value: ',values[box],'\n')
                pair_list[values[box]] = pair_list[values[box]]+[box]

        box_list = [v for v in pair_list.values() if len(v) > 1]
        digit_list = [list(k) for k,v in pair_list.items() if len(v) > 1]

        #flatten the list
        flat_box_list = [item for sublist in box_list for item in sublist]
        flat_digit_list = [item for sublist in digit_list for item in sublist]
        
        for box in unit:
            if box not in flat_box_list and len(values[box])>1:
                for digit in flat_digit_list:
                    if digit in values[box]:
                        print('replacing: ',digit,' in: ',box)
                        values = assign_value(values, box, values[box].replace(digit, ''))
    return values
                
    '''
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]

            if len(dplaces) == 1:
                # substitute assign_value() fnc
                #values[dplaces[0]] = digit
                values = assign_value(values,dplaces[0], digit)

        return values    
    '''


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        
        for peer in peers[box]:
            # substitute assign_value() fnc
            #values[peer] = values[peer].replace(digit,'')
            values = assign_value(values, peer, values[peer].replace(digit, ''))
            
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            
            if len(dplaces) == 1:
                # substitute assign_value() fnc
                #values[dplaces[0]] = digit
                values = assign_value(values,dplaces[0], digit)
                
        return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False

    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values, round = 0):
    """Using depth-first search and propagation, create a search tree and solve the sudoku."""
    # First, reduce the puzzle using the reduce_puzzle function
    #print('Searching..')
    assignments.append(values.copy())
    values = reduce_puzzle(values)
    
    if values is False:
        print('Failed at depth: ', round)
        return False ## Failed earlier
    
    if all(len(values[s]) == 1 for s in boxes):
        print('Solution found at depth: ', round)
        return values ## Solved!
    
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    
    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer    
    round +=1
    print('Search Tree Depth Level: ', round)
    
    for value in values[s]:
        # create a shallow copy
        new_sudoku = values.copy()
        # assign the selected value to the box 's'
        new_sudoku[s] = value
        # pass the new sudoku grid to search 
        # which will run reduce_puzzle and attempt to solve
        attempt = search(new_sudoku, round)
        # if attempt is not false 
        # continue selecting squares with few possibilities
        # and passing those values as new sudoku grids to the solver
        # until a new final solution is reached.
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    
#try:
    solution = search(values)
    print('Solution found!')
    return solution

#except:
    print('Could not solve :(')
    return False

if __name__ == '__main__':

    print('Start Sudoku')
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    try:
        display(solve(diag_sudoku_grid))
    except:
        print('** Issue found in Display call..')
        pass
    print('Sudoku Complete')
    
    try:
        from visualize import visualize_assignments
        print('Attempt PyGame Visualization')
        #visualize_assignments(assignments)
        
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
