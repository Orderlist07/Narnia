""" Simplistic "GUI Widgets" for a Pygame screen.
    
    Most widgets receive a 'surface' argument in the constructor.
    This is the pygame surface to which the widget will draw 
    itself when it's draw() method is called.
    
    Unless otherwise specified, all rectangles are pygame.Rect
    instances, and all colors are pygame.Color instances.
"""

import sys
import time
import pygame

from pygame import Rect, Color
from vec2d import vec2d

from game import *
import simpleanimation

from sys import exit
from random import randint

class WidgetError(Exception): pass
class LayoutError(WidgetError): pass





class Box(object):
    """ A rectangular box. Has a background color, and can have
        a border of a different color.
        
        Has a concept of the "internal rect". This is the rect
        inside the border (not including the border itself).
    """
    def __init__(self, 
            surface,
            rect,
            bgcolor,
            border_width=0,
            border_color=Color('black')):
       
       
        """ rect:
                The (outer) rectangle defining the location and
                size of the box on the surface.
            bgcolor: 
                The background color
            border_width:
                Width of the border. If 0, no border is drawn. 
                If > 0, the border is drawn inside the bounding 
                rect of the widget (so take this into account when
                computing internal space of the box).
            border_color:
                Color of the border.
        """
        
        
        self.surface = surface
        self.rect = rect
        self.bgcolor = bgcolor
        self.border_width = border_width
        self.border_color = border_color
        
        # Internal rectangle
        self.in_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
        
    def draw(self):
        pygame.draw.rect(self.surface, self.border_color, self.rect)        
        pygame.draw.rect(self.surface, self.bgcolor, self.in_rect)

    def get_internal_rect(self):
        
        """ The internal rect of the box.
        """
        
        return self.in_rect
        
        

class MessageBoard(object):
   
    """ A rectangular "board" for displaying messages on the 
        screen. Uses a Box with text drawn inside.
        
        The text is a list of lines. It can be retrieved and 
        changed with the .text attribute.
    """
    
    def __init__(self, 
            surface,
            rect,
            text,
            padding,
            font=('arial', 20),
            font_color=Color('white'),
            bgcolor=Color('gray25'),
            border_width=0,
            border_color=Color('black')):
        
        """ rect, bgcolor, border_width, border_color have the 
            same meaning as in the Box widget.
            
            text:
                The initial text of the message board.
            font:
                The font (a name, size tuple) of the message
            font_color:
                The font color
        """
        
        self.surface = surface
        self.rect = rect
        self.text = text
        self.padding = padding
        self.bgcolor = bgcolor
        self.font = pygame.font.SysFont(*font)
        self.font_color = font_color
        self.border_width = border_width
        
        self.box = Box(surface, rect, bgcolor, border_width, border_color)
        
    def draw(self):
        #Draw the surrounding box
        self.box.draw()
        
        # Internal drawing rectangle of the box 
        #
        #
        # Need a method that takes in a width and height of space required for text and padding
        # width, height = self.font.size(text)
        # Calculate required space for text+padding+border
        # utils.get_messagebox_coords(width, height, padding)
        # returns x, y, height, width?
        
        # Internal rectangle where the text is actually drawn
        text_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
            
        x_pos = text_rect.left
        y_pos = text_rect.top 
        
        # Render all the lines of text one below the other
        #
        for line in self.text:
            line_sf = self.font.render(line, True, self.font_color, self.bgcolor)
            
            #test if we can fit text into the MessageBoard + padding
            
            if ( line_sf.get_width() + x_pos + self.padding > self.rect.right or line_sf.get_height() + y_pos + self.padding > self.rect.bottom):
                raise LayoutError('Cannot fit line "%s" in widget' % line)
            
            self.surface.blit(line_sf, (x_pos+self.padding, y_pos+self.padding))
            y_pos += line_sf.get_height()





