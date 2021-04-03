# -*- coding: utf-8 -*-
"""
Created on Thu March  25 18:18:12 2021
@author: Reuel R. D'silva

A Set of Custom Errors which are used by the LPP class
"""

class ZeroBasicVariableError(Exception):
    """Raised when a Basic Variable has a value of 0."""
    pass
    
class ZeroEnteringVariableError(Exception):
    """Raised when the Entering Variable has a z-row value of 0"""
    pass

class NoPositiveRatioError(Exception):
    """Raised when there is no positive ratio (i.e. No variable can leave)."""
    pass