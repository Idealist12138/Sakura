import random, sys, copy, os, pygame,time
from pygame.locals import *

FPS = 30 
WINWIDTH = 800 
WINHEIGHT = 800 
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 40
CAM_MOVE_SPEED = 1 
OUTSIDE_DECORATION_PCT = 40
BRIGHTBLUE = (  0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    bgm()
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    ico = pygame.image.load('resource/icon.png').convert_alpha()
    pygame.display.set_icon(ico)

    pygame.display.set_caption(r"Sakura's Task "+" "*60+"by Zhang Haoyu")
    BASICFONT = pygame.font.Font('resource/Raleway-Regular-2.ttf', 24)

    IMAGESDICT = {'uncovered goal': pygame.image.load('resource/RedSelector.png').convert_alpha(),
                  'covered goal': pygame.image.load('resource/Selector.png').convert_alpha(),
                  'star': pygame.image.load('resource/Star.png').convert_alpha(),
                  'corner': pygame.image.load('resource/Wall_Block_Tall.png').convert_alpha(),
                  'wall': pygame.image.load('resource/Wood_Block_Tall.png').convert_alpha(),
                  'inside floor': pygame.image.load('resource/Plain_Block.png').convert_alpha(),
                  'outside floor': pygame.image.load('resource/Grass_Block.png').convert_alpha(),
                  'title': pygame.image.load('resource/star_title.png').convert_alpha(),
                  'solved': pygame.image.load('resource/star_solved.png').convert_alpha(),
                  'quit': pygame.image.load('resource/star_quit.png').convert_alpha(),
                  'Sakura_1': pygame.image.load('resource/Sakura_1.png').convert_alpha(),
                  'Syaoran Li': pygame.image.load('resource/Syaoran Li.png').convert_alpha(),
                  'Sakura_2': pygame.image.load('resource/Sakura_2.png').convert_alpha(),
                  'Sakura_3': pygame.image.load('resource/Sakura_3.png').convert_alpha(),
                  'Tomoyo Daidouji': pygame.image.load('resource/Tomoyo Daidouji.png').convert_alpha(),
                  'rock': pygame.image.load('resource/Rock.png').convert_alpha(),
                  'short tree': pygame.image.load('resource/Tree_Short.png').convert_alpha(),
                  'tall tree': pygame.image.load('resource/Tree_Tall.png').convert_alpha(),
                  'ugly tree': pygame.image.load('resource/Tree_Ugly.png').convert_alpha()}

    TILEMAPPING = {'x': IMAGESDICT['corner'],
                   '#': IMAGESDICT['wall'],
                   'o': IMAGESDICT['inside floor'],
                   ' ': IMAGESDICT['outside floor']}
    OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],
                          '2': IMAGESDICT['short tree'],
                          '3': IMAGESDICT['tall tree'],
                          '4': IMAGESDICT['ugly tree']}

    currentImage = 0
    PLAYERIMAGES = [IMAGESDICT['Sakura_1'],
                    IMAGESDICT['Syaoran Li'],
                    IMAGESDICT['Sakura_2'],
                    IMAGESDICT['Tomoyo Daidouji'],
                    IMAGESDICT['Sakura_3']]

    startScreen() 
    instructionscreen()

    levels = readLevelsFile('resource/Levels.txt')
    currentLevelIndex = 0

    while True: 
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            next_level = pygame.mixer.Sound('resource/next_level.wav')
            next_level.play()
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                currentLevelIndex = 0
        elif result == 'back':
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass 


def bgm():
    bgm = 'resource/bgm.mp3'
    pygame.mixer.init()
    pygame.mixer.music.load(bgm)
    pygame.mixer.music.play(-1,0)


def change():
    change_chara = pygame.mixer.Sound('resource/change.wav')
    change_chara.play()


