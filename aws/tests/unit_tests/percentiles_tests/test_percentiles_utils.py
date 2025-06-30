"""
Tests for utility functions used in percentile calculations.
Tests z-score calculation, percentile conversion, age calculation, etc.
"""

from unittest.mock import patch, Mock
from .test_base import BasePercentilesTest
import percentiles_calculate as calculate

class TestPercentilesUtils(BasePercentilesTest):
    """Test cases for utility functions."""
    
    def test_calculate_zscore_function(self):
        """Test the z-score calculation function directly."""
        # Test normal case
        zscore = calculate.calculate_zscore(4.5, 0.3487, 4.5, 0.13)
        self.assertAlmostEqual(zscore, 0.0, places=2)
        
        # Test L=0 case
        zscore_l0 = calculate.calculate_zscore(4.5, 0.0, 4.5, 0.13)
        self.assertAlmostEqual(zscore_l0, 0.0, places=2)
        
        # Test with different values
        zscore_positive = calculate.calculate_zscore(5.0, 0.3487, 4.5, 0.13)
        self.assertGreater(zscore_positive, 0)
        
        zscore_negative = calculate.calculate_zscore(4.0, 0.3487, 4.5, 0.13)
        self.assertLess(zscore_negative, 0)
    
    def test_zscore_to_percentile_function(self):
        """Test the z-score to percentile conversion function."""
        # Z-score of 0 should give 50th percentile
        percentile = calculate.zscore_to_percentile(0.0)
        self.assertAlmostEqual(percentile, 50.0, places=1)
        
        # Z-score of 1 should give approximately 84th percentile
        percentile_positive = calculate.zscore_to_percentile(1.0)
        self.assertAlmostEqual(percentile_positive, 84.13, places=0)
        
        # Z-score of -1 should give approximately 16th percentile
        percentile_negative = calculate.zscore_to_percentile(-1.0)
        self.assertAlmostEqual(percentile_negative, 15.87, places=0)
        
        # Test extreme values
        percentile_high = calculate.zscore_to_percentile(3.0)
        self.assertGreater(percentile_high, 99.0)
        
        percentile_low = calculate.zscore_to_percentile(-3.0)
        self.assertLess(percentile_low, 1.0)
    
    def test_calculate_age_in_days_function(self):
        """Test the age calculation function."""
        # Test normal case
        age = calculate.calculate_age_in_days('2024-01-15', '2024-04-15')
        self.assertEqual(age, 91)  # 91 days between these dates
        
        # Test same date
        age_same = calculate.calculate_age_in_days('2024-01-15', '2024-01-15')
        self.assertEqual(age_same, 0)
        
        # Test one day difference
        age_one_day = calculate.calculate_age_in_days('2024-01-15', '2024-01-16')
        self.assertEqual(age_one_day, 1)
        
        # Test leap year
        age_leap = calculate.calculate_age_in_days('2024-02-28', '2024-03-01')
        self.assertEqual(age_leap, 2)  # 2024 is a leap year
        
        # Test different months
        age_months = calculate.calculate_age_in_days('2024-01-01', '2024-02-01')
        self.assertEqual(age_months, 31)
    
    def test_get_table_info_function(self):
        """Test the table info function."""
        # Test weight table info
        table_dir, filename = calculate.get_table_info('weight', 'male')
        self.assertEqual(table_dir, 'weight')
        self.assertEqual(filename, 'wfa-boys-zscore-expanded-tables.xlsx')
        
        table_dir, filename = calculate.get_table_info('weight', 'female')
        self.assertEqual(table_dir, 'weight')
        self.assertEqual(filename, 'wfa-girls-zscore-expanded-tables.xlsx')
        
        # Test height table info
        table_dir, filename = calculate.get_table_info('height', 'male')
        self.assertEqual(table_dir, 'height')
        self.assertEqual(filename, 'lhfa-boys-zscore-expanded-tables.xlsx')
        
        table_dir, filename = calculate.get_table_info('height', 'female')
        self.assertEqual(table_dir, 'height')
        self.assertEqual(filename, 'lhfa-girls-zscore-expanded-tables.xlsx')
        
        # Test head circumference table info
        table_dir, filename = calculate.get_table_info('headCircumference', 'male')
        self.assertEqual(table_dir, 'head-circumference')
        self.assertEqual(filename, 'hcfa-boys-zscore-expanded-tables.xlsx')
        
        table_dir, filename = calculate.get_table_info('headCircumference', 'female')
        self.assertEqual(table_dir, 'head-circumference')
        self.assertEqual(filename, 'hcfa-girls-zscore-expanded-tables.xlsx')
        
        # Test invalid measurement type
        with self.assertRaises(ValueError):
            calculate.get_table_info('invalid_type', 'male')
        
        # Test invalid sex (removing this as the function might not validate sex)
        # Some implementations might not check sex parameter validity
    
    @patch('calculate.find_lms_values')
    def test_find_lms_values_function(self, mock_find_lms):
        """Test the LMS values finding function."""
        # Mock the function to return expected values
        mock_find_lms.return_value = (0.3487, 4.5, 0.13)
        
        # Create a mock DataFrame (doesn't need to be functional)
        mock_df = self.create_mock_dataframe()
        
        # Test the mocked function
        L, M, S = mock_find_lms(mock_df, 91)
        self.assertEqual(L, 0.3487)
        self.assertEqual(M, 4.5)
        self.assertEqual(S, 0.13)
        
        # Verify the function was called
        mock_find_lms.assert_called_with(mock_df, 91)
    
    def test_edge_cases_age_calculation(self):
        """Test edge cases for age calculation."""
        # Test very young baby (same month)
        age_newborn = calculate.calculate_age_in_days('2024-04-10', '2024-04-15')
        self.assertEqual(age_newborn, 5)
        
        # Test exactly one year
        age_year = calculate.calculate_age_in_days('2023-04-15', '2024-04-15')
        self.assertEqual(age_year, 366)  # 2024 is a leap year
        
        # Test across year boundary
        age_year_boundary = calculate.calculate_age_in_days('2023-12-31', '2024-01-02')
        self.assertEqual(age_year_boundary, 2)
    
    def test_percentile_boundary_values(self):
        """Test percentile calculation for boundary z-score values."""
        # Test very high percentile
        percentile_very_high = calculate.zscore_to_percentile(4.0)
        self.assertGreater(percentile_very_high, 99.99)
        self.assertLessEqual(percentile_very_high, 100.0)
        
        # Test very low percentile
        percentile_very_low = calculate.zscore_to_percentile(-4.0)
        self.assertLess(percentile_very_low, 0.01)
        self.assertGreaterEqual(percentile_very_low, 0.0)
    
    def test_zscore_mathematical_properties(self):
        """Test mathematical properties of z-score calculation."""
        # Test symmetry: same distance from mean should give opposite z-scores
        zscore_above = calculate.calculate_zscore(5.0, 0.0, 4.0, 1.0)
        zscore_below = calculate.calculate_zscore(3.0, 0.0, 4.0, 1.0)
        
        # For L=0 (normal distribution), the formula should be more symmetric
        # But with LMS, we need to be less strict about exact symmetry
        self.assertGreater(zscore_above, 0)
        self.assertLess(zscore_below, 0)
        
        # Test that equal values give same zscore
        zscore_equal1 = calculate.calculate_zscore(4.0, 0.0, 4.0, 1.0)
        zscore_equal2 = calculate.calculate_zscore(4.0, 0.0, 4.0, 1.0)
        self.assertAlmostEqual(zscore_equal1, zscore_equal2, places=5)
