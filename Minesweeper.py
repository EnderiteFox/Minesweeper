#Libraries
from pygame import *
from random import *
import time

#Initialisation
init()

#Screen
screen=display.set_mode((800,800))

#System control
fullscreen=False

#Images
flagImage=image.load("Flag.png").convert_alpha()
flagImage=transform.scale(flagImage,(37,37))
mineImage=image.load("Mine.png").convert_alpha()
mineImage=transform.scale(mineImage,(31,31))
darkOverlay=image.load("darkOverlay.png").convert_alpha()

#Place mines
def generateMap(firstClickPos):
    global map
    global minesPos
    temp=[]
    for k in range(20):
        for i in range(20):
            temp.append((k,i))
    for k in range(randint(40,60)):
        tmp=temp[randint(0,len(temp)-1)]
        temp.remove(tmp)
        map[tmp[0]][tmp[1]]="Mine"
    #First click is safe
    map[firstClickPos[0]][firstClickPos[1]]=None
    if firstClickPos[0]>0:
        map[firstClickPos[0]-1][firstClickPos[1]]=None
    if firstClickPos[0]<19:
        map[firstClickPos[0]+1][firstClickPos[1]]=None
    if firstClickPos[1]>0:
        map[firstClickPos[0]][firstClickPos[1]-1]=None
    if firstClickPos[1]<19:
        map[firstClickPos[0]][firstClickPos[1]+1]=None
    if firstClickPos[0]>0 and firstClickPos[1]>0:
        map[firstClickPos[0]-1][firstClickPos[1]-1]=None
    if firstClickPos[0]<19 and firstClickPos[1]<19:
        map[firstClickPos[0]+1][firstClickPos[1]+1]=None
    if firstClickPos[0]<19 and firstClickPos[1]>0:
        map[firstClickPos[0]+1][firstClickPos[1]-1]=None
    if firstClickPos[0]>0 and firstClickPos[1]<19:
        map[firstClickPos[0]-1][firstClickPos[1]+1]=None
    #Update numbers
    for x in range(20):
        for y in range(20):
            numMines=0
            if x>0 and map[x-1][y]=="Mine":
                numMines+=1
            if x<19 and map[x+1][y]=="Mine":
                numMines+=1
            if y>0 and map[x][y-1]=="Mine":
                numMines+=1
            if y<19 and map[x][y+1]=="Mine":
                numMines+=1
            if x>0 and y>0 and map[x-1][y-1]=="Mine":
                numMines+=1
            if x<19 and y<19 and map[x+1][y+1]=="Mine":
                numMines+=1
            if x>0 and y<19 and map[x-1][y+1]=="Mine":
                numMines+=1
            if x<19 and y>0 and map[x+1][y-1]=="Mine":
                numMines+=1
            if map[x][y]!="Mine":
                map[x][y]=numMines
    #Update mines pos
    for x in range(20):
        for y in range(20):
            if map[x][y]=="Mine":
                minesPos.append((x,y))

#Draw map overlay (hides mines and closed tiles)
def hide():
    for x in range(20):
        for y in range(20):
            #Closed tile
            if (x,y) not in opened:
                draw.rect(screen,(200,200,200),Rect(x*40,y*40,37,37))
                draw.line(screen,(100,100,100),(x*40+35,y*40),(x*40+35,y*40+35),4)
                draw.line(screen,(100,100,100),(x*40,y*40+35),(x*40+37,y*40+35),4)
            #Flag
            if (x,y) in flags:
                screen.blit(flagImage,Rect(x*40-5,y*40,37,37))
            #Unsure
            if (x,y) in unsure:
                screen.blit(font.SysFont("Comic Sans MS",40).render("?",1,(255,165,0)),Rect(x*40+8,y*40-14,37,37))

