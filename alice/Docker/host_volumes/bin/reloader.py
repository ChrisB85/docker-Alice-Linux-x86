#!/home/pi/ProjectAlice/venv/bin/python
# encoding: utf-8

#######!/usr/bin/env python3

import sys
import signal
def terminateProcess(signalNumber, frame):
	sys.exit()
signal.signal(signal.SIGTERM, terminateProcess)
signal.signal(signal.SIGINT, terminateProcess)

import psutil
import os
import subprocess
import time
from threading import Timer
try:
	from watchdog.observers import Observer
except ModuleNotFoundError:
	os.system("/home/pi/ProjectAlice/venv/bin/pip install watchdog")
	from watchdog.observers import Observer

from watchdog.events import PatternMatchingEventHandler


class Reloader():
	"""docstring for Reloader"""
	def __init__(self):
		self.timerStartAlice = None
		self.isInStartAlice = False

		# __pycache__
		self.patterns = "*"
		self.ignore_patterns = ""
		self.ignore_directories = False
		self.case_sensitive = True

		# create the event handler
		self.eventHandler = PatternMatchingEventHandler(self.patterns, self.ignore_patterns,
			self.ignore_directories, self.case_sensitive)

		# Handle all the events
		#self.eventHandler.on_created = self.on_created
		#self.eventHandler.on_deleted = self.on_deleted
		self.eventHandler.on_modified = self.on_modified
		#self.eventHandler.on_moved = self.on_moved

		# Observer
		os.chdir("/home/pi/ProjectAlice/skills")
		self.path = sys.argv[1] if len(sys.argv) > 1 else '.'

		self.recursive = True
		self.observer = Observer()
		self.observer.schedule(self.eventHandler, self.path, recursive=self.recursive)
		self.observer.start()


	#-----------------------------------------------
	def startAlice(self):
		if self.isInStartAlice:
			return
		#print("er  i startAlice")
		self.isInStartAlice = True
		os.system("/home/pi/bin/alice-start > /dev/null 2>&1 &")

		if self.timerStartAlice != None:
			self.timerStartAlice.cancel()
		self.isInStartAlice = False


	#-----------------------------------------------
	def getProcs(self) -> dict:
			"""Return a list of processes matching 'name'."""
			# ls = []
			# for p in psutil.process_iter(["pid", "name", "cmdline"]):
			#         ls.append(p.info)
			# return ls[0]
			dct = dict()
			for p in psutil.process_iter(["pid", "name", "cmdline"]):
							dct.update({p.info["pid"]: {"cmdline": p.info["cmdline"]}})
			return dct


	#-----------------------------------------------
	# Handle all the events
	def on_created(self, event):
		print(f"on_created - hey, {event.src_path} has been created!")
		print()


	#-----------------------------------------------
	def on_deleted(self, event):
		print(f"on_deleted - what the f**k! Someone deleted {event.src_path}!")
		print()


	#-----------------------------------------------
	def on_modified(self, event):
		procsDict = self.getProcs()
		for key in procsDict:
			if 'train' in procsDict[key]["cmdline"]:
				#print(f"Hit: {key} {procsDict[key]}")
				print('Alice is training, wait a while and then enter "ctrl-s" again.')
				print()
				return

		if event.src_path.find("__pycache__") == -1:
			print(f'\nReload, a file is modified, "{event.src_path}", ProjectAlice restarted')
			os.system("kill -2 `ps ax|grep 'venv/bin/python main.py'|grep -v 'grep'|  awk '{print $1}'` > /dev/null 2>&1 &")
			self.timerStartAlice = Timer(1.0, self.startAlice)
			self.timerStartAlice.start()
			print()

	#-----------------------------------------------
	def on_moved(self, event):
		print(f"on_moved - ok ok ok, someone moved {event.src_path} to {event.dest_path}")
		print()


#-----------------------------------------------
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print()
		print('You must provide a Skill to watch')
		print(('Example: ' + os.path.basename(sys.argv[0]) + ' <command> ≃ Lights'))
		print()
		sys.exit(1)

	reloader = Reloader()
	if not os.path.exists('/home/pi/.alice-started'):
		reloader.timerStartAlice = Timer(1.0, reloader.startAlice)
		reloader.timerStartAlice.start()

	try:
		print('Launching your command, "ctrl-c" to stop\n')
		while True:
			time.sleep(1)
	except (KeyboardInterrupt, SystemExit):
		os.system("kill -2 `ps ax|grep 'venv/bin/python main.py'|grep -v 'grep'|  awk '{print $1}'` > /dev/null 2>&1 &")
		try:
			os.unlink("/home/pi/.alice-started'")
		except Exception as e:
			pass
		try:
			reloader.observer.stop()
			reloader.observer.join()
		except Exception as e:
			print(e)

		print('\nDone')