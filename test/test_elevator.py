import unittest
import elevator


class ElevatorTestCase(unittest.TestCase):
    def test_opposite(self):
        self.assertEqual(elevator.oppositeDirection(elevator.UP), elevator.DOWN)
        self.assertEqual(elevator.oppositeDirection(elevator.DOWN), elevator.UP)

    def test_isApproaching(self):
        # Going from floor 2 up, approaching 5 ? should say YES
        self.assertTrue(elevator.isApproaching(5, 2, elevator.UP))
        # Going from floor 2 up, approaching 2 ? should say NO
        self.assertFalse(elevator.isApproaching(2, 2, elevator.UP))
        # Going from floor 2 up, approaching 1 ? should say NO
        self.assertFalse(elevator.isApproaching(1, 2, elevator.UP))
        # Going from floor 20 down, approaching 10 ? should say YES
        self.assertTrue(elevator.isApproaching(10, 20, elevator.DOWN))
        # Going from floor 20 down, approaching 20 ? should say NO
        self.assertFalse(elevator.isApproaching(20, 20, elevator.DOWN))
        # Going from floor 20 down, approaching 30 ? should say NO
        self.assertFalse(elevator.isApproaching(30, 20, elevator.DOWN))

    def test_parseButtonCommand(self):
        correctResults = [
            # Button UP pressed on 2nd floor: we must visit floor 2 on the way up.
            (('2U', None, None), (2, elevator.UP)),
            # Button DOWN pressed on 3rd floor: we must visit floor 3 on the way down.
            (('3D', None, None), (3, elevator.DOWN)),
            # Button 3 pressed inside elevator, we are going up from 2nd floor: we will visit floor 3 on the way up.
            (('3I', 2, elevator.UP), (3, elevator.UP)),
            # Button 3 pressed inside elevator, we are going down from 2nd floor: we will visit floor 3 on the way up.
            (('3I', 2, elevator.DOWN), (3, elevator.UP)),
            # Button 3 pressed inside elevator, we are going up from 5th floor: we will visit floor 3 on the way down.
            (('3I', 5, elevator.UP), (3, elevator.DOWN)),
            # Button 3 pressed inside elevator, we are going down from 5th floor: we will visit floor 3 on the way down.
            (('3I', 5, elevator.DOWN), (3, elevator.DOWN)),
            # Button 3 pressed inside elevator, we are going up from 3rd floor: we will visit floor 3 on the way down.
            (('3I', 3, elevator.UP), (3, elevator.DOWN)),
            # Button 3 pressed inside elevator, we are going down from 3rd floor: we will visit floor 3 on the way up.
            (('3I', 3, elevator.DOWN), (3, elevator.UP)),
        ]
        for args, results in correctResults:
            self.assertEqual(elevator.parseButtonCommand(*args), results)

    def test_no_buttons(self):
        self.assertEqual(elevator.nextFloor(42, elevator.UP, []), 42)

    def test_up_simple(self):
        next = elevator.nextFloor(3, elevator.UP, ['4D'])
        self.assertEqual(next, 4)
        next = elevator.nextFloor(3, elevator.UP, ['4U'])
        self.assertEqual(next, 4)

    def test_down_simple(self):
        next = elevator.nextFloor(3, elevator.DOWN, ['2D'])
        self.assertEqual(next, 2)
        next = elevator.nextFloor(3, elevator.DOWN, ['2U'])
        self.assertEqual(next, 2)

    def test_updown(self):
        next = elevator.nextFloor(3, elevator.UP, ['4D', '2D'])
        self.assertEqual(next, 4)
        next = elevator.nextFloor(3, elevator.UP, ['4U', '2U'])
        self.assertEqual(next, 4)

    def test_downup(self):
        next = elevator.nextFloor(3, elevator.DOWN, ['4D', '2D'])
        self.assertEqual(next, 2)
        next = elevator.nextFloor(3, elevator.DOWN, ['4U', '2U'])
        self.assertEqual(next, 2)

    def test_invalid(self):
        # We can't be going up if the only unprocessed command is below current level
        self.assertRaises(RuntimeError, elevator.nextFloor, 3, elevator.UP, ['2U'])

        # We can't be going down if the only unprocessed command is above current level
        self.assertRaises(RuntimeError, elevator.nextFloor, 3, elevator.DOWN, ['9U'])

    def test_skip_up(self):
        # The elevator is going up, and all buttons are DOWN.
        # It will have to skip to the top and start from there.
        next = elevator.nextFloor(2, elevator.UP, ['3D', '4D'])
        self.assertEqual(next, 4)

    def test_skip_down(self):
        # The elevator is going down, and all buttons are UP.
        # It will have to skip to the bottom and start from there.
        next = elevator.nextFloor(20, elevator.DOWN, ['3U', '4U'])
        self.assertEqual(next, 3)

    def test_current_floor_up(self):
        # If current floor is pressed, ignore it
        next = elevator.nextFloor(2, elevator.UP, ['2D', '2U', '3U'])
        self.assertEqual(next, 3)

    def test_current_floor_down(self):
        # If current floor is pressed, ignore it
        next = elevator.nextFloor(5, elevator.DOWN, ['5D', '5U', '3U'])
        self.assertEqual(next, 3)


if __name__ == '__main__':
    unittest.main()
