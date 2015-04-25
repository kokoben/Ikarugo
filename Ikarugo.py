import pygame, sys, random, time
from pygame.locals import *

#---------------------------constants-------------------------------------
WINDOWWIDTH = 480
WINDOWHEIGHT = 768
BGCOLOR = (0, 0, 0)
TEXTCOLOR = (255, 255, 255)
MENUHIGHLIGHTCOLOR = (243, 182, 61)
FPS = 60
BLUE = (129, 250, 209)
RED = (220, 72, 72)
HEALTHBARCOLOR = (255, 88, 88)
HEALTHBARSIZE = (17, 8)
PLAYERSHIPRATE = 5
PLAYERSHIPSIZE = (20, 20)
ENEMYSHIPSIZE = (30, 30)
LARGEENEMYSHIPSIZE = (80, 80)
PLAYERPROJSIZE = (5, 20)
PLAYERPROJCOLOR = (217, 183, 246)
PLAYERPROJMOVERATE = 10
LARGEENEMYMSGTIME = 3
DEVENENEMYSHIPSIZE = (27, 36)
DEVENENEMYSHIPRATE = 3
LARGEENEMYSHIPRATE = 6
DEVENENEMYSHIPTS = 30
DEVENLARGESHIPTS = 2000
DEVENENEMYPROJSIZE = (5, 15)
LARGEENEMYPROJSIZE = (8, 20)
DEVENENEMYPROJRATE = 5
LARGEENEMYPROJRATE = 8
DEVENENEMYPROJCOLOR = (238, 125, 125)  # red
DEVENENEMYPROJCOLOR2 = (89, 195, 216)  # blue
LARGEENEMYPROJCOLOR = (243, 66, 226)
DEVENPROJFREQUENCY = 50
DEVENLARGEPROJFREQUENCY = 25
INVULNTIME = 2
SHIPCHANGETIME = 1.5  # insane mode only.
#---------------------------------------------------------------------------------
pygame.init()

# aside from constants, this is stuff that either never changes in game or needs to be mutated and/or maintained beyond the scope of each subclass.

# set up the window.
gamewinsurf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Ikarugo')

# Create health bar pieces:
healthBarPiece = pygame.Surface(HEALTHBARSIZE)
healthBarPiece.fill(HEALTHBARCOLOR)
healthBarPieceRect1 = healthBarPiece.get_rect()
healthBarPieceRect1.topleft = (10, 49)
healthBarPieceRect2 = healthBarPiece.get_rect()
healthBarPieceRect2.topleft = (34, 49)
healthBarDict1 = {'rect': healthBarPieceRect1,
                  'body': healthBarPiece}
healthBarDict2 = {'rect': healthBarPieceRect2,
                  'body': healthBarPiece}

# Create the player ship sprite and rect.
playerShip = pygame.Surface(PLAYERSHIPSIZE)
playerShip.fill(BLUE)
playerShipRect = playerShip.get_rect()

# Create enemy ship sprites.
devenEnemyShip = pygame.image.load('enemyship.jpg')
devenEnemyShip2 = pygame.image.load('enemyship2.jpg')
devenLargeShip = pygame.image.load('largeship.jpg')

# set up the framerate.
fpsAdjust = pygame.time.Clock()

# set up the font.
font = pygame.font.SysFont('helvetica', 16)
titleFont = pygame.font.SysFont(None, 72)
menuFont = pygame.font.SysFont(None, 40)

# set up player projectile.
playerProjBody = pygame.Surface(PLAYERPROJSIZE)
playerProjBody.fill(PLAYERPROJCOLOR)
playerProjRect = playerProjBody.get_rect()


# start keeping time at beginning of game. for now, its two purposes are to determine if "Press Any Key" text in intro scene is visible, and two calculate time to change ship color in insane mode.
startTime = int(time.time())
#-----------------------------functions---------------------------------
def main():
    runGame(introScene())

# player movements.
def moveUp(direction, rect, rate):
    if direction and rect.top > 0:
        rect.move_ip(0, -rate)


def moveLeft(direction, rect, rate):
    if direction and rect.left > 0:
        rect.move_ip(-rate, 0)


def moveDown(direction, rect, rate):
    if direction and rect.bottom < WINDOWHEIGHT:
        rect.move_ip(0, rate)


def moveRight(direction, rect, rate):
    if direction and rect.right < WINDOWWIDTH:
        rect.move_ip(rate, 0)


def destroyEnemyShip(eship, proj):
    for i in list(eship):
        for j in list(proj):
            if i['rect'].colliderect(j['rect']):
                eship.remove(i)
                proj.remove(j)


def delHporDestroyLargeShip(eship, proj):
    for i in eship[:]:
        for j in proj[:]:
            if i['rect'].colliderect(j['rect']):
                if i['hp'] == 1:
                    eship.remove(i)
                    proj.remove(j)
                else:
                    i['hp'] -= 1
                    proj.remove(j)


def delProjHittingPlayer(playerrect, proj):
    for i in proj[:]:
        if i['rect'].colliderect(playerrect):
            proj.remove(i)


def moveShipsDown(ship, rate):
    for i in ship[:]:
        i['rect'].move_ip(0, rate)


def moveLargeShipDown(ship, rate, direct, vertc, h, h2):
    if ship['rect'].top < 0:
        ship['rect'].move_ip(0, rate)
    elif 0 <= ship['rect'].top < 20:
        ship['rect'].move_ip(0, rate)
    else:
        if ship['rect'].left > 0 and ship['rect'].right < WINDOWWIDTH and h == [0] and vertc == []:  # determining whether to travel left or right on first "zig".  Ship keeps going in that direction until it hits first wall.
            if direct == 0:
                ship['rect'].move_ip(-rate, 0)
                if ship['rect'].left <= 0:
                    del h[0]
                    h.append(
                        1)  # h being 0 tells us that ship is still in initial stage of choosing first randomly generated direction. h is 1 means it is coming off a direction and just needs code to "push" it along.
            else:
                ship['rect'].move_ip(rate, 0)
                if ship['rect'].right >= WINDOWWIDTH:
                    del h[0]
                    h.append(1)
        elif ship['rect'].left <= 0 and vertc != [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]:  # moving down left wall.
            ship['rect'].move_ip(0, rate)
            vertc.append(1)
        elif ship['rect'].left <= 0 and vertc == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] and h == [
            1]:  # going right after moving down left wall.
            del vertc[:]
            del h2[0]
            h2.append(1)
            ship['rect'].move_ip(rate, 0)
        elif ship['rect'].right >= WINDOWWIDTH and vertc != [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]:  # moving down right wall.
            ship['rect'].move_ip(0, rate)
            vertc.append(1)
        elif ship['rect'].right >= WINDOWWIDTH and vertc == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] and h == [
            1]:  # going left after moving down right wall.
            del vertc[:]
            del h2[0]
            h2.append(0)
            ship['rect'].move_ip(-rate, 0)
        elif ship['rect'].left > 0 and ship['rect'].right < WINDOWWIDTH and h == [
            1]:  # h being true means ship has just left an edge of the screen and is in the process of traveling in a direction.
            if h2 == [1]:  # h2 tells us which side the ship is coming off of.
                ship['rect'].move_ip(rate, 0)  # continue going right.
            if h2 == [0]:
                ship['rect'].move_ip(-rate, 0)  # continue going left.

def drawText(text, font, x, y, surface):
    textbody = font.render(text, 1, TEXTCOLOR)
    textrect = textbody.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textbody, textrect)


def drawTextCenter(text, font, x, y, surface, color=TEXTCOLOR):
    textbody = font.render(text, 1, color)
    textrect = textbody.get_rect()
    textrect.center = (x, y)
    surface.blit(textbody, textrect)

def healthBarOutline(surf, x, y, width):
    pygame.draw.line(surf, (255, 255, 255), (x, y), (x + 48, y), width)  # top side
    pygame.draw.line(surf, (255, 255, 255), (x, y + 14), (x + 48, y + 14), width)  # bottom side
    pygame.draw.line(surf, (255, 255, 255), (x, y), (x, y + 14), width)  # left side
    pygame.draw.line(surf, (255, 255, 255), (x + 24, y), (x + 24, y + 14), width)  # middle
    pygame.draw.line(surf, (255, 255, 255), (x + 48, y), (x + 48, y + 14), width)  # right side

def runGame(scene1):
    activeScene = scene1

    # the infinite scene loop.
    while True:

        filteredEvents = []

        for event in pygame.event.get():
            filteredEvents.append(event)

        activeScene.processInput(filteredEvents)
        activeScene.update()

        activeScene = activeScene.next

        pygame.display.flip()
        fpsAdjust.tick(FPS)


#--------------------------Classes---------------------------------------
class enemyShip():
    def __init__(self, enemyType):
        self.enemytype = enemyType


class enemyShipNormal(enemyShip):
    def __init__(self, shiplist, rate):
        enemyShip.__init__(self, 'enemy')
        self.shiplist = shiplist
        self.rate = rate

    def addShip(self, ship, shipSize,
                shipList):  # append new normal enemy ships to enemy ship lists to spawn. each dictionary represents one enemy ship and its spawn parameters.
        transformedShip = pygame.transform.scale(ship, shipSize)
        shipRect = transformedShip.get_rect()
        shipRect.bottomleft = (random.randint(0, WINDOWWIDTH - DEVENENEMYSHIPSIZE[0]), 0)
        shipDict = {'body': transformedShip,
                    'rect': shipRect}
        shipList.append(shipDict)


class enemyShipLarge(enemyShip):
    def __init__(self, shiplist, rate, hp):
        enemyShip.__init__(self, 'largeenemy')
        self.shiplist = shiplist
        self.rate = rate
        self.hp = hp


class projectile():
    def __init__(self, poe):
        self.poe = poe


