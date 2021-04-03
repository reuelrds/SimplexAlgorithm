from ..dashutils import get_span_char_width
from ..dashutils import get_span_char_height
from ..dashutils import get_span_row_count
from ..dashutils import get_span_column_count

from .cell import Cell


def make_cell(table, span, widths, heights, use_headers, cell_padding, header_rows, last_row, last_col):
    """
    Convert the contents of a span of the table to a grid table cell

    Parameters
    ----------
    table : list of lists of str
        The table of rows containg strings to convert to a grid table
    span : list of lists of int
        list of [row, column] pairs that make up a span in the table
    widths : list of int
        list of the column widths of the table
    heights : list of int
        list of the heights of each row in the table
    use_headers : bool
        Whether or not to use headers in the table

    Returns
    -------
    cell : dashtable.data2rst.Cell
    """

    new_widths = []
    if cell_padding is not None:

        for width in widths:
            width = width + cell_padding*2
            new_widths.append(width)

        
    # width = get_span_char_width(span, widths)
    width = get_span_char_width(span, new_widths)
    height = get_span_char_height(span, heights)
    text_row = span[0][0]
    text_column = span[0][1]
    text = table[text_row][text_column]

    # if cell_padding is not None:

    # #     for width in widths:
    #     width = width + cell_padding*2


    lines = text.split("\n")
    for i in range(len(lines)):
        width_difference = width - len(lines[i])
        # lines[i] = ''.join([lines[i], " " * width_difference])
        lines[i] = ''.join([lines[i], " " * width_difference])

    height_difference = height - len(lines)
    empty_lines = []
    for i in range(0, height_difference):
        # empty_lines.append(" " * width )
        empty_lines.append(" " * width )
    lines.extend(empty_lines)

    # output = [
    #     ''.join(["+", (width * "-") + "+"])
    # ]

    output = []

    if span[0][0] in header_rows:
        output = [
            ''.join(["+", (width * "=") + "+"])
        ]
    else:
        output = [
            ''.join(["+", (width * "-") + "+"])
        ]


    double_pipe = u"\u2016"
    for i in range(0, height):
        if (use_headers and span[0][0] in header_rows) or span[0][1] == last_col: 
            output.append(f"{double_pipe}" + lines[i] + f"{double_pipe}")
        elif span[0][1] == last_col - 1:
            output.append("|" + lines[i] + f"{double_pipe}")

        else:
            output.append(f"{double_pipe}" + lines[i] + "|")


    if (use_headers and span[0][0] in header_rows) or span[0][0] == last_row:
        symbol = "="
    elif span[0][0] - 1 in header_rows:
        symbol = "="
    else:
        symbol = "-"

    output.append(
        ''.join(["+", width * symbol, "+"])
    )

    text = "\n".join(output)

    row_count = get_span_row_count(span)
    column_count = get_span_column_count(span)

    cell = Cell(text, text_row, text_column, row_count, column_count)

    return cell
