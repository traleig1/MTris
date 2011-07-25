#!/usr/bin/python
import pygame, sys, os
from pygame.locals import *
from pygame.transform import rotate,flip,scale
from MyUI import UI_8x8, MenuScreen
from GameLoop import GameUI, Btn
import argparse

#Image Data and methods========================================================
def img(name,ext='png'): return pygame.image.load(os.path.join("Images",name+"."+ext))
def getTile(image,x,y,sx,sy): return image.subsurface(x*sx,y*sy,sx,sy)
def spinFlip(i):
  return [i, rotate(i,90), flip(i,True,False), flip(rotate(i,90),False,True)]
def tileRow(image,row,sx,sy):
  return [getTile(image,col,row,sx,sy) for col in range(image.get_width()//sx)]
def imageDict(keyString,image,row,sx,sy):
  return dict(zip(' '+keyString,[None]+tileRow(image,row,sx,sy)))

class ImgData():
  tiles      = img("Tiles")
  introImage = img("IntroBG")
  bgImage    = img("GameBG")
  twoPlayerBG= img("2Player")
  pauseTxt   = img("Pause")
  gameOverTxt= img("GameOver")
  pointer    = img("Pointer")
  blocks     = imageDict("IOLJSZT",tiles,0,16,16)
  shadows    = imageDict("IOLJSZT",tiles,1,16,16)
  pipe,joint = spinFlip(getTile(tiles,2,2,16,16)),getTile(tiles,3,2,16,16)
  iceBlock   = [getTile(tiles,0+ox,2+oy,16,16) for ox,oy in [(0,1),(1,1),(1,0),(0,0)]]
  smallChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-.,*!@=:"
  largeChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-."
  fontSmall  = imageDict(smallChars,img("Font"),     0,8,8)
  fontLarge  = imageDict(largeChars,img("FontLarge"),0,8,16)
  xBlock     = getTile(tiles,2,3,16,16)
  txtBlocks  = imageDict('ISYOR',img("TitleBlocks"),0,16,16)

class PygameUI(UI_8x8):
  def __init__(o, title, screenDimensions, scale):
    o.width, o.height = screenDimensions
    o.scale = scale if scale in range(0,4) else 1
    o.images = ImgData
    pygame.init()
    window = pygame.display.set_mode(o._scalePt(*screenDimensions))
    pygame.display.set_caption(title)
    pygame.key.set_repeat(200,75) # we should implement this through the game loop
    o._screen = pygame.display.get_surface()
    o._keyMap = {K_z: Btn.B, K_LEFT:   Btn.Left,  K_UP:        Btn.Up,
                 K_x: Btn.A, K_DOWN:   Btn.Down,  K_RIGHT:     Btn.Right,
                 K_a: Btn.L, K_RETURN: Btn.Start, K_BACKSLASH: Btn.Select}

  def drawFrame(o):
    o.state.drawFrame()
    pygame.display.flip()

  def processInput(o):
    for event in pygame.event.get():
      if  (event.type == QUIT): sys.exit(0)
      elif(event.type == KEYDOWN):
        if(event.key == K_ESCAPE): sys.exit(0)
        elif(event.key in o._keyMap): o.state.input(o._keyMap[event.key])

  def getTime(o):
    return pygame.time.get_ticks()

  def draw(o,image,pt):
    if image is None: return
    x,y = pt
    h,w = image.get_height(), image.get_width()
    screenCoords = (x,o.height-y-h)
    scaledImage = scale(image,o._scalePt(w,h))
    o._screen.blit(scaledImage,o._scalePt(*screenCoords))

  def _scalePt(o,x,y):
    return (x*o.scale,y*o.scale)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='A puzzle game of falling blocks')
  parser.add_argument('--scale', action="store", dest="scale", type=int, default=1)
  args = parser.parse_args()
  PygameUI('Tetris', (480,320), args.scale).run(MenuScreen)