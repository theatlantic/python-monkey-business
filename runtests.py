import os
import unittest
import sys


current_dir = os.path.abspath(os.path.dirname(__file__))
test_dir = os.path.join(current_dir, 'monkeybiz', 'tests')


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, top_level_dir=current_dir)
    results = unittest.TextTestRunner().run(suite)
    if results.failures or results.errors:
        sys.exit(1)
