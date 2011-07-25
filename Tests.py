import unittest
from TetrisBlock import *
from Tetris import *
from Data import *
from MyUI import *
from AI import *
from copy import deepcopy as clone

tid = lambda pt: pt
tstBlk = {block.kind : block for block in blocks}
def getBlock(kind): return clone(tstBlk[kind])
def rotBlock(block,rotations):
  b = clone(block)
  for x in range(rotations): b.rotate(clockwise)
  return b


class BlockTests(unittest.TestCase): #=========================================
  def testShift(o):
    x,y = 2,1
    b = getBlock('Z').shift(x,y)
    o._checkPts(tstBlk['Z'],b,lambda pt: (pt.x+x,pt.y+y))

  def testRotate(o): #ADD: check actual point values after a rotation
    a = getBlock('Z').shift(7,7)
    b = clone(a).rotate(clockwise).rotate(clockwise).rotate(clockwise)
    c = clone(a).rotate(counterClockwise)
    d = clone(a).rotate(clockwise).rotate(clockwise) \
                .rotate(clockwise).rotate(clockwise)
    e = clone(a).rotate(counterClockwise).rotate(clockwise)
    o._checkRotate(b,c)
    o._checkRotate(a,d)
    o._checkRotate(a,e)
    o.failUnless(rotBlock(a,4).rotation == 0 and rotBlock(a,1).rotation == 1
             and rotBlock(a,2).rotation == 2 and rotBlock(a,3).rotation == 3)

  def _checkPts(o,a,b,check):
    for i,sq in enumerate(a):
      o.failUnless(check(sq.pt) == b.squares[i].pt)

  def _checkRotate(o,a,b):
    o._checkPts(a,b,tid)
    o.failUnless(a.rotation == b.rotation)


class BoardTests(unittest.TestCase): #=========================================
  def setUp(o):
    o.board = Board(20,10)

  def testAdd(o):
    newBlock = getBlock('Z')
    o.board.add(newBlock)
    for sq in newBlock:
      x,y = sq.pt
      o.failUnless(o.board.board[x][y] == sq)

  def testClearLines(o):
    def addBlock(block,x=0,y=0,rotations=0):
      b = getBlock(block).shift(x,y)
      for x in range(rotations): b.rotate(clockwise)
      o.board.add(b)
    def addBlocks(blockList):
      for block in blockList: addBlock(*block)
    addBlocks([('I',0,-2),('I',4,-2),('I',2,-1)])
    o.board.clearLines()
    #print o.board
    addBlock('Z',7,-1)
    o.board.clearLines()
    #print o.board
    o.failUnless(o.board[0,0]==None
             and o.board[7,1]==None
             and o.board[3,0].broken==False
             and o.board[7,0].broken==True)
    addBlocks([('O',-1,-1),('I',2,-1),('L',6,0,2)])
    o.board.clearLines()
    #print o.board
    addBlock('I',8,0,3)
    o.board.clearLines()
    #print o.board

  def testValid(o):
    blockOnBoard     = getBlock('I')
    blockBelowBottom = getBlock('I').rotate(clockwise).shift(0,-2)
    blockOffLeft     = getBlock('I').shift(-2,0)
    def testValidity(block, valid): o.failUnless(o.board.valid(block) == valid)
    testValidity(blockOnBoard,True)
    testValidity(blockBelowBottom,False)
    testValidity(blockOffLeft,False)


class GameTests(unittest.TestCase): #==========================================
  def setUp(o):
    o.game = Tetris()

  def testSetBlock(o):
    o.game._setBlock(o.game.blocks['I'].clone().shift(0,-2))
    for x in range(4):
      o.failUnless(o.isType(x,0,'I'))

  def testFall(o):
    o.game._initBlock(o.game.blocks['I'])
    for x in range(o.game.board.height+4): o.game.move(Act.Down)
    for x in range(4):
      o.failUnless(o.isType(3+x,0,'I'))

  def testDrop(o):
    o.game._initBlock(o.game.blocks['I'])
    o.game.move(Act.Drop)
    for x in range(4):
      o.failUnless(o.isType(3+x,0,'I'))

  def isType(o,x,y,k):
    return o.game.board[x,y]!=None \
       and o.game.board[x,y].kind==k


class AITests(unittest.TestCase): #============================================
  def setUp(o):
    o.game = Tetris()

  def testHeuristics(o):
    y = getPieceMap(o.game.board)
    _,y = addBlock(y,Block('I', [(0,1),(1,1),(2,1),(3,1)], 4))
    _,y = addBlock(y,Block('I', [(0,3),(1,3),(2,3),(3,3)], 4))
    _,y = addBlock(y,Block('I', [(5,0),(5,1),(5,2),(5,3)], 4))
    _,y = addBlock(y,Block('I', [(7,0),(7,1),(7,2),(7,3)], 4))
    results = (getShadowedHoles(y),getOccupiedCells(y),
               getWeightedCells(y),getWellHeightSum(y))
    # print pieceMapStr(y)
    # print results
    o.failUnless(results == (8,16,44,8))


if __name__ == '__main__': unittest.main()