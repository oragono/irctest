import unittest
import operator
import itertools

class NotImplementedByController(unittest.SkipTest, NotImplementedError):
    def __str__(self):
        return 'Not implemented by controller: {}'.format(self.args[0])

class OptionalExtensionNotSupported(unittest.SkipTest):
    def __str__(self):
        return 'Unsupported extension: {}'.format(self.args[0])

class OptionalSaslMechanismNotSupported(unittest.SkipTest):
    def __str__(self):
        return 'Unsupported SASL mechanism: {}'.format(self.args[0])

class OptionalityReportingTextTestRunner(unittest.TextTestRunner):
    """Small wrapper around unittest.TextTestRunner that reports the
    number of tests that were skipped because the software does not support
    an optional feature."""
    def run(self, test):
        result = super().run(test)
        if result.skipped:
            print()
            print('Some tests were skipped because the following optional'
                    'specifications/mechanisms are not supported:')
            msg_to_tests = itertools.groupby(result.skipped,
                    key=operator.itemgetter(1))
            for (msg, tests) in sorted(msg_to_tests):
                print('\t{} ({} test(s))'.format(msg, sum(1 for x in tests)))
        return result