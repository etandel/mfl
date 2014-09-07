import unittest

from utils import project_dict, project_tuple


class TestProjectTuple(unittest.TestCase):
    def test_a_copy_is_made_when_no_columns_are_given(self):
        t = [1, 2, 3]
        self.assertEqual(project_tuple()(t), [1,2,3])
        self.assertFalse(project_tuple()(t) is t)

    def test_out_of_bounds(self):
        self.assertRaises(IndexError, project_tuple(5), (1,2))

    def test_project_tuple(self):
        t = tuple(range(10))
        self.assertEqual(project_tuple(1, 4, 6, 7)(t), (1,4,6,7))

class TestProjectDict(unittest.TestCase):
    def test_raise_exception_when_no_columns_are_given(self):
        self.assertRaises(ValueError, project_dict)

    def test_key_doesnt_exist(self):
        self.assertRaises(KeyError, project_dict('a'), {'b': 1})

    def test_project_dict(self):
        d = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        self.assertEqual(project_dict('a', 'c')(d), (1, 3))


if __name__ == '__main__':
    unittest.main()

