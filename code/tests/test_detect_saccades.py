import unittest

import numpy as np
import pandas as pd

from functions.detect_saccades import interpolate_gaze


class GazeInterpolationTest(unittest.TestCase):
    def test_blink_gap_retains_legacy_pchip_intervals(self):
        times = np.linspace(0, 1, 5)
        samples = pd.DataFrame(
            {
                "smpl_time": times,
                "gx": [1, 2, np.nan, 4, 5],
                "gy": 10 + times,
                "type": ["sample", "sample", "blink", "sample", "sample"],
            }
        )

        gaze = interpolate_gaze(samples, fs=16)
        grid = np.linspace(0, 1, 17)
        expected_x = (
            [1, 1.15625, 1.5, 1.84375] + [np.nan] * 8 + [4, 4.15625, 4.5, 4.84375, 5]
        )

        np.testing.assert_array_equal(gaze["smpl_time"], grid)
        np.testing.assert_allclose(gaze["gx"], expected_x, equal_nan=True)
        np.testing.assert_allclose(gaze["gy"], 10 + grid)
        self.assertEqual(gaze["is_blink"].iloc[8], 1)
