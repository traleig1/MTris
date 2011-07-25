from Tetris import Act
from copy import deepcopy as clone
from TetrisBlock import clockwise,counterClockwise

weights = {
  'linesCleared'  :  0.30,
  'occupiedCells' :  0.00,
  'shadowedHoles' : -0.65,
  'weightedCells' : -0.10,
  'wellHeightSum' : -0.20}

def calculateBestMove(ai):
  """
     Compute a sequence of moves for the current block.

     This is a re-implementation of Colin Fahey's Tetris AI.
  """
  bestMerit  = None
  r,t = 0,0
  boardWidth = ai.board.width
  clonedBlock = ai.block.clone()
  pieceMap = getPieceMap(ai.board)
  occupiedCells = getOccupiedCells(pieceMap) + 4
  for rotation in range(4):
    if rotation != 0: clonedBlock.rotate(False)
    xs = [sq.x for sq in clonedBlock]
    blockLeft,blockRight  = min(xs),max(xs)
    for translation in range(-blockLeft, boardWidth-blockRight):
      testBlock = clonedBlock.clone().shift(translation,0)
      if not ai.board.valid(testBlock): continue
      testBlock = ai.board.dropLocation(testBlock)
      lines, testMap = addBlock(pieceMap,testBlock)
      heuristics = {'linesCleared'  : lines,
                    'occupiedCells' : occupiedCells - (boardWidth*lines),
                    'shadowedHoles' : getShadowedHoles(testMap),
                    'weightedCells' : getWeightedCells(testMap),
                    'wellHeightSum' : getWellHeightSum(testMap)}
      weightedHeuristics = [weights[key]*heuristics[key] \
                  for key in heuristics.keys() if weights.has_key(key)]
      merit = sum(weightedHeuristics)
      if bestMerit is None or merit > bestMerit:
        bestMerit  = merit
        r, t = rotation, translation
  move = [Act.Right if t>0 else Act.Left]*abs(t) \
       + ([Act.RotCCW] if r==3 else [Act.RotCW]*r)
  return move

def getPieceMap(board):
  """Return a simplified representation of a board."""
  return [[board[x,y] != None \
           for x in range(board.width)] for y in range(board.height)]

def pieceMapStr(pieceMap):
  """Print a simplified board representation as ASCII."""
  rowStr = lambda row: ''.join(['[X]' if cell else ' - ' for cell in row])
  return '\n'.join(rowStr(row) for row in reversed(pieceMap))

def addBlock(pieceMap,block):
  """
     Add a block to a simplified board representation
     and return a (# of lines cleared, result pieceMap) tuple.
  """
  occupied = lambda row,col: pieceMap[row][col] or block.containsPoint((col,row))
  newMap = [[occupied(row,col) for col in range(len(pieceMap[row]))] for row in range(len(pieceMap))]
  rowFull = lambda row: all(row)
  finalMap = [row for row in newMap if not rowFull(row)]
  linesCleared = len(pieceMap)-len(finalMap)
  finalMap += [[False]*len(finalMap[0])]*linesCleared
  return (linesCleared,finalMap)

def getOccupiedCells(pieceMap):
  """Return the number of occupied cells in a pieceMap."""
  cellCount = 0
  for row in pieceMap:
    for cell in row:
      if cell: cellCount += 1
  return cellCount

def getShadowedHoles(pieceMap):
  """Return the number of spaces which have a block somewhere above them."""
  def colShadowHoles(col):
    numShadowedHoles = 0
    colHasSquare = False
    for row in reversed(pieceMap):
      if row[col]: colHasSquare = True
      elif colHasSquare: numShadowedHoles += 1
    return numShadowedHoles
  return sum(colShadowHoles(x) for x in range(len(pieceMap[0])))

def getWeightedCells(pieceMap):
  """Return the occupied cells, weighted by their height in a pieceMap."""
  cellCount = 0
  for y,row in enumerate(pieceMap):
    for cell in row:
      if cell: cellCount += (y+1)
  return cellCount

def getWellHeightSum(pieceMap):
  """
     Calculate the sum of the heights of 'wells' in the pieceMap.

     A well height is considered to be the difference between a column
     and its smallest neighbor when both neighbors are taller.
  """
  def getColumnHeight(column):
    for y in reversed(range(len(pieceMap))):
      if pieceMap[y][column]: return y+1
    return 0
  columnHeights = [getColumnHeight(x) for x in range(len(pieceMap[0]))]
  leftWalls     = [len(pieceMap)] + columnHeights[:-1]
  rightWalls    = columnHeights[1:] + [len(pieceMap)]
  minWalls      = [min(L,R) for L,R in zip(leftWalls,rightWalls)]
  wellHeights   = [minAdjacent - colHeight
                   for minAdjacent,colHeight in zip(minWalls,columnHeights)
                   if minAdjacent > colHeight]
  return sum(wellHeights)