class Button(object):
	"""     Employs some crap from Box to draw a rectangular button, 
			has some methods to handle click events.
	"""
        
	# needs to be replaced.
	(UNCLICKED, CLICKED) = range(2)
        
	def __init__(self, surface, pos=vec2d(0, 0), btntype="", imgnames=[], text="", textcolor=(0,0,0), 
		textimg=0,padding=0, attached=""):
		print "In button init method"
		self.surface = surface
		self.pos = pos
		self.btntype = btntype
		self.imgnames = imgnames
		self.text = text
		self.textcolor = textcolor
		self.textimg = textimg
		self.padding = padding
		self.attached = attached
		self.state = Button.UNCLICKED
		self.toggle = 0 
			
		#load images
		self.imgs = []
		for name in self.imgnames:
			img = pygame.image.load(name).convert_alpha()
			#img = img.set_colorkey((255,255,255))
			#it would be nice to make the images transparent,
			#but it throws an error not worth fighting
			self.imgs.append(img)
                
		self.imgwidth, self.imgheight = self.imgs[self.toggle].get_size()
		self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)
		print "Image dimensions are: " + str(self.imgwidth) + ", " + str(self.imgheight)
		
		#creates a text label to place in the middle of the button
		font = pygame.font.SysFont("Times New Roman", 25)
		self.textOverlay =  font.render(self.text,1,self.textcolor)
		self.textSize = vec2d(font.size(self.text))
		self.textRect = Rect(self.pos.x+self.imgwidth/2-self.textSize.x/2,self.pos.y+self.imgheight/2-self.textSize.y/2,0,0)
                
                
	def draw(self):
		if self.btntype == "Close":
			self.surface.blit(self.imgs[0], self.rect)
		elif self.btntype == "Toggle":
			self.surface.blit(self.imgs[self.toggle], self.rect)
			if self.toggle == self.textimg:
				self.surface.blit(self.textOverlay, self.textRect)
			
 
	def mouse_click_event(self, pos):
		if self.btntype == "Close":
			if self._point_is_inside(vec2d(pos)):
				self.state = Button.CLICKED
		elif self.btntype == "Toggle":
			if self._point_is_inside(vec2d(pos)):
				self.state = not self.state
				self.toggle = not self.toggle
				self.imgwidth, self.imgheight = self.imgs[self.toggle].get_size()
				self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)
				self.textRect = Rect(self.pos.x+self.imgwidth/2-self.textSize.x/2,self.pos.y+self.imgheight/2-self.textSize.y/2,0,0)
		elif self.btntype == "Action":
			if self._point_is_inside(vec2d(pos)):
				self.count = 100
				expl = simpleanimation.start()
				print "Action"
        
	def _point_is_inside(self, mpos):
		if mpos.x > self.rect.x and mpos.x < self.rect.x+self.imgwidth:
			if mpos.y > self.rect.y and mpos.y < self.rect.y+self.imgheight:
				return True





class textEntry(object):
	""" allows for reading input from the user """        
	def __init__(self, surface, pos=vec2d(0, 0), size = vec2d(200,50), text="", textcolor=(0,0,0),padding=0, bgcolor = (255,255,255)):
		print "In textEntry init method"
		self.surface = surface
		self.pos = pos
		self.size = size
		self.text = text
		self.textcolor = textcolor
		self.padding = padding
		self.clicked = False
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		self.lastKey = ""
		self.delay = 1
		
		#creates a text label to place in the middle of the rectangle
		self.font = pygame.font.SysFont("Times New Roman", 25)
		self.textOverlay =  self.font.render(self.text,1,self.textcolor)
		self.textSize = vec2d(self.font.size(self.text))
		self.textRect = Rect(self.pos.x, self.pos.y, self.textSize.x, self.textSize.y)
                
	def draw(self):
		if self.clicked:
			if pygame.key.get_focused():
				pressed = pygame.key.get_pressed()
				for i in range(len(pressed)):
					if pressed[i] == 1:
						key = pygame.key.name(i)
						if self.lastKey == key and self.delay <= 1:
							#delay time please fix
							self.delay += .4
						elif len(key) == 1 and self.font.size(self.text)[0] <= self.size.x:
							self.text+= key
							self.delay = 0
							self.lastKey = key
						elif key == "tab":
							self.text += "    "
							self.delay = 0
							self.lastKey = key
						elif key == "space":
							self.text += " "
							self.delay = 0
							self.lastKey = key
						elif key == "backspace":
							self.text = self.text[:-1]
							self.delay = 0
							self.lastKey = key
						
						self.textOverlay = self.font.render(self.text,1,self.textcolor)

		pygame.draw.rect(self.surface, (255,255,255), self.rect)
		self.surface.blit(self.textOverlay, self.textRect)
			
	def mouse_click_event(self, pos):
		if self._point_is_inside(vec2d(pos)):
			self.clicked = not self.clicked
        
	def _point_is_inside(self, mpos):
		if mpos.x > self.pos.x and mpos.x < self.pos.x+self.size.x:
			if mpos.y > self.pos.y and mpos.y < self.pos.y+self.size.y:
				return True
				
				
				
				





