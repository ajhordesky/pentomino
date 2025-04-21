from typing import Tuple, Generator
from collections.abc import Callable
from typing import List, Any


class Matrix_Cell:
    def __init__(self, name, l=None, r=None, u=None, d=None, c=None):
        self.name = name
        self.l = l # left
        self.r = r # right
        self.u = u # up
        self.d = d # down
        self.c = c

class Column(Matrix_Cell):
    def __init__(self, name, size=0, l=None, r=None, u=None, d=None, c=None):
        super().__init__(name, l, r, u, d, c)
        self.size = size

class Matrix_Root(Column):
    def __init__(self):
        super().__init__(name="root")


class SMatrix:
    def __init__(self, a):
        self._a = a
        self._h = Matrix_Root()
        self.transform_to_linked_list()

###
# Encapsulation
###
    @property
    def h(self):
        return self._h
    @property
    def a(self):
        return self._a
    @property
    def matrix_shape(self):
        return len(self._a), len(self._a[0])

    # take 2d matrix and set it up to a tiroidal(circle thingy) link list
    def transform_to_linked_list(self):
        self.populate_columns()
        self.connect_rows_together()

###
# Helper funcs to transform matrix 
###
    def connect_rows_together(self):
        for i in range(self.matrix_shape[0]):
            correct_positions = [x for x in range(self.matrix_shape[1]) if self.a[i][x] == 1]
            if len(correct_positions) == 0:
                continue
            original = self.find_next_cell(i, correct_positions[0])
            unoriginal = original
            for x in correct_positions[1:]:
                # swap
                cell = self.find_next_cell(i, x)
                cell.l = unoriginal
                unoriginal.r = cell
                unoriginal = cell
            original.l = unoriginal
            unoriginal.r = original

    def populate_columns(self):
        previous_column = self.h
        for x in range(self.matrix_shape[1]):
            current_column = Column(f"C{x}")
            current_column.l = previous_column
            previous_column.r = current_column
            previous_column = current_column
            previous_row = current_column
            for i in range(self.matrix_shape[0]):
                if self.a[i][x] == 0:
                    continue
                current_row = Matrix_Cell(name = f"R{i}C{x}", c = current_column)
                current_column.size = current_column.size + 1
                # Swap
                current_row.u = previous_row
                previous_row.d = current_row
                previous_row = current_row
            current_column.u = previous_row
            previous_row.d = current_column
        self.h.l = previous_column
        previous_column.r = self.h

    def find_next_cell(self, i, j):
        if (self.a[i][j] == 0):
            return None
        col = self.h
        while (col.name != f"C{j}"):
            col = col.r
        cell = col
        while (cell.name != f"R{i}C{j}"):
            cell = cell.d
        return cell


# returns a list of tuples where each tuple has the row
# numbers to solve the exact cover problem.
def dlx(a):
    # picks column with fewest 1's, makes searching faster
    def choose_col():
        return min(loop_through("r", head), key=lambda col: col.size)
    # backtracking search
    def search_for_solutions():
        # The base case, all constraints are coverd ONCE
        if head.r is head: # if header points to itself, all constraints are covered
            yield tuple([int(x.name[1:].split("C")[0]) for x in potential_solution]) # grab row info

        else:
            c = choose_col() # choose a column
            cover_columns(c) # cover that column(removed from matrix)
            """
                for each row that covers the column, add it to the
                stack (potential solution) and cover all other columns 
                that the row touches. recursively search again.
            """
            for r in loop_through("d", c):
                potential_solution.append(r)
                for j in loop_through("r", r):
                    cover_columns(j.c)
                yield from search_for_solutions()
                # UNDO all operations to try the next possibility
                potential_solution.pop()
                for j in loop_through("l", r):
                    uncover_columns(j.c)
            uncover_columns(c)

    # convert the matrix to a sparse dancing link structure
    # and start searching
    head = SMatrix(a).h
    potential_solution = []
    yield from search_for_solutions()

###
# Other functions to help
###
def cover_columns(c):
    show("h", c)
    for i in loop_through("d", c):
        for j in loop_through("r", i):
            show("v", j)
            j.c.size = j.c.size - 1

def uncover_columns(c):
    for i in loop_through("u", c):
        for j in loop_through("l", i):
            j.c.size = j.c.size + 1
            connect_again("v", j)
    connect_again("h", c)


def loop_helper(direction, func, head):
    assert direction in ("l", "r", "u", "d")
    x = head

    while True:
        x = getattr(x, direction)
        if x is head:
            break
        yield func(x)


def show(direction, cell):
    if direction == "h":
        cell.l.r = cell.r
        cell.r.l = cell.l
    elif direction == "v":
        cell.u.d = cell.d 
        cell.d.u = cell.u


def connect_again(direction, cell):
    if direction == "h":
        cell.l.r = cell
        cell.r.l = cell
    elif direction == "v":
        cell.d.u = cell
        cell.u.d = cell


def loop_through(direction, cell):
    return loop_helper(direction, lambda x: x, cell)

