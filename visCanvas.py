'''
System for making visuals
The canvas handles the overall board, including calling updates on sprites and tracking frames passed
Sprites keep track of individual values, such as positon and movement changes
'''


import tkinter as tk
import tkinter.font as tkFont
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageTk

CHARS = {
    "grave":"`",
    "minus":"-",
    "equal":"=",
    "bracketleft":"[",
    "bracketright":"]",
    "backslash":"\\",
    "semicolon":";",
    "apostrophe":"\'",
    "comma":",",
    "period":".",
    "slash":"/",
    "asciitilde":"~",
    "exclam":"!",
    "at":"@",
    "numbersign":"#",
    "dollar":"$",
    "percent":"%",
    "asciicircum":"^",
    "ampersand":"&",
    "asterisk":"*",
    "parenleft":"(",
    "parenright":")",
    "underscore":"_",
    "plus":"+",
    "braceleft":"{",
    "braceright":"}",
    "bar":"|",
    "colon":":",
    "quotedbl":"\"",
    "less":"<",
    "greater":">",
    "question":"?",
    "space":" "
}

IGNORE_CHARS = [
    "tab", "caps_lock", "return", "shift_l", "shift_r", "super_l", "super_r",
    "control_l", "control_r", "alt_l", "alt_r", "meta_l", "meta_r", "left",
    "right", "up", "down"
]

