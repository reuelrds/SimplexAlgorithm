# -*- coding: utf-8 -*-
"""
Created on Fri March 13 13:09:50 2021

@author: Reuel R. D'silva
"""

# Imports
import re
import numpy as np

from equation import Equation

class Constraint:
    """Used to represent constraints in a LPP


    Attributes
    ----------
        sign_type: str
            Type of constraint. It can either be >= or <= or =
        constraint_str: str
            The constraint in string format.
    """
    def __init__(self, constraint, variables, slack_variables):
        """Initialize Constraint class

        Parameters
        ----------
        constraint_str : str
            The constraint of an LPP in string format.
            e.g. 5x1 + 6x2 - 2x3 >= 4
        variables : list[str]
            Variables of the constraint as list of strings.
            e.g. ["x1", "x2", "x3"]
        slack_variables: [str]
            a List of Slack Variables
        equation: object
            A Constraint expressed as an equation by adding appropriate
            slack variable and representes as an object of the 
            Equation Class
        """
        
        
        # Initialize initial object variables
        self.constraint_str = constraint
        self.variables = variables
        
        self.slack_variables = slack_variables
        
        
        
        
        
    def parse(self):
        """Parses a Constraint
        
        This method parses a constraint by converting it into
        an equation by adding appropriate slack variables

        """
        
        # Splits the constraint.
        # eg: 6x1 + 4x2 <= 24
        #   lhs: 6x1 + 4x2
        #   sign_type: <=
        #   rhs: 24
        lhs, sign_type, rhs = re.split(
            r"(>=|=|<=)",
            self.constraint_str
        )
        
        # Flag to keep track of whether >= constraint can be changed 
        # into >= by multiplying by -1.
        flip_sign = False
        
        if sign_type != "==":
            
            
            # Get the Last variable
            last_variable = self.variables[-1]
            
            # Get the subscript of the last variable
            last_variable_subscript = int(last_variable[-1])
            
            # Create a variable to act as slack or surplus
            slack_var = f"s{last_variable_subscript + 1}"
            
            # Append the new Variable to the variables list
            self.variables.append(slack_var)
            
            self.slack_variables.append(slack_var)
            
            
            
            if sign_type == "<=":
                
                print(f"Adding a Slack Variable {slack_var} as the constraint "
                      f"{self.constraint_str} is of <= type")

                # Add the Slack Variable to the LP
                lhs += f"+ {slack_var}"
                
            if sign_type == ">=" and float(rhs.strip()) < 0:
                
                
                print(f"Multiplying constraint {self.constraint_str} by -1 "
                      f"and Adding a Slack Variable {slack_var} as the "
                      "constraint is of >= type but the RHS is negative.")

                # Add the Slack Variable to the LP
                lhs += f"- {slack_var}"
                flip_sign = True

        # Convert the constraint into an equation
        self.equation = Equation(lhs, rhs, self.variables, flip_sign=flip_sign)
        
        
    def pad(self):
        
        pad_size =  len(self.variables) - len(self.equation.A)
        
        if pad_size >= 0:
            # self.equation.A += [0] * pad_size
            self.equation.A = np.pad(self.equation.A, (1, pad_size))
            

    


    def __str__(self):
        """Returns String representation of the constraint.

        The methods gets called when the constraint is printed to console.
        eg. print(constraint)

        Returns
        -------
        str
            String representation of the constraint.

        """
        return self.constraint_str
