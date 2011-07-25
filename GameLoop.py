import abc
from Enum import Enum

MaxFrameSkip = 10
class GameUI(object):
  """The interface for a UI, with a default implementation of a game loop."""
  __metaclass__ = abc.ABCMeta

  def run(o,initialState):
    """Run a basic game loop."""
    o.state       = initialState(o)
    nextTick      = o.getTime()
    hasTicked     = lambda: o.getTime() > nextTick
    framesSkipped = MaxFrameSkip+1 #Force draw on first loop
    while True:
      if (not hasTicked() or framesSkipped > MaxFrameSkip): #should draw
        o.processInput()
        o.state.runAI()
        o.drawFrame()
        framesSkipped = 0
      else: framesSkipped +=1
      if (hasTicked()):
        o.state.runEngine()
        nextTick += o.state.msPerFrame()

  @abc.abstractmethod
  def drawFrame(o):
    """
       Set up a frame, draw it to the screen, and tear it down.

       Control should be passed to the current State's draw method
       so that the State can draw itself to the frame buffer using
       this class' draw method.
    """
    pass

  @abc.abstractmethod
  def processInput(o):
    """
       Read player input and pass it on to the current State.

       Player inputs should be passed to the State class in a
       form enumerated in the Btn object.
    """
    pass

  @abc.abstractmethod
  def getTime(o):
    """Return the current time in milliseconds."""
    pass

  @abc.abstractmethod
  def draw(o,image,pt):
    """Draw the given image to the framebuffer at pt."""
    pass

#Possible inputs modelled on the Gameboy Advance button layout
Btn = Enum(["Up","Down","Left","Right","A","B","L","R","Select","Start"])

class State(object):
  """
     A state in the GameUI state machine.

     Each state uses the primitives provided by the GameUI class
     to manage IO in a device/OS/framework independent way.
  """

  def __init__(o,ui):
    o.ui = ui

  def msPerFrame(o):
    """Return the delay between calls to runEngine."""
    return 1000//5

  def runAI(o):
    """Execute input from computer player."""
    pass

  def runEngine(o):
    """Execute actions specified by the game rules."""
    pass

  def input(o,button):
    """Map button to an action and execute it."""
    pass

  def drawFrame(o):
    """Draw screen to the framebuffer using the GameUI's draw method."""
    pass

#Change to run runEngine more often, move processInput and runAI into
#the same area as runEngine, and then restrict how often runEngine runs
#in the state class. This should also let us kill the msPerFrame methods