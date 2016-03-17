#!/usr/bin/python2
# -*- coding: utf-8 -*-
#not tested on python 3, but should(?) be compliant
#from __future__ import print_function
import sys, os
if sys.version_info[0] >= 3:
	import _thread as thread
else:
	import thread

#getch.py mainly provices 3 functions:
#	- getch(raw=False):
#		blocks until a key has been pressed, then returns it
#		set raw to True, to disable any key conversion
#		each key is mapped to a character, have a look below under "special keys"
#	- kbhit():
#		returns True if a key has been hit. if True, then the next call to getch() won't block, at least more than 50ms
#	- key2word(key):
#		converts a key returned by getch() into a word, mainly used for printing
#	- isSpecial(key):
#		returns True if the key is a special key and not a character, with space excluded from the special keys

#special keys:
k_Escape = chr(200)
k_Up = chr(201)
k_Down = chr(202)
k_Left = chr(203)
k_Right = chr(204)
k_Home = chr(205)
k_End = chr(206)
k_Insert = chr(207)
k_Del = chr(208)#same as Delete
k_PgUp = chr(209)
k_PgDown = chr(210)
k_F1 = chr(211)
k_F2 = chr(212)
k_F3 = chr(213)
k_F4 = chr(214)
k_F5 = chr(215)
k_F6 = chr(216)
k_F7 = chr(217)
k_F8 = chr(218)
k_F9 = chr(219)
k_F10 = chr(220)
k_F11 = chr(221)
k_F12 = chr(222)
k_Tab = "\t"
k_Backspace = "\b"
k_Space = " "
k_Enter = "\n"
k_Return = "\n"#alias

#Todo linux and windows compatible:
k_Tilde = chr(126)#escape

k_Ignored = chr(254)
k_Unknown = chr(255)

def key2word(k):
	if k in WORDS:
		return WORDS[k]
	return k

def isSpecial(k):
	if k and ord(k) >= 200 or k in "\n\b\t":
		return True
	return False

#Namedictionary, can be changed if needed:
WORDS = {chr(200):"Escape",
         chr(201):"Up",
         chr(202):"Down",
         chr(203):"Left",
         chr(204):"Right",
         chr(205):"Home",
         chr(206):"End",
         chr(207):"Insert",
         chr(208):"Del",
         chr(209):"Page Up",
         chr(210):"Page Down",
		 "\t":"Tab",
		 "\b":"Backspace",
		 " ":"Space",
		 "\n":"Enter",
         chr(255):"Unknown"}
for i in range(12): WORDS[chr(210+i+1)] = "F%i" % (1+i)#F1-F12

if os.name == "nt":#Windows
	import msvcrt, time
	_winEscape0Key = {27:k_Ignored,
	                  83:k_Del,#delete
	                  71:k_Home,#numpad
	                  73:k_PgUp,#numpad
	                  81:k_PgDown,#numpad
	                  79:k_End,#numpad
	                  72:k_Up,#numpad
	                  80:k_Down,#numpad
	                  75:k_Left,#numpad
	                  77:k_Right,#numpad
	                  82:k_Insert,#numpad
	                  131:k_Ignored}#áéíóúý modifier
	_winEscape224Key={72:k_Up,
	                  80:k_Down,
	                  75:k_Left,
	                  77:k_Right,
	                  113:k_F11,
	                  134:k_F12,
	                  71:k_Home,
	                  79:k_End,
	                  82:k_Insert,
	                  83:k_Del,
	                  73:k_PgUp,
	                  81:k_PgDown}
	
	kbhit = msvcrt.kbhit
	
	def getch(raw=False):
		k = msvcrt.getch()
		if k == "\x03":
			#raise KeyboardInterrupt
			thread.interrupt_main()
		elif raw:
			return k
		
		if k == "\r":
			return "\n"
		elif k == "\x1b":
			return k_Escape
		#elif k == "\x7e":
		#	return k_Tilde
		elif k in ("\x00", "\xe0"):
			t = time.time() + 0.05
			while time.time() <= t:
				if msvcrt.kbhit():
					break
			else:
				return k_Unknown
			
			if k == "\x00":
				conv = _winEscape0Key
			else:
				conv = _winEscape224Key
			
			k2 = ord(msvcrt.getch())
			
			if k2 in conv:
				return conv[k2]
			else:
				return k_Unknown
			
		return k
