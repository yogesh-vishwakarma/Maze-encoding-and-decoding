from tkinter import *
from tkinter import font
from tkinter import messagebox
from functools import partial
from operator import attrgetter
import webbrowser
import numpy
import random
import math
import os


class Maze:

    class CreateToolTip(object):
        """
        Helper class that creates a tooltip for a given widget
        """
        def __init__(self, widget, text='widget info'):
            self.waittime = 500  # milliseconds
            self.wraplength = 180  # pixels
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.widget.bind("<ButtonPress>", self.leave)
            self._id = None
            self.tw = None

        def enter(self, event=None):
            self.schedule()

        def leave(self, event=None):
            self.unschedule()
            self.hidetip()

        def schedule(self):
            self.unschedule()
            self._id = self.widget.after(self.waittime, self.showtip)

        def unschedule(self):
            _id = self._id
            self._id = None
            if _id:
                self.widget.after_cancel(_id)

        def showtip(self, event=None):
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            # creates a toplevel window
            self.tw = Toplevel(self.widget)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = Label(self.tw, text=self.text, justify='left', background="#ffffff",
                          relief='solid', borderwidth=1, wraplength=self.wraplength)
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tw
            self.tw = None
            if tw:
                tw.destroy()

    class MyMaze(object):
        """
        Helper class that creates a random, perfect (without cycles) maze
        """

        def __init__(self, x_dimension, y_dimension):
            self.dimensionX = x_dimension              # dimension of maze
            self.dimensionY = y_dimension
            self.gridDimensionX = x_dimension * 2 + 1  # dimension of output grid
            self.gridDimensionY = y_dimension * 2 + 1
            # output grid
            self.mazeGrid = [[' ' for y in range(self.gridDimensionY)] for x in range(self.gridDimensionX)]
            # 2d array of Cells
            self.cells = [[self.Cell(x, y, False) for y in range(self.dimensionY)] for x in range(self.dimensionX)]
            self.generate_maze()
            self.update_grid()

        class Cell(object):
            """
            inner class to represent a cell
            """
            def __init__(self, x, y, is_wall=True):
                self.neighbors = []  # cells this cell is connected to
                self.open = True     # if true, has yet to be used in generation
                self.x = x           # coordinates
                self.y = y
                self.wall = is_wall  # impassable cell

            def add_neighbor(self, other):
                """
                add a neighbor to this cell, and this cell as a neighbor to the other
                """
                if other not in self.neighbors:  # avoid duplicates
                    self.neighbors.append(other)
                if self not in other.neighbors:  # avoid duplicates
                    other.neighbors.append(self)

            def is_cell_below_neighbor(self):
                """
                used in update_grid()
                """
                return self.__class__(self.x, self.y + 1) in self.neighbors

            def is_cell_right_neighbor(self):
                """
                used in update_grid()
                """
                return self.__class__(self.x + 1, self.y) in self.neighbors

            def __eq__(self, other):
                """
                useful Cell equivalence
                """
                if isinstance(other, self.__class__):
                    return self.x == other.x and self.y == other.y
                else:
                    return False

        def generate_maze(self):
            """
            generate the maze from upper left (In computing the y increases down often)
            """
            start_at = self.get_cell(0, 0)
            start_at.open = False  # indicate cell closed for generation
            cells = [start_at]
            while cells:
                # this is to reduce but not completely eliminate the number
                # of long twisting halls with short easy to detect branches
                # which results in easy mazes
                if random.randint(0, 9) == 0:
                    cell = cells.pop(random.randint(0, cells.__len__()) - 1)
                else:
                    cell = cells.pop(cells.__len__() - 1)
                # for collection
                neighbors = []
                # cells that could potentially be neighbors
                potential_neighbors = [self.get_cell(cell.x + 1, cell.y), self.get_cell(cell.x, cell.y + 1),
                                       self.get_cell(cell.x - 1, cell.y), self.get_cell(cell.x, cell.y - 1)]
                for other in potential_neighbors:
                    # skip if outside, is a wall or is not opened
                    if other is None or other.wall or not other.open:
                        continue
                    neighbors.append(other)
                if not neighbors:
                    continue
                # get random cell
                selected = neighbors[random.randint(0, neighbors.__len__()) - 1]
                # add as neighbor
                selected.open = False  # indicate cell closed for generation
                cell.add_neighbor(selected)
                cells.append(cell)
                cells.append(selected)

        def get_cell(self, x, y):
            """
            used to get a Cell at x, y; returns None out of bounds
            """
            if x < 0 or y < 0:
                return None
            try:
                return self.cells[x][y]
            except IndexError:  # catch out of bounds
                return None

        def update_grid(self):
            """
            draw the maze
            """
            back_char = ' '
            wall_char = 'X'
            cell_char = ' '
            # fill background
            for x in range(self.gridDimensionX):
                for y in range(self.gridDimensionY):
                    self.mazeGrid[x][y] = back_char
            # build walls
            for x in range(self.gridDimensionX):
                for y in range(self.gridDimensionY):
                    if x % 2 == 0 or y % 2 == 0:
                        self.mazeGrid[x][y] = wall_char
            # make meaningful representation
            for x in range(self.dimensionX):
                for y in range(self.dimensionY):
                    current = self.get_cell(x, y)
                    grid_x = x * 2 + 1
                    grid_y = y * 2 + 1
                    self.mazeGrid[grid_x][grid_y] = cell_char
                    if current.is_cell_below_neighbor():
                        self.mazeGrid[grid_x][grid_y + 1] = cell_char
                    if current.is_cell_right_neighbor():
                        self.mazeGrid[grid_x + 1][grid_y] = cell_char

    class Cell(object):
        """
        Helper class that represents the cell of the grid
        """

        def __init__(self, row, col):
            self.row = row  # the row number of the cell(row 0 is the top)
            self.col = col  # the column number of the cell (column 0 is the left)
            self.g = 0      # the value of the function g of A* 
            self.h = 0      # the value of the function h of A* 
            self.f = 0      # the value of the function f of A* 
            # the distance of the cell from the initial position of the robot
            # Ie the label that updates the Dijkstra's algorithm
            self.dist = 0
            # Each state corresponds to a cell
            # and each state has a predecessor which
            # stored in this variable
            self.prev = self.__class__

        def __eq__(self, other):
            """
            useful Cell equivalence
            """
            if isinstance(other, self.__class__):
                return self.row == other.row and self.col == other.col
            else:
                return False

    #######################################
    #                                     #
    #      Constants of Maze42 class      #
    #                                     #
    #######################################
    INFINITY = sys.maxsize  # The representation of the infinite
    EMPTY = 0       # empty cell
    OBST = 1        # cell with obstacle
    ROBOT = 2       # the position of the robot
    TARGET = 3      # the position of the target
    FRONTIER = 4    # cells that form the frontier (OPEN SET)
    CLOSED = 5      # cells that form the CLOSED SET
    ROUTE = 6       # cells that form the robot-to-target path

    MSG_DRAW_AND_SELECT = "\"Paint\" obstacles, then click 'Real-Time' or 'Animation'"
    MSG_SELECT_STEP_BY_STEP_ETC = "Click 'Animation' or 'Clear'"
    MSG_NO_SOLUTION = "There is no path to the target !!!"

    def __init__(self, maze):
        """
        Constructor
        """
        self.center(maze)

        self.rows = 41                             # the number of rows of the grid
        self.columns = 41                          # the number of columns of the grid
        self.square_size = int(500/self.rows)      # the cell size in pixels
        #self.arrow_size = int(self.square_size/2)  # the size of the tips of the arrow pointing the predecessor cell

        self.openSet = []    # the OPEN SET
        self.closedSet = []  # the CLOSED SET
        self.graph = []      # the set of vertices of the graph to be explored by Dijkstra's algorithm

        self.robotStart = self.Cell(self.rows - 2, 1)    # the initial position of the robot
        self.targetPos = self.Cell(1, self.columns - 2)  # the position of the target

        self.grid = [[]]            # the grid
        self.realTime = False       # Solution is displayed instantly
        self.found = False          # flag that the goal was found
        self.searching = False      # flag that the search is in progress
        self.endOfSearch = False    # flag that the search came to an end
        self.animation = False      # flag that the animation is running
        self.delay = 50            # time delay of animation (in msec)
        self.expanded = 0           # the number of nodes that have been expanded
        self.selected_algo = "A*"  

        self.array = numpy.array([0] * (83 * 83))
        self.cur_row = self.cur_col = self.cur_val = 0
        app_highlight_font = font.Font(app, family='Helvetica', size=10, weight='bold')

        ##########################################
        #                                        #
        #   the widgets of the user interface    #
        #                                        #
        ##########################################
        self.message = Label(app, text=self.MSG_DRAW_AND_SELECT, width=55, anchor='center',
                             font=('Helvetica', 12), fg="RED")
        self.message.place(x=5, y=510)

        rows_lbl = Label(app, text="Rows: 41", width=16, anchor='e', font=("Helvetica", 9))
        rows_lbl.place(x=520, y=5)

        cols_lbl = Label(app, text="Columns: 41", width=16, anchor='e', font=("Helvetica", 9))
        cols_lbl.place(x=530, y=35)

        self.buttons = list()

        for i, action in enumerate(("Maze", "Clear", "Real-Time", "Animation")):
            btn = Button(app, text=action,  width=20, font=app_highlight_font,  bg="light grey",
                         command=partial(self.select_action, action))
            btn.place(x=515, y=65+30*i)
          #  self.CreateToolTip(btn, buttons_tool_tips[i])
            self.buttons.append(btn) 

        time_delay = Label(app, text="Delay:(msec)", width=27, anchor='center', font=("Times New Roman", 8))
        time_delay.place(x=515, y=240)
        slider_value = IntVar()
        slider_value.set(50)
        self.slider = Scale(app, orient=HORIZONTAL, length=165, width=10, from_=50, to=500, 
                           showvalue=1, variable=slider_value,)
        self.slider.place(x=515, y=260)
        self.CreateToolTip(self.slider, "Regulates the delay for each step (0 to 1000 msec)")

        self.frame = LabelFrame(app, text="Algorithms", width=170, height=100)
        self.frame.place(x=515, y=300)
        self.radio_buttons = list()

        for i, algorithm in enumerate(("A*","Dijkstra")):
            btn = Radiobutton(self.frame, text=algorithm,  font=app_highlight_font, value=i + 1,
                              command=partial(self.select_algo, algorithm))
            btn.place(x=7 if i % 2 == 0 else 80, y=int(i/2)*25)
           # self.CreateToolTip(btn, radio_buttons_tool_tips[i])
            btn.deselect()
            self.radio_buttons.append(btn)
        self.radio_buttons[0].select()

        self.diagonal = IntVar()

        self.canvas = Canvas(app, bd=0, highlightthickness=0)
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.drag)

        self.initialize_grid(False)

    def validate_rows(self, entry):
        """
        Validates entry in rowsSpinner

        :param entry: the value entered by the user
        :return:      True, if entry is valid
        """
        try:
            value = int(entry)
            valid = value in range(5, 84)
        except ValueError:
            valid = False
        if not valid:
            app.bell()

            self.rowsSpinner.after_idle(lambda: self.rowsSpinner.config(validate='focusout'))
        return valid

    def invalid_rows(self):
        """
        Sets default value to rowsSpinner in case of invalid entry
        """
        self.rows_var.set(50)

    def validate_cols(self, entry):
        """
        Validates entry in colsSpinner

        :param entry: the value entered by the user
        :return:      True, if entry is valid
        """
        try:
            value = int(entry)
            valid = value in range(5, 84)
        except ValueError:
            valid = False
        if not valid:
            app.bell()
            self.colsSpinner.after_idle(lambda: self.colsSpinner.config(validate='focusout'))
        return valid

    def invalid_cols(self):
        """
        Sets default value to colsSpinner in case of invalid entry
        """
        self.cols_var.set(41)

    def select_action(self, action):
        #if action == "New grid":
         #   self.reset_click()
        if action == "Maze":
            self.maze_click()
        elif action == "Clear":
            self.clear_click()
        elif action == "Real-Time":
            self.real_time_click()
        elif action == "Animation":
            self.animation_click()

    def select_algo(self, algorithm):
        self.selected_algo = algorithm

    def left_click(self, event):
        """
        Handles clicks of left mouse button as we add or remove obstacles
        """
        row = int(event.y/self.square_size)
        col = int(event.x/self.square_size)
        if row in range(self.rows) and col in range(self.columns):
            if True if self.realTime else (not self.found and not self.searching):
                if self.realTime:
                    self.fill_grid()
                self.cur_row = row
                self.cur_col = col
                self.cur_val = self.grid[row][col]
                if self.cur_val == self.EMPTY:
                    self.grid[row][col] = self.OBST
                    self.paint_cell(row, col, "BLACK")
                if self.cur_val == self.OBST:
                    self.grid[row][col] = self.EMPTY
                    self.paint_cell(row, col, "WHITE")
                if self.realTime and self.selected_algo == "Dijkstra":
                    self.initialize_dijkstra()
        if self.realTime:
            self.animation_action()

    def drag(self, event):
        """
        Handles mouse movements as we "paint" obstacles or move the robot and/or target.
        """
        row = int(event.y/self.square_size)
        col = int(event.x/self.square_size)
        if row in range(self.rows) and col in range(self.columns):
            if True if self.realTime else (not self.found and not self.searching):
                if self.realTime:
                    self.fill_grid()
                if self.Cell(row, col) != self.Cell(self.cur_row, self.cur_col) and\
                        self.cur_val in [self.ROBOT, self.TARGET]:
                    new_val = self.grid[row][col]
                    if new_val == self.EMPTY:
                        self.grid[row][col] = self.cur_val
                        if self.cur_val == self.ROBOT:
                            self.grid[self.robotStart.row][self.robotStart.col] = self.EMPTY
                            self.paint_cell(self.robotStart.row, self.robotStart.col, "WHITE")
                            self.robotStart.row = row
                            self.robotStart.col = col
                            self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
                            self.paint_cell(self.robotStart.row, self.robotStart.col, "RED")
                        else:
                            self.grid[self.targetPos.row][self.targetPos.col] = self.EMPTY
                            self.paint_cell(self.targetPos.row, self.targetPos.col, "WHITE")
                            self.targetPos.row = row
                            self.targetPos.col = col
                            self.grid[self.targetPos.row][self.targetPos.col] = self.TARGET
                            self.paint_cell(self.targetPos.row, self.targetPos.col, "GREEN")
                        self.cur_row = row
                        self.cur_col = col
                        self.cur_val = self.grid[row][col]
                elif self.grid[row][col] != self.ROBOT and self.grid[row][col] != self.TARGET:
                    self.grid[row][col] = self.OBST
                    self.paint_cell(row, col, "BLACK")
                if self.realTime and self.selected_algo == "Dijkstra":
                    self.initialize_dijkstra()
        if self.realTime:
            self.animation_action()

    def initialize_grid(self, make_maze):
        """
        Creates a new clean grid or a new maze

        :param make_maze: flag that indicates the creation of a random maze
        """
        self.rows = 41
        self.columns = 41
        if make_maze and self.rows % 2 == 0:
            self.rows -= 1
        if make_maze and self.columns % 2 == 0:
            self.columns -= 1
        self.square_size = int(500/(self.rows if self.rows > self.columns else self.columns))
        self.arrow_size = int(self.square_size/2)
        self.grid = self.array[:self.rows*self.columns]
        self.grid = self.grid.reshape(self.rows, self.columns)
        self.canvas.configure(width=self.columns*self.square_size+1, height=self.rows*self.square_size+1)
        self.canvas.place(x=10, y=10)
        self.canvas.create_rectangle(0, 0, self.columns*self.square_size+1,
                                     self.rows*self.square_size+1, width=0, fill="DARK GREY")

        for r in list(range(self.rows)):
            for c in list(range(self.columns)):
                self.grid[r][c] = self.EMPTY
        self.grid[self.rows-2][1] = self.ROBOT
        self.grid[1][self.columns-2] = self.TARGET
        self.robotStart = self.Cell(self.rows-2, 1)
        self.targetPos = self.Cell(1, self.columns-2)
        self.fill_grid()
        if make_maze:
            maze = self.MyMaze(int(self.rows/2), int(self.columns/2))
            for x in range(maze.gridDimensionX):
                for y in range(maze.gridDimensionY):
                    if maze.mazeGrid[x][y] == 'X':  # maze.wall_char:
                        self.grid[x][y] = self.OBST
        self.repaint()

    def fill_grid(self):
        """
        Gives initial values ​​for the cells in the grid.
        """
        # With the second click removes any obstacles also.
        if self.searching or self.endOfSearch:
            for r in list(range(self.rows)):
                for c in list(range(self.columns)):
                    if self.grid[r][c] in [self.FRONTIER, self.CLOSED, self.ROUTE]:
                        self.grid[r][c] = self.EMPTY
                    if self.grid[r][c] == self.ROBOT:
                        self.robotStart = self.Cell(r, c)
            self.searching = False
        else:
            for r in list(range(self.rows)):
                for c in list(range(self.columns)):
                    self.grid[r][c] = self.EMPTY
            self.robotStart = self.Cell(self.rows-2, 1)
            self.targetPos = self.Cell(1, self.columns-2)
        if self.selected_algo in ["A*"]:
            self.robotStart.g = 0
            self.robotStart.h = 0
            self.robotStart.f = 0
        self.expanded = 0
        self.found = False
        self.searching = False
        self.endOfSearch = False

        self.openSet.clear()
        self.closedSet.clear()
        self.openSet = [self.robotStart]
        self.closedSet = []

        self.grid[self.targetPos.row][self.targetPos.col] = self.TARGET
        self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
        self.message.configure(text=self.MSG_DRAW_AND_SELECT)

        self.repaint()

    def repaint(self):
        """
        Repaints the grid
        """
        color = ""
        for r in list(range(self.rows)):
            for c in list(range(self.columns)):
                if self.grid[r][c] == self.EMPTY:
                    color = "WHITE"
                elif self.grid[r][c] == self.ROBOT:
                    color = "RED"
                elif self.grid[r][c] == self.TARGET:
                    color = "GREEN"
                elif self.grid[r][c] == self.OBST:
                    color = "BLACK"
                elif self.grid[r][c] == self.FRONTIER:
                    color = "BLUE"
                elif self.grid[r][c] == self.CLOSED:
                    color = "CYAN"
                elif self.grid[r][c] == self.ROUTE:
                    color = "YELLOW"
                self.paint_cell(r, c, color)

    def paint_cell(self, row, col, color):
  
        self.canvas.create_rectangle(1 + col * self.square_size, 1 + row * self.square_size,
                                     1 + (col + 1) * self.square_size - 1, 1 + (row + 1) * self.square_size - 1,
                                     width=0, fill=color)

    def maze_click(self):
        """
        Action performed when user clicks "Maze" button
        """
        self.animation = False
        for but in self.buttons:
            but.configure(state="normal")
        self.buttons[2].configure(fg="BLACK")             # Real-Time button
        for but in self.radio_buttons:
            but.configure(state="normal")
        self.initialize_grid(True)

    def clear_click(self):
        """
        Action performed when user clicks "Clear" button
        """
        self.animation = False
        self.realTime = False
        self.fill_grid()
        for but in self.buttons:
            but.configure(state="normal")
        self.buttons[2].configure(fg="BLACK")             # Real-Time button
        
        for but in self.radio_buttons:
            but.configure(state="normal")

    def real_time_click(self):
        """
        Action performed when user clicks "Real-Time" button
        """
        if self.realTime:
            return
        self.realTime = True
        self.searching = True
        self.buttons[2].configure(fg="RED")             # Real-Time button
        #self.buttons[4].configure(state="disabled")     # Step-by-Step button
        self.buttons[3].configure(state="disabled")     # Animation button
        
        for but in self.radio_buttons:
            but.configure(state="disabled")
        if self.selected_algo == "Dijkstra":
            self.initialize_dijkstra()
        self.animation = True
        self.delay = 0
        self.animation_action()

    def animation_click(self):
        """
        Action performed when user clicks "Animation" button
        """
        if not self.searching and self.selected_algo == "Dijkstra":
            self.initialize_dijkstra()
        self.animation = True
        self.searching = True
        self.message.configure(text=self.MSG_SELECT_STEP_BY_STEP_ETC)
        self.buttons[3].configure(state="disabled")     # Real-Time button
        for but in self.radio_buttons:
            but.configure(state="disabled")
        self.delay = self.slider.get()
        self.animation_action()

    def animation_action(self):
        """
        The action periodically performed during searching in animation mode
        """
        if self.animation:
            self.check_termination()
            if self.endOfSearch:
                return
            self.canvas.after(self.delay, self.animation_action) 

    def check_termination(self):
        """
        Checks if search is completed
        """
        # 2. If OPEN SET = [], then terminate. There is no solution.
        if (self.selected_algo == "Dijkstra" and not self.graph) or\
                self.selected_algo != "Dijkstra" and not self.openSet:
            self.endOfSearch = True
            self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
            self.message.configure(text=self.MSG_NO_SOLUTION)
            #self.buttons[4].configure(state="disabled")     # Step-by-Step button
            self.buttons[3].configure(state="disabled")     # Animation button
            self.slider.configure(state="disabled")
            self.repaint()
        else:
            self.expand_node()
            if self.found:
                self.endOfSearch = True
                self.plot_route()
                self.buttons[3].configure(state="disabled")  # Animation button
                self.slider.configure(state="disabled")

    def expand_node(self):
        """
        Expands a node and creates his successors
        """
        # Dijkstra's algorithm to handle separately
        if self.selected_algo == "Dijkstra":
            # 11: while Q is not empty:
            if not self.graph:
                return
            # 12:  u := vertex in Q (graph) with smallest distance in dist[] ;
            # 13:  remove u from Q (graph);
            u = self.graph.pop(0)
            # Add vertex u in closed set
            self.closedSet.append(u)
            # If target has been found ...
            if u == self.targetPos:
                self.found = True
                return
            # Counts nodes that have expanded.
            self.expanded += 1
            # Update the color of the cell
            self.grid[u.row][u.col] = self.CLOSED
            # paint the cell
            self.paint_cell(u.row, u.col, "CYAN")
            # 14: if dist[u] = infinity:
            if u.dist == self.INFINITY:
                # ... then there is no solution.
                # 15: break;
                return
                # 16: end if
            # Create the neighbors of u
            neighbors = self.create_successors(u, False)
            # 18: for each neighbor v of u:
            for v in neighbors:
                # 20: alt := dist[u] + dist_between(u, v) ;
                alt = u.dist + self.dist_between(u, v)
                # 21: if alt < dist[v]:
                if alt < v.dist:
                    # 22: dist[v] := alt ;
                    v.dist = alt
                    # 23: previous[v] := u ;
                    v.prev = u
                    # Update the color of the cell
                    self.grid[v.row][v.col] = self.FRONTIER
                    # paint the cell
                    self.paint_cell(v.row, v.col, "BLUE")
                    # 24: decrease-key v in Q;
                    # (sort list of nodes with respect to dist)
                    self.graph.sort(key=attrgetter("dist"))
        # The handling of the other four algorithms
        else:
            if 1:
                # Here is the 3rd step of the algorithms A*
                self.openSet.sort(key=attrgetter("f"))
                current = self.openSet.pop(0)
            # ... and add it to CLOSED SET.
            self.closedSet.insert(0, current)
            # Update the color of the cell
            self.grid[current.row][current.col] = self.CLOSED
            # paint the cell
            self.paint_cell(current.row, current.col, "CYAN")
            # If the selected node is the target ...
            if current == self.targetPos:
                # ... then terminate etc
                last = self.targetPos
                last.prev = current.prev
                self.closedSet.append(last)
                self.found = True
                return
            # Count nodes that have been expanded.
            self.expanded += 1
            successors = self.create_successors(current, False)
            # Here is the 5th step of the algorithms
            # 5. For each successor of Si, ...
            for cell in successors:
                if 0:
                    # ... add the successor at the beginning of the list OPEN SET
                    self.openSet.insert(0, cell)
                    # Update the color of the cell
                    self.grid[cell.row][cell.col] = self.FRONTIER
                    # paint the cell
                    self.paint_cell(cell.row, cell.col, "BLUE")
                elif 0:
                    # ... add the successor at the end of the list OPEN SET
                    self.openSet.append(cell)
                    # Update the color of the cell
                    self.grid[cell.row][cell.col] = self.FRONTIER
                    # paint the cell
                    self.paint_cell(cell.row, cell.col, "BLUE")
                # ... if we are running A* algorithms (step 5 of A* algorithm) ...
                elif self.selected_algo in ["A*"]:
                    # ... calculate the value f(Sj) ...
                    dxg = current.col - cell.col
                    dyg = current.row - cell.row
                    dxh = self.targetPos.col - cell.col
                    dyh = self.targetPos.row - cell.row
                    if 1:
                        # with diagonal movements, the Euclidean distance
                        
                        cell.g = current.g + math.sqrt(dxg*dxg + dyg*dyg)
                        cell.h = math.sqrt(dxh*dxh + dyh*dyh)
                    else:
                        
                        cell.g = current.g + abs(dxg) + abs(dyg)
                        cell.h = abs(dxh) + abs(dyh)
                    cell.f = cell.g+cell.h
                    
                    if cell not in self.openSet and cell not in self.closedSet:
                        # ... then add Sj in the OPEN SET ...
                        # ... evaluated as f(Sj)
                        self.openSet.append(cell)
                        # Update the color of the cell
                        self.grid[cell.row][cell.col] = self.FRONTIER
                        # paint the cell
                        self.paint_cell(cell.row, cell.col, "BLUE")
                    # Else ...
                    else:
                        # ... if already belongs to the OPEN SET, then ...
                        if cell in self.openSet:
                            open_index = self.openSet.index(cell)
                            # ... compare the new value assessment with the old one.
                            # If old <= new ...
                            if self.openSet[open_index].f <= cell.f:
                                # ... then eject the new node with state Sj.
                                # (ie do nothing for this node).
                                pass
                            # Else, ...
                            else:
                                # ... remove the element (Sj, old) from the list
                                # to which it belongs ...
                                self.openSet.pop(open_index)
                                # ... and add the item (Sj, new) to the OPEN SET.
                                self.openSet.append(cell)
                                # Update the color of the cell
                                self.grid[cell.row][cell.col] = self.FRONTIER
                                # paint the cell
                                self.paint_cell(cell.row, cell.col, "BLUE")
                        # ... if already belongs to the CLOSED SET, then ...
                        elif cell in self.closedSet:
                            closed_index = self.closedSet.index(cell)
                            # ... compare the new value assessment with the old one.
                            # If old <= new ...
                            if self.closedSet[closed_index].f <= cell.f:
                                # ... then eject the new node with state Sj.
                                # (ie do nothing for this node).
                                pass
                            # Else, ...
                            else:
                                # ... remove the element (Sj, old) from the list
                                # to which it belongs ...
                                self.closedSet.pop(closed_index)
                                # ... and add the item (Sj, new) to the OPEN SET.
                                self.openSet.append(cell)
                                # Update the color of the cell
                                self.grid[cell.row][cell.col] = self.FRONTIER
                                # paint the cell
                                self.paint_cell(cell.row, cell.col, "BLUE")

    def create_successors(self, current, make_connected):
        """
        Creates the successors of a state/cell
        """
        r = current.row
        c = current.col
        # We create an empty list for the successors of the current cell.
        temp = []

        if r > 0 and self.grid[r-1][c] != self.OBST and\
                (self.selected_algo in ["A*","Dijkstra"] 
                and not self.Cell(r-1, c) in self.openSet and not self.Cell(r-1, c) in self.closedSet):
            cell = self.Cell(r-1, c)
            if self.selected_algo == "Dijkstra":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                # ... update the pointer of the up-side cell so it points the current one ...
                cell.prev = current
                # ... and add the up-side cell to the successors of the current one.
                temp.append(cell)

        if 1:

            if r > 0 and c < self.columns-1 and self.grid[r-1][c+1] != self.OBST and \
                    (self.grid[r-1][c] != self.OBST or self.grid[r][c+1] != self.OBST) and \
                    (self.selected_algo in ["A*", "Dijkstra"] or
                     (0
                     and not self.Cell(r-1, c+1) in self.openSet and not self.Cell(r-1, c+1) in self.closedSet)):
                cell = self.Cell(r-1, c+1)
                if self.selected_algo == "Dijkstra":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                else:
                    # ... update the pointer of the up-right-side cell so it points the current one ...
                    cell.prev = current
                    # ... and add the up-right-side cell to the successors of the current one.
                    temp.append(cell)
        # and (only in the case are not running the A* )
        # not already belongs neither to the OPEN SET nor to the CLOSED SET ...
        if c < self.columns-1 and self.grid[r][c+1] != self.OBST and\
                (self.selected_algo in ["A*", "Dijkstra"] or
                 (0
                 and not self.Cell(r, c+1) in self.openSet and not self.Cell(r, c+1) in self.closedSet)):
            cell = self.Cell(r, c+1)
            if self.selected_algo == "Dijkstra":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                # ... update the pointer of the right-side cell so it points the current one ...
                cell.prev = current
                # ... and add the right-side cell to the successors of the current one.
                temp.append(cell)

        if 1:
            # If we are not even at the lowermost nor at the rightmost border of the grid
            # and the down-right-side cell is not an obstacle
            # and one of the down-side or right-side cells are not obstacles
            # and (only in the case are not running the A*)
            # not already belongs neither to the OPEN SET nor to the CLOSED SET ...
            if r < self.rows-1 and c < self.columns-1 and self.grid[r+1][c+1] != self.OBST and \
                    (self.grid[r+1][c] != self.OBST or self.grid[r][c+1] != self.OBST) and \
                    (self.selected_algo in ["A*", "Dijkstra"] or
                     (0
                     and not self.Cell(r+1, c+1) in self.openSet and not self.Cell(r+1, c+1) in self.closedSet)):
                cell = self.Cell(r+1, c+1)
                if self.selected_algo == "Dijkstra":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                else:
                    # ... update the pointer of the downr-right-side cell so it points the current one ...
                    cell.prev = current
                    # ... and add the down-right-side cell to the successors of the current one.
                    temp.append(cell)

        # not already belongs neither to the OPEN SET nor to the CLOSED SET ...
        if r < self.rows-1 and self.grid[r+1][c] != self.OBST and \
                (self.selected_algo in ["A*", "Dijkstra"] or
                 (0
                 and not self.Cell(r+1, c) in self.openSet and not self.Cell(r+1, c) in self.closedSet)):
            cell = self.Cell(r+1, c)
            if self.selected_algo == "Dijkstra":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                # ... update the pointer of the down-side cell so it points the current one ...
                cell.prev = current
                # ... and add the down-side cell to the successors of the current one.
                temp.append(cell)

        if 1:

            # not already belongs neither to the OPEN SET nor to the CLOSED SET ...
            if r < self.rows-1 and c > 0 and self.grid[r+1][c-1] != self.OBST and \
                    (self.grid[r+1][c] != self.OBST or self.grid[r][c-1] != self.OBST) and \
                    (self.selected_algo in ["A*", "Dijkstra"] or
                     (0
                     and not self.Cell(r+1, c-1) in self.openSet and not self.Cell(r+1, c-1) in self.closedSet)):
                cell = self.Cell(r+1, c-1)
                if self.selected_algo == "Dijkstra":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                else:
                    # ... update the pointer of the down-left-side cell so it points the current one ...
                    cell.prev = current
                    # ... and add the down-left-side cell to the successors of the current one.
                    temp.append(cell)
        if c > 0 and self.grid[r][c-1] != self.OBST and \
                (self.selected_algo in ["A*", "Dijkstra"] or
                 (0
                 and not self.Cell(r, c-1) in self.openSet and not self.Cell(r, c-1) in self.closedSet)):
            cell = self.Cell(r, c-1)
            if self.selected_algo == "Dijkstra":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                # ... update the pointer of the left-side cell so it points the current one ...
                cell.prev = current
                # ... and add the left-side cell to the successors of the current one.
                temp.append(cell)

        if 1:
            if r > 0 and c > 0 and self.grid[r-1][c-1] != self.OBST and \
                    (self.grid[r-1][c] != self.OBST or self.grid[r][c-1] != self.OBST) and \
                    (self.selected_algo in ["A*","Dijkstra"] or
                     (0
                     and not self.Cell(r-1, c-1) in self.openSet and not self.Cell(r-1, c-1) in self.closedSet)):
                cell = self.Cell(r-1, c-1)
                if self.selected_algo == "Dijkstra":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                else:
                    # ... update the pointer of the up-left-side cell so it points the current one ...
                    cell.prev = current
                    # ... and add the up-left-side cell to the successors of the current one.
                    temp.append(cell)

        if self.selected_algo!=0:
            return temp

    def plot_route(self):
        """
        Calculates the path from the target to the initial position of the robot,
        counts the corresponding steps and measures the distance traveled.
        """
        self.repaint()
        self.searching = False
        steps = 0
        distance = 0.0
        index = self.closedSet.index(self.targetPos)
        cur = self.closedSet[index]
        self.grid[cur.row][cur.col] = self.TARGET
        self.paint_cell(cur.row, cur.col, "GREEN")
        while cur != self.robotStart:
            steps += 1
            if 1:
                dx = cur.col - cur.prev.col
                dy = cur.row - cur.prev.row
                distance += math.sqrt(dx*dx + dy*dy)
            else:
                distance += 1
            cur = cur.prev
            self.grid[cur.row][cur.col] = self.ROUTE
            self.paint_cell(cur.row, cur.col, "YELLOW")

        self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
        self.paint_cell(self.robotStart.row, self.robotStart.col, "RED")
        msg = "Nodes expanded: {0}, Steps: {1}, Distance: {2:.3f}".format(self.expanded, steps, distance)
        self.message.configure(text=msg)

    def dist_between(self, u, v):

        dx = u.col - v.col
        dy = u.row - v.row
        if 1:
            # with diagonal movements calculate the Euclidean distance
            return math.sqrt(dx*dx + dy*dy)
        else:
            # without diagonal movements calculate Manhattan distance
            return abs(dx) + abs(dy)

    def find_connected_component(self, v):
        """
        Appends to the list containing the nodes of the graph only
        the cells belonging to the same connected component with node v.

        :param v: the starting node
        """
        stack = [v]
        self.graph.append(v)
        while stack:
            v = stack.pop()
            successors = self.create_successors(v, True)
            for c in successors:
                if c not in self.graph:
                    stack.append(c)
                    self.graph.append(c)

    def initialize_dijkstra(self):
        """
        Initialization of Dijkstra's algorithm
        """
        self.graph.clear()
        self.find_connected_component(self.robotStart)
        # Here is the initialization of Dijkstra's algorithm
        # 2: for each vertex v in Graph;
        for v in self.graph:
            # 3: dist[v] := infinity ;
            v.dist = self.INFINITY
            # 5: previous[v] := undefined ;
            v.prev = None
        # 8: dist[source] := 0;
        self.graph[self.graph.index(self.robotStart)].dist = 0
        self.graph.sort(key=attrgetter("dist"))
        # Initializes the list of closed nodes
        self.closedSet.clear()

    @staticmethod
    def center(window):
        """
        Places a window at the center of the screen
        """
        window.update_idletasks()
        w = window.winfo_screenwidth()
        h = window.winfo_screenheight()
        size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        window.geometry("%dx%d+%d+%d" % (size + (x, y)))

if __name__ == '__main__':
    app = Tk()
    app.title("Group 21")
    app.geometry("693x545")
    app.resizable(False, False)
    Maze(app)
    
    app.mainloop()