class movingImg(object):
	def __init__(self, surface, image, pos=vec2d(0,0), speed=vec2d(1,0), gravity=1):
		self.surface = surface
		self.surfaceSize = vec2d(self.surface.get_size())
		self.image = pygame.image.load(image)
		self.pos = pos
		self.speed = speed
		self.gravity = gravity
		self.size = vec2d(self.image.get_size())
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
	
	def draw(self):
		if self.pos.x + self.size.x > self.surfaceSize.x or self.pos.x < 0:
			self.speed.x *= -1
		if self.pos.y + self.size.y > self.surfaceSize.y or self.pos.y < 0:
			self.speed.y *= -1
		self.pos.x += self.speed.x
		self.pos.y += self.speed.y
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		self.surface.blit(self.image, self.rect)







class Scene(object):

	def enter(self):
		print "Welcome to the Chronicles of Narnia."
		print "You are about to embark on the journey of,"
		print "'The Magicians Nephew'"
		pass
		
		
class Engine(object):

	def __init__(self, scene_map):
		self.scene_map = scene_map
		
	def play(self):
		current_scene = self.scene_map.opening_scene()
        last_scene = self.scene_map.next_scene('finished')
        
        while current_scene != last_scene:
            next_scene_name = current_scene.enter()
            current_scene = self.scene_map.next_scene(next_scene_name)
            
            
        current_scene.enter()
		
class Death(Scene):

	quips = [
        "The evil witch has killed you"
    ]

    def enter(self):
        print Death.quips[randint(0, len(self.quips)-1)]
        exit(1)

# This is a game that should play from both first person and top down view?
# Think Zelda (some scenes require top down view like when in a building)
# There should be a home screen to show your inventory (IE: green, yellow rings) 
		
# First Scene
# Introduction to Digory and Polly
# Digory has to find Polly to unlock the next Scene
# If Digory cannot find Polly he will break down and cry
# If Digory tries to leave from the gate which he came in from, he will return to same Scene

class Gardens(Scene):

	def enter(self, Polly):
		print "You 'Digory' have moved into the city and need to find a friend to play with"
		
		if find friend
			print "Why are you sad Digory? Don't you want to play?
			
			#How to include an action and sound effect?		
			action == door unlocks, sound effect
			
			#How to use key strokes walk to door?
			#Is it okay if I use an If statment inside of another If statment?
			#Is there a better way?
			raw_input == ("> ")
			if raw_input == "new door"
				# key music and switch to next_scene
				next_scene(<self, Polly>, <Attic>)
		
		elif exit scene then return next_scene(<self, Polly>, <Gardens>)
		

class Attic(Scene):

	def enter(self, Polly):
		print Digory says: "What is this place?"
		print Polly replies: "I'm not sure but I think we are inbetween the houses in
		print "some kind of secret passage way to the Attic."
		print Digory says: "What a creepy place to be!"
		print Polly replies: "Yeah I am starting to feel chills!...(Hears Sound)
		print "WHAT's THAT NOISE!"
		
		# Digory and Polly are both breathing heavily now.
		# Every 15 seconds Polly or Digory (alternating) say "I'm Scared"
		# If both of them do not move within 30 seconds then Digory starts crying!"
		# Think "Left for dead" creepy feeling.
		
		# They must find a vase with key inside to unlock a locked door at the end of the
		# attic. 
		# This requires a grab function, equip function, and use function.
		# Zelda type functions
		
		raw_input == ('> ')
		if raw_input == grab vase
			print "You have found a key (play sound effect and show key)"
		elif raw_input == grab vase (empty)
			print "There used to be something important in here."
		
		# only if found key then can go to inventory to equip it
		# only if key is equiped then can use it
		if key is equiped and raw_input == open door
			print "This key seems to fit perfectly"
			# There should be a visual/sound effect of door unlocking.
			# Switch to next scene
			next_scene(<self, Polly>, <StudyRoom>)
			
		elif key is not equiped and raw_input == open door
			print "You need something to unlock this door."
			
