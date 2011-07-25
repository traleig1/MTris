import random
from collections import deque
import abc
from Data import *

class BlockQueue(object):
  """A queue of blocks positioned at (0,0) to be dropped onto the board."""
  __metaclass__ = abc.ABCMeta

  def __init__(o,size):
    o._queue = deque([o.newBlock() for n in range(size)])

  def __iter__(o):
    return o._queue.__iter__()

  def pop(o):
    """Get a block from the queue."""
    o._queue.append(o.newBlock())
    return o._queue.popleft()

  @abc.abstractmethod
  def newBlock(o):
    """Add a new block to the back of the queue."""
    pass


class RandomQueue(BlockQueue):
  """A queue which cycles through available blocks in a random order."""

  def __init__(o,size): #needs blocks passed in
    o._blockSet = []
    BlockQueue.__init__(o,size)

  def newBlock(o):
    if o._blockSet == []:
      o._blockSet = [block for block in blocks]
    newBlock = random.choice(o._blockSet)
    o._blockSet.remove(newBlock)
    return newBlock


class FixedQueue(BlockQueue):
  """
     A queue which returns the specified blocks in order.
     Intended to ease testing.
  """

  def __init__(o,size,blockString):
    bDict = {block.kind : block for block in blocks}
    o._blockSet = [bDict[key] for key in blockString]
    BlockQueue.__init__(o,size)

  def newBlock(o):
    try:               newBlock = o._blockSet.pop()
    except IndexError: newBlock = Block('X',[(1,1)],3)
    return newBlock