# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, time, pygame, sys
from pygame.locals import *

FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.
#MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....'],
                    ['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

LSPIECES = ['S', 'Z', 'J', 'L','I','O','T']

#bag setup
#format: availability (1/0) of s z j l i o t
shapeBag = [1,1,1,1,1,1,1]

hotkeys = {
    "left": K_LEFT,
    "right": K_RIGHT,
    "down": K_DOWN,
    "hard_drop": K_SPACE,
    "hold": K_c,
    "rotate_left": K_z,
    "rotate_right": K_x,
    "pause": K_p,
    "settings": K_1,
    "quit": K_ESCAPE,
}

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, MEDIUMFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    MEDIUMFONT = pygame.font.Font("freesansbold.ttf", 32)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    showTextScreen('Tetromino')
    while True: # game loop
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load('tetrisb.mid')
        else:
            pygame.mixer.music.load('tetrisc.mid')
        pygame.mixer.music.play(-1, 0.0)
        runGame()
        pygame.mixer.music.stop()
        showTextScreen('Game Over')


def runGame():
    # setup variables for the start of the game
    global shapeBag
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)
    #hasHeld: has the user held a piece yet? defines whether hold piece is drawn on screen
    hasHeld = False
    #is this a holdable piece? e.g has the user placed their previous held piece?
    canHold = True
    
    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()
    heldPiece = None 

    while True: # game loop
        
        #if bag has been exhausted, refresh bag
        if 1 not in shapeBag:
            shapeBag = [1,1,1,1,1,1,1]
            
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime
        

        if not isValidPosition(board, fallingPiece):
            return # can't fit a new piece on the board, so game over

        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == KEYUP:
                if (event.key == hotkeys['pause']):
                    # Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.stop()
                    showTextScreen('Paused') # pause until a key press
                    pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif event.key == hotkeys['left']:
                    movingLeft = False
                elif event.key == hotkeys['right']:
                    movingRight = False
                elif event.key == hotkeys['down']:
                    movingDown = False
                elif event.key == hotkeys['settings']:
                    DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.stop()
                    showSettingsScreen()
                    pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()

            elif event.type == KEYDOWN:
                # moving the piece sideways
                if (event.key == hotkeys['left']) and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False
                    lastMoveSidewaysTime = time.time()

                elif (event.key == hotkeys['right']) and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    lastMoveSidewaysTime = time.time()

                # rotating the piece (if there is room to rotate)
                elif (event.key == hotkeys['rotate_right']):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                elif (event.key == hotkeys['rotate_left']): # rotate the other direction
                    fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])

                # making the piece fall faster with the down key
                elif (event.key == hotkeys['down']):
                    movingDown = True
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()

                # move the current piece all the way down
                elif event.key == hotkeys['hard_drop']:
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    fallingPiece['y'] += i - 1
                
                #if hold key pressed:
                elif event.key == hotkeys['hold'] and canHold:
                    #pieces stop moving for now
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    #copy the falling piece for transfer
                    tempPiece = holdPiece(fallingPiece)
                    #if the user has not yet held, the falling piece goes to hold and the next piece falls.
                    if not hasHeld:
                        heldPiece = holdPiece(fallingPiece)
                        fallingPiece = nextPiece
                        nextPiece = getNewPiece()
                        lastFallTime = time.time()
                        hasHeld = True
                    #if the user has previously held, the falling piece goes to hold and the held piece begins falling.
                    else:
                        fallingPiece = holdPiece(heldPiece)
                        heldPiece = holdPiece(tempPiece)
                        lastFallTime = time.time()
                    
                    #reset canHold so the user cannot endlessly switch pieces.
                    canHold = False
                    

        # handle moving the piece because of user input
        if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['x'] -= 1
            elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['x'] += 1
            lastMoveSidewaysTime = time.time()

        if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and isValidPosition(board, fallingPiece, adjY=1):
            fallingPiece['y'] += 1
            lastMoveDownTime = time.time()

        # let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            # see if the piece has landed
            if not isValidPosition(board, fallingPiece, adjY=1):
                # falling piece has landed, set it on the board
                addToBoard(board, fallingPiece)
                score += removeCompleteLines(board)
                level, fallFreq = calculateLevelAndFallFreq(score)
                fallingPiece = None
                #if the user has held, the held piece has been set down and they can hold again.
                canHold = True
            else:
                # piece did not land, just move the piece down
                fallingPiece['y'] += 1
                lastFallTime = time.time()

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        #if the user has held, draw held piece. otherwise, no held piece drawn.
        if hasHeld:
            drawHeldPiece(heldPiece)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
            drawPiece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showTextScreen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def createSettingsObject(name, vertical_pos, text_color=TEXTCOLOR, font_size=18):
    '''
    creates a settings object with the given name and vertical position

    Args:
        name (str): the name of the setting
        vertical_pos (int): the vertical position of the setting
        text_color (tuple): the color of the text
        font_size (int): the size of the font

    Returns:
        tuple: a tuple containing the surface, rect, name, and vertical position of the setting
    '''
    font = font_size
    if type(font_size) == int:
        font = pygame.font.Font("freesansbold.ttf", font_size)
    keySurf, keyRect = makeTextObjs(
       name, font, text_color
    )
    
    keyRect.center = (int(WINDOWWIDTH / 2), vertical_pos)
    DISPLAYSURF.blit(keySurf, keyRect)
    return keySurf, keyRect, name, vertical_pos


