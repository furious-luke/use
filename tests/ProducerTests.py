from unittest import TestCase
from use.Producer import Producer

class MatchTests(TestCase):

    def setUp(self):
        self.prod = Producer(None)
        self.patterns = ['test\d+', 'another\d+']
        self.prod.source_pattern = self.patterns
        self.fail_nodes   = ['fail0', 'fail1']
        self.first_nodes  = ['test1', 'test2']
        self.second_nodes = ['another1', 'another2']
        self.both_nodes   = ['test1', 'another1']
        self.mixed_nodes  = ['test1', 'another23', 'fail0', 'test2']

    def test_empty_nodes(self):
        self.assertEqual(self.prod.match(None), False)
        self.assertEqual(self.prod.match([]), False)

    def test_nodes_not_list(self):
        self.assertEqual(self.prod.match(self.fail_nodes[0]), False)
        self.assertEqual(self.prod.match(self.first_nodes[0]), True)
        self.assertEqual(self.prod.match(self.first_nodes[1]), True)
        self.assertEqual(self.prod.match(self.second_nodes[0]), True)
        self.assertEqual(self.prod.match(self.second_nodes[1]), True)

    def test_match(self):
        self.assertEqual(self.prod.match(self.first_nodes), True)
        self.assertEqual(self.prod.match(self.second_nodes), True)
        self.assertEqual(self.prod.match(self.both_nodes), True)

    def test_non_match(self):
        self.assertEqual(self.prod.match(self.fail_nodes), False)

    def test_not_all_match(self):
        self.assertEqual(self.prod.match(self.mixed_nodes), False)

    def test_source_pattern_not_list(self):
        self.prod.source_pattern = self.patterns[0]
        self.assertEqual(self.prod.match(self.fail_nodes), False)
        self.assertEqual(self.prod.match(self.first_nodes), True)
        self.assertEqual(self.prod.match(self.second_nodes), False)
        self.assertEqual(self.prod.match(self.both_nodes), False)
