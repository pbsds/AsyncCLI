#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

#todo: maybe change the key valuesto not overide certain utf-8 values?

#special keys:
k_Escape = chr(200)
k_Up = chr(201)
k_Down = chr(202)
k_Left = chr(203)
k_Right = chr(204)
k_Home = chr(205)
k_End = chr(206)
k_Insert = chr(207)
k_Del = chr(208)#same as Delete, no need to differentiate
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
k_Tilde = chr(126)
k_Ignored = chr(254)
k_Unknown = chr(255)

def key2word(k):
	if k in WORDS:
		return WORDS[k]
	return k

def isSpecial(k):
	if k and 222 >= ord(k) >= 200 or k in "\n\b\t":
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
         chr(254):"Ignored",
         chr(255):"Unknown"}
for i in range(12): WORDS[chr(210+i+1)] = "F%i" % (1+i)#F1-F12

if os.name == "nt":#Windows
	import msvcrt, time
	if sys.version_info[0] >= 3:
		_kbcode = os.popen('chcp', 'r').read().split(": ")[-1].split("\n")[0]
	
	#combine these? are they alike?
	_winEscape0Key = {27:k_Ignored,
	                  59:k_F1,
	                  60:k_F2,
	                  61:k_F3,
	                  62:k_F4,
	                  63:k_F5,
	                  64:k_F6,
	                  65:k_F7,
	                  66:k_F8,
	                  67:k_F9,
	                  68:k_F10,
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
	                  133:k_F11,#
	                  134:k_F12,#
	                  71:k_Home,
	                  79:k_End,
	                  82:k_Insert,
	                  83:k_Del,
	                  73:k_PgUp,
	                  81:k_PgDown}
	
	kbhit = msvcrt.kbhit
	
	def getch(raw=False):
		k = msvcrt.getch()
		kord = ord(k)
		
		if kord == 0x03:
			#raise KeyboardInterrupt
			thread.interrupt_main()
		elif raw:
			return k
		
		if kord == ord("\r"):
			return "\n"
		elif kord == 0x1b:
			return k_Escape
		#elif kord == 0x7e:
		#	return k_Tilde
		elif kord in (0x00, 0xe0):
			t = time.time() + 0.05
			while time.time() <= t:
				if msvcrt.kbhit():
					break
			else:
				return k_Unknown
			
			if kord == 0:
				conv = _winEscape0Key
			else:
				conv = _winEscape224Key
			
			k2 = ord(msvcrt.getch())
			
			if k2 in conv:
				return conv[k2]
			else:
				return k_Unknown
		
		if sys.version_info[0] >= 3:
			return k.decode(_kbcode)
		else:
			return k
else:#linux
	import tty, termios, atexit
	from threading import Thread
	if sys.version_info[0] >= 3:
		import queue as Queue, builtins as __builtin__
	else:
		import Queue, __builtin__
	
	#0x1b 0x5b 0xXX 0x7e escape sequences, 0xXX could be ommited
	_escSequenceKey = {}
	_escSequenceKey[0x31] = {49:k_F1,
	                         50:k_F2,
	                         51:k_F3,
	                         52:k_F4,
	                         53:k_F5,
	                         55:k_F6,
	                         56:k_F7,
	                         57:k_F8,
	                         126:k_Home}#only 4 characters
	_escSequenceKey[0x32] = {48:k_F9,
	                         49:k_F10,
	                         51:k_F11,
	                         52:k_F12,
	                         126:k_Insert}#only 4 characters
	_escSequenceKey[0x33] = {126:k_Del}#only 4 characters
	_escSequenceKey[0x34] = {126:k_End}#only 4 characters
	_escSequenceKey[0x35] = {126:k_PgUp}#only 4 characters
	_escSequenceKey[0x36] = {126:k_PgDown}#only 4 characters
	
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
	class Returnator:#watch out
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
			except Queue.Empty:
				k2 = None
			
			if k2 == "\x5b":#escape sequence. mostly arrowkeys and F1-F12
				try:
					k3 = READER.queue.get(timeout=0.05)
					READER.queue.task_done()
				except Queue.Empty:
					k3 = None
				
				if k3 == "\x41":#Up
					return k_Up
				elif k3 == "\x42":#Down
					return k_Down
				elif k3 == "\x43":#Right
					return k_Right
				elif k3 == "\x44":#Left
					return k_Left
				elif ord(k3) in _escSequenceKey:#escape sequence
					try:
						k4 = ord(READER.queue.get(timeout=0.05))
						READER.queue.task_done()
					except Queue.Empty:
						k4 = -1
					
					check = _escSequenceKey[ord(k3)]
					
					if k4 in check:
						if k4 != 126:
							try:
								k5 = READER.queue.get(timeout=0.05)
								READER.queue.task_done()
							except Queue.Empty:
								k5 = None
							
							if k5 == "\x7e":
								return check[k4]
						else:
							return check[k4]
					elif k4 != 126:
						#k5 ignored
						try:
							k5 = READER.queue.get(timeout=0.05)
							READER.queue.task_done()
						except Queue.Empty:
							pass
			elif k2 == None:
				return k_Escape
			else:
				return k_Unknown
		elif k == "\r":
			return "\n"
		elif k == "\x7f":
			return "\b"
		return k


if __name__ == "__main__":
	import time, random
	
	print("\nWelcome to the getch example, try pressing some keys!\n")
	
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

