#This code is not actually executed when running the game
# This is the uncompressed form of the wall-kick data, and
# a method for recompressing it into the (more readable) form
# used in the sourcecode


def toStrLst(lst):
  conv = lambda direction,pos,neg: (pos if direction>0 else neg)*abs(direction)
  return ','.join([conv(hzn,'R','L')+conv(vert,'U','D') for hzn,vert in lst])

aCW  =[#J,L,S,T,Z Blocks - clockwise
  [( 0, 0),(-1, 0),(-1,-1),( 0, 2),(-1, 2)],
  [( 0, 0),(-1, 0),(-1, 1),( 0,-2),(-1,-2)],
  [( 0, 0),( 1, 0),( 1,-1),( 0, 2),( 1, 2)],
  [( 0, 0),( 1, 0),( 1, 1),( 0,-2),( 1,-2)]]
aCCW =[#J,L,S,T,Z Blocks - counter
  [( 0, 0),( 1, 0),( 1,-1),( 0, 2),( 1, 2)],
  [( 0, 0),(-1, 0),(-1, 1),( 0,-2),(-1,-2)],
  [( 0, 0),(-1, 0),(-1,-1),( 0, 2),(-1, 2)],
  [( 0, 0),( 1, 0),( 1, 1),( 0,-2),( 1,-2)]]
iCW  =[#I Block (SRS-Arika) - clockwise
  [( 0, 0),(-2, 0),( 1, 0),(-2, 1),( 1,-2)],
  [( 0, 0),(-2, 0),( 1, 0),( 1, 2),(-2,-1)],
  [( 0, 0),(-1, 0),( 2, 0),(-1, 2),( 2,-1)],
  [( 0, 0),( 2, 0),(-1, 0),( 2, 1),(-1,-1)]]
iCCW =[#I Block (SRS-Arika) - counter
  [( 0, 0),( 2, 0),(-1, 0),( 2, 1),(-1,-2)],
  [( 0, 0),(-2, 0),( 1, 0),(-2, 1),( 1,-1)],
  [( 0, 0),( 1, 0),(-2, 0),( 1, 2),(-2,-1)],
  [( 0, 0),( 2, 0),(-1, 0),(-1, 2),( 2,-1)]]
#Data from: http://www.tetrisconcept.net/wiki/SRS
