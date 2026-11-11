import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from e2e_stack import validate_database_name

class E2EDatabaseGuardTests(unittest.TestCase):
    def test_refuses_non_generated_database_names(self):
        for name in ('portfolio','portfolio_test_backend','postgres','portfolio_e2e_','portfolio_e2e_abc;drop database portfolio','portfolio_e2e_123'):
            with self.assertRaises(ValueError):
                validate_database_name(name)
        self.assertEqual(validate_database_name('portfolio_e2e_0123456789abcdef'), 'portfolio_e2e_0123456789abcdef')

if __name__ == '__main__':
    unittest.main()