class Sprite():
    def __init__(self, x:int=0, y:int=0, gravityScale:float=0):
        '''
        Sets up a base sprite
        
        :param self: n/a
        :param x: the x position of the center of the dot
        :type x: int
        :param y: the y position of the center of the dot
        :type y: int
        :param gravityScale: the amount of gravity that will be applied to the object, where 1 corresponds to +1 pixel/frame
        :type gravityScale: float
        '''
        self.x = x
        self.y = y

        self.dX = 0
        self.dY = 0
        self.endChange = 0

        self.vX = 0
        self.vY = 0
        self.gravityScale = gravityScale

        self.wait = 0

        self.initialized = False
    
    def delay(self, delayAmount:int):
        '''
        Sets a delay for the number of frames to wait before the next update for this sprite
        
        :param self: n/a
        :param delayAmount: the delay length in frames
        :type delayAmount: int
        '''
        if not self.initialized:
            return
        self.wait = delayAmount
    
    def change_pos(self, newX:int, newY:int, duration:int=0):
        '''
        Changes the position to a new position over the duration. If the duration is 0, the position will be immediately changed
        
        :param self: n/a
        :param self: Description
        :param newX: the desired x position
        :type newX: int
        :param newY: the desired y position
        :type newY: int
        :param duration: the duration of the change in frames
        :type duration: int
        '''
        if not self.initialized:
            return
        
        if duration == 0:
            self.x = newX
            self.y = newY
            self.CANVAS.coords(self.dot, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
        else:
            self.endChange = duration
            self.dX = (newX-self.x)/duration
            self.dY = (newY-self.y)/duration
    
    def add_velocity(self, vX=0, vY=0):
        self.vX += vX
        self.vY += vY

    def set_velocity(self, vX=0, vY=0):
        self.vX = vX
        self.vY = vY
    
    def base_update(self, framesPassed):
        '''
        Updates the sprite
        
        :param self: n/a
        :param framesPassed: the overall frame count
        '''
        if not self.initialized:
            return
        
        if self.wait > 0:
            self.wait -= 1
            self.endChange += 1
        else:
            if self.vX != 0 or self.vY != 0:
                self.change_pos(self.x+self.vX, self.y+self.vY)

            if self.dX != 0 or self.dY != 0:
                self.change_pos(self.x+self.dX, self.y+self.dY)

                # TODO: change from checking frames passed to checking closeness
                if framesPassed >= self.endChange:
                    self.dX = 0
                    self.dY = 0
            
            # TODO: check if on ground
            self.vY += self.gravityScale


class Dot(Sprite):
    def __init__(self, color:str="white", outline:str="white", r:int=5, x:int=0, y:int=0, gravityScale:float=0):
        '''
        Sets up a dot sprite
        
        :param self: n/a
        :param color: a hex code for the color of the dot
        :type color: str
        :param outline: a hex code for the color of the outline
        :type outline: str
        :param r: the radius of the dot
        :type r: int
        :param x: the x position of the center of the dot
        :type x: int
        :param y: the y position of the center of the dot
        :type y: int
        :param gravityScale: the amount of gravity that will be applied to the object, where 1 corresponds to +1 pixel/frame
        :type gravityScale: float
        '''
        super().__init__(x, y, gravityScale)

        self.r = r

        self.targetR = 0
        self.dR = 0

        self.wait = 0

        self.color = color
        self.outline = outline
    
    def initialize(self, canvas):
        '''
        Finishes creating a dot sprite on a canvas
        
        :param self: n/a
        :param canvas: the overall tkinter canvas
        '''
        if not self.initialized:
            self.CANVAS = canvas
            self.dot = self.CANVAS.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r, fill=self.color, outline=self.outline)
            self.initialized = True
    
    def change_size(self, newR:int, duration:int=0):
        '''
        Changes the size to a new size over the duration. If the duration is 0, the size will be immediately changed
        
        :param self: n/a
        :param newR: the desired radius
        :type newR: int
        :param duration: the duration of the change in frames
        :type duration: int
        '''
        if not self.initialized:
            return
        
        if duration == 0:
            self.r = newR
            self.CANVAS.coords(self.dot, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
        else:
            self.targetR = newR
            self.dR = (self.targetR-self.r)/duration
    
    def change_color(self, newColor:str):
        '''
        Changes the dot's color to the new color.
        
        :param self: n/a
        :param newColor: a hex code for the desired color
        :type newColor: str
        '''
        if not self.initialized:
            return
        
        self.color = newColor
        self.CANVAS.itemconfig(self.dot, fill=newColor)
    
    def update(self, framesPassed):
        '''
        Updates the sprite
        
        :param self: n/a
        :param framesPassed: the overall frame count
        '''
        super().base_update(framesPassed)

        if not self.initialized:
            return
        
        if self.wait <= 0:
            if self.dR != 0:
                if abs(self.targetR-self.r) <= abs(self.dR*2):
                    self.dR = 0
                    self.change_size(self.targetR)
                else:
                    self.change_size(self.r+self.dR)

class Rect(Sprite):
    def __init__(self, color:str="white", outline:str="white", w:int=5, h:int=5, x:int=0, y:int=0, gravityScale:float=0):
        '''
        Sets up a rectangle sprite
        
        :param self: n/a
        :param color: a hex code for the color of the dot
        :type color: str
        :param outline: a hex code for the color of the outline
        :type outline: str
        :param w: the width of the rectangle
        :type w: int
        :param h: the height of the rectangle
        :type h: int
        :param x: the x position of the upper left corner of the rectangle
        :type x: int
        :param y: the y position of the upper left corner of the rectangle
        :type y: int
        :param gravityScale: the amount of gravity that will be applied to the object, where 1 corresponds to +1 pixel/frame
        :type gravityScale: float
        '''
        super().__init__(x, y, gravityScale)

        self.w = w
        self.h = h

        self.targetW = 0
        self.dW = 0
        self.targetH = 0
        self.dH = 0

        self.wait = 0

        self.color = color
        self.outline = outline
    
    def initialize(self, canvas):
        '''
        Finishes creating a dot sprite on a canvas
        
        :param self: n/a
        :param canvas: the overall tkinter canvas
        '''
        if not self.initialized:
            self.CANVAS = canvas
            self.rect = self.CANVAS.create_rectangle(self.x, self.y, self.x+self.w, self.y+self.h, fill=self.color, outline=self.outline)
            self.initialized = True
    
    def change_size(self, newW:int, newH:int, duration:int=0):
        '''
        Changes the size to a new size over the duration. If the duration is 0, the size will be immediately changed
        
        :param self: n/a
        :param newR: the desired radius
        :type newR: int
        :param duration: the duration of the change in frames
        :type duration: int
        '''
        if not self.initialized:
            return
        
        if duration == 0:
            self.w = newW
            self.h = newH
            self.CANVAS.coords(self.x, self.y, self.x+self.w, self.y+self.h, fill=self.color, outline=self.outline)
        else:
            self.targetW = newW
            self.dW = (self.targetW-self.w)/duration

            self.targetH = newH
            self.dH = (self.targetH-self.h)/duration
    
    def change_color(self, newColor:str):
        '''
        Changes the rect's color to the new color.
        
        :param self: n/a
        :param newColor: a hex code for the desired color
        :type newColor: str
        '''
        if not self.initialized:
            return
        
        self.color = newColor
        self.CANVAS.itemconfig(self.rect, fill=newColor)
    
    def update(self, framesPassed):
        '''
        Updates the sprite
        
        :param self: n/a
        :param framesPassed: the overall frame count
        '''
        super().base_update(framesPassed)

        if not self.initialized:
            return
        
        if self.wait <= 0:
            if self.dW != 0:
                if abs(self.targetW-self.w) <= abs(self.dW*2):
                    self.dW = 0
                    self.change_size(self.targetW)
                else:
                    self.change_size(self.w+self.dW)
            if self.dH != 0:
                if abs(self.targetH-self.h) <= abs(self.dh*2):
                    self.dh = 0
                    self.change_size(self.targetH)
                else:
                    self.change_size(self.h+self.dh)

class Text():
    def __init__(self, text:str, width:int, x:int=0, y:int=0, font:str="Calibri", fontSize:int=50, color:str="#000000", justify:str="center", autoSize:bool=True, maxSize:int=100):
        '''
        Sets up a text sprite
        
        :param self: n/a
        :param text: the text to be displayed
        :type text: str
        :param width: the width of the text box
        :type width: int
        :param x: the x coordinate of the text box
        :type x: int
        :param y: the y coordinate of the text box
        :type y: int
        :param font: the name of the font to use
        :type font: str
        :param fontSize: the size of the text
        :type fontSize: int
        :param color: a hex code for the color of the text
        :type color: str
        :param justify: left, right, etc for text alignment
        :type justify: str
        :param autoSize: if true, the font size will be changed to fit the text within the width of the text box
        :type autoSize: bool
        :param maxSize: the maximum font height for auto sized text
        :type maxSize: int
        '''
        # TODO work in auto sizing
        # self.label = tk.Label(root, font=("Calibri", 50), background="#1192a6", foreground="black") #CHANGE
        # self.label.pack(anchor="center") #CHANGE
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.font = font
        self.fontSize = fontSize
        self.color = color
        self.justify = justify

        self.dX = 0
        self.dY = 0
        self.endChange = 0

        self.dChars = 0
        self.targetText = ""
        self.deletingChars = True
        self.charIdx = 0

        self.wait = 0

        self.autoSize = autoSize
        self.maxSize = maxSize

        self.initialized = False

        self.auto_size_text()
    
    def initialize(self, canvas):
        '''
        Finishes creating a text sprite on a canvas
        
        :param self: n/a
        :param canvas: the overall tkinter canvas
        '''
        if not self.initialized:
            self.CANVAS = canvas
            self.label = self.CANVAS.create_text(self.x, self.y, fill=self.color, font=(self.font, self.fontSize), text=self.text, justify=self.justify, width=self.width, anchor="nw")
            self.initialized = True
    
    def delay(self, delayAmount:int):
        '''
        Sets a delay for the number of frames to wait before the next update for this sprite
        
        :param self: n/a
        :param delayAmount: the delay length in frames
        :type delayAmount: int
        '''
        if not self.initialized:
            return
        
        self.wait = delayAmount
    
    def change_pos(self, newX:int, newY:int, duration:int=0):
        '''
        Changes the position to a new position over the duration. If the duration is 0, the position will be immediately changed
        
        :param self: n/a
        :param self: Description
        :param newX: the desired x position
        :type newX: int
        :param newY: the desired y position
        :type newY: int
        :param duration: the duration of the change in frames
        :type duration: int
        '''
        if not self.initialized:
            return
        
        if duration == 0:
            self.x = newX
            self.y = newY
            self.CANVAS.coords(self.label, self.x, self.y)
        else:
            self.endChange = duration
            self.dX = (newX-self.x)/duration
            self.dY = (newY-self.y)/duration
    
    def auto_size_text(self):
        if self.autoSize:
            if self.text == "":
                return
            currFont = tkFont.Font(family=self.font, size=self.fontSize)
            textWidth = currFont.measure(self.text)
            scale = self.width/textWidth

            newFontSize = int(self.fontSize * scale)
            if newFontSize > self.maxSize:
                newFontSize = self.maxSize
            self.change_font_size(newFontSize)
    
    def change_text(self, newText:str, duration:int=0):
        '''
        Changes the text to a new text over the duration by deleting and writing characters. If the duration is 0, the text will be immediately changed
        
        :param self: n/a
        :param newText: the desired text
        :type newText: str
        :param duration: the duration of the change in frames
        :type duration: int
        '''
        if not self.initialized:
            return
        
        if duration == 0:
            self.text = newText
            self.CANVAS.itemconfig(self.label, text=newText)
        else:
            self.dChars = (len(newText)+len(self.text))/duration
            self.targetText = newText
            self.deletingChars = True
            self.charIdx = len(self.text)
        
        self.auto_size_text()

    def change_color(self, newColor:str):
        '''
        Changes the color to the new color.
        
        :param self: n/a
        :param newColor: a hex code for the desired color
        :type newColor: str
        '''
        if not self.initialized:
            return
        
        self.CANVAS.itemconfig(self.label, fill=newColor)
        
    def change_font_type(self, newFont):
        '''
        Changes the font type to the new font
        
        :param self: n/a
        :param newFont: the name of the desired font
        '''
        if not self.initialized:
            return
        
        self.font = newFont
        self.CANVAS.itemconfig(self.label, font=(self.font, self.fontSize))    
        
    def change_font_size(self, newFontSize):
        '''
        Changes the font size to the new font size
        
        :param self: n/a
        :param newFontSize: the desired font size
        '''
        if not self.initialized:
            return
        
        self.fontSize = newFontSize
        self.CANVAS.itemconfig(self.label, font=(self.font, self.fontSize))

    def update(self, framesPassed:int):
        '''
        Updates the sprite
        
        :param self: n/a
        :param framesPassed: the overall frame count
        '''
        if not self.initialized:
            return
        
        if self.wait > 0:
            self.wait -= 1
            self.endChange += 1
        else:
            if self.dX != 0 or self.dY != 0:
                self.change_pos(self.x+self.dX, self.y+self.dY)

                if framesPassed >= self.endChange:
                    self.dX = 0
                    self.dY = 0

            if self.dChars != 0:
                if self.deletingChars:
                    if len(self.text) <= self.dChars:
                        self.deletingChars = False
                        self.change_text("")
                    else:
                        self.charIdx -= self.dChars
                        self.change_text(self.text[:int(self.charIdx)])
                else:
                    self.charIdx += self.dChars
                    if self.charIdx >= len(self.targetText):
                        self.dChars = 0
                        self.change_text(self.targetText)
                    else:
                        self.change_text(self.targetText[:int(self.charIdx)])

class VisCanvas():
    def __init__(self, canvas, screenWidth:int, screenHeight:int):
        '''
        Creates a Canvas
        
        :param self: n/a
        :param canvas: the tkinter canvas
        :param screenWidth: the width of the screen
        :type screenWidth: int
        :param screenHeight: the height of the screen
        :type screenHeight: int
        '''
        self.canvas = canvas
        self.width = screenWidth
        self.height = screenHeight

        self.framesPassed = 0

        self.allSprites = []
        self.taggedSprites = {}
        self.numSprites = 0

        self.paused = False
        self.takingTextInputDuringPause = False
        self.takingTextInput = False
        self.endOnExitKey = False

        self.textInput = ""
        self.shiftDown = True
        self.capsLock = False

    def update(self):
        '''
        Updates all sprites attached to this canvas
        
        :param self: n/a
        '''
        if not self.paused:
            self.framesPassed += 1

            for sprite in self.allSprites:
                sprite.update(self.framesPassed)
        else:
            pass

    def add_sprite(self, newSprite, tags:list|str=[]):
        '''
        Adds a sprite to this canvas to finish initializing it
        
        :param self: n/a
        :param newSprite: the sprite that has been added
        :param tags: a list of string tags that apply to the sprite
        :type tags: list
        '''

        newSprite.initialize(self.canvas)
        self.allSprites.append(newSprite)
        if type(tags) == str:
            # just one tag
            if tags in self.taggedSprites.keys():
                self.taggedSprites[tags].append(newSprite)
            else:
                self.taggedSprites[tags] = [newSprite]
        else:
            # possibly multiple tags
            for tag in tags:
                if tag in self.taggedSprites.keys():
                    self.taggedSprites[tag].append(newSprite)
                else:
                    self.taggedSprites[tag] = [newSprite]

    def get_sprites_with_tag(self, tag:str) -> list:
        '''
        Returns a list of all sprites with the given tag
        
        :param self: n/a
        :param tag: the desired tag
        :type tag: str
        :return: all sprites with the given tag
        :rtype: list
        '''
        return self.taggedSprites[tag]
    
    def check_collision(self, cX1, cY1, w1, h1, cX2, cY2, w2, h2) -> bool:
        retVal = False
        if cX1 > cX2 and cX1 < (cX2 + w2):
            if cY1 > cY2 and cY1 < (cY2 + h2):
                retVal = True
        elif cX2 > cX1 and cX2 < (cX1 + w1):
            if cY2 > cY1 and cY2 < (cY1 + h1):
                retVal = True
        return retVal

    def start_text_input(self, pause=True, endOnExitKey=True):
        '''
        Starts taking text input to get a text entry
        
        :param self: n/a
        :param pause: if true, pauses all other updates until done taking text input
        :param endOnEnter: if true, the text entry ends when the user hits enter/return
        '''
        self.paused = pause
        self.takingTextInputDuringPause = pause
        self.takingTextInput = True
        self.endOnExitKey = endOnExitKey

        self.textInput = ""
    
    def stop_text_input(self):
        self.takingTextInput = False

        if self.paused and self.takingTextInputDuringPause: # paused due to text input
            self.paused = False
    
    def update_keyboard_input(self, keypress):
        if (self.paused and self.takingTextInputDuringPause) or (not self.paused and self.takingTextInput):
            if keypress.lower() in ["backspace", "delete"]:
                self.textInput = self.textInput[:len(self.textInput)-1]
            elif self.endOnExitKey and keypress.lower() in ["escape", "enter", "return"]:
                self.stop_text_input()
            elif keypress.lower() not in IGNORE_CHARS:
                if keypress in CHARS.keys():
                    self.textInput += CHARS[keypress]
                else:
                    self.textInput += keypress
    
    def get_text_input(self) -> str:
        return self.textInput
    
    def update_mouse_click(self, clickX, clickY):
        # TODO check buttons
        return