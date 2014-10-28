from unittest import TestCase
from use.Package import Version
from use.Feature import Feature

class VersionTests(TestCase):

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

    def test_iter_producers_no_features(self):
        self.assertEqual(list(self.basic.iter_producers()), ['a', 'b'])

    def test_iter_producers_with_features(self):
        self.assertEqual(list(self.feat.iter_producers()), ['a', 'b', 'c', 'd', 'e', 'f'])

    def test_iter_producers_with_duplicates(self):
        val = list(self.dup.iter_producers())
        self.assertEqual(val, ['a', 'b', 'c', 'd', 'e', 'f'])