def showSettingsScreen():
    ''' 
    This function displays the settings screen where the user can change the hotkeys
    '''
    global hotkeys
    # this function displays hotkey settings such as side speed and down speed
    createSettingsObject("Settings", 80, font_size=MEDIUMFONT)

    # Draw the current hotkeys being used for the game
    settingsObjectTuples = [
        createSettingsObject(f"Left: {pygame.key.name(hotkeys['left'])}", 150),
        createSettingsObject(f"Right: {pygame.key.name(hotkeys['right'])}", 175),
        createSettingsObject(f"Soft Drop: {pygame.key.name(hotkeys['down'])}", 200),
        createSettingsObject(f"Hard Drop: {pygame.key.name(hotkeys['hard_drop'])}", 225),
        createSettingsObject(f"Rotate Left: {pygame.key.name(hotkeys['rotate_left'])}", 250),
        createSettingsObject(f"Rotate Right: {pygame.key.name(hotkeys['rotate_right'])}", 275),
        createSettingsObject(f"Hold: {pygame.key.name(hotkeys['hold'])}", 300),
        createSettingsObject(f"Pause: {pygame.key.name(hotkeys['pause'])}", 325),
        createSettingsObject(f"Settings: {pygame.key.name(hotkeys['settings'])}", 350),
        createSettingsObject(f"Quit: {pygame.key.name(hotkeys['quit'])}", 375),
    ]

    # mapping of the settings object to the hotkeys key
    objectToKeyMap = {
        0: 'left',
        1: 'right',
        2: 'down',
        3: 'hard_drop',
        4: 'rotate_left',
        5: 'rotate_right',
        6: 'hold',
        7: 'pause',
        8: 'settings',
        9: 'quit',
    }


    # Draw the additional "Press a key to play." text.
    createSettingsObject(f"Press {pygame.key.name(hotkeys['settings'])} to play.", 425)

    # Cursor variables for blinking when typing
    cursor_visible = False
    cursor_blink_time = 0
    cursor_blink_interval = 500 # milliseconds

    # Index of the clicked setting (-1 if none is clicked)
    clicked_index = -1


    while True: # game loop
        # mouse info
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            
            # Check if the user wants to go back to the game
            if event.type == KEYUP:
                if event.key == hotkeys['settings']:
                    return
            
            # Check if the user wants to change the a specific hotkey
            if event.type == KEYUP and clicked_index != -1:
                key = event.key
                # validate that the required key is not already in use
                if key not in hotkeys.values():
                    # update settings display
                    DISPLAYSURF.fill(BGCOLOR)
                    createSettingsObject("Settings", 80, font_size=MEDIUMFONT)
                    createSettingsObject(f"Press {pygame.key.name(hotkeys['settings'])} to play.", 425, text_color=TEXTCOLOR, font_size=BASICFONT)
                    hotkeys[objectToKeyMap[clicked_index]] = key # update the hotkey
                    
                    for i, (keySurf, keyRect, *_) in enumerate(settingsObjectTuples):
                        # got to the clicked index, update display and reset clicked index
                        if i == clicked_index:
                            settingsObjectTuples[clicked_index] = createSettingsObject(settingsObjectTuples[clicked_index][2].split(':')[0] + ': ' + pygame.key.name(key), settingsObjectTuples[clicked_index][3], text_color=WHITE)
                            clicked_index = -1
                        else:
                            DISPLAYSURF.blit(keySurf, keyRect)
                    
                    
            # highlight settings when hovered or clicked (clicked to change hotkey)
            if event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                # are any of the settings hovered over
                any_hovered = False
                for i, (_, keyRect, name, vertical_pos) in enumerate(settingsObjectTuples):
                    # Check if the mouse is over the rectangle
                    if keyRect.colliderect(mouse_pos[0], mouse_pos[1], 1, 1):
                        any_hovered = True # update hovered state so clicked_index gets reset

                        # check if the mouse has been clicked and update the setting to have a cursor
                        if mouse_clicked:
                            clicked_index = i
                            settingsObjectTuples[i] = createSettingsObject(name.split(':')[0] + ':' + ' _', vertical_pos, text_color=GRAY)
                        else:
                            settingsObjectTuples[i] = createSettingsObject(name, vertical_pos, text_color=GRAY)
                    else:
                        # ignore settings object with clicked index, that's handled separately
                        if i == clicked_index:
                            continue
                        settingsObjectTuples[i] = createSettingsObject(name, vertical_pos, text_color=TEXTCOLOR)

                # if clicked index is not updated, reset it to the old hotkey
                if not any_hovered and mouse_clicked and clicked_index != -1:
                    # get key, vertical position, and name of the setting
                    key = pygame.key.name(hotkeys[objectToKeyMap[clicked_index]])
                    vertical_pos = settingsObjectTuples[clicked_index][3]
                    name = settingsObjectTuples[clicked_index][2]

                    # update display for the setting (getting rid of the cursor)
                    settingsObjectTuples[clicked_index] = createSettingsObject(name.split(':')[0] + ': ' + key, vertical_pos)
                    clicked_index = -1

                updateSettingsDisplay(settingsObjectTuples)

        # update cursor state
        if cursor_visible and time.time() * 1000 - cursor_blink_time > cursor_blink_interval:
            # If the cursor is visible and the blink interval has passed, hide the cursor
            cursor_visible = False
            cursor_blink_time = time.time() * 1000
        elif not cursor_visible and time.time() * 1000 - cursor_blink_time > cursor_blink_interval:
            # If the cursor is not visible and the blink interval has passed, show the cursor
            cursor_visible = True
            cursor_blink_time = time.time() * 1000
        
        # draw the cursor if the clicked index is not -1
        if clicked_index != -1:
            if cursor_visible:
                # Draw the cursor
                settingsObjectTuples[clicked_index] = createSettingsObject(settingsObjectTuples[clicked_index][2].split(':')[0] + ':' + ' _', settingsObjectTuples[clicked_index][3], text_color=TEXTCOLOR)
            else:
                settingsObjectTuples[clicked_index] = createSettingsObject(settingsObjectTuples[clicked_index][2].split(':')[0] + ':' + ' ', settingsObjectTuples[clicked_index][3], text_color=TEXTCOLOR)
            
            updateSettingsDisplay(settingsObjectTuples)
        
        pygame.display.update()
        FPSCLOCK.tick()

