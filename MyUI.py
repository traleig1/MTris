import abc
from Tetris import Tetris, MultiplayerEngine, Act
from GameLoop import *
from TetrisBlock import Square, Block
from AI import calculateBestMove

#Add an abstract ImageCollection class
  #To force UI writers to include all referenced images

scale8 = lambda x,y: (x*8,y*8)
class UI_8x8(GameUI):
  """
     A GameUI extended with higher level drawing methods.

     Drawing is done according to an 8x8 pixel grid,
     with origin in the lower-left corner.
  """

  def getBlockImg(o, square, isShadow):
    """Return a reference to the image that should be drawn for a square."""
    if square.kind is 'X': return o.images.xBlock
    if isShadow: return o.images.shadows[square.kind]
    if square.kind is 'T':
      if square.index is 1: return o.images.joint
      else: return o.images.pipe[(square.index-square.rotation)%4]
      #Add special cases for last remaining square in pipe?
    elif square.kind is 'O' and not square.broken:
      return o.images.iceBlock[(square.index-square.rotation)%4]
    else: return o.images.blocks[square.kind]

  def drawSquare(o,sq, x,y, isShadow=False):
    """Draw a Square to the framebuffer."""
    o.draw(o.getBlockImg(sq,isShadow), scale8(2*sq.x+x,2*sq.y+y))

  def drawBlock(o,block, x,y, centered = False, isShadow = False):
    """Draw a Block to the framebuffer."""
    if block is None: return
    if centered: x,y = (x+(4-block.gridSize), y-(1 if block.kind is 'I' else 0))
    for square in block: o.drawSquare(square,x,y, isShadow)

  def drawBoard(o,board, x,y):
    """Draw a Board to the framebuffer."""
    for row in range(board.height):
      for square in board.getRow(row):
        if square is not None: o.drawSquare(square, x,y)

  def drawString(o,string, x,y, large=False):
    """
       Draw a string to the framebuffer.

       The optional paramter 'large' uses an 8x16 font instead of 8x8.
    """
    font = o.images.fontLarge if large else o.images.fontSmall
    for p,char in enumerate(string): o.draw(font[char],scale8(x+p,y))

  def drawValue(o,title,value,maxDigits, x,y):
    """Draw a label and number (padded to maxDigits) to the framebuffer."""
    if title is not None: o.drawString(title,x,y)
    yOffset = 0 if title is None else 2 #2 = large font's height in 8x8 scale
    valStr = str(value)
    o.drawString(valStr,x+maxDigits-len(valStr),y-yOffset,large=True)

class MenuScreen(State): #=====================================================
  """The initial state; A menu screen where the player can select a game type."""

  def __init__(o,ui):
    State.__init__(o,ui)
    o.choice = 0
    o.gameTypes = [Marathon, Against_AI]

  def input(o,button):
    if button in [Btn.Start, Btn.A]:
      o.ui.state = o.gameTypes[o.choice](o.ui)
    elif button == Btn.Up   and o.choice>0:                  o.choice-=1
    elif button == Btn.Down and o.choice<len(o.gameTypes)-1: o.choice+=1

  def drawFrame(o):
    text = ["RRR RRR RRR RRR R RRR",
            " O  O    O  O O O O  ",
            " Y  YY   Y  YY  Y YYY",
            " S  S    S  S S S   S",
            " I  III  I  I I I III"]
    o.ui.draw(o.ui.images.introImage,(0,0))
    for y,row in enumerate(reversed(text)):
      for x,blockType in enumerate(row):
        o.ui.draw(o.ui.images.txtBlocks[blockType],scale8(2*x+9,2*y+18))
    o.ui.drawString("MARATHON",25,11)
    o.ui.drawString("VS. AI",25,9)
    o.ui.draw(o.ui.images.pointer,scale8(23,11-o.choice*2))

buttonMap = {                                 Btn.L: Act.Hold,
  Btn.Up  : Act.Drop,  Btn.Left : Act.Left,   Btn.A: Act.RotCW,
  Btn.Down: Act.Down,  Btn.Right: Act.Right,  Btn.B: Act.RotCCW}