# Polly and Digory are in a passage and know how to get home but see a dim light from
# underneath a strange door. (The StudyRoom)			
class StudyRoom(Scene):

	def enter(self, Polly, Uncle Andrew):
		print "Oh I know where we are says Digory!"
		print "Hey whats the light coming from that door? says Polly"
		print "Digory replies: 'Lets go look'"
		
		raw_input == ('> ')
		if raw_input == open door [1]
			print "Polly and Digory quietly opened the door and saw Uncle Andrew!"
			print "Before they could say anything they saw two guinea pigs vanish into"
			print "'thin air'!"
			print "Uncle Andrew! Digory exclaims; and before he relised it Uncle Andrew had"
			print "a hold of both of them!"
			print "OH PERFECT! Uncle Andrew says with a mysterious laugh."
			print "I have a present for both of you. Uncle Andrew hands them a cloth with"
			print "something inside."
			print "Polly was more eager than Digory thus she opened it first and saw a"
			print "shiny yellow ring."
			print "When she touched it she vasnished into 'thin air' just like the" 
			print "guinea pigs."
			print "Digory was shocked and scared by what he just saw!"
			print "Digory was about to inquire as Uncle Andrew began to explain: If you"
			print "ever want to see her or the two guinea pigs again you must take this"
			print "yellow ring to go to where she has gone and take these two green rings"
			print "to come back!"
		
		# to prevent a bug there should be a way to prevent from leaving the room without
		# having completed the mission at hand. IE: returning with the Witch
		
				raw_input == ('> ')
			if raw_input == equip yellow ring
				print "Digory finds himself in a wormhole and within mere seconds he falls"
				print "on soft grass.
					next_scene(<self,Polly>, <Sleepywoods>)
			elif raw_input == equip green ring
				print "That is strange nothing happened." 		
				
			
		#action is wrong so should take them back to the Attic scene
		elif raw_input == open door [2]
			print "That's strange how did we get here?"

class Sleepywoods(Scene):

	def enter(self, Polly, 2 guinea pigs):
		if found Polly
			print Digory "Polly is that you!? I have been looking all over for you."
			print Digory "Wake up Polly do not fall asleep again!"
			print Polly "Where are we?"
			print Digory "I do not know but Uncle Andrew tricked us and now I am here to
			print Digory " take you back!"
			print Polly "Okay! but let us take a look around first before we go back."
			print Digory "what are all of these pools?"
			print Polly "I don't know but I think they lead to another world. As if we
			print Polly "are in a woods between worlds."
			
			raw_input == ('> ')
		if raw_input == jump in pool
			print "AHHHHHH! There is darkness, and then slowly there is light!"
			next_scene(<self, Polly>, <AbandonedcityFrozen>)
			

class AbandonedcityFrozen(Scene):

	def enter(self, Polly, Witch):
		print Digory "Wow this place is cold and it looks like everything is dead!"
		print Polly "Maybe there are people inside the city because it is so cold outside?"
		print Polly "Lets go in to check, unless you are scared and want to go back?"
		print Digory "No I am not scared, unless you are scared?"
		print Polly "No I am not scared."
		print Digory "Lets go inside then."
		
		# I am trying to include more choices for a better UX
		# How to allow free movement and exploration within each scene?
		# Does my raw input have to be so 'Limited'?
		# How do I include more sideline stories to make the game seem less linear?
		raw_input == ('> ')
		if raw_input == 'walk into city'
			action == go to the city center
			print "There seems to be something wrong with this city, everything is so quiet"
			print "It seems like everything is dead."
			print "There is a big dining room up ahead."
			print "Maybe there is someone there."

			
			
			raw_input == ('> ')
			if raw_input == 'dinning room'
				# there should be a change in visual/sound effect when entering room
				action == walk into dining room
				print Digory "Wow look Polly, what happened here!?"
				print Digory "Why are there statues sitting at the dinning table?"
				print Polly "I do not know but it seems like they were alive"
				print Polly "and became frozen instantly."
				print Polly "The head of the table seems to be happy but"
				print Polly "the farther you go down the sadder they look."
				print Digory "Look at that beautiful lady at the end! She must be the queen."
				
				# How can you put an object in plane sight, waiting for impulse to enacted
				# upon. IE: Zelda you can click to read a sign and then after 
				# you can perform an action to unlock that puzzle
				print Polly "Look here Digory, there is a hammer with a bell and this"
				print Polly "sign says 'Those who dare to strike the bell"
				print Polly "or else you will go to hell'."

				
				
				raw_input == ('> ')
				if raw_input == 'ring bell'
					print "Despite protests from Polly, Digory rings the bell."
					print "The ground began to shake and there were strange lights in"
					print "the sky. Before Polly and Digory could run out of there one"
					print "of the statues began to move.
					print "It was the queen. She slowly came to life and seemed to be
					print "Taller and Stronger than Digory had imagined before!
					print Witch "Who has rung the bell and awakened me from my slumber!?"
					print Witch "Where is my faithful servant?"
					print "Digory stepped out into the light, trembling with fear."
					print "He thought he might get a prize from this awe powerful queen."
					print Witch "Well, well what do we have here, a child it seems."
					print Witch "Where is your offering, lest I might eat you?"
					print Digory "I don't know about offering but here is my friend Polly"
					print Witch "Oh so you want me to eat your friend!?"
					print Digory "No, No! I mean I am the one who rang the bell 
					print Digory "even though she told me not to."
					print Witch "So I should eat her because she is defiant!"
					print Polly "No please don't eat me!"
					print Digory "No my queen I can go get food and bring it back for you."
					print "Digory and Polly knew that they must leave immediately"
					print "before something bad happens to either of them!"
					print "They both reached into their pockets at the same time,"
					print "but before they could touch their green rings the Queen grabbed
					print "them both by their coats!"
					print "AHHH!"
					next_scene(<self, Polly, Witch>, <StudyRoom>)		
				raw_input == ('> ')

		