else:#linux
	import tty, termios, atexit, Queue, __builtin__
	from threading import Thread
	
	class _reader(Thread):
		def __init__(self):
			Thread.__init__(self)
			self.daemon = True
			self.queue = Queue.Queue()
			
		def run(self):#reads the stdin
			#set terminal to raw mode:
			fd = sys.stdin.fileno()
			old_settings = termios.tcgetattr(fd)
			tty.setraw(fd)
			atexit.register(termios.tcsetattr, fd, termios.TCSADRAIN, old_settings)
			#atexit.register(lambda: print("\r\n"))
			
			#read the terminal:
			while 1:
				k = sys.stdin.read(1)
				if k == "\x03":
					#raise KeyboardInterrupt
					thread.interrupt_main()
				self.queue.put(k)
	
	READER = _reader()
	READER.start()
	
	#override the stdout and stderr to compensate for the raw terminal mode
	class Returnator:
		file = None
		def __init__(self, dest):
			self.file = dest
		def write(self, text):
			self.file.write(text.replace("\n", "\r\n"))
		def flush(self):
			self.file.flush()
	sys.stdout = Returnator(sys.stdout)#is this global?
	sys.stderr = Returnator(sys.stderr)#is this global?
	
	def kbhit():
		return not READER.queue.empty()
	
	def getch(raw=False):
		k = READER.queue.get()
		READER.queue.task_done()
		if raw:
			return k
		
		if k == "\x1b":#escape
			k = k_Escape
			
			try:
				k2 = READER.queue.get(timeout=0.05)
				READER.queue.task_done()
			except Empty:
				k2 = None
			
			if k2 == "\x5b":#arrowkeys and F1-F12
				try:
					k3 = READER.queue.get(timeout=0.05)
					READER.queue.task_done()
				except Empty:
					k3 = None
				
				if k3 == "\x41":#Up
					return k_Up
				elif k3 == "\x42":#Down
					return k_Down
				elif k3 == "\x43":#Right
					return k_Right
				elif k3 == "\x44":#Left
					return k_Left
				elif k3 == "\x31":#F1-F8
					try:
						k4 = ord(READER.queue.get(timeout=0.05))
						READER.queue.task_done()
					except Empty:
						k4 = -1
					
					if k4 >= 55:
						k4 -= 1#i can't even
					if 1 <= k4-48 <= 8:
						out = (k_F1, k_F2, k_F3, k_F4, k_F5, k_F6, k_F7, k_F8)[k4-49]
								
						try:
							k5 = READER.queue.get(timeout=0.05)
							READER.queue.task_done()
						except Empty:
							k5 = None
						
						if k5 == "\x7e":
							return out
				elif k3 == "\x32":#F9-F12
					try:
						k4 = ord(READER.queue.get(timeout=0.05))
						READER.queue.task_done()
					except Empty:
						k4 = -1
					
					if k4 >= 51:
						k4 -= 1#i can't even
					if 1 <= k4-47 <= 4:
						out = (k_F9, k_F10, k_F11, k_F12)[k4-48]
						
						try:
							k5 = READER.queue.get(timeout=0.05)
							READER.queue.task_done()
						except Empty:
							k5 = None
						
						if k5 == "\x7e":
							return out
			elif k2 == None:
				return k_Escape
			else:
				return k_Unknown
		elif k == "\r":
			return "\n"
		
		return k


if __name__ == "__main__":
	import time, random
	
	print("Welcome to the getch example, try pressing some keys!\n")
	
	doAsync = True
	doRaw = False
	if len(sys.argv) > 1:
		if sys.argv[1] == "raw":
			doRaw = True
	
	i = 0
	top = 40
	while 1:
		if kbhit():
			k = getch(raw=doRaw)
			#print("\r" + " "*79 + "\r0x%.2X,% 12s, Dec: %i" % (ord(k), key2word(k), ord(k)))
			print("0x%.2X,% 12s, Dec: %i" % (ord(k), key2word(k), ord(k)) + " "*45)
		elif doAsync:
			sys.stdout.write("Asynchronous work: [%s%s] %.2f%%\r" % ("="*int(i+0.5), "-"*(top-int(i+0.5)), float(i)/top*100.))
			sys.stdout.flush()
			time.sleep(0.1)
			i += random.random()
			if i >= top:
				i -= top

