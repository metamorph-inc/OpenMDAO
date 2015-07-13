""" Unit test for the ShelveRecorder. """

import unittest
import shelve
from pickle import HIGHEST_PROTOCOL
from openmdao.recorders.shelverecorder import ShelveRecorder
from recordertests import RecorderTests
from openmdao.util.recordutil import format_iteration_coordinate
from openmdao.test.testutil import assert_rel_error


class TestShelveRecorder(RecorderTests.Tests):
    filename = "shelve_test"

    def setUp(self):
        self.recorder = ShelveRecorder(self.filename, flag="n", protocol=HIGHEST_PROTOCOL)

    def assertDatasetEquals(self, expected, tolerance):
        # Close the file to ensure it is written to disk.
        self.recorder.out.close()
        self.recorder.out = None

        sentinel = object()

        f = shelve.open(self.filename)
        for coord, expect in expected:
            icoord = format_iteration_coordinate(coord)
            groupings = (
                ("/Parameters", expect[0]),
                ("/Unknowns", expect[1]),
                ("/Residuals", expect[2])
            )

            for label, values in groupings:
                local_name = icoord + label
                actual = f[local_name]
                # If len(actual) == len(expected) and actual <= expected, then
                # actual == expected.
                self.assertEqual(len(actual), len(values))
                for key, val in values:
                    found_val = actual.get(key, sentinel)
                    if found_val is sentinel:
                        self.fail("Did not find key '{0}'".format(key))
                    assert_rel_error(self, found_val, val, tolerance)
                del f[local_name]

        # Having deleted all found values, the file should now be empty.
        self.assertEqual(len(f), 0)

        f.close()


if __name__ == "__main__":
    unittest.main()