# player projectile subclass.
class pProj(projectile):
    def __init__(self, projlist, rate):
        projectile.__init__(self, 'p')
        self.projlist = projlist
        self.rate = rate


# enemy projectile subclass.
class eProj(projectile):
    def __init__(self, projlist, size, rate, freq, color):
        projectile.__init__(self, 'e')
        self.projlist = projlist
        self.size = size
        self.rate = rate
        self.freq = freq
        self.color = color
        self.body = pygame.Surface(size)
        self.body.fill(color)

    def addProj(self, ship,
                missile):  # append new enemy projectiles to missile lists. each dictionary represents one enemy missile body and its spawn parameters.
        if random.randint(0, self.freq) == 10:
            missileRect = missile.body.get_rect()
            missileRect.centerx = ship['rect'].centerx
            missileRect.top = ship['rect'].bottom
            missileDict = {'body': missile.body,
                           'rect': missileRect}
            missile.projlist.append(missileDict)


# game state (UI, i.e number of lives left, life bar, score)
class gameState():
    def __init__(self):
        self.insaneMode = False
        self.score = 0  # we want the score to reset to 0 every time the user dies and restarts the game.
        self.highScoreNormal = 0  # we want the score to NOT reset every time the user dies and/or restarts the game.
        self.highScoreInsane = 0
        self.changeShipColor = False  # default player ship color to blue.
        self.invulnerableMode = False  # default player to vulnerable.
        self.invulnerableStartTime = 0  # time marker for when player becomes struck and invulnerable in order to calculate time elapsed while invulnerable. for now, initialize to zero.
        self.invulnTime = INVULNTIME  # amount of time player is invulnerable after being struck by an enemy ship or projectile.
        self.timeToAdd = 0  # if player pauses while in invulnerable mode, time to add to invulntime after unpausing.
        self.flashIsOn = False  # determine if ship should be in mid-blink using localFlashIsOn. if localFlashIsOn, then gS.flashIsOn is on.
        self.preventChangeShipColor = False  # INSANE MODE ONLY: allow or prevent ship color from changing colors.
        self.preventStartTime = 0  #INSANE MODE ONLY: time marker for when color change prevention starts in order to calculate how much time elapsed while color change prevention is on. for now, initialize to zero.
        self.shipChangeTime = SHIPCHANGETIME  # INSANE MODE ONLY: amount of ship color prevention time after ship changes color.
        self.shipChangeTimeToAdd = 0  # INSANE MODE ONLY. amount of time to add to player's ship color prevention time after pausing and unpausing.
        self.enemyShipAddCounter = 0  # initial enemy ship counter.
        self.largeEnemyShipAddCounter = 0  # initial large enemy ship counter.
        self.cMtopM = False  # checks if user should return to main menu or pause menu from controls menu.

        # set up starting health UI at full health: 
        self.healthBarPieceList = [healthBarDict1, healthBarDict2]

        # enemy units and player/enemy projectiles to be wiped whenever they leave the screen, or whenever player returns to main menu from in-game. (so that if you start a new game, the enemies and projectiles from the previous game aren't still onscreen.)
        self.unitsToWipe = [myDuderMissile.projlist, normalShipDuders.shiplist, normalShipDuders2.shiplist,
                            largeShipDuders.shiplist, normalShipMissile.projlist, normalShipMissile2.projlist,
                            largeShipMissile.projlist]

    def wipeUnits(self, unitlist):  # wipe units on-screen upon returning to the main menu from in-game.
        for i in unitlist:
            [i.remove(j) for j in list(i)]

    def wipeOffScreenUnits(self, unitlist):  # wipe units that have flown off-screen.
        for i in unitlist:
            [i.remove(j) for j in list(i) if j['rect'].top > WINDOWHEIGHT]

    def refillHealth(self):
        [self.healthBarPieceList.remove(i) for i in list(self.healthBarPieceList)]
        self.healthBarPieceList.append(healthBarDict1)
        self.healthBarPieceList.append(healthBarDict2)

    def applyPostPauseInvulnTime(self):
        if self.invulnerableMode:
            self.invulnTime = self.timeToAdd
            self.invulnerableStartTime = time.time()

    def applyPostPauseColorChangePreventTime(self):
        if self.preventChangeShipColor:
            self.shipChangeTime = self.shipChangeTimeToAdd
            self.preventStartTime = time.time()

    def resetGameState(self):
        # reset score.
        self.score = 0
        # refill health bar.
        self.refillHealth()
        # wipe units from screen.
        self.wipeUnits(gS.unitsToWipe)
        # turn invulnerable mode off.
        self.invulnerableMode = False
        # turn sprite flash off.
        self.flashIsOn = False
        # reset invulntime
        self.invulnTime = INVULNTIME
        # reset normal ship spawn counter.
        gS.enemyShipAddCounter = 0
        # reset large ship spawn counter.
        gS.largeEnemyShipAddCounter = 0
        # move ship back to starting location.
        playerShipRect.center = ((WINDOWWIDTH / 2), (WINDOWHEIGHT - 25))
        self.changeShipColor = False  # default player ship color back to blue.
        # for insane mode, set ship color changing flat back to false in case it was set to true at point of ending last session.
        self.preventChangeShipColor = False
        # for insane mode, reset ship color prevention time.
        self.shipChangeTime = SHIPCHANGETIME


# scene handlers.
class sceneBase():
    def __init__(self):
        self.next = self

    def processInput(self, events):
        print('overriding in subclasses')

    def update(self):
        print('overriding in subclasses')

    def switchToScene(self, next_scene):  # aka self.next becomes the new object instance held by the variable.
        self.next = next_scene

    def terminate(self):
        self.switchToScene(None)


class introScene(sceneBase):  # "press any key" screen.

    def __init__(self):
        sceneBase.__init__(self)
        self.pressedKey = False

    def processInput(self, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    self.pressedKey = True
            if event.type == MOUSEBUTTONDOWN:
                self.pressedKey = True

    def update(self):
        # make the mouse cursor visible.
        pygame.mouse.set_visible(True)

        # the time during this particular frame of the intro screen. used to determine whether the "Press any Key" text is visible.
        introScreenTime = int(time.time())

        # location of ship during intro screen.
        playerShipRect.center = ((WINDOWWIDTH / 2), (WINDOWHEIGHT - 25))

        gamewinsurf.fill(BGCOLOR)
        drawTextCenter('IKARUGO', titleFont, WINDOWWIDTH / 2, WINDOWHEIGHT / 4, gamewinsurf, PLAYERPROJCOLOR)
        if (introScreenTime - startTime) % 2 == 0:
            drawTextCenter('Hey duder! Press any key!', font, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 3) / 4), gamewinsurf)

        gamewinsurf.blit(playerShip, playerShipRect)

        if self.pressedKey:
            self.switchToScene(mainMenuScene())


class mainMenu():
    def __init__(self, optionslist):
        self.optionslist = optionslist
        self.option_to_highlight = 0  # highlight flag. used in highlightoption method for mouse but also later used for keyboard highlighting.
        # flag ensuring that exiting the controls menu while in game returns the player to the pause menu, rather than the main menu.
        gS.cMtopM = False

    def addOption(self, option, txtcolor, x, y):  # option = string for item text
        menuitemobj = menuFont.render(option, 1, txtcolor)
        menuitemrect = menuitemobj.get_rect()
        menuitemrect.center = (x, y)
        self.optionslist.append({'menuitem': menuitemobj,
                                 'menurect': menuitemrect,
                                 'menuitemcolor': txtcolor,
                                 'menuitemname': option})

    def highlightOption(self):

        # detect mousing over of option and assign it to the highlight flag. give all other options not moused over the regular text color.
        # keyboard strokes are handled in processinput method but also assign to this flag.
        i = 0
        while i < len(self.optionslist):
            if self.optionslist[i]['menurect'].collidepoint(pygame.mouse.get_pos()):
                self.option_to_highlight = i
            else:
                self.optionslist[i]['menuitemcolor'] = TEXTCOLOR
            i += 1

        # give appropriate menu option the highlight color.
        self.optionslist[self.option_to_highlight]['menuitemcolor'] = MENUHIGHLIGHTCOLOR

        # updating font colors of menu item objects to reflect highlighted option.
        for i in self.optionslist:
            changedgMFontObj = menuFont.render(i['menuitemname'], 1, i['menuitemcolor'])
            i['menuitem'] = changedgMFontObj


