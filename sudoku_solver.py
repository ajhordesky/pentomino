# A soduku solver using dancing links
import sys
import re
from itertools import chain, product
from dancing_links import dlx

def get_data():
	lines = sys.stdin.read() # one-line string
	cleaned = re.sub(r'[|\-\+\s]', '', lines) # replaces +,|,-, and whitespace with ''
	digits = list(map(int, cleaned)) # converts every char into an integer
	sudoku_grid = [digits[i:i+9] for i in range(0, 81, 9)] # list of list of 9 each
	return sudoku_grid


def solve_sudoku(sudoku_grid):
	"""
		(row, col, number) the block below creates/holds a list of tuples where
		each tuple COULD solve the puzzle. its the boards possiblies.
	"""
	all_possiblities = [] # a list of tuples (row, col, POSSIBLE number)
	for row, col in product(range(9), range(9)): # product returns [0,0], [0,1], all possible combinatins
		if sudoku_grid[row][col] == 0: # if that row and col == 0 (meaning empty on the board inputed)
			for number in range(9): # then the possiblites must be 1-9 so (row, col, 1), (row, col, 2), etc...
				all_possiblities.append((row, col, number))
		else:
			number = sudoku_grid[row][col] - 1 # if its not empty, then that row/col has a FIXED number already given.
			all_possiblities.append((row, col, number))

	"""
		This block defines the rules, it creates a list of all constraints
		represented as strings. these define a VALID sudoku solution. We also
		add a dictionary at the end for indexing to the constraint string, this 
		is for fast lookup, O(1).
	"""
	all_constraints = []
	for row in range(9): # -> each cell (row, col) must have ONE number ONLY
		for col in range(9):
			all_constraints.append(f"R{row+1}C{col+1}")
	for row in range(9): # -> each row must have 1-9
		for number in range(9):
			all_constraints.append(f"R{row+1}#{number+1}")
	for col in range(9): # -> each column must have 1-9
		for number in range(9):
			all_constraints.append(f"C{col+1}#{number+1}")
	for box in range(9): # -> each box must contain 1-9
		for number in range(9):
			all_constraints.append(f"B{box+1}#{number+1}")

	# a dictionary for fast constraint lookup by index
	constraints_index = {constraint: index for index, constraint in enumerate(all_constraints)}

	# BUILDING the exact cover matrix
	"""
		this makes the 2d matrix, initializing all to 0 at the start, for each row(possiblility)
		we get their 4 constraints and add it to a list and then we look up there index
		and in the 2d matrix we set them to 1's. so each row should have all 0's and FOUR 1's,
		this sets up the 2d matrix for dancing links to solve. 
	"""
	cover_matrix = [[0] * len(all_constraints) for x in range(len(all_possiblities))]
	for index, (row, col, number) in enumerate(all_possiblities):
		box_index = 3 * (row//3) + col // 3 # finding the box index, 0 is top left, 8 is bottome right box.
		mark_possible_constraints = [f"R{row+1}C{col+1}", f"R{row+1}#{number+1}", f"C{col+1}#{number+1}", f"B{box_index+1}#{number+1}"]
		for x in mark_possible_constraints:
			cover_matrix[index][constraints_index[x]] = 1

	########
	# HELPERS
	########
	def purple_color(x):
		return f"\033[95m{x}\033[0m"

	def board_format():
		bar = " - - - + - - - + - - -\n"
		line = " {} {} {} | {} {} {} | {} {} {}\n"
		template = ""
		for i in range(9):
			template += line
			if i in {2, 5}:
				template += bar
		return template

	def format_board(solved):
		selected_possibilities = []
		for i in solved:
			selected_possibilities.append(all_possiblities[i])
		sorted_possibilities = sorted(selected_possibilities)
		solved_grid = []
		for row, col, number in sorted_possibilities:
			solved_grid.append(number+1) # instead of 0-8 its 1-9
		solved_grid = list(zip(*[iter(solved_grid)] * 9)) # reshaping to 9*9
		formatted_grid = []
		for x, y in zip(chain(*sudoku_grid), chain(*solved_grid)):
			if x == 0:
				formatted_grid.append(purple_color(str(y)))
			else:
				formatted_grid.append(x)

		return board_format().format(*formatted_grid)


	#retore stdin to the terminal
	sys.stdin = open('/dev/tty')

	# solve
	index = 0
	for index, solved in enumerate(dlx(cover_matrix), start=1):
		if index == 2:
			answer = input("Find all solutions? y/n ")
			if answer == "n":
				break
		print(f"\n ------SOLUTION #{index}-\n"+format_board(solved))
	else:
		print(f'There are {index} solution{"s" if index > 1 else ""}.\n')



def main():
	sudoku_grid = get_data()
	solve_sudoku(sudoku_grid) # returns NONE

if __name__ == "__main__":
	main()