def updateSettingsDisplay(settingsObjectTuples):
    '''
    updates display of settings screen

    Args:
        settingsObjectTuples (list): list of tuples containing rectangles, surfaces, positions.
    '''
    DISPLAYSURF.fill(BGCOLOR)
    createSettingsObject("Settings", 80, font_size=MEDIUMFONT)

    createSettingsObject(f"Press {pygame.key.name(hotkeys['settings'])} to play.", 425, text_color=TEXTCOLOR, font_size=BASICFONT)

    for i, (keySurf, keyRect, *_) in enumerate(settingsObjectTuples):
        DISPLAYSURF.blit(keySurf, keyRect)


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq


def getNextShape():
    '''
    #This function implements a pseudorandom "bag" distribution of piece shapes, as opposed to the previous random shapes.

    Returns: 
        shape (str): represents the shape chosen.
    '''
    global shapeBag
    #available represents the shapes that have not yet been taken (1 in shapeBag)
    available = []
    for i in range(0, len(shapeBag)):
        if shapeBag[i] == 1:
            available.append(LSPIECES[i])
    shape = random.choice(available)
    
    #update shapeBag availability
    shapeBag[LSPIECES.index(shape)] = 0
    return shape


def getNewPiece():
    # return a pseudorandom new piece in random color (derandomized rotation)
    shape = getNextShape()
    newPiece = {'shape': shape,
                'rotation': 0,
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}
    return newPiece


def holdPiece(piece):
    '''
    return the held version of a falling/held piece by resetting its rotation and position. Essentially a deep copy.

    Args:
        piece (obj): the piece to hold or unhold
    Returns: 
        heldPiece (obj): the held or unheld piece, reset to only its shape.
    '''
    shape = piece.get('shape')
    heldPiece = {'shape': shape,
                'rotation': 0,
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}
    return heldPiece


def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']


def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])


def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawPiece(piece, pixelx=None, pixely=None):
    '''
    draw the current held piece to the left of the board

    Args:
        piece (obj): the piece to draw
        pixelx: horizontal location
        pixely:vertical location
    '''
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def drawNextPiece(piece):
    '''
    draw the next piece to the right of the board

    Args:
        piece (obj): the piece to draw
    '''
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)
    
#draw the current "held" piece in the upper left side of the game screen
def drawHeldPiece(piece):
    '''
    draw the current held piece to the left of the board

    Args:
        piece (obj): the piece to draw
    '''
    # draw the "hold" text
    holdSurf = BASICFONT.render('Hold:', True, TEXTCOLOR)
    holdRect = holdSurf.get_rect()
    holdRect.topleft = (WINDOWWIDTH - 580, 80)
    DISPLAYSURF.blit(holdSurf, holdRect)
    # draw the "held" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-580, pixely=100)




if __name__ == '__main__':
    main()