#!/usr/bin/python
#replaces input() in python3 and raw_input() in python2, with one with a asynchronous interface
import sys, threading

def input(prompt = ""):
	"""
	First time it's called, it starts prompting the user for a line of input.
	After the user has returned a line, the function will return the result as a string
	If called after this, then a new prompt will be started.
	"""
	global _listener
	if not _listener:
		_listener = _reader(prompt)
		_listener.start()
		return None
	elif _listener.isAlive():
		return None
	else:
		if _listener.result != None:
			ret = _listener.result
			_listener = None
			return ret
		else:#softlocked?
			return None


#private:
_listener = None
class _reader(threading.Thread):
	def __init__(self, prompt):
		threading.Thread.__init__(self)
		self.daemon = True
		
		self.prompt = prompt
		self.result = None
	def run(self):
		if sys.version_info[0] >= 3:
			ech = input(self.prompt)
		else:
			ech = raw_input(self.prompt)
		self.result = ech

#example:
if __name__ == "__main__":
	import os
	if os.name == "nt":#windows
		def setColor(n = None):
			if n != None:
				os.system("color %x" % n)
			else:
				os.system("color 7")
		def clean():
			os.system("cls")
	else:#unix
		def setColor(n = None):
			pass
		def clean():
			os.system("clear")
	
	clean()
	print("Welcome to the input example!")
	
	n = 0
	while 1:
		query = input("Please write something: ")
		
		if query:
			print("Result: %s" % query)
			setColor()#color cleanup
			break
		else:
			setColor(n)
			n = (n+1)%16