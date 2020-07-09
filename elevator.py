
UP = 'U'
DOWN = 'D'
INSIDE = 'I'


def oppositeDirection(direction):
    return {
        UP: DOWN,
        DOWN: UP
    }[direction]


def isApproaching(targetFloor, currentFloor, currentDirection):
    return (
            (currentFloor < targetFloor and currentDirection == UP)
            or
            (targetFloor < currentFloor and currentDirection == DOWN)
    )


def parseButtonCommand(command, currentFloor, currentDirection):
    """Given an elevator button, along with current floor and direction,
    return tuple (floor, direction).

    For example:
        '5U' -> (5, UP)
        '9I' -> (9, <direction>)

    In the last example, the <direction> is determined based on current
    floor and direction of the elevator — if we are moving towards the 9th floor,
    the answer will be `currentDirection`, otherwise the opposite direction.

    :param command: a symbolic representation of the button, e.g. '5U' or '9I'.
    :param currentFloor: current floor number
    :param currentDirection: UP or DOWN
    :return: tuple (floor, direction)
    """
    NON_DIGITS = (UP, DOWN, INSIDE)
    for i, char in enumerate(command):
        if char in NON_DIGITS:
            break
    targetFloor = int(command[:i])
    modifier = command[i:]
    if modifier == INSIDE:
        if isApproaching(targetFloor, currentFloor, currentDirection):
            modifier = currentDirection
        else:
            modifier = oppositeDirection(currentDirection)
    return targetFloor, modifier


def nextFloor(currentFloor, currentDirection, buttonsPressed):
    """Returns the next floor the elevator will stop on.

    If there are no commands in the direction of current movement, a RuntimeError will be raised.

    :param currentFloor: What floor we are passing at the moment?
    :param currentDirection: Are we going UP or DOWN at the moment?
    :param buttonsPressed: Which buttons have been pressed?
    :return: Next floor number
    :raises RuntimeError for invalid parameters
    """
    if not buttonsPressed:
        return currentFloor  # Assume we are not moving if no buttons are pressed
    instructions = [parseButtonCommand(button, currentFloor, currentDirection)
                    for button in buttonsPressed]

    # We will construct two lists of floors:
    #  - the floors we will visit before turning around (`nextFloors`),
    #  - and the floors we will visit on the way back before reaching
    #    the current point again (`afterTurningAround`).
    #
    # The rationale is this: suppose we are moving up from floor 2.
    # If there are any "up" commands above 2, we will stop at the lowest of those.
    # Otherwise, we will stop at the highest of the "down" commands above 2,
    # because that will be our turn-around point.
    # The same logic is applied to the downward motion, with mirrored directions.
    nextFloors = []
    afterTurningAround = []
    for floor, direction in instructions:
        if isApproaching(floor, currentFloor, currentDirection):
            if direction == currentDirection:
                nextFloors.append(floor)
            else:
                afterTurningAround.append(floor)

    if not nextFloors and not afterTurningAround:
        raise RuntimeError('Invalid state: cannot be moving %s with commands %s'
                           % (currentDirection, buttonsPressed))

    if nextFloors:
        return (min if currentDirection == UP else max)(nextFloors)
    else:
        return (max if currentDirection == UP else min)(afterTurningAround)