class StudyRoom(Scene):

	def enter(self, Polly, Witch, Uncle Andrew):
		print "In a blink of an eye they were back in Uncle Andrew's study room."
		print "Digory thought to himself 'that is strange it seems as if no time has passed
		print "at all even though they had been gone for what seemed for hours!"
		print Polly "Oh no Digory the Witch grabbed our coats and came with us."
		print "Little did polly know that the Witch no longer had her powers in their world."
		print Witch "Now you must be my servent!" "speaking to Uncle Andrew"
		print Uncle Andrew "Why yes ofcourse I am here at your service!"
		print Uncle Andrew "How may I help you?" "speaking in the most curtious way he"
		print Uncle Andrew "possible, because he was in awe of such a beautiful woman."
		print Witch "Fetch me a chariot and take me out of this filth!"
		print Witch "It is time to rule this place you call 'Earth'!"
		print Uncle Andrew "Yes ma'm right away!"
		
		raw_input == ('> ')
		if raw_input == 'open door [1]'
			next_scene(<self, Uncle Anderw, Witch>, <England>)
			
class England(Scene):

	def enter(self, Uncle Andrew, Witch, Cabby):
		print "Uncle Andrew quickly rushed outside and called a cab."
		print Uncle Andrew "Take us through the streets of England to all the fancy stores."
		print "For that was what Uncle Andrew thought the beautiful woman wanted."
		print "Little did he know that the beautiful woman was actually a witch in another world."
		print Cabby "Here we are sir. That would be 5 pence."
		print Witch "Muhaha you are a funny little rodent arent you!"
		print "The Witch walks into the store and grabs all of the jewelry."
		print "Uncle was paralized in shock by what just happened and appologized to the owner."
		print Witch "This is great! Take me to next place!"
		print "At this time the sirens of the police were just down the street"
		
		raw_input == ('> ')
		if raw_input == 'run away'
			next_scene(<self, Uncle Andrew, Witch, Polly, Cabby>, <Crash>)
		elif raw_input == 'stay'
			print "The police have arrested the Witch!"
			print "She stays and rules over 'Earth' until all things die!"
			return Death
		
		
class Crash(Scene):

	def enter(self, Uncle Andrew, Witch, Polly, Cabby):
		print Police "Pull over now or you will face capitol punishment!"
		print Witch "NEVER MUHAHAHA!"
		print Cabby "We should listen to what they say. Oh nooo!"
		print "The cabby lost control of the cab and crashed right into a lampost"
		print "oustide of Digorys house."
		print Digory "Look Polly they came back!"
		print Polly "Oh no Digory it looks like trouble. Look at what we have done."
		print Polly "We should take her back to her world as soon as possible before"
		print Polly "She destorys our world just as she has destroyed hers!"
		print Digory "You are right but how? There are Police and rioters everywhere!"
		
		raw_input == ('> ')
		if raw_input == 'go outside'
			print Digory "No polly its too dangerous. I cannot do it."
			print Polly "Grow a pair of balls and fix the problem you started!"
			
			raw_input == ('> ')
			if raw_input == 'grab the Witch'
				print "Polly and Digory run accros the lawn to the lamp post with bullets"
				print "flying by them left and right. Digory see's his uncle is in danger"
				print "and helps him up! Then Digory and Polly grab on to the Witch."
				
				raw_input == ('> ')
				if raw_input == 'green ring'
					print "You put on the wrong rings and while fumbling for the other"
					print "ring you get shot by a stray bullet!"
					print "Game Over"
					return Death
				elif raw_input == 'yellow ring'
					print Digory "Oh no Polly look what happened!"
					print "Digory and Polly did not realize that the Witch was holding"
					print "onto the cab and the lamp post. In doing so she brought the"
					print "Cabby, Uncle Andrew, the cab and lampost with her."
					next_scene(<self, Uncle Andrew, Polly, Witch, Cabby>, <Sleepywoods>)

