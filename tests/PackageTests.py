from unittest import TestCase
from use.Package import Package, Version
from use.Feature import Feature
from use.Producer import Producer

class IterProducersTests(TestCase):

    def setUp(self):
        self.basic = Version()
        self.basic.producers = ['a', 'b']
        self.feat = Version()
        self.feat.producers = ['a', 'b']
        self.feat.features = [Feature(self.feat), Feature(self.feat)]
        self.feat.features[0].producers = ['c', 'd']
        self.feat.features[1].producers = ['e', 'f']
        self.dup = Version()
        self.dup.producers = ['a', 'b', 'c', 'd']
        self.dup.features = [Feature(self.dup), Feature(self.dup)]
        self.dup.features[0].producers = ['c', 'd']
        self.dup.features[1].producers = ['e', 'f']
        self.basic_pkg = Package()
        self.basic_pkg.add_version(self.basic)
        self.basic_pkg.producers = ['c', 'd']
        self.dup_pkg = Package()
        self.dup_pkg.add_version(self.dup)
        self.dup_pkg.producers = ['a', 'b', 'e', 'f']

    def test_no_duplicates(self):
        self.assertEqual(list(self.basic_pkg.iter_producers()), ['c', 'd', 'a', 'b'])

    def test_with_duplicates(self):
        val = list(self.dup_pkg.iter_producers())
        self.assertEqual(val, ['a', 'b', 'e', 'f', 'c', 'd'])

class MatchProducersTests(TestCase):

    def setUp(self):
        self.pkg = Package()
        self.producers = [
            Producer(None, source_pattern='first\d+'),
            Producer(None, source_pattern=['first\d+', 'third\d+']),
            Producer(None, source_pattern='second\d+'),
            Producer(None, source_pattern=['first\d+', 'third\d+', 'fourth\d+']),
        ]
        self.pkg.producers = self.producers
        self.first_nodes  = ['first0', 'first1']
        self.second_nodes = ['second0', 'second1']
        self.occluded_nodes = ['first10', 'third83']
        self.not_occluded_nodes = ['first10', 'third83', 'fourth4']

    def test_no_producers(self):
        self.pkg.producers = []
        self.assertEqual(self.pkg.match_producers(self.first_nodes), [])
        self.assertEqual(self.pkg.match_producers(self.second_nodes), [])

    def test_no_nodes(self):
        self.assertEqual(self.pkg.match_producers(None), [])
        self.assertEqual(self.pkg.match_producers([]), [])

    def test_first_producer(self):
        self.pkg.producers = [self.producers[0]]
        self.assertEqual(self.pkg.match_producers(self.first_nodes), [self.pkg.producers[0]])
        self.assertEqual(self.pkg.match_producers(self.second_nodes), [])

    def test_later_producer(self):
        self.pkg.producers = [self.producers[0], self.producers[2]]
        self.assertEqual(self.pkg.match_producers(self.second_nodes), [self.pkg.producers[1]])
        self.assertEqual(self.pkg.match_producers(self.occluded_nodes), [])

    def test_occluded(self):
        self.assertEqual(self.pkg.match_producers(self.occluded_nodes), [self.pkg.producers[1], self.pkg.producers[3]])
        self.assertEqual(self.pkg.match_producers(self.not_occluded_nodes), [self.pkg.producers[3]])