class mainMenuScene(sceneBase):  # the main menu

    def __init__(self):
        sceneBase.__init__(self)
        # set up main menu objects using mainMenu class. (class within a class...)
        self.mM = mainMenu([])
        self.mM.addOption('Normal', MENUHIGHLIGHTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 3) / 4) - 30)
        self.mM.addOption('INSANE!!!', TEXTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 3) / 4))
        self.mM.addOption('Controls', TEXTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 3) / 4) + 30)
        self.mM.addOption('Credits', TEXTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 3) / 4) + 60)
        self.mM.addOption('Exit Game', TEXTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 3) / 4) + 90)

    def selectOption(self, option):
        if option['menuitemname'] == 'Normal':
            gS.insaneMode = False
            gS.score = 0
            pygame.mouse.set_visible(False)
            pygame.mouse.set_pos(playerShipRect.centerx, playerShipRect.centery)
            self.switchToScene(mainGameScene())
        elif option['menuitemname'] == 'INSANE!!!':
            gS.insaneMode = True
            gS.score = 0
            pygame.mouse.set_visible(False)
            pygame.mouse.set_pos(playerShipRect.centerx, playerShipRect.centery)
            self.switchToScene(mainGameScene())
        elif option['menuitemname'] == 'Controls':
            self.switchToScene(controlsMenuScene())
        elif option['menuitemname'] == 'Credits':
            self.switchToScene(creditsScene())
        elif option['menuitemname'] == 'Exit Game':
            pygame.quit()
            sys.exit()

    def processInput(self, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == ord('s') or event.key == K_DOWN:
                    i = 0
                    while i < len(self.mM.optionslist):
                        if self.mM.optionslist[i]['menuitemcolor'] == MENUHIGHLIGHTCOLOR and i < len(
                                self.mM.optionslist) - 1:  # for example, if you are at index 2 in a menu containing 3 options, that means you're at the last option and can't proceed furt
                            self.mM.option_to_highlight = i + 1
                            break
                        i += 1
                if event.key == ord('w') or event.key == K_UP:
                    i = 0
                    while i < len(self.mM.optionslist):
                        if self.mM.optionslist[i][
                            'menuitemcolor'] == MENUHIGHLIGHTCOLOR and i > 0:  # same as when player presses down but the opposite; don't want to go up when you can't anymore.
                            self.mM.option_to_highlight = i - 1
                        i += 1
                if event.key == K_RETURN:
                    for option in self.mM.optionslist:
                        if option['menuitemcolor'] == MENUHIGHLIGHTCOLOR:
                            self.selectOption(option)
            # allow user to click on menu options to select them.
            if event.type == MOUSEBUTTONDOWN:
                for option in self.mM.optionslist:
                    if option['menurect'].collidepoint(pygame.mouse.get_pos()):
                        if event.button == 1:
                            self.selectOption(option)

        self.mM.highlightOption()

    def update(self):
        # main menu ship location and color.
        playerShipRect.center = ((WINDOWWIDTH / 2), (WINDOWHEIGHT - 25))
        playerShip.fill(BLUE)

        gamewinsurf.fill(BGCOLOR)
        drawTextCenter('IKARUGO', titleFont, WINDOWWIDTH / 2, WINDOWHEIGHT / 4, gamewinsurf, PLAYERPROJCOLOR)
        for i in self.mM.optionslist:
            gamewinsurf.blit(i['menuitem'], i['menurect'])
        gamewinsurf.blit(playerShip, playerShipRect)


class pauseMenu():
    def __init__(self, optionslist):
        self.optionslist = optionslist
        self.option_to_highlight = 0

    def addOption(self, option, txtcolor, x, y):  # centers the line at the specified coordinate.
        menuitemobj = menuFont.render(option, 1, txtcolor)
        menuitemrect = menuitemobj.get_rect()
        menuitemrect.center = (x, y)
        self.optionslist.append({'menuitem': menuitemobj,
                                 'menurect': menuitemrect,
                                 'menuitemcolor': txtcolor,
                                 'menuitemname': option})

    def dim(self, surface):
        surface.set_colorkey(BGCOLOR)
        surface.fill(BGCOLOR)

    def highlightOption(self):
        # detect if option is moused over and assign its index to the highlight flag.  give all other options not moused over the regular text color.
        # keyboard strokes are handled in processinput method but also assign to this flag.
        i = 0
        while i < len(self.optionslist):
            if self.optionslist[i]['menurect'].collidepoint(pygame.mouse.get_pos()):
                self.option_to_highlight = i
            else:
                self.optionslist[i]['menuitemcolor'] = TEXTCOLOR
            i += 1

        # give appropriate menu option the highlight color.
        self.optionslist[self.option_to_highlight]['menuitemcolor'] = MENUHIGHLIGHTCOLOR

        # updating font colors of menu item objects to reflect highlighted option.
        for i in self.optionslist:
            changedgMFontObj = menuFont.render(i['menuitemname'], 1, i['menuitemcolor'])
            i['menuitem'] = changedgMFontObj


class pauseMenuScene(sceneBase):  # the pause menu.

    def __init__(self):
        sceneBase.__init__(self)

        # set up pause menu objects.
        self.pM = pauseMenu([])
        self.pM.addOption('Resume Game', MENUHIGHLIGHTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 2) / 3))
        self.pM.addOption('Main Menu', TEXTCOLOR, WINDOWWIDTH / 2, (((WINDOWHEIGHT * 2) / 3) + 30))
        self.pM.addOption('Controls', TEXTCOLOR, WINDOWWIDTH / 2, (((WINDOWHEIGHT * 2) / 3) + 60))
        self.pM.addOption('Exit Game', TEXTCOLOR, WINDOWWIDTH / 2, (((WINDOWHEIGHT * 2) / 3) + 90))

    def selectOption(self, option):

        if option['menuitemname'] == 'Resume Game':
            pygame.mouse.set_visible(False)
            pygame.mouse.set_pos(playerShipRect.centerx, playerShipRect.centery)
            # if player was invulnerable before pausing, set new invulntime and invulnerableStartTime.
            gS.applyPostPauseInvulnTime()
            # switch to post-pause ship color prevention time (works like invulnerable flash time adder).
            gS.applyPostPauseColorChangePreventTime()
            self.switchToScene(mainGameScene())
        elif option['menuitemname'] == 'Controls':
            gS.cMtopM = True
            # switch to control settings scene.
            self.switchToScene(controlsMenuScene())
        elif option['menuitemname'] == 'Main Menu':
            gS.resetGameState()
            self.switchToScene(mainMenuScene())
        elif option['menuitemname'] == 'Exit Game':
            pygame.quit()
            sys.exit()

    def unpause(self):
        pygame.mouse.set_visible(False)
        pygame.mouse.set_pos(playerShipRect.centerx, playerShipRect.centery)
        # if player was invulnerable before pausing, set new invulntime and invulnerableStartTime.
        gS.applyPostPauseInvulnTime()
        # if ship color prevention prior to pausing, switch to post-pause ship color prevention time (works like invulnerable flash time adder).
        gS.applyPostPauseColorChangePreventTime()
        self.switchToScene(mainGameScene())

    def processInput(self, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == daControls.moves['Back'][0]:
                    self.unpause()
                if event.key == daControls.moves['Down'][0] or event.key == daControls.moves['Down'][1]:
                    i = 0
                    while i < len(self.pM.optionslist):
                        if self.pM.optionslist[i]['menuitemcolor'] == MENUHIGHLIGHTCOLOR and i < len(
                                self.pM.optionslist) - 1:  # for example, if you are at index 2 in a menu containing 3 options, that means you're at the last option and can't proceed furt
                            self.pM.option_to_highlight = i + 1
                            break
                        i += 1
                if event.key == daControls.moves['Up'][0] or event.key == daControls.moves['Up'][1]:
                    i = 0
                    while i < len(self.pM.optionslist):
                        if self.pM.optionslist[i][
                            'menuitemcolor'] == MENUHIGHLIGHTCOLOR and i > 0:  # same as when player presses down but the opposite; don't want to go up when you can't anymore.
                            self.pM.option_to_highlight = i - 1
                        i += 1
                # pressing the Select key while an option is highlighted with the mouse selects that option and triggers the appropriate behavior.       
                if event.key == daControls.moves['Select'][0]:
                    for option in self.pM.optionslist:
                        if option['menuitemcolor'] == MENUHIGHLIGHTCOLOR:
                            self.selectOption(option)

            # clicking the Select button while an option is highlighted with the mouse selects that option and triggers the appropriate behavior.
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for option in self.pM.optionslist:
                        if option['menurect'].collidepoint(pygame.mouse.get_pos()):
                            self.selectOption(option)

                # SAME AS KEYDOWN EVENTS BUT FOR MOUSEBUTTON DOWN.
                elif event.button == daControls.moves['Back'][0] and daControls.moves['Back'][0] != 1:
                    self.unpause()
                elif event.button == daControls.moves['Back'][0] and daControls.moves['Back'][
                    0] == 1:  # EXCEPTION: If Back is mapped to Mouse 1, unlike with other keys, have Mouse 1 just select the option rather than go back when clicking on option.
                    for option in self.pM.optionslist:
                        if not option['menurect'].collidepoint(pygame.mouse.get_pos()):
                            self.unpause()
                elif event.button == daControls.moves['Down'][0] or event.button == daControls.moves['Down'][1]:
                    i = 0
                    while i < len(self.pM.optionslist):
                        if self.pM.optionslist[i]['menuitemcolor'] == MENUHIGHLIGHTCOLOR and i < len(
                                self.pM.optionslist) - 1:  # for example, if you are at index 2 in a menu containing 3 options, that means you're at the last option and can't proceed furt
                            self.pM.option_to_highlight = i + 1
                            break
                        i += 1
                elif event.button == daControls.moves['Up'][0] or event.button == daControls.moves['Up'][1]:
                    i = 0
                    while i < len(self.pM.optionslist):
                        if self.pM.optionslist[i][
                            'menuitemcolor'] == MENUHIGHLIGHTCOLOR and i > 0:  # same as when player presses down but the opposite; don't want to go up when you can't anymore.
                            self.pM.option_to_highlight = i - 1
                        i += 1

        self.pM.highlightOption()

    def update(self):
        self.pM.dim(gamewinsurf)

        # update font objects to reflect which menu options are highlighted and which are not. works like main menu.
        for i in self.pM.optionslist:
            changedpMFontObject = menuFont.render(i['menuitemname'], 1, i['menuitemcolor'])
            i['menuitem'] = changedpMFontObject

        # draw UI state at time of pause using either normal or insane mode high score, depending on which mode player has chosen. also update high scores.
        drawText('Score: %s' % (gS.score), font, 5, 5, gamewinsurf)
        if not gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreNormal), font, 5, 23, gamewinsurf)
        elif gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreInsane), font, 5, 23, gamewinsurf)

        # draw health UI at time of pause.
        healthBarOutline(gamewinsurf, 6, 45, 1)
        [gamewinsurf.blit(i['body'], i['rect']) for i in gS.healthBarPieceList]

        # if localFlashIsOn is true, then gS.flashIsOn is also true to keep ship in blinking state while paused.
        if not (gS.invulnerableMode and gS.flashIsOn):
            gamewinsurf.blit(playerShip, playerShipRect)

        # blit enemy ships, player projectiles, enemy projectiles at time of pause.        
        for i in [normalShipDuders.shiplist, normalShipDuders2.shiplist, largeShipDuders.shiplist,
                  myDuderMissile.projlist, normalShipMissile.projlist, normalShipMissile2.projlist,
                  largeShipMissile.projlist]:
            [gamewinsurf.blit(j['body'], j['rect']) for j in i]

        drawTextCenter('Paused', menuFont, WINDOWWIDTH / 2, (WINDOWHEIGHT / 2) - 80, gamewinsurf)

        # blit menu options.
        for i in self.pM.optionslist:
            gamewinsurf.blit(i['menuitem'], i['menurect'])


