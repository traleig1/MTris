import random
from TetrisBlock import *
from Data import *

class Board(object):
  """A grid that blocks fall onto."""

  def __init__(o, height=20, width=10): #buffer = blockMaxHeight; kill globals
    blockMaxHeight = max([block.gridSize for block in blocks])
    o.height, o.width = height, width
    o._Height = height * 2 + blockMaxHeight
    o.board = [ [None]*o._Height for row in range(width)]
    o.startPosition = ((width-blockMaxHeight)//2,height-1)

  def __getitem__(o,pt):
    x,y = pt
     #should we add bounds checking? or just let it pass on the exception?
    return o.board[x][y]

  def getRow(o,y):
    """Return an iterator of Squares in the requested row number."""
    return (o.board[x][y] for x in range(o.width))

  def __str__(o):
    def concatMap(func,lst): return ''.join(map(func,lst))
    def colStr(row):
      return concatMap(lambda sq: " - " if not sq else "["+sq.kind+"]",row)
    def outline(rows):
      border = ['o'+"="*(o.width*3)+'o']
      return '\n'.join(border+['|'+ r +'|' for r in reversed(rows)]+border)
    return '\n' + outline(map(colStr,(o.getRow(y) for y in range(o.height)) ))

  def clearLines(o):
    """Clear full lines, shift blocks down, and return # of lines cleared."""
    def rowFull(y):
      return not any(o.board[x][y]==None for x in range(o.width))
    lines = 0
    for y in range(o._Height):
      if rowFull(y):
        for square in o.getRow(y): square.broken = True
        lines+=1
      else: o._shiftRow(y,-lines)
    for y in range(o._Height-lines, o._Height):
      for x in range(o.width): o.board[x][y] = None
    return lines

  def addRows(o,numRows):
    """Add 9/10 full line to bottom of board."""
    if numRows <= 0: return
    xSquare = lambda x,y: Block('X',[(0,0)],1).shift(x,y).squares[0]
    for y in reversed(range(o._Height-numRows)): o._shiftRow(y,numRows)
    for y in range(numRows):
      for x in range(o.width): o.board[x][y] = xSquare(x,y)
      o.board[random.choice(range(o.width))][y] = None

  def _shiftRow(o,row,numRows):
    for x in range(o.width):
      if o.board[x][row] is not None: o.board[x][row].shift(0,numRows)
      newRow = row + numRows
      if newRow < o._Height: o.board[x][newRow] = o.board[x][row]

  def add(o,block):
    """Add a block to the board."""
    #if any(sq.x<0 or sq.y<0 for sq in block): raise OutOfBoundsException
    for sq in block: o.board[sq.x][sq.y] = sq

  def valid(o,block):
    """Check if block is within board bounds and not overlapping another block."""
    onBoard = lambda sq: sq.x >= 0 and sq.x < o.width \
                     and sq.y >= 0 and sq.y < o._Height
    collision = lambda sq: o.board[sq.x][sq.y] != None
    return all([onBoard(sq) and not collision(sq) for sq in block])

  def dropLocation(o,block):
    """Return a Block representing where the block will land if dropped."""
    location, temp = block, block.clone()
    while o.valid(temp.shift(0,-1)): location = temp.clone()
    return location