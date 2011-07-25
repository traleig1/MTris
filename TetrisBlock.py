from collections import namedtuple

Point = namedtuple('Point','x y')
Point.shift   = lambda o,x,y: Point( o.x+x,  o.y+y)
Point.scale   = lambda o,s:   Point( o.x*s,  o.y*s)
Point.descale = lambda o,s:   Point( o.x//s, o.y//s)
Point._rot    = lambda o,d:   Point( o.y,-o.x) if d is clockwise \
                       else   Point(-o.y, o.x)
Point.rotate  = lambda o,d,x,y: o.shift(-x,-y)._rot(d).shift(x,y)
Point.__str__ = lambda o: '('+str(o.x)+','+str(o.y)+')'

class Square(object):
  """One square of a tetromino."""

  def __init__(o,block,index,pt):
    o._block, o.index, o.pt = block, index, pt

  def _setBroken(o,state):
    o._block.broken = state

  def __str__(o):
    return o.kind+str(o.pt)

  kind     = property(lambda o: o._block.kind    )
  rotation = property(lambda o: o._block.rotation)
  broken   = property(lambda o: o._block.broken  , _setBroken)
  x = property(lambda o: o.pt.x)
  y = property(lambda o: o.pt.y)

  #mutators return self to support method chaning, list comprehensions
  def shift(o,x,y):
    """Translate square by (x,y)."""
    o.pt = o.pt.shift(x,y);
    return o

  def scale(o,s):
    o.pt = o.pt.scale(s)
    return o

  def descale(o,s):
    o.pt = o.pt.descale(s)
    return o

  def rotate(o,direction,centerOfRotation):
    """Rotate square clockwise/counterclockwise about centerOfRotation."""
    o.pt = o.pt.rotate(direction,*centerOfRotation)
    return o

# - Expand square's "broken" to indicate which squares are still on the board
# - Can we add extra methods to the block class, etc,
#   to make determining rotation easier?

clockwise,counterClockwise = False,True

class Block(object):
  """A Tetromino"""
  def __init__(o, kind, grid, gridSize):
    o.squares = [Square(o,n,Point(*pt)) for n,pt in enumerate(grid)]
    o.kind, o.gridSize = kind, gridSize
    o._center = Point(gridSize-1,gridSize-1) #Note[1]
    o.rotation = 0
    o.broken = False

  def __iter__(o):
    return o.squares.__iter__()

  def __str__(o):
    return o.kind+'['+','.join(str(sq.pt) for sq in o.squares)+']'

  def shift(o,x,y):
    """Translate block by (x,y)"""
    for sq in o.squares: sq.shift(x,y)
    o._center = o._center.shift(2*x,2*y) #Note[1]
    return o

  def rotate(o, direction):
    """Rotate block clockwise/counterclockwise"""
    for sq in o.squares:
      sq.scale(2).rotate(direction,o._center).descale(2) #Note[1]
    o.rotation = (o.rotation + (1 if direction is clockwise else -1)) % 4
    return o

  def containsPoint(o,pt):
    """Check if the block contains a square at pt"""
    return (pt in (sq.pt for sq in o))

  def clone(o):
    """Return a copy of this block"""
    #copy.copy creates too shallow of a copy -
    #  modifying the grid modifies both the original and the copy
    #copy.deepcopy creates an unnecessarily deep copy, killing performance
    newBlock = Block(o.kind, [sq.pt for sq in o.squares], o.gridSize)
    newBlock._center  = o._center
    newBlock.rotation = o.rotation
    newBlock.broken   = o.broken
    return newBlock

#Notes:
# [1] - 3 square wide blocks (Z,S,L,J,T) have a non-integral center,
#       but the result of rotation is always integral. To avoid unnecessary
#       type conversions, we simulate fixed-point division by scaling
#       all points by a factor of 2 during rotation. (hence the upper-right
#       corner of the block grid becomes the center after scaling)