#Draw map
def drawMap():
    global map
    for x in range(20):
        for y in range(20):
            #Tile is a mine
            if map[x][y]=="Mine":
                #If you touched the mine its background is red, if not it's grey
                if (x,y)not in explosedMine:
                    draw.rect(screen,(100,100,100),Rect(x*40,y*40,37,37))
                else:
                    draw.rect(screen,(255,0,0),Rect(x*40,y*40,37,37))
                screen.blit(mineImage,Rect(x*40+2,y*40+3,37,37))
            else:
                #Render numbers
                draw.rect(screen,(170,170,170),Rect(x*40,y*40,37,37))
                if map[x][y]==1:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("1",1,(0,0,255)),Rect(x*40+8,y*40-11,37,37))
                if map[x][y]==2:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("2",1,(0,200,0)),Rect(x*40+7,y*40-11,37,37))
                if map[x][y]==3:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("3",1,(255,0,0)),Rect(x*40+8,y*40-11,37,37))
                if map[x][y]==4:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("4",1,(0,0,100)),Rect(x*40+8,y*40-11,37,37))
                if map[x][y]==5:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("5",1,(109,7,26)),Rect(x*40+8,y*40-11,37,37))
                if map[x][y]==6:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("6",1,(13,153,150)),Rect(x*40+8,y*40-11,37,37))
                if map[x][y]==7:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("7",1,(0,0,0)),Rect(x*40+7,y*40-11,37,37))
                if map[x][y]==8:
                    screen.blit(font.SysFont("Comic Sans MS",40).render("8",1,(120,90,170)),Rect(x*40+6,y*40-11,37,37))

#Opens all adjacent tiles that don't have a flag or unsure
def clearSafeTiles(tilePos,useAutoScan):
    global opened
    global flags
    global scanned
    for x in range(-1,2):
        for y in range(-1,2):
            if tilePos[0]+x>=0 and tilePos[0]+x<=19 and tilePos[1]+y>=0 and tilePos[1]+y<=19:
                if (tilePos[0]+x,tilePos[1]+y) not in flags and (tilePos[0]+x,tilePos[1]+y) not in unsure:
                    if (tilePos[0]+x,tilePos[1]+y) not in opened:
                        opened.append((tilePos[0]+x,tilePos[1]+y))
                    if map[tilePos[0]+x][tilePos[1]+y]==0 and (tilePos[0]+x,tilePos[1]+y) not in scanned and useAutoScan==True:
                        #Use safeTilesAutoOpen if tiles not scanned yet, if tile is safe and if the function is called from click and not from safeTilesAutoOpen
                        #Not using useAutoScan correctly will cause crash due to recursion
                        safeTilesAutoOpen((tilePos[0]+x,tilePos[1]+y))

#Automatically opens safe adjacent tiles that don't have a mine next to them, and uses clearSafeTiles on them
def safeTilesAutoOpen(firstTilePos):
    global opened
    global flags
    global scanned
    scanned.append(firstTilePos)
    clearSafeTiles(firstTilePos,False)
    if map[firstTilePos[0]][firstTilePos[1]]==0 and firstTilePos not in scanned:
        clearSafeTiles(firstTilePos,False)
    scannPos=(firstTilePos[0]-1,firstTilePos[1])
    if scannPos[0]>=0 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)
    scannPos=(firstTilePos[0]+1,firstTilePos[1])
    if scannPos[0]<=19 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)
    scannPos=(firstTilePos[0],firstTilePos[1]-1)
    if scannPos[1]>=0 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)
    scannPos=(firstTilePos[0],firstTilePos[1]+1)
    if scannPos[1]<=19 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)
    scannPos=(firstTilePos[0]-1,firstTilePos[1]-1)
    if scannPos[0]>=0 and scannPos[1]>=0 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)
    scannPos=(firstTilePos[0]+1,firstTilePos[1]+1)
    if scannPos[0]<=19 and scannPos[1]<=19 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)
    scannPos=(firstTilePos[0]-1,firstTilePos[1]+1)
    if scannPos[0]>=0 and scannPos[1]<=19 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)
    scannPos=(firstTilePos[0]+1,firstTilePos[1]-1)
    if scannPos[0]<=19 and scannPos[1]>=0 and map[scannPos[0]][scannPos[1]]==0 and scannPos not in scanned:
        clearSafeTiles(scannPos,False)
        safeTilesAutoOpen(scannPos)