class Sleepywoods(Scene):

	def enter(self, Uncle Andrew, Polly, Witch, Cabby):
		print "Polly and Digory look at each other knowing that only they have been in"
		print "the sleepy woods before. They gave each other a look and quick glance"
		print "at the pool in front of them."
		print Digory "Now Polly!"
		
		raw_input == ('> ')
		if raw_input == 'jump in pool'
			print "They both grabbed the Witch and jumped into the pool thinking that it would"
			print "go back to the abandoned city where the Witch came from!"
			print "But no that is not at all what happened."
			next_scene(<self, Uncle Andrew, Polly, Cabby, Witch>, <Newworld>)

class Newworld(Scene):

	def enter(self, Uncle Andrew, Polly, Cabby, Witch,):
		print "It was strange, cold and Dark. Polly cold feel Digory grabbing her hand"
		print "but could not see him."
		print Polly "Digory! she whispered"
		print Digory "I'm right here!"
		print "Then all of sudden there was bring white light that made them all tremble."
		print "And then right before their eyes they could see water and mountains forming."
		print "They saw an entire new world come to life!"
		print "The Witch thought to herself 'This is perfect!' and quietly left."
		
		raw_input == ('> ')
		if raw_input == 'search for Witch'
			print "Where did she go they all thought! But were overcome with a great sleep"
			print "for the Witch had cast a spell on them."
			next_scene(<self, Uncle Andrew, Polly, Cabby>, <Narnia>)
			
class Narnia(Scene):
		
	def enter(self Uncle Andrew, Polly, Cabby, Aslan, Talking Animals):
		print "As they all woke up from their sleep they saw a lion speaking in familiar"
		print "toung. He was speaking to trees and plants and animals."
		print "Strange they all thought because it sounded as if the animals were speaking"
		print "to the Lion also!"
		print Digory "Common guys, quickly get up! The Lion is comming this way!"
		print Aslan "Hello my name is Aslan. What brings you to my world?"
		print "The others were so terrified by the whole seen that they dare not even move."
		print Digory "Responded, hello Aslan, I am Digory and this is Polly. We came here"
		print "to... 'he thought to himself it doesn't feel right to lie I should tell him"
		print "the truth' get rid of this evil Witch who destroys everything in her path!"
		print Aslan "Oh so you are the one who let her into my world!"
		print Aslan "Well then it just seems right that you would be the one to fix what
		print "you have done! How dare you bring evil to my world!"
		print Digory "I am terribly sorry Aslan! I will do anything to make it up to you."
		print Aslan "Here take this fine horse 'It was the cabbys horse' and go up to the"
		print "tallest mountain and get an apple from that tree and bring it back to me."
		print "Do not eat from that tree or take something that is not yours!"
		print Digory "Yes sir."
		print "Aslan at that moment took a deep breath and blew on the horses face."
		print "Instantly the horse transformed before everyones eyes and grew wings!"
		print "They all stood in awe of what just Happened."
		print Aslan "Now GO!"
		
		raw_input == ('> ')
		if raw_input == 'mountain'
			next_scene(<self, Polly>, <GardenMountain>)
		elif raw_input == 'stay'
			print "You pissed off Aslan and got struck by lightning!"
			return Death
class GardenMountain(Scene):

	def enter(self):
		pass
		
class Narnia(Scene):

	def enter(self):
		pass

class Attic(Scene):

	def enter(self):
		pass

class Mansion(Scene):

	def enter(self):
		pass
			
class Map(object):

    def __init__(self, start_scene):
        pass

    def next_scene(self, scene_name):
        pass

    def opening_scene(self):
        pass


a_map = Map('Gardens')
a_game = Engine(a_map)
a_game.play()