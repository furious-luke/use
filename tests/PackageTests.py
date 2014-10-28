from unittest import TestCase
from use.Package import Package, Version
from use.Feature import Feature

class PackageTests(TestCase):

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

    def test_iter_producers(self):
        self.assertEqual(list(self.basic_pkg.iter_producers()), ['c', 'd', 'a', 'b'])

    def test_iter_producers_with_duplicates(self):
        val = list(self.dup_pkg.iter_producers())
        self.assertEqual(val, ['a', 'b', 'e', 'f', 'c', 'd'])

