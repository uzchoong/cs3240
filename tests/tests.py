import unittest


def make_orderer():
    order = {}

    def ordered(f):
        order[f.__name__] = len(order)
        return f

    def compare(a, b):
        return [1, -1][order[a] < order[b]]

    return ordered, compare


ordered, compare = make_orderer()
unittest.defaultTestLoader.sortTestMethodsUsing = compare

class TestQueries(unittest.TestCase):
    @ordered
    def random_test(self):
        self.assertEquals(True, True)
        self.assertTrue(True)
        self.assertIsNone(None)
        self.assertFalse(False)

if __name__ == '__main__':
    unittest.main()