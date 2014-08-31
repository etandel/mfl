import unittest

from utils import project


class TestProject(unittest.TestCase):
    def test_project_makes_copy_when_no_columns_are_given(self):
        t = [1, 2, 3]
        self.assertEqual(project()(t), [1,2,3])
        self.assertFalse(project()(t) is t)

    def test_projection_out_of_bounds(self):
        self.assertRaises(IndexError, project(5), (1,2))

    def test_projection(self):
        t = tuple(range(10))
        self.assertEqual(project(1, 4, 6, 7)(t), (1,4,6,7))


if __name__ == '__main__':
    unittest.main()