class controls():
    def __init__(self):
        # flag for flashing a selected slot.
        self.flashIsOn = False
        # accompanying flash counter.
        self.flashCounter = 0
        # accompanying flash visible flag.
        self.flashIsVisible = False
        # slot to remap. will be a dict from controls_options_list
        self.moveToRemap = None
        # key in setControls whose value needs to be remapped. used in remap method.
        self.setControls_keytochange = ''
        # index reflecting whether it's the primary or secondary move key we want to change.
        self.setControls_indextochange = None
        # slotrect to flash
        self.slotRectToFlash = None
        self.setControls_newmovekey = ''
        # strings list for reference in next two lists below it in their functions. 
        self.controls_strings_list = []
        # text, slots, and slot outlines to blit in blitControlsAndSlot.
        self.controls_options_list = []
        # default controls strings. move --> displayed key string.
        self.setControls = {'Up': ['W', u'\u2191'],
                            'Down': ['S', u'\u2193'],
                            'Left': ['A', u'\u2190'],
                            'Right': ['D', u'\u2192'],
                            'Shoot': ['Mouse 1'],
                            'Color Swap': ['Space'],
                            'Select': ['Enter'],
                            'Back': ['Esc']}
        # default controls mappings. move --> key event.
        self.moves = {'Up': [K_w, K_UP],
                      'Down': [K_s, K_DOWN],
                      'Left': [K_a, K_LEFT],
                      'Right': [K_d, K_RIGHT],
                      'Shoot': [1],
                      'Color Swap': [K_SPACE],
                      'Select': [K_RETURN],
                      'Back': [K_ESCAPE]}
        # key mappings to blit in blitKeys. each item in list contains a textbody, textrect, and if there are secondary keys, textbody2, and textrect2.
        self.controls_keys_list = []
        self.bank = {'Esc': K_ESCAPE, 'F1': K_F1, 'F2': K_F2, 'F3': K_F3, 'F4': K_F4, 'F5': K_F5, 'F6': K_F6,
                     'F7': K_F7, 'F8': K_F8, 'F9': K_F9, 'F12': K_F12, 'Prt Scrn': K_PRINT, 'Scrllock': K_SCROLLOCK,
                     'Pause': K_PAUSE,
                     '`': K_BACKQUOTE, '1': K_1, '2': K_2, '3': K_3, '4': K_4, '5': K_5, '6': K_6, '7': K_7, '8': K_8,
                     '9': K_9, '0': K_0, '-': K_MINUS, '=': K_EQUALS, 'Back': K_BACKSPACE, 'Ins': K_INSERT,
                     'Home': K_HOME, 'Pg Up': K_PAGEUP, 'Numlock': K_NUMLOCK, '/': K_KP_DIVIDE, '*': K_KP_MULTIPLY,
                     '-': K_KP_MINUS,
                     'Tab': K_TAB, 'Q': K_q, 'W': K_w, 'E': K_e, 'R': K_r, 'T': K_t, 'Y': K_y, 'U': K_u, 'I': K_i,
                     'O': K_o, 'P': K_p, '[': K_LEFTBRACKET, ']': K_RIGHTBRACKET, '\\': K_BACKSLASH, 'Del': K_DELETE,
                     'End': K_END, 'Pg Dwn': K_PAGEDOWN, 'Num 7': K_KP7, 'Num 8': K_KP8, 'Num 9': K_KP9, '+': K_KP_PLUS,
                     'Capslock': K_CAPSLOCK, 'A': K_a, 'S': K_s, 'D': K_d, 'F': K_f, 'G': K_g, 'H': K_h, 'J': K_j,
                     'K': K_k, 'L': K_l, ';': K_SEMICOLON, "'": K_QUOTE, 'Enter': K_RETURN, 'Num 4': K_KP4,
                     'Num 5': K_KP5, 'Num 6': K_KP6,
                     'L Shift': K_LSHIFT, 'Z': K_z, 'X': K_x, 'C': K_c, 'V': K_v, 'B': K_b, 'N': K_n, 'M': K_m,
                     ',': K_COMMA, ' . ': K_PERIOD, '/': K_SLASH, 'R Shift': K_RSHIFT, u'\u2191': K_UP, 'Num 1': K_KP1,
                     'Num 2': K_KP2, 'Num 3': K_KP3, 'Num Ent': K_KP_ENTER,
                     'L Ctrl': K_LCTRL, 'L Win': K_LSUPER, 'L Alt': K_LALT, 'Space': K_SPACE, 'R Alt': K_RALT,
                     'R Win': K_RSUPER, 'Menu': K_MENU, 'R Ctrl': K_RCTRL, u'\u2190': K_LEFT, u'\u2193': K_DOWN,
                     u'\u2192': K_RIGHT, 'Num 0': K_KP0, '.': K_KP_PERIOD,
                     'Mouse 1': 1, 'Mouse 2': 2, 'Mouse 3': 3}

    def addOptions(self, font_color, slot_size, slot_color, x, y, slot_rightx,
                   surface):  # includes option text and slot and rects for both. for column 1, which will most likely be the only column. x = left coordinate. y = top coordinate of first control in list.
        for name in self.controls_strings_list:
            textbody = font.render(name + ':', 1, font_color)
            textrect = textbody.get_rect()
            textrect.left = x
            textrect.top = y + 30 * self.controls_strings_list.index(name)
            move_slot = pygame.Surface(slot_size)
            move_slot.fill(slot_color)
            move_slot_rect = move_slot.get_rect()
            move_slot_rect.right = slot_rightx
            move_slot_rect.centery = textrect.centery
            self.controls_options_list.append({'body': textbody,
                                               'textrect': textrect,
                                               'slotbody': move_slot,
                                               'slotrect': move_slot_rect,
                                               'name': name})

            # if control has two input options, add a second move slot in second column.
            if name not in ['Shoot', 'Color Swap', 'Select', 'Back']:
                move_slot2 = pygame.Surface(slot_size)
                move_slot2.fill(slot_color)
                move_slot2_rect = move_slot2.get_rect()
                move_slot2_rect.right = slot_rightx + slot_size[0] + 10
                move_slot2_rect.centery = textrect.centery
                # add the additional keys to the existing dict items. use strings list to identify the correct index.
                self.controls_options_list[self.controls_strings_list.index(name)]['body2'] = move_slot2
                self.controls_options_list[self.controls_strings_list.index(name)]['slotrect2'] = move_slot2_rect


    def blitControlsAndSlot(self, surface):  # blit text, slot, second slot, and slot outline.
        for i in self.controls_options_list:
            surface.blit(i['body'], i['textrect'])
            surface.blit(i['slotbody'], i['slotrect'])
            pygame.draw.rect(gamewinsurf, (255, 255, 255), i['slotrect'], 1)
            # check if there exists a second slot rect key in the dictionary.  if so, blit the second slot and outline.
            if 'slotrect2' in i:
                surface.blit(i['body2'], i['slotrect2'])
                pygame.draw.rect(gamewinsurf, (255, 255, 255), i['slotrect2'], 1)

    def addKeyText(self):  # filling in controls_keys_list.
        # primary controls (first column)
        for i in self.controls_options_list:
            keytextbody = font.render(self.setControls[i['name']][0], 1,
                                      TEXTCOLOR)  # use index zero here to blit the primary key, in case the control has a secondary key.
            keytextrect = keytextbody.get_rect()
            # center text inside of move slot using list index.
            keytextrect.center = i['slotrect'].center
            self.controls_keys_list.append({'textbody': keytextbody,
                                            'textrect': keytextrect,
                                            'textname': i[
                                                'name']})  # the name is needed as a way of referencing the right dict in replaceKeyText.
            # for controls that have a secondary key (check for index), create a dict item for that key (second column).
            if 'slotrect2' in i:
                keytextbody2 = font.render(self.setControls[i['name']][1], 1,
                                           TEXTCOLOR)  # use index 1 to blit secondary key.
                keytextrect2 = keytextbody.get_rect()
                keytextrect2.center = i['slotrect2'].center
                # add the additional keys to the existing dict items. again, use controls_strings_list to identify the correct index.
                self.controls_keys_list[self.controls_strings_list.index(i['name'])]['textbody2'] = keytextbody2
                self.controls_keys_list[self.controls_strings_list.index(i['name'])]['textrect2'] = keytextrect2

    def blitKeys(self, surface):
        for i in self.controls_keys_list:
            surface.blit(i['textbody'], i['textrect'])
            if 'textrect2' in i:
                surface.blit(i['textbody2'], i['textrect2'])


    def highlightSlot(self,
                      highlight_color):  # highlights move slot (make sure it's the same size as slot in blitControlandSlot) with yellow outline if mouse is positioned over it.
        # check to see if a slot is already selected.  if one is, then don't highlight slots. otherwise, proceed.
        if not self.flashIsOn:
            for option in self.controls_options_list:
                if option['slotrect'].collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(gamewinsurf, MENUHIGHLIGHTCOLOR, option['slotrect'], 2)
                if 'slotrect2' in option:
                    if option['slotrect2'].collidepoint(pygame.mouse.get_pos()):
                        pygame.draw.rect(gamewinsurf, MENUHIGHLIGHTCOLOR, option['slotrect2'], 2)

    def remap(self, move_value):  # move value is a keydown event. possibly can also be a mouse click event later?
        # will be used in the event handler (all the key presses). key = keypress event. will iterate over all keys in controls.bank.

        rectforblankkey = None

        # see if the move_value exists anywhere else and unmap it from that move.
        for keystring in list(self.moves):
            # check primary slots.
            if self.moves[keystring][0] == move_value:
                self.moves[keystring][0] = None
            # check secondary slots
            if len(self.moves[keystring]) == 2:
                if self.moves[keystring][1] == move_value:
                    self.moves[keystring][1] = None

        self.moves[self.setControls_keytochange][self.setControls_indextochange] = move_value

        for keystring in list(
                self.bank):  # in self.bank, identify the key for the string to change to. This key will actually be used as a KEY.
            if self.bank[keystring] == move_value:
                self.setControls_newmovekey = keystring  # store string in a variable, to be identified as a KEY.

        # if the key string is already mapped to another move, change it to blank string before mapping the new move string. rewrite appropriate dict items for controls_keys_list.
        for keystring in list(self.setControls):
            # check primary slots.
            if self.setControls[keystring][0] == self.setControls_newmovekey:
                self.setControls[keystring][0] = ''
                for i in self.controls_options_list:
                    if i['name'] == keystring:
                        rectforblankkey = i['slotrect']
                keytextbody = font.render(self.setControls[keystring][0], 1, TEXTCOLOR)
                keytextrect = keytextbody.get_rect()
                keytextrect.center = rectforblankkey.center
                for j in self.controls_keys_list:
                    if j['textname'] == keystring:
                        j['textbody'] = keytextbody
                        j['textrect'] = keytextrect
            # check secondary slots.
            if len(self.setControls[keystring]) == 2:
                if self.setControls[keystring][1] == self.setControls_newmovekey:
                    self.setControls[keystring][1] = ''
                    for i in self.controls_options_list:
                        if i['name'] == keystring:
                            rectforblankkey = i['slotrect2']
                    keytextbody = font.render(self.setControls[keystring][1], 1, TEXTCOLOR)
                    keytextrect = keytextbody.get_rect()
                    keytextrect.center = rectforblankkey.center
                    for j in self.controls_keys_list:
                        if j['textname'] == keystring:
                            j['textbody2'] = keytextbody
                            j['textrect2'] = keytextrect

        # set new move string.        
        self.setControls[self.setControls_keytochange][
            self.setControls_indextochange] = self.setControls_newmovekey  # replace the old string value identified using the movekey KEY with the new STRING value in newkeystring.

        # map new move string, rewriting the appropriate dict items for controls_keys_list.
        if self.setControls_indextochange == 0:  # if remapping a primary key.
            # redefine the body and rect.
            for i in self.controls_options_list:
                if i['name'] == self.setControls_keytochange:
                    keytextbody = font.render(self.setControls[i['name']][0], 1, TEXTCOLOR)
                    keytextrect = keytextbody.get_rect()
                    keytextrect.center = i['slotrect'].center
                    # replace old with new. identify the correct dict item using its name key.
                    for j in self.controls_keys_list:
                        if j['textname'] == self.setControls_keytochange:
                            j['textbody'] = keytextbody
                            j['textrect'] = keytextrect

        elif self.setControls_indextochange == 1:  # if remapping a secondary key.
            # redefine the body and rect.
            for i in self.controls_options_list:
                if i['name'] == self.setControls_keytochange:
                    keytextbody2 = font.render(self.setControls[i['name']][1], 1, TEXTCOLOR)
                    keytextrect2 = keytextbody2.get_rect()
                    keytextrect2.center = i['slotrect2'].center
                    # again, replace old with new.
                    for j in self.controls_keys_list:
                        if j['textname'] == self.setControls_keytochange:
                            j['textbody2'] = keytextbody2
                            j['textrect2'] = keytextrect2
        self.flashIsOn = False
        self.flashIsVisible = False

    def resetToDefault(self):  # resets key mappings to defaults.
        # redefine map strings to their defaults.

        self.setControls['Up'][0], self.setControls['Up'][1] = 'W', u'\u2191'
        self.setControls['Down'][0], self.setControls['Down'][1] = 'S', u'\u2193'
        self.setControls['Left'][0], self.setControls['Left'][1] = 'A', u'\u2190'
        self.setControls['Right'][0], self.setControls['Right'][1] = 'D', u'\u2192'
        self.setControls['Shoot'][0] = 'Mouse 1'
        self.setControls['Color Swap'][0] = 'Space'
        self.setControls['Select'][0] = 'Enter'
        self.setControls['Back'][0] = 'Esc'

        self.moves['Up'][0], self.moves['Up'][1] = K_w, K_UP
        self.moves['Down'][0], self.moves['Down'][1] = K_s, K_DOWN
        self.moves['Left'][0], self.moves['Left'][1] = K_a, K_LEFT
        self.moves['Right'][0], self.moves['Right'][1] = K_d, K_RIGHT
        self.moves['Shoot'][0] = 1
        self.moves['Color Swap'][0] = K_SPACE
        self.moves['Select'][0] = K_RETURN
        self.moves['Back'][0] = K_ESCAPE

        del self.controls_keys_list[:]
        self.addKeyText()


