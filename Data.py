from TetrisBlock import Block, clockwise, counterClockwise
from collections import Counter

blocks = {                                   Block('I', [(0,2),(1,2),(2,2),(3,2)], 4),
  Block('O', [(1,1),(2,1),(2,2),(1,2)], 4),  Block('T', [(0,1),(1,1),(2,1),(1,2)], 3),
  Block('Z', [(0,2),(1,2),(1,1),(2,1)], 3),  Block('L', [(0,1),(1,1),(2,1),(2,2)], 3),
  Block('S', [(0,1),(1,1),(1,2),(2,2)], 3),  Block('J', [(0,1),(1,1),(2,1),(0,2)], 3)}

def _getWallKickTable():
  def parse(strList):
    def toTuple(string): #example: 'LLU' -> (-2,1)
      cnt = Counter(string)
      return (cnt['R']-cnt['L'], cnt['U']-cnt['D'])
    return [[toTuple(item) for item in s.split(',')] for s in strList]
  aCCW = parse([',R,RD,UU,RUU',',L,LU,DD,LDD',',L,LD,UU,LUU',',R,RU,DD,RDD'])
  aCW  = parse([',L,LD,UU,LUU',',L,LU,DD,LDD',',R,RD,UU,RUU',',R,RU,DD,RDD'])
  iCCW = parse([',RR,L,RRU,LDD',',LL,R,LLU,RD ',',R,LL,RUU,LLD',',RR,L,LUU,RRD'])
  iCW  = parse([',LL,R,LLU,RDD',',LL,R,RUU,LLD',',L,RR,LUU,RRD',',RR,L,RRU,LD '])
  aWK = {counterClockwise: aCCW, clockwise: aCW}
  iWK = {counterClockwise: iCCW, clockwise: iCW}
  return  {'I':iWK,'O':aWK,'T':aWK,'L':aWK,'J':aWK,'S':aWK,'Z':aWK}
WallKick = _getWallKickTable()