"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

Alanna Kim (yk557) Haoshen Li (hl2239)
December 4, 2018
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        direction: the direction aliens is moving to ['right','left']
        step: the step aliens take [int>=0]

    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializer: Creates and controls alien waves, a ship, and lives.
        """
        self._aliens = self.alien()
        self._ship = Ship(GAME_WIDTH/2,SHIP_BOTTOM,SHIP_WIDTH,
        SHIP_HEIGHT,'profship.png')
        self._dline = GPath(points=[0,100,800,100],linewidth=2,linecolor='black')
        self._time = 0
        self.direction = 'right'
        self._bolts=[]
        self.step = 0
        self.steprate = random.randint(1, BOLT_RATE)
        self.speed = ALIEN_SPEED
        self._lives = SHIP_LIVES
        self.pewSound1= Sound('pop2.wav')
        self.pewSound2= Sound('pew1.wav')
        self.pewSound3= Sound('blast3.wav')


    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, input, dt):
        """
        Animates an alien wave, ship, and laser bolts.

        Parameter input: the user input, used to control the ship and change state
        Precondition: instance of GInput; it is inherited from GameApp

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        if self.checkgame():
            if self._ship != None:
                self._ship.moveship(input,self._ship)
            else:
                self.checkgame()
            self._time += dt
            if self.direction == 'right':
                self.rightmove()
            elif self.direction == 'left':
                self.leftmove()
            if input.is_key_down('up') or input.is_key_down('spacebar'):
                if not self.isplayerbolt():
                    self.pewSound1.play()
                    self._bolts.append(Bolt(self._ship.x, self._ship.y+SHIP_HEIGHT/2,
                    BOLT_WIDTH, BOLT_HEIGHT, 'black', 'black', BOLT_SPEED))
            if self.whentofire():
                a = self.whotofire()
                self._bolts.append(Bolt(a.x, a.y-ALIEN_HEIGHT/2,
                BOLT_WIDTH, BOLT_HEIGHT, 'black', 'black', BOLT_SPEED))
                self.steprate = random.randint(1, BOLT_RATE)
            if self._bolts!=[]:
                self.movingbolts()
                self.deletingbolts()
                self.detectcollison()


    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self,view):
        """
        Draws THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS.
        """

        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.draw(view)
        if self._ship != None:
            self._ship.draw(view)
        self._dline.draw(view)
        for x in self._bolts:
            if x !='' and x != None:
                x.draw(view)


    # HELPER METHODS FOR COLLISION DETECTION
    def detectcollison(self):
        """
        Removes laser bolts when they collide with either aliens or the ship.
        """

        for bolt in self._bolts:
            if bolt.getv()>0:
                for row in range(len(self._aliens)):
                    for col in range(len(self._aliens[row])):
                        a = self._aliens[row][col]
                        if a != None:
                            if self._aliens[row][col].aliencollision(bolt,a):
                                self.pewSound2.play()
                                self._aliens[row][col] = None
                                self._bolts.remove(bolt)
            else:
                if self._ship!=None:
                    if self._ship.shipcollision(bolt,self._ship):
                        self.pewSound3.play()
                        self._ship = None
                        self._bolts.remove(bolt)


    #HELPER METHODS TO CREATE WAVE OF ALIENS
    def alien(self):
        """
        Creates wave of aliens.
        """
        col = ALIENS_IN_ROW
        row = ALIEN_ROWS
        st1 = ALIEN_H_SEP+(1/2)*ALIEN_WIDTH
        st2 = GAME_HEIGHT-ALIEN_CEILING-(row-1)*(ALIEN_V_SEP+ALIEN_HEIGHT)-(1/2)*ALIEN_HEIGHT
        a = []
        for x in range(row):
            p = x%6
            b = []
            for y in range(col):
                if p == 0 or p == 1:
                    b.append(Alien(st1,st2,ALIEN_WIDTH,ALIEN_HEIGHT,'alienone.png'))
                    st1 +=ALIEN_WIDTH+ALIEN_H_SEP
                if p == 2 or p == 3:
                    b.append(Alien(st1,st2,ALIEN_WIDTH,ALIEN_HEIGHT,'alientwo.png'))
                    st1 += ALIEN_WIDTH+ALIEN_H_SEP
                if p == 4 or p == 5:
                    b.append(Alien(st1,st2,ALIEN_WIDTH,ALIEN_HEIGHT,'alienthree.png'))
                    st1 += ALIEN_WIDTH+ALIEN_H_SEP
            a.append(b)
            st1 = ALIEN_V_SEP+(1/2)*ALIEN_WIDTH
            st2 += ALIEN_V_SEP+ALIEN_HEIGHT
        return a


    # HELPER METHODS FOR MOVING ALIENS
    def rightmove(self):
        """
        Helps aliens to move right and down.
        """

        if self._time > self.speed and self.edge()!=None:
            if self.edge()[0] < GAME_WIDTH-ALIEN_WIDTH/2-ALIEN_H_SEP:
                for row in range(len(self._aliens)):
                    for col in range(len(self._aliens[row])):
                        if self._aliens[row][col]!= None:
                            self._aliens[row][col].x +=ALIEN_H_WALK
            else:
                for row in range(len(self._aliens)):
                    for col in range(len(self._aliens[row])):
                        if self._aliens[row][col]!= None:
                            self._aliens[row][col].y -= ALIEN_V_WALK
                self.direction = 'left'
            self._time = 0
            self.step += 1


    def leftmove(self):
        """
        Helps aliens to move left and down.
        """

        if self._time > ALIEN_SPEED:
            if self.edge()[1]  > ALIEN_WIDTH/2+ALIEN_H_SEP:
                for row in range(len(self._aliens)):
                    for col in range(len(self._aliens[row])):
                        if self._aliens[row][col]!= None:
                            self._aliens[row][col].x -=ALIEN_H_WALK
            else:
                for row in range(len(self._aliens)):
                    for col in range(len(self._aliens[row])):
                        if self._aliens[row][col]!= None:
                            self._aliens[row][col].y -= ALIEN_V_WALK
                self.direction = 'right'
            self._time = 0
            self.step += 1


    def edge(self):
        """
        Helps aliens to only stay in allowed range-so that they do not
        move outside of the window.
        """
        a=[]
        b=[]
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    a.append(alien.x)
        if a != []:
            right = max(a)
            left = min(a)
            b.append(right)
            b.append(left)
            return b


        #HELPER METHOD FOR DETERMINING BOLTS DIRECTION
    def isplayerbolt(self):
        """
        Returns whether the laser bolt is heading towards aliens or the ship.
        """

        a = 0
        for bolt in self._bolts:
            if bolt.getv()>0:
                a += 1
        if a == 1:
            return True
        else:
            return False


        #HEPER METHOD FOR MOVING BOLTS
    def movingbolts(self):
        """
        Controls laser bolts to move either upward or downward.
        """
        for bolt in self._bolts:
            if bolt.getv()>0:
                bolt.y+=BOLT_SPEED
            else:
                bolt.y-=BOLT_SPEED


        #HEPER METHODS FOR DELETING BOLTS
    def deletingbolts(self):
        """
        Removes a laser bolt that passes the GAME_HEIGHT.
        """
        a = self._bolts
        for x in a:
            if (x.y-BOLT_HEIGHT/2)>=GAME_HEIGHT or x.y+BOLT_HEIGHT/2<=0:
                a.remove(x)


        #HELPER METHODS FOR IS SHIP FIRING
    def isshipfiring(self):
        """
        Returns whether the player can fire a laser bolt.
        """
        a = 0
        for x in self._bolts:
            if self.isplayerbolt():
                a+=1
        if a == 0:
            return True
        else:
            return False


        #HELPER METHODS FOR WHEN TO FIRE
    def whentofire(self):
        """
        Returns True or False to determine when to shoot the laser bolt.
        """
        if self.step == self.steprate:
            self.step = 0
            return True
        else:
            return False


        #HELPER METHODS FOR WHO TO FIRE
    def whotofire(self):
        """
        Determines which alien to shoot the laser bolt.
        """
        a = []
        for x in range(ALIENS_IN_ROW):
            b = 0
            for y in range(ALIEN_ROWS):
                if self._aliens[y][x] != None:
                    b+=1
            if b!=0:
                a.append(x)
        c = random.choice(a)
        d = 0
        e = []
        for x in range(ALIEN_ROWS):
            p = 0
            if self._aliens[x][c]!= None:
                d = self._aliens[x][c]
                return d


        #HELPER METHODS FOR CHECKING WHETHER CONTINUIE THE GAME
    def checkgame(self):
        """
        Returns True if the conditions fulfills for the player to lose the game.
        """
        if self._lives < 0 or self.checkalien() or self.checkalien1():
            return False
        else:
            return True


    def checkalien(self):
        """
        Return True if one of aliens has crossed defense line.
        """
        for x in range(len(self._aliens)):
            for y in range(len(self._aliens[x])):
                if self._aliens[x][y] != None:
                    if self._aliens[x][y].y-ALIEN_HEIGHT/2 < DEFENSE_LINE:
                        return True
                else:
                    return False


    def checkalien1(self):
        """
        Returns True if all of alines are destroyed
        """
        a = 0
        for x in range(len(self._aliens)):
            for y in range(len(self._aliens[x])):
                if self._aliens[x][y]!= None:
                    a += 1
        if a == 0:
            return True
        else:
            return False


    def checkship(self):
        """
        Returns True if ship has lost one of lives and still alive
        """
        if self._ship == None and self._lives > 0:
            self._ship = Ship(GAME_WIDTH/2,SHIP_BOTTOM,SHIP_WIDTH,
            SHIP_HEIGHT,'profship.png')
            self._lives -= 1
            return True
        else:
            return False