class controlsMenuScene(sceneBase):
    def __init__(self):
        sceneBase.__init__(self)
        # the Reset button.
        self.resetoptiontextbody = pygame.font.SysFont('helvetica', 22).render('Reset', 1, (255, 255, 255))
        self.resetoptiontextrect = self.resetoptiontextbody.get_rect()
        self.resetoptiontextrect.centerx = WINDOWWIDTH / 2
        self.resetoptiontextrect.y = ((3 / 4) * WINDOWHEIGHT) - 180
        # another body for when highlighted.
        self.resetoptiontextbodyH = pygame.font.SysFont('helvetica', 22).render('Reset', 1, MENUHIGHLIGHTCOLOR)
        # the Back button.
        self.backoptiontextbody = pygame.font.SysFont('helvetica', 22).render('Back', 1, (255, 255, 255))
        self.backoptiontextrect = self.backoptiontextbody.get_rect()
        self.backoptiontextrect.centerx = WINDOWWIDTH / 2
        self.backoptiontextrect.y = self.resetoptiontextrect.y + 30
        # another body for when highlighted.
        self.backoptiontextbodyH = pygame.font.SysFont('helvetica', 22).render('Back', 1, MENUHIGHLIGHTCOLOR)

    def processInput(self, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if daControls.flashIsOn:
                    for i in daControls.bank.values():
                        if event.key == i:
                            daControls.key_pressed = i
                            daControls.remap(daControls.key_pressed)
                elif not daControls.flashIsOn:
                    if event.key == daControls.moves['Back'][0]:
                        # if cMtopM is false, return player to main menu. if true, return player to pause menu. cMtopM is set to False wheenver player returns to main menuc, and to true whenever player enters controls menu from pause menu.
                        if gS.cMtopM:
                            self.switchToScene(pauseMenuScene())
                        else:
                            self.switchToScene(mainMenuScene())
                    elif event.key == daControls.moves['Select'][0]:
                        # if mouse is highlighting Reset button.
                        if self.resetoptiontextrect.collidepoint(pygame.mouse.get_pos()):
                            daControls.resetToDefault()
                        # if mouse is highlighting Back button.
                        elif self.backoptiontextrect.collidepoint(pygame.mouse.get_pos()):
                            if gS.cMtopM:
                                self.switchToScene(pauseMenuScene())
                            else:
                                self.switchToScene(mainMenuScene())
            elif event.type == MOUSEBUTTONDOWN:
                if not daControls.flashIsOn:

                    if event.button == 1:
                        # if mouse is highlighting Reset button.
                        if self.resetoptiontextrect.collidepoint(pygame.mouse.get_pos()):
                            daControls.resetToDefault()
                            return
                        # iterate over slot rects, checking if mouse clicks each one.  if so, set flashIsOn gate to True and start incrementing flashCounter.  Set flashIsVisible counter to true/false when counter threshold is met, then rest counter.
                        for i in daControls.controls_options_list:
                            if i['slotrect'].collidepoint(pygame.mouse.get_pos()):
                                # if flashIsOn is True, flashCounter increments in main loop.
                                daControls.slotRectToFlash = i['slotrect']
                                daControls.moveToRemap = daControls.setControls[i['name']][
                                    0]  # a key within a key...omg. and the primary key index...omg. gives primary move event.  first value in key.
                                daControls.setControls_keytochange = i['name']
                                daControls.setControls_indextochange = 0
                                daControls.flashIsOn = True
                                return
                            # check secondary slots, too.
                            elif 'slotrect2' in i:
                                if i['slotrect2'].collidepoint(pygame.mouse.get_pos()):
                                    daControls.slotRectToFlash = i['slotrect2']
                                    daControls.moveToRemap = daControls.setControls[i['name']][
                                        1]  # a key within a key, and then the secondary key index...omg. gives secondary move event. second value in key.
                                    daControls.setControls_keytochange = i['name']
                                    daControls.setControls_indextochange = 1
                                    daControls.flashIsOn = True
                                    return
                        # if mouse is highlighting Back button.
                        if self.backoptiontextrect.collidepoint(pygame.mouse.get_pos()):
                            if gS.cMtopM:
                                self.switchToScene(pauseMenuScene())
                            else:
                                self.switchToScene(mainMenuScene())

                    # if Back move is mapped to a mouse button then you return to the previous menu.

                    if event.button == daControls.moves['Back'][0]:
                        if gS.cMtopM:
                            self.switchToScene(pauseMenuScene())
                        else:
                            self.switchToScene(mainMenuScene())


                elif daControls.flashIsOn:
                    if event.button == 1 or event.button == 2 or event.button == 3:
                        daControls.key_pressed = event.button
                        daControls.remap(daControls.key_pressed)


    def update(self):
        # flashing mechanic that occurs when you click on a slot to remap the key.
        if daControls.flashIsOn:
            if daControls.flashCounter < 20:
                daControls.flashCounter += 1
            else:
                # switch flashIsVisible flag when counter reaches threshold.
                daControls.flashIsVisible = not daControls.flashIsVisible
                daControls.flashCounter = 0

        gamewinsurf.fill(BGCOLOR)
        drawTextCenter('Controls', menuFont, WINDOWWIDTH / 2, 70, gamewinsurf)
        daControls.blitControlsAndSlot(gamewinsurf)
        daControls.blitKeys(gamewinsurf)
        # blit reset button using font color that depends on if mouse is highlighting the button.
        if self.resetoptiontextrect.collidepoint(pygame.mouse.get_pos()):
            gamewinsurf.blit(self.resetoptiontextbodyH, self.resetoptiontextrect)
        else:
            gamewinsurf.blit(self.resetoptiontextbody, self.resetoptiontextrect)
        # blit back button using font color that depends on if mouse is highlighting the button.
        if self.backoptiontextrect.collidepoint(pygame.mouse.get_pos()):
            gamewinsurf.blit(self.backoptiontextbodyH, self.backoptiontextrect)
        else:
            gamewinsurf.blit(self.backoptiontextbody, self.backoptiontextrect)

        daControls.highlightSlot(MENUHIGHLIGHTCOLOR)

        if daControls.flashIsOn and daControls.flashIsVisible:
            pygame.draw.rect(gamewinsurf, MENUHIGHLIGHTCOLOR, daControls.slotRectToFlash, 2)


class credits():
    def __init__(self, move_rate, speed_up_rate):
        self.credits_strings_list = []  # only containts strings.
        self.credits_list = []  # turns each string in credits_string_list into a rect + body dict unit.
        self.threshold = 20  # interval at which to blit credits.
        self.counter = 0  # counts down interval.
        self.position = 0  # marks which line in credits to blit.
        self.move_rate = move_rate  # the speed at which credits roll.
        self.speed_up_rate = speed_up_rate
        self.optionslist = []

    def addCredit(self,
                  line):  # adds a line of credit from credits_strings_list as a body + rect dict unit to credits_list. rect spawns just below bottom center.
        textbody = font.render(line, 1, TEXTCOLOR)
        textrect = textbody.get_rect()
        textrect.centerx = WINDOWWIDTH / 2
        textrect.top = WINDOWHEIGHT
        self.credits_list.append({'body': textbody,
                                  'rect': textrect})

    def moveCredits(self):
        for line in self.credits_list:
            line['rect'].move_ip(0, -self.move_rate)

    def displayCredits(self, surface):
        for line in self.credits_list:
            surface.blit(line['body'], [line['rect'][0], line['rect'][1] % WINDOWHEIGHT])


class creditsScene(sceneBase):
    def __init__(self):
        sceneBase.__init__(self)
        self.streetCred = credits(1, 3)
        self.streetCred.credits_strings_list = ['Producer: Ben Lee', 'Programmer: Ben Lee', 'Level Designer: Ben Lee',
                                                'Sound Designer: Ben Lee', '', 'Special Thanks:', 'Winston Chou']
        self.return_key_flag = False  # need this flag to prevent initial enter key up event (from hitting enter to switch to this scene from main menu) from screwing up credits scroll rate/direction.
        self.speed_up_flag = False  # speeds up line-adding counter to match scroll rate when user holds down enter, so that it doesn't create lag space between lines.

    def processInput(self, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # return player to main menu.
                    self.switchToScene(mainMenuScene())
                elif event.key == K_RETURN:
                    # return key flag detects first time user hits enter while in this scene, and sets to True to allow Enter key to function as intended.
                    self.return_key_flag = True
                    self.speed_up_flag = True
                    # speed up credits if player holds down the enter key.
                    self.streetCred.move_rate += self.streetCred.speed_up_rate
            if event.type == KEYUP:
                if event.key == K_RETURN and self.return_key_flag:
                    self.speed_up_flag = False
                    # set credits to normal speed again when player releases enter key.
                    self.streetCred.move_rate -= self.streetCred.speed_up_rate
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.switchToScene(mainMenuScene())

    def update(self):
        gamewinsurf.fill(BGCOLOR)
        if self.speed_up_flag:
            self.streetCred.counter += 4
        else:
            self.streetCred.counter += 1
        if self.streetCred.position < len(self.streetCred.credits_strings_list):
            if self.streetCred.counter >= self.streetCred.threshold:
                self.streetCred.addCredit(self.streetCred.credits_strings_list[self.streetCred.position])
                self.streetCred.position += 1
                self.streetCred.counter = 0

        self.streetCred.moveCredits()
        self.streetCred.displayCredits(gamewinsurf)


class gameOverMenu():
    def __init__(self):
        self.optionslist = []
        self.option_to_highlight = 0  # highlight flag

    def addOption(self, option, txtcolor, x, y):  # centers the line at the specified coordinate.
        menuitemobj = menuFont.render(option, 1, txtcolor)
        menuitemrect = menuitemobj.get_rect()
        menuitemrect.center = (x, y)
        self.optionslist.append({'menuitem': menuitemobj,
                                 'menurect': menuitemrect,
                                 'menuitemcolor': txtcolor,
                                 'menuitemname': option})

    def highlightOption(self):
        # detect if option is moused over and assign its index to the highlight flag.  give all other options not moused over the regular text color.
        i = 0
        while i < len(self.optionslist):
            if self.optionslist[i]['menurect'].collidepoint(pygame.mouse.get_pos()):
                self.option_to_highlight = i
            else:
                self.optionslist[i]['menuitemcolor'] = TEXTCOLOR
            i += 1

        # give appropriate menu option the highlight color.
        self.optionslist[self.option_to_highlight]['menuitemcolor'] = MENUHIGHLIGHTCOLOR

        # updating font colors of menu item objects to reflect highlighted option.
        for i in self.optionslist:
            changedgMFontObj = menuFont.render(i['menuitemname'], 1, i['menuitemcolor'])
            i['menuitem'] = changedgMFontObj


class gameOverScene(sceneBase):  # game over scene. appears when you die.

    def __init__(self):
        sceneBase.__init__(self)
        self.gM = gameOverMenu()
        self.gM.addOption('Play Again', MENUHIGHLIGHTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 2) / 3))
        self.gM.addOption('Main Menu', TEXTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 2) / 3) + 30)
        self.gM.addOption('Exit Game', TEXTCOLOR, WINDOWWIDTH / 2, ((WINDOWHEIGHT * 2) / 3) + 60)

    def selectOption(self, option):
        if option['menuitemname'] == 'Play Again':
            # if player chooses to play again, reset game state (wipe units, refill health, update high score as needed).
            gS.resetGameState()
            pygame.mouse.set_visible(False)
            pygame.mouse.set_pos(playerShipRect.centerx, playerShipRect.centery)
            self.switchToScene(mainGameScene())
        elif option['menuitemname'] == 'Main Menu':
            # if player chooses to return to the main menu, reset game state and switch to main menu scene.
            gS.resetGameState()
            self.switchToScene(mainMenuScene())
        elif option['menuitemname'] == 'Exit Game':
            pygame.quit()
            sys.exit()

    def processInput(self, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == ord('s') or event.key == K_DOWN:
                    # highlight option when using keyboard to scroll down menu options.
                    i = 0
                    while i < len(self.gM.optionslist):
                        if self.gM.optionslist[i]['menuitemcolor'] == MENUHIGHLIGHTCOLOR and i < len(
                                self.gM.optionslist) - 1:
                            self.gM.option_to_highlight = i + 1
                            break
                        i += 1
                elif event.key == ord('w') or event.key == K_UP:
                    # highlight option when using keyboard to scroll up menu options.
                    i = 0
                    while i < len(self.gM.optionslist):
                        if self.gM.optionslist[i]['menuitemcolor'] == MENUHIGHLIGHTCOLOR and i > 0:
                            self.gM.option_to_highlight = i - 1
                        i += 1
                elif event.key == K_RETURN:
                    for option in self.gM.optionslist:
                        if option['menuitemcolor'] == MENUHIGHLIGHTCOLOR:
                            self.selectOption(option)
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for option in self.gM.optionslist:
                        if option['menurect'].collidepoint(pygame.mouse.get_pos()):
                            self.selectOption(option)

        self.gM.highlightOption()

    def update(self):
        gamewinsurf.fill(BGCOLOR)

        # draw UI state at time of death using either normal or insane mode high score, depending on which mode player has chosen. 
        drawText('Score: %s' % (gS.score), font, 5, 5, gamewinsurf)
        if not gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreNormal), font, 5, 23, gamewinsurf)
        elif gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreInsane), font, 5, 23, gamewinsurf)

        # draw health UI at time of death.
        healthBarOutline(gamewinsurf, 6, 45, 1)
        [gamewinsurf.blit(i['body'], i['rect']) for i in gS.healthBarPieceList]

        # blit player ship, enemy ships, player projectiles, enemy projectiles at time of death.
        if not (gS.invulnerableMode and gS.flashIsOn):
            gamewinsurf.blit(playerShip, playerShipRect)
        for i in [normalShipDuders.shiplist, normalShipDuders2.shiplist, largeShipDuders.shiplist,
                  myDuderMissile.projlist, normalShipMissile.projlist, normalShipMissile2.projlist,
                  largeShipMissile.projlist]:
            [gamewinsurf.blit(j['body'], j['rect']) for j in i]

        drawTextCenter('You died.  Good job.', font, WINDOWWIDTH / 2, WINDOWHEIGHT / 4, gamewinsurf)

        # blit menu options.
        for i in self.gM.optionslist:
            gamewinsurf.blit(i['menuitem'], i['menurect'])

