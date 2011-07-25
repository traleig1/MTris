import random
from Board import Board
from BlockQueue import RandomQueue
from TetrisBlock import *
from Data import *
from Enum import Enum

Act = Enum(["Drop","Down","Left","Right","Hold","RotCW","RotCCW"])

class Tetris(object):
  """Represents a player's board, falling block, hold, score, and block queue."""
  def __init__(o, blocks = blocks, board = None, wallKick = WallKick): #blockQueue
    o.blocks   = {block.kind : block for block in blocks}
    o.board    = Board() if board is None else board
    o.wallKick = wallKick #Note[1]
    o.queue    = RandomQueue(3)
    o.canHold  = True; o.hold = None
    o.level    = 1
    o.lines    = 0
    o.penalty  = 0 #Garbage rows from opponent, added on setBlock
    o.onGameOver, o.onClearLines = None, None
    o._initBlock(o.queue.pop())
    o._cachedShadow = None

  def _initBlock(o,block):
    """Move block into position and set as falling block."""
    o.block = block.clone().shift(*o.board.startPosition)

  @property
  def shadowBlock(o):
    """Return a Block representing where the block will land if dropped."""
    return o._cachedShadow if o._cachedShadow is not None \
      else o.board.dropLocation(o.block)

  def _setBlock(o,block):
    """Add block to board, clear lines, and adjust score."""
    o.board.add(block)
    o._cachedShadow = None
    clearedLines = o.board.clearLines()
    o.lines += clearedLines
    if clearedLines > 0 and o.onClearLines is not None:
      o.onClearLines(clearedLines)
    o.board.addRows(o.penalty)
    o.penalty = 0
    o._initBlock(o.queue.pop())
    if o.lines >= o.level*10: o.level+=1
    o.canHold = True
    isGameOver = all(sq.y >= o.board.height for sq in block) \
              or any(o.board[sq.x,sq.y] != None for sq in o.block)
    if isGameOver and o.onGameOver: o.onGameOver(o)

  def _tryShift(o,block,pt):
    newBlock = block.clone().shift(*pt)
    blockValid = o.board.valid(newBlock)
    if blockValid:
      o.block = newBlock
      if pt.x != 0: o._cachedShadow = None
    return blockValid

  def _Rotate(o,direction):
    temp = o.block.clone().rotate(direction)
    def tryRotate(shift=Point(0,0)): return o._tryShift(temp,shift)
    if not o.wallKick: tryRotate()
    else:
      for x,y in o.wallKick[temp.kind][direction][temp.rotation]:
        if tryRotate(shift=Point(x,y)): break;
    o._cachedShadow = None

  def _Hold(o):
    if o.canHold:
      o.hold, newBlock = o.blocks[o.block.kind], o.hold
      o._initBlock(o.queue.pop() if newBlock is None else newBlock)
      o.canHold = False
      o._cachedShadow = None

  def applyGravity(o):
    """Shift falling block down by one row."""
    if not o._tryShift(o.block,Point(0,-1)): o._setBlock(o.block)

  def move(o, action):
    """Perform an action (enumerated in the Act object)."""
    # if action not in Act: raise...?
    { Act.Down  : lambda: o.applyGravity(),
      Act.Left  : lambda: o._tryShift(o.block,Point(-1,0)),
      Act.Right : lambda: o._tryShift(o.block,Point( 1,0)),
      Act.Drop  : lambda: o._setBlock(o.shadowBlock),
      Act.Hold  : lambda: o._Hold(),
      Act.RotCW : lambda: o._Rotate(clockwise),
      Act.RotCCW: lambda: o._Rotate(counterClockwise),
    }[action]()

  def msPerFrame(o):
    return 1000/(0.5+0.75*o.level) #speed chosen arbitrarily


class MultiplayerEngine(object):
  def __init__(o, numPlayers):
    o.players = [Tetris() for p in range(numPlayers)]
    if len(o.players) > 1:
      for playerNum,player in enumerate(o.players): #Note[2]
        player.onClearLines = \
          lambda numRows, p=playerNum: o._distributeRows(p,numRows)

  def _distributeRows(o,playerNumber,numRows):
    opponents = [p for p in range(len(o.players)) if p!=playerNumber]
    target = random.choice(opponents)
    o.players[target].penalty += numRows
  #add interface methods for the State classes?

#Notes:
# [1] - The WallKick tables contain a list of shift values to try after rotation
#       so that a block can still be rotated when it is at the edge of the board.
#       Which shift values should be tried depend on the block being rotated,
#       as well as the direction of rotation and the block's current state.
#       Explanation at: http://www.tetrisconcept.net/wiki/SRS
#       Note that each list starts with a comma - the rotation is first tried
#       without any shifting. This does not have to be the case; Shifting
#       can be used to implement other rotation systems.
# [2] - Here we are creating a lexical closure. We use the default argument
#       (p=playerNum) here to force python to use a different reference for
#       each closure. Without this, each closure would reference playerNum,
#       which is mutated by the loop, as opposed what we want - its current value.

#Issues:
# - Add board initialization code to allow pre-placed blocks
# - Add lock delay?
# - Can we remove key-repeat from up/down/rotate/hold?

#When holding button, have 20Hz key repeat (DAS)
  #TetrisDS: 11 frames delay, period of 5 frames
#Can we remove DAS for the up, hold, rotate and pause buttons?
#T-Spin    - http://tetrisconcept.net/wiki/T-spin
#Scoring   - http://tetrisconcept.net/wiki/Scoring
#TetrisDS  - http://tetrisconcept.net/wiki/Tetris_DS
#TetrisNES - http://gaming.stackexchange.com/questions/13057/tetris-difficulty