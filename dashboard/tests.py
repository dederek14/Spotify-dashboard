import numpy as np
from django.test import TestCase
import pandas as pd
from .analyze import load_and_clean_data, plot
import numpy as py
class AnalyzeTests(TestCase):

    def test_load_and_clean_data(self):
        df = pd.DataFrame({
            'endTime': ['2024-01-01 12:00:00', '2024-01-01 13:00:00'],
            'msPlayed': [10000, 30000],
            'trackName': ['Short Song', 'Real Song']
        })

        cleaned = load_and_clean_data(df)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]['trackName'], 'Real Song')
        self.assertIn('hour', cleaned.columns)
        self.assertTrue(isinstance(cleaned.iloc[0]['hour'], (int, np.integer)))

    def test_plot(self):
        df = pd.DataFrame({
            'endTime': pd.date_range(start='2024-01-01', periods=48, freq='H')
        })

        img1, img2 = plot(df)

        self.assertIsInstance(img1, str)
        self.assertIsInstance(img2, str)
        self.assertGreater(len(img1), 100)
        self.assertGreater(len(img2), 100)