def runLevel(levels, levelNum):
    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True 
    levelSurf = BASICFONT.render('Level %s / %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT

    levelIsComplete = False
    cameraOffsetX = 0
    cameraOffsetY = 0
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False
    
    while True: 
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get(): 
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True
                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'
                elif event.key == K_ESCAPE:
                    terminate() 
                elif event.key == K_BACKSPACE:
                    return 'reset' 
                elif event.key == K_p:
                    currentImage += 1
                    change()
                    if currentImage >= len(PLAYERIMAGES):
                        currentImage = 0
                    mapNeedsRedraw = True

            elif event.type == KEYUP:
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo != None and not levelIsComplete:

            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True
                keyPressed = False

        DISPLAYSURF.fill(BGCOLOR)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX, HALF_WINHEIGHT + cameraOffsetY)

        DISPLAYSURF.blit(mapSurf, mapSurfRect)
        draw_chracter(currentImage)

        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)

        if levelIsComplete:
            solvedRect = IMAGESDICT['solved'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGESDICT['solved'], solvedRect)
            if keyPressed:
                return 'solved'

        pygame.display.update() 
        FPSCLOCK.tick()


def isWall(mapObj, x, y):
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False 
    elif mapObj[x][y] in ('#', 'x'):
        return True 
    return False


def decorateMap(mapObj, startxy):
    startx, starty = startxy 

    mapObjCopy = copy.deepcopy(mapObj)

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                   (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                   (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                   (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):

    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True 

    elif (x, y) in gameStateObj['stars']:
        return True 

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):

    playerx, playery = gameStateObj['player']

    stars = gameStateObj['stars']

    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
                ind = stars.index((playerx + xOffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
            else:
                return False
        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True


def textdraw():
    instructionText = ['------------------How to play----------------------',
                        ' ',
                        r'\^O^/ Push CERBERUS over the marks. \^O^/',
                        ' ',
                       'ARROW keys to move.', 
                       'WASD for camera control.', 
                       'P to change character.',
                       'BACKSPACE to reset level.', 
                       'ESC to quit.',
                       'N for next level', 
                       'B to go back a level.',
                       ' ',
                       '------------PRESS A KEY TO CONTINUE--------------']

    topCoord_1=40
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord_1 += 10 
        instRect.top = topCoord_1
        instRect.centerx = HALF_WINWIDTH
        topCoord_1 += instRect.height 
        DISPLAYSURF.blit(instSurf, instRect)


def startScreen():

    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 0 
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    DISPLAYSURF.fill(BGCOLOR)

    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

    while True: 
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return 

        pygame.display.update()
        FPSCLOCK.tick()


def instructionscreen():
    DISPLAYSURF.fill(BGCOLOR)
    textdraw()
    while True: 
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return 

        pygame.display.update()
        FPSCLOCK.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = [] 
    levelNum = 0
    mapTextLines = [] 
    mapObj = [] 
    for lineNum in range(len(content)):

        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            line = line[:line.find(';')]

        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])

            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            startx = None 
            starty = None
            goals = [] 
            stars = [] 
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        stars.append((x, y))

            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))

            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
            
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):

    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) 
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) 
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) 
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) 


def drawMap(mapObj, gameStateObj, goals):

    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR) 

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']

            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in OUTSIDEDECOMAPPING:
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                mapSurf.blit(IMAGESDICT['star'], spaceRect)
            elif (x, y) in goals:
                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect)
            if (x, y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES[currentImage], spaceRect)

    return mapSurf


def draw_chracter(currentImage):
    if currentImage==1:
        f1 = pygame.image.load('resource/Syaoran Li_c.png').convert_alpha()
        DISPLAYSURF.blit(f1,(25,25))
    elif currentImage==3:
        f2 = pygame.image.load('resource/Tomoyo Daidouji_c.png').convert_alpha()
        DISPLAYSURF.blit(f2,(25,25))
    else:
        f3 = pygame.image.load('resource/Sakura_c.png').convert_alpha()
        DISPLAYSURF.blit(f3,(25,25))


def isLevelFinished(levelObj, gameStateObj):
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            return False
    return True


def drawquit():
    quitRect = IMAGESDICT['quit'].get_rect()
    topCoord = 0 
    quitRect.top = topCoord
    quitRect.centerx = HALF_WINWIDTH
    topCoord += quitRect.height
    BGCOLOR_1 =(255,192,203)

    DISPLAYSURF.fill(BGCOLOR_1)

    DISPLAYSURF.blit(IMAGESDICT['quit'], quitRect)

    pygame.display.update()
    time.sleep(3)
    FPSCLOCK.tick()
    pygame.quit()


def terminate():
    drawquit()
    sys.exit()


if __name__ == '__main__':
    main()