#The game
def game():
    global screen
    global fullscreen
    global firstClick
    global gameState
    global explosedMine
    global flags
    global scanned
    explosedMine=[]
    while True:
        for events in event.get():
            if events.type==QUIT:
                quit()
                exit()
            if events.type==KEYDOWN and events.key==K_ESCAPE:
                quit()
                exit()
            if events.type==KEYDOWN and events.key==K_f:
                #Fullscreen toggle
                if fullscreen==True:
                    screen=display.set_mode((800,800))
                    fullscreen=False
                else:
                    screen=display.set_mode((800,800),FULLSCREEN)
                    fullscreen=True
            #Left click
            if events.type==MOUSEBUTTONDOWN and events.button==1:
                clickPos=(events.pos[0]//40,events.pos[1]//40)
                #Generate map only after first click
                if firstClick==False:
                    generateMap(clickPos)
                    firstClick=True
                #Clicked on open tile
                if clickPos in opened:
                    scanned=[]
                    clearSafeTiles(clickPos,True)
                    scanned=[]
                #Clicked on closed tile
                if clickPos not in opened:
                    opened.append(clickPos)
                    #Use auto safe tiles opener
                    if map[clickPos[0]][clickPos[1]]==0:
                        scanned=[]
                        safeTilesAutoOpen(clickPos)
                        scanned=[]
                #Remove flag
                if clickPos in flags:
                    flags.remove(clickPos)
                #Remove unsure
                if clickPos in unsure:
                    unsure.remove(clickPos)
            #Right click
            if events.type==MOUSEBUTTONDOWN and events.button==3:
                clickPos=(events.pos[0]//40,events.pos[1]//40)
                #Add/remove flag
                if clickPos in flags:
                    flags.remove(clickPos)
                elif clickPos not in opened and clickPos not in unsure:
                    flags.append(clickPos)
            #Middle click
            if events.type==MOUSEBUTTONDOWN and events.button==2:
                clickPos=(events.pos[0]//40,events.pos[1]//40)
                #Add/remove unsure
                if clickPos in unsure:
                    unsure.remove(clickPos)
                elif clickPos not in opened and clickPos not in flags:
                    unsure.append(clickPos)
            #Restart game
            if events.type==KEYDOWN and events.key==K_r:
                return None
        #Win detection
        win=True
        if len(minesPos)==len(flags):
            for mine in minesPos:
                if mine not in flags:
                    win=False
        else:
            win=False
        if not len(opened)==400-len(minesPos):
            win=False
        if win==True and firstClick==True:
            gameState="Won"
        #Explosion detection
        temp=False
        for mine in minesPos:
            if mine in opened and gameState=="Playing":
                temp=True
                if mine not in explosedMine:
                    explosedMine.append(mine)
        if temp==True:
            gameState="Lost"
            for mine in minesPos:
                if mine not in opened:
                    opened.append(mine)
            flags=[]
        screen.fill((0,0,0))
        drawMap()
        hide()
        if gameState=="Won":
            screen.blit(darkOverlay,Rect(0,0,800,800))
            screen.blit(font.SysFont("Comic Sans MS",100).render("You win!",1,(0,255,0)),Rect(200,300,100,50))
            screen.blit(font.SysFont("Comic Sans MS",40).render("Press R to play again",1,(255,255,255)),Rect(200,500,100,50))
        if gameState=="Lost":
            screen.blit(darkOverlay,Rect(0,0,800,800))
            screen.blit(font.SysFont("Comic Sans MS",100).render("You lost!",1,(255,0,0)),Rect(200,300,100,50))
            screen.blit(font.SysFont("Comic Sans MS",40).render("Press R to play again",1,(255,255,255)),Rect(200,500,100,50))
        display.flip()

#Start game
while True:
    #Map
    map=[[None for x in range(20)] for y in range(20)]

    #Game state indicators
    firstClick=False
    gameState="Playing"
    explosedMine=[]

    #Lists
    opened=[]
    flags=[]
    scanned=[]
    minesPos=[]
    unsure=[]

    #Game start
    game()