class mainGameScene(sceneBase):  # the main game loop.

    def __init__(self):
        sceneBase.__init__(self)
        # set the player's initial position and movement status.
        self.left = self.right = self.up = self.down = False
        # set up snorlax message time marker.
        self.msgStartTime = 0

    def processInput(self, events):
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # if player presses keys down to move ship, update rect coords.
            if event.type == KEYDOWN:
                if event.key == daControls.moves['Up'][0] or event.key == daControls.moves['Up'][1]:
                    self.up = True
                    self.down = False
                if event.key == daControls.moves['Left'][0] or event.key == daControls.moves['Left'][1]:
                    self.left = True
                    self.right = False
                if event.key == daControls.moves['Down'][0] or event.key == daControls.moves['Down'][1]:
                    self.down = True
                    self.up = False
                if event.key == daControls.moves['Right'][0] or event.key == daControls.moves['Right'][1]:
                    self.right = True
                    self.left = False
                if event.key == daControls.moves['Shoot'][0]:
                    myDuderMissile.projlist.append(self.playerProj)
                if event.key == daControls.moves['Back'][0]:
                    # if player happens to be invulnerable, subtract from the total invulnTime the time that has passed between when player became invulnerable to the point he paused.
                    # this is the amount of invulnTime left after player pauses. Make this new time the new invulnTime when player unpauses.
                    if gS.invulnerableMode:
                        gS.timeToAdd = gS.invulnTime - (time.time() - gS.invulnerableStartTime)
                        if self.localFlashIsOn:
                            gS.flashIsOn = True
                        else:
                            gS.flashIsOn = False
                    # in insane mode, subtract from the total gS.shipChangeTime the time that has passsed between the start of the last shipchangetime and the point the player paused.
                    # this is the amount of gS.shipChangeTime left after player pauses.  make this the new gS.shipChangeTime for when player unpauses.
                    if gS.insaneMode and gS.preventChangeShipColor:
                        gS.shipChangeTimeToAdd = gS.shipChangeTime - (time.time() - gS.preventStartTime)
                    pygame.mouse.set_pos(WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
                    pygame.mouse.set_visible(True)
                    self.switchToScene(pauseMenuScene())
                if event.key == daControls.moves['Color Swap'][0]:
                    if not gS.insaneMode:
                        gS.changeShipColor = not gS.changeShipColor

            # update any keys that are released
            if event.type == KEYUP:
                if event.key == daControls.moves['Up'][0] or event.key == daControls.moves['Up'][1]:
                    self.up = False
                if event.key == daControls.moves['Left'][0] or event.key == daControls.moves['Left'][1]:
                    self.left = False
                if event.key == daControls.moves['Down'][0] or event.key == daControls.moves['Down'][1]:
                    self.down = False
                if event.key == daControls.moves['Right'][0] or event.key == daControls.moves['Right'][1]:
                    self.right = False

            # moves player ship in place using mouse. NOTE: also updates projectile rect since playerShipRect is built into playerProjRect below, which updates based on playerShipRect.
            if event.type == MOUSEMOTION:
                playerShipRect.move_ip(event.pos[0] - playerShipRect.centerx, event.pos[1] - playerShipRect.centery)

            # if player shoots projectile, add a projectile to player's projectile dict:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == daControls.moves['Shoot'][0]:
                    myDuderMissile.projlist.append(self.playerProj)

                # EVERYTHING BELOW A DUPLICATE OF ABOVE KEYDOWN EVENTS, BUT FOR MOUSE BUTTONS.
                # if player presses mouse button to move ship, update rect coords.
                if event.button == daControls.moves['Up'][0] or event.button == daControls.moves['Up'][1]:
                    self.up = True
                    self.down = False
                if event.button == daControls.moves['Left'][0] or event.button == daControls.moves['Left'][1]:
                    self.left = True
                    self.right = False
                if event.button == daControls.moves['Down'][0] or event.button == daControls.moves['Down'][1]:
                    self.down = True
                    self.up = False
                if event.button == daControls.moves['Right'][0] or event.button == daControls.moves['Right'][1]:
                    self.right = True
                    self.left = False
                if event.button == daControls.moves['Back'][0]:
                    # if player happens to be invulnerable, subtract from the total invulnTime the time that has passed between when player became invulnerable to the point he paused.
                    # this is the amount of invulnTime left after player pauses. Make this new time the new invulnTime when player unpauses.
                    if gS.invulnerableMode:
                        gS.timeToAdd = gS.invulnTime - (time.time() - gS.invulnerableStartTime)
                        if self.localFlashIsOn:
                            gS.flashIsOn = True
                        else:
                            gS.flashIsOn = False
                    # in insane mode, subtract from the total gS.shipChangeTime the time that has passsed between the start of the last shipchangetime and the point the player paused.
                    # this is the amount of gS.shipChangeTime left after player pauses.  make this the new gS.shipChangeTime for when player unpauses.
                    if gS.insaneMode and gS.preventChangeShipColor:
                        gS.shipChangeTimeToAdd = gS.shipChangeTime - (time.time() - gS.preventStartTime)
                    pygame.mouse.set_pos(WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
                    pygame.mouse.set_visible(True)
                    self.switchToScene(pauseMenuScene())
                if event.button == daControls.moves['Color Swap'][0]:
                    if not gS.insaneMode:
                        gS.changeShipColor = not gS.changeShipColor

            if event.type == MOUSEBUTTONUP:
                if event.button == daControls.moves['Up'][0] or event.button == daControls.moves['Up'][1]:
                    self.up = False
                if event.button == daControls.moves['Left'][0] or event.button == daControls.moves['Left'][1]:
                    self.left = False
                if event.button == daControls.moves['Down'][0] or event.button == daControls.moves['Down'][1]:
                    self.down = False
                if event.button == daControls.moves['Right'][0] or event.button == daControls.moves['Right'][1]:
                    self.right = False


    def update(self):
        # spawn player projectiles. each dictionary represents one projectile and its spawn parameters. 
        self.playerProjRect = playerProjBody.get_rect()
        self.playerProjRect.center = ((playerShipRect.centerx, playerShipRect.centery - 15))
        self.playerProj = {'body': playerProjBody,
                           'rect': self.playerProjRect}

        # set up UI using either normal or insane mode high score, depending on which mode player has chosen.
        drawText('Score: %s' % (gS.score), font, 5, 5, gamewinsurf)
        if not gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreNormal), font, 5, 23, gamewinsurf)
        elif gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreInsane), font, 5, 23, gamewinsurf)

        # in insane mode, ship has certain chance to change color every gS.shipChangeTime seconds.
        if gS.insaneMode:
            if not gS.preventChangeShipColor:
                if random.randint(0, 1) == 0:  # 50% chance
                    gS.changeShipColor = not gS.changeShipColor
                gS.preventChangeShipColor = True
                gS.preventStartTime = time.time()

        # restart ship color prevention timer after it has completed. if ship color c hange preventione time was set to a shorter time to account for pause, reset it to default.
        if ((time.time() - gS.preventStartTime) > gS.shipChangeTime) and gS.preventChangeShipColor:
            gS.preventChangeShipColor = False
            gS.shipChangeTime = SHIPCHANGETIME

        if gS.changeShipColor:
            playerShip.fill(RED)
        if not gS.changeShipColor:
            playerShip.fill(BLUE)

        self.localFlashIsOn = round(time.time(), 1) * 10 % 2 == 1

        # delete player projectiles, enemy ships, and enemy projectiles that have flown off screen.
        gS.wipeOffScreenUnits(gS.unitsToWipe)

        # count number of existing enemy ships before player projectiles have destroyed them.
        initialScoreStock = 0
        for i in normalShipDuders.shiplist:
            initialScoreStock += 1
        for i in normalShipDuders2.shiplist:
            initialScoreStock += 1
        for i in largeShipDuders.shiplist:
            initialScoreStock += 25

        # delete normal enemy ships when they are hit by player projectiles.
        destroyEnemyShip(normalShipDuders.shiplist, myDuderMissile.projlist)
        destroyEnemyShip(normalShipDuders2.shiplist, myDuderMissile.projlist)

        # reduce hp of large enemy ships by 1 when hey are struck by a player projectile.  when hp = 0, delete the large enemy ship.
        delHporDestroyLargeShip(largeShipDuders.shiplist, myDuderMissile.projlist)

        # count number of existing enemy ships after player projectiles have destroyed them.
        finalScoreStock = 0
        for i in normalShipDuders.shiplist:
            finalScoreStock += 1
        for i in normalShipDuders2.shiplist:
            finalScoreStock += 1
        for i in largeShipDuders.shiplist:
            finalScoreStock += 25

        # calculate points to add based on difference between number of existing ships before and after player projectiles have destroyed them.
        gS.score += initialScoreStock - finalScoreStock

        # if player is invulnerable, check if he's been invulnerable over 2 seconds.  if so, turn off invulnerability.
        if gS.invulnerableMode and time.time() - gS.invulnerableStartTime > gS.invulnTime:
            gS.invulnerableMode = False
            # if invulnTime was set to a shorter time to account for the player pausing while invulnerable, reset invulnTime to default invulnTime (2) after making player vulnerable again.
            if gS.invulnTime == gS.timeToAdd:
                gS.invulnTime = INVULNTIME


        # move deven enemy ships down.
        moveShipsDown(normalShipDuders.shiplist, normalShipDuders.rate)
        moveShipsDown(normalShipDuders2.shiplist, normalShipDuders2.rate)
        for i in largeShipDuders.shiplist:
            moveLargeShipDown(i, LARGEENEMYSHIPRATE, i['initialdir'], i['vertcounter'], i['hor1'], i['hor2'])

        # move player projectiles up.
        for i in myDuderMissile.projlist[:]:
            i['rect'].move_ip(0, -myDuderMissile.rate)

        # move enemy projectiles down.
        for i in normalShipMissile.projlist:
            i['rect'].move_ip(0, normalShipMissile.rate)

        for i in normalShipMissile2.projlist:
            i['rect'].move_ip(0, normalShipMissile2.rate)

        for i in largeShipMissile.projlist:
            i['rect'].move_ip(0, largeShipMissile.rate)

        # spawn new ship once counter threshold is met. has 50/50 chance of being either of two normal ship types.
        gS.enemyShipAddCounter += 1
        if gS.enemyShipAddCounter == DEVENENEMYSHIPTS:
            gS.enemyShipAddCounter = 0
            if random.randint(0, 1) == 0:
                normalShipDuders.addShip(devenEnemyShip, DEVENENEMYSHIPSIZE, normalShipDuders.shiplist)
            else:
                normalShipDuders2.addShip(devenEnemyShip2, DEVENENEMYSHIPSIZE, normalShipDuders2.shiplist)

        gS.largeEnemyShipAddCounter += 1
        if gS.largeEnemyShipAddCounter == DEVENLARGESHIPTS:
            gS.largeEnemyShipAddCounter = 0
            transformedLargeShip = pygame.transform.scale(devenLargeShip, LARGEENEMYSHIPSIZE)
            devenLargeShipRect = transformedLargeShip.get_rect()
            devenLargeShipRect.bottomleft = (random.randint(0, WINDOWWIDTH - LARGEENEMYSHIPSIZE[0]), 0)
            largeEnemyShipDict = {'body': transformedLargeShip,
                                  'rect': devenLargeShipRect,
                                  'initialdir': random.randint(0, 1),
                                  'vertcounter': [],
                                  'hor1': [0],
                                  'hor2': [0],
                                  'hp': largeShipDuders.hp}
            largeShipDuders.shiplist.append(largeEnemyShipDict)
            self.msgStartTime = time.time()

        # spawn enemy projectiles.
        for i in normalShipDuders.shiplist:
            normalShipMissile.addProj(i, normalShipMissile)
        for i in normalShipDuders2.shiplist:
            normalShipMissile2.addProj(i, normalShipMissile2)
        for i in largeShipDuders.shiplist:
            largeShipMissile.addProj(i, largeShipMissile)

        # move player ship if player uses keyboard.  NOTE: must also update mouse coordinate to mouse location of ship, otherwise ship will jump back to where mouse pointer was if player starts using mouse to move again.
        moveUp(self.up, playerShipRect, PLAYERSHIPRATE)
        moveLeft(self.left, playerShipRect, PLAYERSHIPRATE)
        moveDown(self.down, playerShipRect, PLAYERSHIPRATE)
        moveRight(self.right, playerShipRect, PLAYERSHIPRATE)
        # set mouse position to player ship rect. without doing so, mouse will remain where it was last before keyboard movement started, causing ship to "jump" back to mouse position if player resumes using mouse.
        pygame.mouse.set_pos(playerShipRect.centerx, playerShipRect.centery)

        gamewinsurf.fill(BGCOLOR)

        # if the player has been recently struck so that he is invulnerable AND flashIsOpen happens to be on during this particular loop run,  do not blit the player's ship (creates the flashing effect).
        # otherwise, blit player ship.
        if not (gS.invulnerableMode and self.localFlashIsOn):
            gamewinsurf.blit(playerShip, playerShipRect)

        # blit player ship, enemy ships, player projectiles, enemy projectiles.
        for i in [normalShipDuders.shiplist, normalShipDuders2.shiplist, largeShipDuders.shiplist,
                  myDuderMissile.projlist, normalShipMissile.projlist, normalShipMissile2.projlist,
                  largeShipMissile.projlist]:
            [gamewinsurf.blit(j['body'], j['rect']) for j in i]

        # display large enemy ship snorlax message if large enemy ship has just appeared and if message time limit has not been passed.
        if time.time() - self.msgStartTime <= LARGEENEMYMSGTIME:
            drawText('A wild Snorlax appears!', font, 6, 70, gamewinsurf)

        # NOTE: Game immediately halts once player health reaches zero.  As such, any code deleting health must folow enemy projectiles and ship
        # positions being blitted based on LATEST positional update.  Otherwise
        # we run into the problem of the player looking like he hasn't been struck
        # by a projectile or ship yet upon death (since latest enemy ship/projectile
        # position has not been blitted and therefore is not displayed).  Basically, health deletions must follow ship and projectile blits.
        # NOTE 2: Any code deleting health must precede UI being updated so that last health piece is visibly lost upon death.

        # delete a health piece when player ship hits an enemy ship. then make the player invulnerable for 2 seconds. 
        if not gS.invulnerableMode:
            enemyShipLists = [normalShipDuders.shiplist, normalShipDuders2.shiplist, largeShipDuders.shiplist]
            for shiplist in enemyShipLists:
                for ship in shiplist:
                    if ship['rect'].colliderect(playerShipRect) and gS.healthBarPieceList != []:
                        gS.invulnerableMode = True
                        gS.invulnerableStartTime = time.time()
                        del gS.healthBarPieceList[-1]

        # delete a health piece when player ship is hit by normal enemy projectile whose color does NOT match player's ship color. Then make the player invulnerable for 2 seconds.
        if not gS.invulnerableMode:
            for i in list(normalShipMissile.projlist):  # if enemy missile color is red,
                if i['rect'].colliderect(
                        playerShipRect) and gS.healthBarPieceList != []:  # when player collides with projectile,
                    if len(
                            gS.healthBarPieceList) == 2 or gS.changeShipColor:  # projectile disappears if player is at full health or if projectile is same color as player.
                        normalShipMissile.projlist.remove(i)
                    gS.invulnerableStartTime = time.time()
                    if not gS.changeShipColor:  # if player ship is blue,
                        del gS.healthBarPieceList[
                            -1]  # delete a health piece and make player invulnerable if not killed.
                        if gS.healthBarPieceList:
                            gS.invulnerableMode = True
            for i in list(normalShipMissile2.projlist):  # if enemy missile color is blue
                if i['rect'].colliderect(
                        playerShipRect) and gS.healthBarPieceList != []:  # when player collides with projectile
                    if len(
                            gS.healthBarPieceList) == 2 or not gS.changeShipColor:  # projectile disappears if player is at full health or if projectile is same color as player.
                        normalShipMissile2.projlist.remove(i)
                    gS.invulnerableStartTime = time.time()
                    if gS.changeShipColor:  # if player ship is red,
                        del gS.healthBarPieceList[
                            -1]  # delete a health piece and make player invulnerable if not killed.
                        if gS.healthBarPieceList:
                            gS.invulnerableMode = True

                            # delete a health piece when player ship is hit by large enemy projectile.
        for i in largeShipMissile.projlist:
            if i['rect'].colliderect(playerShipRect) and gS.healthBarPieceList != []:
                largeShipMissile.projlist.remove(i)
                gS.invulnerableMode = True
                gS.invulnerableStartTime = time.time()
                del gS.healthBarPieceList[-1]

        # update displayed UI using either normal or insane mode high score, depending on which mode player has chosen.
        drawText('Score: %s' % (gS.score), font, 5, 5, gamewinsurf)
        if not gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreNormal), font, 5, 23, gamewinsurf)
        elif gS.insaneMode:
            drawText('High Score: %s' % (gS.highScoreInsane), font, 5, 23, gamewinsurf)

        # draw health UI.
        healthBarOutline(gamewinsurf, 6, 45, 1)
        [gamewinsurf.blit(i['body'], i['rect']) for i in gS.healthBarPieceList]

        # once player dies, switch to game over scene. also update high score if needed.
        if not gS.healthBarPieceList:
            if not gS.insaneMode:
                if gS.score > gS.highScoreNormal:
                    gS.highScoreNormal = gS.score
            elif gS.insaneMode:
                if gS.score > gS.highScoreInsane:
                    gS.highScoreInsane = gS.score
            pygame.mouse.set_pos(WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
            pygame.mouse.set_visible(True)
            self.switchToScene(gameOverScene())

#------------------------------------------------------------------------

# create unit objects.
myDuderMissile = pProj([], PLAYERPROJMOVERATE)
normalShipDuders = enemyShipNormal([], DEVENENEMYSHIPRATE)
normalShipDuders2 = enemyShipNormal([], DEVENENEMYSHIPRATE)
largeShipDuders = enemyShipLarge([], LARGEENEMYSHIPRATE, 10)
normalShipMissile = eProj([], DEVENENEMYPROJSIZE, DEVENENEMYPROJRATE, DEVENPROJFREQUENCY, DEVENENEMYPROJCOLOR)
normalShipMissile2 = eProj([], DEVENENEMYPROJSIZE, DEVENENEMYPROJRATE, DEVENPROJFREQUENCY, DEVENENEMYPROJCOLOR2)
largeShipMissile = eProj([], LARGEENEMYPROJSIZE, LARGEENEMYPROJRATE, DEVENLARGEPROJFREQUENCY, LARGEENEMYPROJCOLOR)

# create game state object
gS = gameState()

# initialize an instance of the controls class.  need to do it here and not in the controlsmenu scene because mapped controls need to carry over from that scene into gameplay.
daControls = controls()
daControls.controls_strings_list.extend(['Left', 'Right', 'Up', 'Down', 'Shoot', 'Color Swap', 'Select', 'Back'])
daControls.addOptions(TEXTCOLOR, (80, 22), (127, 127, 127), WINDOWWIDTH / 5, 120, (3 / 4) * WINDOWWIDTH - 50,
                      gamewinsurf)
daControls.addKeyText()

if __name__ == "__main__":
    main()
