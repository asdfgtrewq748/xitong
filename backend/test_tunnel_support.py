import unittest

from backend.tunnel_support import TunnelSupportCalculator, batch_calculate_tunnel_support


class TunnelSupportCalculatorTest(unittest.TestCase):
    def setUp(self):
        self.calculator = TunnelSupportCalculator()
        self.params = {
            "B": 4.0,
            "H": 3.0,
            "K": 1.0,
            "depth": 200.0,
            "gamma": 18.0,
            "C": 0.5,
            "phi": 30.0,
            "f_top": 2.0,
        }

    def test_complete_result_uses_updated_anchor_and_rod_formulas(self):
        result = self.calculator.calculate_complete(self.params)

        self.assertAlmostEqual(result["basic"]["Lb"], 2.514, places=3)

        self.assertAlmostEqual(result["anchor"]["Nt"], 349.31, places=2)
        self.assertAlmostEqual(result["anchor"]["diameter"], 15.393, places=3)
        self.assertAlmostEqual(result["anchor"]["Lm"], 1.235, places=3)
        self.assertAlmostEqual(result["anchor"]["L_resin"], 1.311, places=3)
        self.assertAlmostEqual(result["anchor"]["L_total"], 4.25, places=3)
        self.assertAlmostEqual(result["anchor"]["plate_capacity_min"], 523.962, places=3)

        self.assertAlmostEqual(result["rod"]["Nt"], 144.513, places=3)
        self.assertAlmostEqual(result["rod"]["diameter"], 20.0, places=3)
        self.assertAlmostEqual(result["rod"]["La"], 0.548, places=3)
        self.assertAlmostEqual(result["rod"]["L_resin"], 0.336, places=3)
        self.assertAlmostEqual(result["rod"]["L_top"], 2.514, places=3)
        self.assertAlmostEqual(result["rod"]["L_side"], 2.662, places=3)
        self.assertAlmostEqual(result["rod"]["plate_capacity_min"], 187.867, places=3)

    def test_batch_result_contains_updated_columns(self):
        frame = batch_calculate_tunnel_support([self.params])

        self.assertEqual(len(frame), 1)
        row = frame.iloc[0].to_dict()

        self.assertIn("Lb(m)", row)
        self.assertIn("L_resin_anchor(m)", row)
        self.assertIn("Tb_anchor(kN)", row)
        self.assertIn("L3_rod(m)", row)
        self.assertIn("L_resin_rod(m)", row)
        self.assertIn("Q_tray_rod(kN)", row)
        self.assertAlmostEqual(row["Nt_rod(kN)"], 144.513, places=3)


if __name__ == "__main__":
    unittest.main()
