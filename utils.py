# -*- coding: utf-8 -*-
"""
Created on Fri March 13 13:16:30 2021
@author: Reuel R. D'silva

A set of Utility functions to help aid the LPP module
"""

# Import required pacakges
import re
import numpy as np

from table import data2rst


def pause():
    """Pause the script untill a key press

    Returns
    -------
    None.

    """
    _ = input("Press a Key to Continue...")


def read_lp(input_filename = "input.txt"):
    """Read The LPP from the input text file

    read_lp is a Generator Function that reads a text file
    and yields one single LPP.

    The Yield is triggered when it encounters a blank line.
    It ignores the Comments, which are lines starting with a # sign.


    Parameters
    ----------
    input_filename : str, optional
        The Input file Name. The default is "input.txt".

    Yields
    ------
    lp_lines : list
        Yields a LPP as a list of strings.

    """
    with open(input_filename, "r", encoding="utf8") as input_file:

        lp_lines = []
        for line in input_file:

            # Remove the leading and the trailing whiteshapces
            line = line.strip()

            # We can test if line is None as the strip() function
            # returns None it the line is empty
            if not line:
                
                # Yield the LP to the main function to parse and solve
                yield lp_lines
                lp_lines = []

            # Ignore Subject to and Comments 
            elif line[:7] == "Subject" or line[0] == "#":
                continue

            # Else append the line to the current LP
            elif line != "":
                lp_lines.append(line)
                
        # This else loop runs when the for loop exits successfully.
        # It is used to yield last LP which is not yielded by the first
        # yield if there is no empty line at the end of the file.
        else:
            if len(lp_lines) != 0:
                yield lp_lines


def parse_equation(equation_string):
    """Parse an function

    This function parses the coefficients and variables from a funtion
    that is represented as a string using Regular Expressions.

    Parameters
    ----------
    equation_string : str
        function represented as a string.

    Returns
    -------
    c : list
        list of coeffieients as integers.
    X : list
        list of variables as strings.

    """
    
    # A regular Expression to group coefficient and variable
    # eg: 5x_1: 
    #       first group 5, second group x_1.
    pattern = r"([-+]{0,1}\d*)([\w\d]+)"

    # Use findall to find all pairs of variables and coeffieients
    match = re.findall(pattern, equation_string.replace(" ", ""))

    X = []
    c = []

    for pair in match:
        X.append(pair[1])

        # Takes care of case like -x_1 (no coefficient present)
        if pair[0] == "-":
            c.append(-1)
        
        # takes care of case like x_1 or +x_1 (coefficient is implied to be 1)
        elif pair[0] == "" or pair[0] == "+":
            c.append(1)
        else:
            c.append(int(pair[0]))

    return c, X


def create_slack_or_surplus_variable(last_variable):
    """Creates a Slack or a Surplus Variable
    

    Parameters
    ----------
    last_variable : str
        The last variable in the variables list.

    Returns
    -------
    str
        A Slack or Surplus variable with its subscript continuing after
        the last_variable's subscript.

    """
    
    # Get the subscript of the last variable
    last_variable_subscript = last_variable[-1]
    
    # Create and reutrn a slack or surplus variable
    return f"s{last_variable_subscript + 1}"


def pad(array, variables):
    """Pads an numpy array

    Parameters
    ----------
    array : numpy.Array
        A NumPy Array to be padded.

    variables : list of str
        Variables as a list of strings.

    Returns
    -------
    array : numpy.Array
        The Padded Array.

    """
        
    pad_size =  len(variables) - len(array)
    
    if pad_size >= 0:
        # self.equation.A += [0] * pad_size
        array = np.pad(array, (1, pad_size))
        
    return array


