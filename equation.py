# -*- coding: utf-8 -*-
"""
Created on Fri March 13 12:42:35 2021

@author: Reuel R. D'silva
"""


# Imports
import re

import numpy as np
from utils import parse_equation


class Equation:
    """Used to represent an Equation

    The Equation class is used to represent an Equation of type ax + by = c
    So, lhs refers to "ax + by" and rhs refers to "c"
    
    It can be used to represent an equation with any number of variables.

    Attributes
    ----------
        b: str
            Value of the equation ax + by + cz = d represented as
            float. (i.e. d)
        A: str
            Coefficients of the equation ax + by + cz = d represented as
            a Numpy vector of size (number_of_variables, ).
            (i.e. [a b c])
        variables: list
            A list strings which are used to represent variables.
            (i.e. ["x", "y", "z"])
    """

    def __init__(self, lhs, rhs, variables, flip_sign=False):
        """Initializes the Equation class with coeffs and variables
        
        Parameters
        ----------
        lhs: str
            Left hand side of the equation ax + by = c
        rhs: str
            Right hand side of the equation ax + by = c
        variables: list
            A list strings which are used to represent variables
        flip_sign: boolean
            A boolean ot indicate whether to multiply the equation by -1
        """


        self.b = float(rhs)
        self.variables = variables
        self.A = self.parse(lhs)
        
        if flip_sign:
            self.b = -self.b
            self.A = self.A * -1


    def parse(self, lhs):
        """
        This method parses the lhs "ax + by".
        It extracts the coefficients a & b and converts them
        into integers and finally stacks them in a Numpy vector
        of size (num_of_variables, )

        eg:
            Input: 5x1 + 7x2 - 6x3
            Output: [5 7 -6]

        Parameters
        ----------
        lhs : str
            left hand side of the equation ax + by = c

        Returns
        -------
        NumPy Array
            The method returns the coefficients of the equation
            in an numpy array

        """
        c, X = parse_equation(lhs)

        if len(X) != len(self.variables):

            coeffs_vars_dict = dict(zip(X,c))

            # Fills the coefficient of the missing variables with 0
            c = [coeffs_vars_dict[var]
                 if var in coeffs_vars_dict else 0
                 for var in self.variables]

        return np.array(c)