class Marathon(State): #===========================================================
  """A one-player game with no opponents, that speeds up until Game Over."""

  def __init__(o,ui):
    State.__init__(o,ui)
    o.game = Tetris()
    o.game.onGameOver = o.gameOver

  def gameOver(o,loser):
    o.ui.state = GameOver(o.ui,o)

  def runEngine(o):
    o.game.applyGravity()

  def input(o,button):
    if button == Btn.Start: o.ui.state = Pause(o.ui,o)
    else: o.game.move(buttonMap[button])

  def msPerFrame(o):
    #We need to keep drop gravity independent from user input speed
    #How many actions can a player do per second?
    return o.game.msPerFrame()

  def drawFrame(o):
    ui = o.ui; x = o.game
    boardOrigin = (16,0)
    ui.draw(ui.images.bgImage,(0,0))
    ui.drawBoard(x.board,       *boardOrigin)
    ui.drawBlock(x.shadowBlock, *boardOrigin, isShadow = True)
    ui.drawBlock(x.block,       *boardOrigin)
    for block,location in zip(x.queue,[(38,30),(48,30),(48,18)]):
      ui.drawBlock(block, *location, centered = True)
    ui.drawBlock(x.hold, *(4,30), centered = True)
    ui.drawValue("LEVEL",x.level,6, 37,18)
    ui.drawValue("LINES",x.lines,6, 37,22)

#Generalize multiplayer - skip out on local multiplyer (as if it's a GBA)
# - Ask how many AIs, how many humans
class Against_AI(State): #======================================================
  """A one-player game against an AI."""

  def __init__(o,ui):
    State.__init__(o,ui)
    o.engine = MultiplayerEngine(2)
    for player in o.engine.players:
      player.onGameOver = o.gameOver
    o.newBlock = True
    o.moveStack = []
    o.AIcountdown = 0

  def gameOver(o,loser):
    isWinner = (loser != o.engine.players[0])
    #needs to be fixed for more than 2 players...
      #We'll need to move some code into the MultiplayerEngine class
    o.ui.state = GameOver(o.ui,o,isWinner)

  def runEngine(o):
    for player in o.engine.players:
      player.applyGravity()

  def input(o,button):
    #User Input
    player1 = o.engine.players[0]
    if button == Btn.Start:
      o.ui.state = Pause(o.ui,o)
    else:
      player1.move(buttonMap[button])

  def runAI(o):
    if o.AIcountdown > 0:
      o.AIcountdown -= 1
      return
    o.AIcountdown = 10
    ai = o.engine.players[1] #FIX THIS - make it work for any # of AIs
    if o.newBlock:
      o.moveStack = calculateBestMove(ai)
      o.newBlock = False
    if o.moveStack == []:
      ai.move(Act.Drop)
      o.newBlock = True
    else: ai.move(o.moveStack.pop())

  #change game speed (override msPerFrame)?
    #What about games where players are playing at different speeds/levels?

  def drawFrame(o):
    ui = o.ui
    player1 = o.engine.players[0]
    boardOrigins = [(10,0),(40,0)]
    o.ui.draw(o.ui.images.twoPlayerBG,(0,0))
    for player,position in zip(o.engine.players, boardOrigins):
      ui.drawBoard(player.board,       *position)
      ui.drawBlock(player.shadowBlock, *position, isShadow = True)
      ui.drawBlock(player.block,       *position)
    for block,location in zip(player1.queue,[(31,29),(31,19),(31,9)]):
      ui.drawBlock(block, *location, centered = True)
    ui.drawBlock(player1.hold, *(1,29), centered = True)

class Pause(State): #==========================================================
  def __init__(o,ui,previousState):
    State.__init__(o,ui)
    o.previousState = previousState

  def input(o,button):
    if button == Btn.Start: o.ui.state = o.previousState

  def drawFrame(o):
    o.previousState.drawFrame()
    o.ui.draw(o.ui.images.pauseTxt,(175,145))

class GameOver(State): #=======================================================
  def __init__(o,ui,previousState, isWinner=False):
    State.__init__(o,ui)
    o.previousState = previousState
    o.win = isWinner

  def input(o,button):
    if button == Btn.Start: o.ui.state = MenuScreen(o.ui)

  def drawFrame(o):
    o.previousState.drawFrame()
    if o.win: o.ui.draw(o.ui.images.gameOverTxt,(95,145)) #change to 'Winner'
    else:     o.ui.draw(o.ui.images.gameOverTxt,(95,145))
