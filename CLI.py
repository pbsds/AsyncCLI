from getch import getch, isSpecial as keyIsSpecial, k_Left, k_Right, k_Del, k_Home, k_End
from threading import Thread
import sys, os, time, __builtin__, Queue

#todo:
#add the option of letting the daemon call CommandLineInterface.refresh_prompt()

class CommandLineInterface():
	class Daemon(Thread):
		def __init__(self, cli):
			Thread.__init__(self)
			self.daemon = True
			self.cli = cli
		def run(self):
			while 1:
				k = getch()
				self.cli.queue.put(k)
		
	markerGuard = 8
	refreshTime = 0.5#seconds
	def __init__(self, replacePrint=False):#replacePrint:python3 only
		#what should be in front of the prompt:
		self.prompt = " > "
		self.markerBack = 0
		
		#the buffer for what is currently in the prompt:
		self.line = []#string instead?
		self.inputs = []#submitted lines
		self.updated = True
		
		#os specific stuff:
		if os.name == "nt":#windows
			self.clearCMD = "cls"
		else:#unix
			self.clearCMD = "clear"
		
		if replacePrint and sys.version_info[0] >= 3:
			eval("__builtin__.print = self.printf")
		
		#timers:
		self.twTimer = 0
		self.twValue = None
		
		#daemon:
		self.queue = Queue.Queue()
		self.daemon = self.Daemon(self)
		self.daemon.start()
		
		self.refresh_prompt()
	@property
	def terminal_width(self):
		if os.name == "nt":
			return 80
		else:
			if time.time()-self.twTimer > self.refreshTime:				
				try:
					_, width = map(int, os.popen('stty size', 'r').read().split())
				except ValueError:
					width = 80
				self.twTimer = time.time()
				self.twValue = width
				return width
			else:
				return self.twValue
	def clear(self, lineOnly=False):
		if lineOnly:
			sys.stdout.write("\r%s\r" % (" "*(self.terminal_width-1)))
		else:
			os.system(self.clearCMD, clear=False)
			self.refresh_prompt(force=True)
	def printf(self, *text, **kwargs):#sep=" ", end="\n", file=sys.stdout, end is sadly ignored if file==sys.stdout
		sep = " "
		if "sep" in kwargs:
			sep = kwargs["sep"]
		end = "\n"
		if "end" in kwargs:
			end = kwargs["end"]
		
		if "file" not in kwargs or kwargs["file"] is sys.stdin:
			self.clear(lineOnly=True)
			sys.stdout.write(sep.join(text))
			sys.stdout.write("\n")#(end)
			#sys.stdout.flush()#handled in the refresh below
			self.refresh_prompt(clear=False, force=True)
		else:
			kwargs["file"].write(sep.join(text))
			if end:
				kwargs["file"].write(end)
			kwargs["file"].flush()
	def input(self, block=False, doPrompt=True):#returns the input line if any is inputted, returns None if not and not blicking. does not block
		if doPrompt:
			self.refresh_prompt()
		
		if self.inputs:
			return self.inputs.pop(0)
		
		if block:
			while not self.inputs:
				time.sleep(0.2)
				if doPrompt:
					self.refresh_prompt()
				
			return self.inputs.pop(0)
		
		return None
	def setPrompt(self, prompt=" > "):
		self.prompt = prompt
		self.refresh_prompt()
	#private helpers:
	def refresh_line(self):
		while not self.queue.empty():
			k = self.queue.get()
			self.queue.task_done()
			didSomething = True
			
			if k == k_Left:
				if self.markerBack < len(self.line):
					self.markerBack += 1
			elif k == k_Right:
				if self.markerBack > 0:
					self.markerBack -= 1
			elif k == k_Home:
				self.markerBack = len(self.line)
			elif k == k_End:
				self.markerBack = 0
			elif k in ("\b", k_Del):
				dir = 0 if k == k_Del else -1
				if self.line and ((self.markerBack < len(self.line) and dir) or (self.markerBack > 0 and not dir)):
					self.line.pop(dir - self.markerBack)
					if not dir:
						self.markerBack -= 1
			elif k == "\n":
				self.inputs.append("".join(self.line))
				self.line = []
				self.markerBack = 0
			elif keyIsSpecial(k):
				didSomething = False
			else:
				if not self.markerBack:
					self.line.append(k)
				else:
					self.line.insert(-self.markerBack, k)
			
			if didSomething:
				self.updated = True
	def refresh_prompt(self, clear=True, doLine=True, force=False):
		if doLine:
			self.refresh_line()
		if self.updated or force:
			if clear:
				self.clear(lineOnly=True)
				#sys.stdout.write("\b")
			sys.stdout.write(self.prompt)
			
			
			#determine what window of line to print:
			linelen = len(self.line)
			back = linelen - self.terminal_width + 1 + len(self.prompt)
			mpos = linelen-self.markerBack
			back = min(back, mpos-self.markerGuard)
			
			if back < 0:
				back = 0
			
			#print the prompt
			sys.stdout.write("".join(self.line[back:back+self.terminal_width-1-len(self.prompt)]))
			
			#position the marker
			if self.markerBack:
				scroll = max(0, linelen+len(self.prompt)+1 - self.terminal_width) - back
				sys.stdout.write("\b" * (self.markerBack - scroll))
				sys.stdout.write("#\b")#todo: make this blink
			
			sys.stdout.flush()
			self.updated = False

#aliases:
CLI = CommandLineInterface

if __name__ == "__main__":
	cli = CLI()
	cli.printf("Welcome to the CLI echo example, hit ctrl-c to exit\n")
	
	epoch = time.time()-1
	i = 1
	while 1:
		line = cli.input()#should be called often, as updates happens here
		
		if line:
			cli.printf("You said: %s" % line)
		
		if time.time()-epoch > 1.5:
			epoch = time.time()
			cli.printf("%i You can write in the prompt while the program prints undisturbed" % i)
			i += 1



