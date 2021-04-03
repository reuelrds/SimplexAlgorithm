# -*- coding: utf-8 -*-
"""
Created on Fri March 13 13:13:13 2021

@author: Reuel R. D'silva
"""

# Imports
import re
import itertools
import numpy as np

from constraint import Constraint

from utils import parse_equation
from utils import display_tableau

from LPPErrors import ZeroBasicVariableError
from LPPErrors import ZeroEnteringVariableError
from LPPErrors import NoPositiveRatioError

class LPP:
    """A Class used to represent a Linear Programming Problem

    The solve method can be used to find intersection points,
    corner points of the fesiable region and calculate the
    objective function.

    An example of a Linear Programming Problem:
        Maximize: z = 5x_1 + 4x_2
        Subject to:
            6x_1 + 4x_2 <= 24
            x_1 + 2x_2 <= 6
            -x_1 + x_2 <= 1
            x_2 <= 2
            x_1 >= 0
            x_2 >= 0

    Attributes
    ----------

        obj_var: str
            Objective Variable.
            (for the example above, the obj_var will be z)

        obj_fn: str
            The Objective function represented as a string
            (for the example above, the obj_fn will be 5x_1 + 4x_2)

        X: list[str]
            X represents the variables.
            (for the example above, X will be ["x_1", "x_2"])

        c: NumPy Array
            A vector of coefficients of the objective function
            with size (number_of_variables).

            (for the example above, c will be [5 4])

        problem_type: str
            A String that indicates the type of the LPP.
            It can either be "maximize" or "minimize"

        constraints: list
            It is a list of constraint objects.

        intersection_points: list
            The interection points of the constraints where each point
            is represented as a vector.

        corner_points: list
            The list of corner points of the Feasible Region

        sol_point: NumPy Array
            The point at which the LPP is maximized or minimized

        z: float
            The solution of the LPP
        
        z_values: list
            list of value of the objective function as float
            at each Corner Point.

    """
    def __init__(self, objective, constraints):
        """Initialize LPP

        Parameters
        ----------
        objective : string
            The objective function of the LPP.
        constraints : list
            The constraints of the LPP as a list of strings

        """

        # Parse the first line of the LPP
        # Eg: Maximize: z = 5x1 + 4x2
        #   problem_type = Maximize
        #   obj_var = z
        #   obj_fn = 5x1 + 4x2
        self.problem_type, self.obj_var, self.obj_fn = re.split(
            r":|=",
            objective,
        )
        
        

        # basic_variables list is used to keep track of Basic Variables
        self.basic_variables = []
        
        # Parse the Objective Function Equation and the Constraints
        self.c, self.X = parse_equation(self.obj_fn)
        self.constraints = self.parse_constraints(constraints)
        
        
        
        # Solution Dictionary and the Alternative Solution Dictionary are
        # used to keep track of Solutions of the variables
        #
        # The Alternative Solution Dictionary is only used when the LPP has
        # multiple Optimas
        self.solution = dict.fromkeys(self.X)
        self.alternative_solution = dict.fromkeys(self.X)
        
        
        # Flags to handle special cases in LPPs
        # They help to change the way the program prints
        # the final solution
        self.alternative_optima_exist = False
        self.degenerate_solution = False
        self.unbounded_feasible_region = False
        

       

    def parse_constraints(self, constraints):
        """Parse the string Constraint into Constraint Object


        Parameters
        ----------
        constraints : list
            The constraints of the LPP as a list of strings

        Returns
        -------
        constraints_array : list
            The constraints of the LPP as a list of Constraint Objects

        """
        constraints_array = []

        for constraint in constraints:

            new_constraint = Constraint(constraint, self.X, self.basic_variables)
            new_constraint.parse()
            constraints_array.append(new_constraint)
            
        for constraint in constraints_array:
            constraint.pad()

        return constraints_array
    

    def generate_simplex_tableau(self):
        """A Method to generate a Simplex Tableau
        
        This method Generates a Simplex Tableau as an NumPy Matrix
        """
        
        # Empty Lists to hold the coefficients of the constraints and its value
        A_matrix = []
        b_vector = []

        
        # Populate the A_matrix and the b_vector
        for constraint in self.constraints:
            A_matrix.append(constraint.equation.A)
            b_vector.append(constraint.equation.b)
            
        # Convert them into NumPy Objects
        A = np.array(A_matrix)
        b = np.array(b_vector)
        
        # We multiply c with -1 because:
        #   Maximize z = 5x1 + 4 x2 will be need to be converted into
        #   z - 5x1 - 4x2 = 0
        #   This is because an Easy LP always has the zero-vector (i.e., the origin)
        #   as its trivial solution.
        #   So we can start at the origin by setting z to 0 and then find
        #   the optimum value of z.
        c = np.array(self.c) * -1

        
        # Pad the z-row vector with 1 at the starting and 0 for
        # the slack variables and the solution column
        c = np.pad(c, (1, len(self.X) - len(self.c)), constant_values=(1, 0))
        
        # Pad the b vector (i.e., the RHS column) with 0 at the beginning
        # to account for the value of z.
        b = np.pad(b, (1, 0))
        
        # Stack the c vector on top of the A martix
        partial_tableau = np.vstack((c, A))
        
        # Stack the B vector on the Right side of the c vector and A martix
        # The reshape(-1, 1) is used to expand the dimensions of the b-vector
        #   i.e. convert it from shape (5,) to (5, 1) so that it can be stacked
        #   using hstack
        self.simplex_tableau = np.hstack((partial_tableau, b.reshape(-1, 1)))
        
        

    def _display_intermediate_result(self, non_basic_variables):
        """A Method to display the intermediate solution of the LPP
        

        Parameters
        ----------
        non_basic_variables : list
            A List of Non-Basic Variables for the current Iteration.

        Returns
        -------
        None.

        """       
        # Display the Tableau
        display_tableau(self.simplex_tableau, self.X, self.basic_variables)
        
        print("\nIntermediate Solution: ")
        
        
        # Display value of z
        self.z = self.simplex_tableau[0, -1]
        print(f"\tz = {self.z:.2f}")
        
        
        # Display Non-Basic Variables
        print("Non-Basic Variables: ")
        for idx, var in enumerate(non_basic_variables):
            print(f"\t{var} = 0")
            
            self.solution[var] = 0
        
        
        # Display Basic Variables
        print("\nBasic Variables: ")
        for idx, var in enumerate(self.basic_variables):
            
            self.solution[var] = self.simplex_tableau[idx + 1, -1]
            print(f"\t{var} = {self.solution[var]:.2f}")
            
            
            # Check if the LPP is Degenerate
            # If a Basic variable is 0 at two consective iterations,
            # then the LPP is considered to be Degenerate
            if self.solution[var] == 0:
                
                raise ZeroBasicVariableError("A Basic Variable is zero")
                
                # if not is_potentially_degenerate:
                #     is_potentially_degenerate = True
                # elif is_potentially_degenerate:
                    
                #     # The LP is Degenerate
                #     self.degenerate_solution = True
                #     break
            
    def _get_entering_variable(self, non_basic_variables):
        """A Method to get the Entering Varible and its Index
        

        Parameters
        ----------
        non_basic_variabless : list
            A List of Non-Basic Variables for the current Iteration.

        Returns
        -------
        None.

        """
        
        if self.problem_type.lower() == "maximize":
            
            # Select the Most Negative coefficient in the z-row
            # The [1:] was added to ignore the z-row
            #    
            # This value corrosponds to the the z-row value of the
            # variable and not the actual value
            entering_variable_value = np.min(self.simplex_tableau[0][1:])

            # Get the Index of the Most Negative coefficient in the z-row
            # The [1:] was added to ignore the z-row
            # and the + 1 was added to account for the exclusion of the
            # z-row
            pivot_col_idx = np.argmin(self.simplex_tableau[0][1:]) + 1
        
        elif self.problem_type.lower() == "minimize":
            
            # Select the Most Positive coefficient in the z-row
            # The [1:] was added to ignore the z-row
            #    
            # This value corrosponds to the the z-row value of the
            # variable and not the actual value
            entering_variable_value = np.max(self.simplex_tableau[0][1:])

            # Get the Index of the Most Positive coefficient in the z-row
            # The [1:] was added to ignore the z-row
            # and the + 1 was added to account for the exclusion of the
            # z-row
            pivot_col_idx = np.argmax(self.simplex_tableau[0][1:]) + 1
        
        
        # Get the Pivot Column (The Entering Variable) name
        # The -1 was again added to account for the z-row.
        # Because self.X does not have "z" in it.
        pivot_col_name = self.X[pivot_col_idx - 1]

        

        # If the z-row value of the entering variable is 0,
        # then the LPP is at optimal in both minimization and the
        # maximization cases
        if entering_variable_value == 0:

            
            # Condition to handle special case in LPP where the LPP has
            # Alternative Optimal Solutions
            #
            # This happens when the entering variable has a value of 0 in the z-row
            # and it is a non-basic variable
            #
            # The alternative_optima_exist flag is used to get the second
            # basic optimum solution.
            #
            # The rest of the optimum solutions can then be represented as
            # a convex combination of these two Solutions.

            if not self.alternative_optima_exist and \
                pivot_col_name in non_basic_variables:
                
                # Set the alternative_optima_exist Flag and create
                print("\n\nAlternative Optima Exist")
                print("Because the entering variable has a value of 0 in the z-row and it is a non-basic variable")
                print("Continuing the Iteration to get the next Basic Optimal Solution")
                print(f"{'=' * 50}\n")
                self.alternative_optima_exist = True
                self.alternative_solution = self.solution.copy()
                
            else:
                raise ZeroEnteringVariableError("Entering Variable is Zero")
    

        # If entering_variable_value is not zero, 
        # then print it and return the variable name and its index
        print(f"\n\nEntering Variable: {pivot_col_name}")
        
        return pivot_col_name, pivot_col_idx
    
    
    def _get_leaving_variable(self, pivot_col_idx):
        """A Method to find the Leaving Varible and its Index

        Parameters
        ----------
        pivot_col_idx : int
            The index of the pivot column in the Simplex Tableau.

        Returns
        -------
        None.

        """
        
        # Get the leaving Variable index
        try:
            pivot_row_idx, pivot_row_name  = self._get_pivot_row(pivot_col_idx)
        except NoPositiveRatioError:
            raise
        
        print(f"\nLeaving Variable: {pivot_row_name}")
        
        return pivot_row_name, pivot_row_idx


            
    def _update_tableau(self, pivot_row_idx, pivot_col_idx, pivot_element):
        """Updates the Simplex Tableau
        

        Parameters
        ----------
        pivot_row_idx : int
            The Row Index of the Pivot Row in the Simplex table.
    
        pivot_col_idx : int
            The Column Index of the Pivot Column in the Simplex table.
    
        pivot_element : float
            The Element at the intersection of the Pivot Row and the Pivot Column.

        Returns
        -------
        None.

        """
        
        # Update the Pivot row to New Pivot Row because we need it later
        # to calculate values for the other rows of the Simplex Table
        #
        # New_pivot_row = current_pivot_row_values / pivot_element
        new_pivot_row = self.simplex_tableau[pivot_row_idx, :] / pivot_element
        self.simplex_tableau[pivot_row_idx, :] = new_pivot_row
        


        # Update the rest of the simplex tableau
        # new_row = current_row - (corr_pivot_element) * new_pivot_row
        #
        for idx in range(self.simplex_tableau.shape[0]):
            
            # Update rest of the rows of the Simplex Tableau
            if idx != pivot_row_idx:
                
                old_row = self.simplex_tableau[idx, :]
                corr_pivot_element = self.simplex_tableau[idx, pivot_col_idx]
                
                new_row = old_row - corr_pivot_element * new_pivot_row 

                
                self.simplex_tableau[idx, :] = new_row

    
    def _get_pivot_row(self, pivot_col_idx):
        """Finds the Pivot row
            

        Returns
        -------
        None.

        """
        rhs_column = self.simplex_tableau[1:, -1]
        pivot_column = self.simplex_tableau[1: , pivot_col_idx]
        
        # Initialize an array of -1's to store the ratio
        # ratios = np.ones((simplex_tableau.shape[0] - 1, )) * -1
        ratios = np.full((rhs_column.shape), np.nan)
        
        print("Ratios:")
        
        
            
        
        
        np.divide(
            rhs_column,
            pivot_column,
            out=ratios,
            where=pivot_column != 0
        )
        
        for idx, (rhs_element, pivot_column_element) in \
            enumerate(zip(rhs_column, pivot_column)):
            
            print(f"\t{rhs_element:.2f} / {pivot_column_element:.2f} = {ratios[idx]:.2f}")
        
        
        min_ratio = np.where(ratios > 0, ratios, np.inf).min()
        
        # print(f"rer: {min_ratio}")
        
        if min_ratio <= 0 or min_ratio == np.inf:
            raise NoPositiveRatioError("No Positive Ratio Found")
        
        min_ratio_idx = np.where(ratios > 0, ratios, np.inf).argmin()
        
        
        
        
        pivot_row_idx = min_ratio_idx + 1
        pivot_row_name = self.basic_variables[min_ratio_idx]
        
        
        
        return pivot_row_idx, pivot_row_name
       
    
    def solve(self):
        """Solve the LPP

        The solve method uses the Simplex Algorithm to find the solution of
        the LPP.

        """
        
        # Flag to detect Degeneracy
        is_potentially_degenerate = False    

        for idx in itertools.count(start = 0, step = 1):
            
            print(f"\n\nIteration {idx}:")
            print(f"{'=' * 50}\n")
            
            
            
            # Step 1: Display Intermediate Result
            
            # Get Non Basic Variable List
            non_basic_variables = [
                variable for variable in self.X 
                if variable not in self.basic_variables
            ]
            
            # Call the method that displays the result
            
            try:
                self._display_intermediate_result(non_basic_variables)
            except ZeroBasicVariableError as error:
                print("\n")
                print(f"ZeroBasicVariableError: {error}")
                
                # If a Basic variable is 0 at two consective iterations,
                # then the LPP is considered to be Degenerate
                #
                # So the first Exception marks the LPP as 
                # potentially degenerate
                #
                # And if the expection is raised the Second time 
                # (i.e. at the next iteration), the LPP is marked as
                # Degenerate and the program stops.

                if not is_potentially_degenerate:
                    is_potentially_degenerate = True

                elif is_potentially_degenerate:
                    
                    # The LP is Degenerate
                    self.degenerate_solution = True
                    break
            
            
            
            # Step 2: Get the Entering Variable
            
            try:
                pivot_col_name, pivot_col_idx = self._get_entering_variable(
                    non_basic_variables
                )
            except ZeroEnteringVariableError:
                # print("\n")
                # print(f"ZeroEnteringVariableError: {error}")
                
                # This means that Entering Variable's z-row Value is Zero
                # Therefore, it means that we have reached optimum, and so
                # we break the loop
                break
            
            
            # Step 3: Get the Leaving Variable
            try:
                pivot_row_name, pivot_row_idx = self._get_leaving_variable(
                    pivot_col_idx
                )
            except NoPositiveRatioError as error:
                
                # This error means that there is no positive ratio
                # (i.e., No Variable can leave.)
                # Having no positive ratio means that the Fesiable Region is
                # UnBounded and the value of the objective function can
                # increase infinitely.
                # 
                # So we set the unbounded_feasible_region flag to True and
                # break the loop.
                
                print("\n\n")
                print(f"NoPositiveRatioError: {error}")
                
                self.unbounded_feasible_region = True
                
                break
            
            
            
            # Step 4: The Pivot Element
            
            # Get the Pivot Element using the pivot row index and the pivot
            # column index obtained in the previous two steps.
    
            pivot_element = self.simplex_tableau[pivot_row_idx, pivot_col_idx]
            print(f"Pivot Element: {pivot_element:.4f}")
            
            
            
            # Step 5: Update the Basic Variable List
            
            # Update Basic Variable List to replace the leaving variable
            # with the entering variable
            self.basic_variables[pivot_row_idx - 1] = pivot_col_name
            
            
            
            # Step 6: Update the Simplex Tableau
        
            self._update_tableau(pivot_row_idx, pivot_col_idx, pivot_element)