def display_tableau(tableau, variables, basic_variables):
    """Displays the Simplex Tableau
    

    Parameters
    ----------
    tableau : numpy.Array
        A Simplex Tableau as a NumPy Array.

    variables : list of str
        Variables of an LPP as a list of strings.

    basic_variables : list of str
        The Basic Variables as a List of strings.


    """
    
    # Generate empty Cells List
    # These cells are merged with the All Variables Cell so that
    # it can span over all the variables
    empty_cells = [""] * len(variables)
    
    # Construct the Header Row of the Simplex Tableau
    table = [
        ["Basic Vars", "All Variables", *empty_cells,"RHS (Solution)"],
        ["", "z", *variables, ""]
    ]
    
    
    # Insert z at the head of basic variables list
    # This list is used to make the LHS or the Basic variables Column
    # of the Simplex Tableau.
    basic_variables_copy = basic_variables[:]
    basic_variables_copy.insert(0, "z")
    
    
    # Used to control the precision of the values in the Simplex Tableau
    # The Precision is restricted to 3 places after the decimal
    format_float = lambda x: np.format_float_positional(x, precision=3)
    
    
    # Add the rest of the rows to the Simplex Tableau list
    for idx, basic_variable in enumerate(basic_variables_copy):
        
        
        elements = [ format_float(element) for element in tableau[idx]]
        new_row = [basic_variable, *elements]

        table.append(new_row)
        
    
    
    # Row and the Column Spans in the Simplex Tableau
    
    # The Basic Variables Cell Spans two rows
    basic_vars_span = [
        [0, 0], [1, 0]    
    ]
    
    
    # Similarly, the RHS(Solution) cell Spans two rows
    RHS_solution_span = [
        [0, len(table[0]) - 1], [1, len(table[0]) - 1],    
    ]
    
    # The All Variables cell spans over all the variable columns
    all_vars_span = [ [0, i + 1] for i in range(len(variables) + 1) ]


    my_spans = [
        basic_vars_span,
        RHS_solution_span,
        all_vars_span
    ]



    # Generate the Simplex Tableau as ASCII String    
    table = data2rst(
        table,
        spans=my_spans,
        use_headers=True,
        center_cells=True,
        center_headers=True,
        header_rows=[0, 1],
        cell_padding=2
    )
    
    # Print the Simplex Tableaus
    print(table)


def print_lpp(lpp):
    """Prints the LPP which was recieved as input
    

    Parameters
    ----------
    lpp : Object of type LPP
        An LPP Object with its solve method already called.

    """
    print("\n{}: {} = {}".format(lpp.problem_type.capitalize(), lpp.obj_var, lpp.obj_fn))
    print("Subject to:")
    for constraint in lpp.constraints:
        print("\t{}".format(constraint.constraint_str))


def display_result(lpp):
    """Print the Solution of the LPP to the console window.
    
    Parameters
    ----------
    lpp : Object of type LPP
        An LPP Object with its solve method already called.
    """
    
    # Separator
    print(f"\n{'='*50}")
    print("Solution:")
    
    # Print the input LPP
    print_lpp(lpp)
    
    
    if lpp.alternative_optima_exist:
        
        print("\nThe above LPP has Multiple Alternative Optimum Solutions.")
        print("Two such solutions are: ")
        
        print("\nAlternative Solution 1: ")
        for var, value in lpp.alternative_solution.items():
            print("\t{:} = {:.2f}".format(var, value))
    
        print("With Optimal Solution: z = {}".format(lpp.z))
        
        print("\nAlternative Solution 2: ")
        for var, value in lpp.solution.items():
            print("\t{:} = {:.2f}".format(var, value))
    
        print("With Optimal Solution: z = {}".format(lpp.z))
        
        
        print("\n\nAll the Solutions can be written as a convex combination ")
        print("of the above two Basic Optimal Solutions: ")
        
        print(f"\n\tLet A = {list(lpp.alternative_solution.values())}")
        print(f"\tAnd B = {list(lpp.solution.values())}")
        
        alpha = u"\u03b1"
        print("\nAll the Solutions can be represented as:")
        print(f"\tP = {alpha}1 * A + {alpha}2 * B, where {alpha}1 + {alpha}2 = 1 and {alpha}1, {alpha}2 >= 0")

                
        
        
    elif lpp.degenerate_solution:
        pass
    elif lpp.unbounded_feasible_region:
        print("\nThe above Problem has Unbounded Feasible Region")
        print("And the objective function's value can be increased infinitely")
    else:
        # Print Solution
        print("\nThe above LPP is optimized at: ")
        for var, value in lpp.solution.items():
            print("\t{:} = {:.2f}".format(var, value))
    
        print("With Optimal Solution: z = {}".format(lpp.z))
    
    
    
    