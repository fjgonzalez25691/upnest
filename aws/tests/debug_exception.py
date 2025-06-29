#!/usr/bin/env python3
import sys
import os
# Use babies lambda as reference for validation_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '../lambdas/babies'))

from validation_utils import BabyValidator, ValidationError

# Test the actual error structure
invalid_data = {'name': 'Baby Test'}

try:
    BabyValidator.validate_baby_data(invalid_data)
except ValidationError as e:
    print(f"Exception type: {type(e)}")
    print(f"Exception message: {str(e)}")
    print(f"Exception args: {e.args}")
    print(f"Has errors attribute: {hasattr(e, 'errors')}")
    if hasattr(e, 'errors'):
        print(f"Errors: {e.errors}")
    print(f"Exception dir: {[attr for attr in dir(e) if not attr.startswith('_')]}")
