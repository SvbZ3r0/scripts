#!/usr/bin/env python

# Original work © 2014 Alan Dillman
# Modified work © 2020 $vBZ3r0
# This Software Is Licensed Under The WTFPL: Http://Www.Wtfpl.Net/
# In A Nutshell: Do Whatever You Want With It. Have Fun Learning.

import sys, os

# Output file uses name of calling script
filename = os.path.basename(__file__.split('.py', -1)[0].capitalize())
todo_file = os.path.join(os.path.dirname(sys.argv[0]), 'data', 'Notes', f'{filename}.todo')

class ListHandler(object):
	def __init__(self):
		self.cmds = {
				"add":self.add_task, 
				"del":self.del_task,
				"sub":self.del_task,
				"rot":self.rotate_tasks,
				"prom":self.promote_task, # promote item
				"demo":self.demote_task, # demote item in list
				"pop":self.pop_task
				}
		try:
			with open(todo_file, 'r') as f:
				show, self.noshow = f.read().split('<donotshow>')
				show = [i for i in show.split('\n') if i]
			self.tasks = [line.split('‐ ', 1)[1].rstrip() for line in show]
			# Encoding issue with Rainmeter. Use ‐ not -

		except IOError:
			self.tasks = []

	def add_task(self, string):
		self.tasks.append(string)

	def del_task(self, number):
		try:
			del self.tasks[int(number)-1]
		except IndexError:
			print(f'The list does not contain {number} elements.')

	def pop_task(self, ignored):
		try:
			del self.tasks[0]
		except IndexError:
			print('The list does not contain any elements.')

	def rotate_tasks(self, steps):
		number = int(steps)
		self.tasks = self.tasks[number:] + self.tasks[:number]

	def promote_task(self, number):
		num = int(number)
		curr_task = self.tasks[num-1]
		self.tasks.insert(max(0, num-2), curr_task)
		del self.tasks[num]

	def demote_task(self, number):
		num = int(number)
		curr_task = self.tasks[num-1]
		self.tasks.insert(num+1, curr_task)
		del self.tasks[num-1]

	def parse(self, args):
		try:
			# Here I would fix it to be aware of types. args[2] might be
			# a string or a number, but it could also be a number
			# intended as a string. No easy solution? Must research.
			if len(args) > 2:
				self.data = args[2]
			else:
				self.data = 0 # will be ignored too
			self.func = args[1]
		except IndexError:
			self.list_tasks()
		else:
			self.cmds[self.func](self.data)

	def list_tasks(self):
		for i, item in enumerate(self.tasks):
			print(f'{i+1} {item}')

	def update_file(self):
		with open(todo_file, 'w') as f:
			for line in self.tasks:
				f.write(f'‐ {line}\n\n')
			f.write('<donotshow>')
			f.write(self.noshow)

if __name__ == '__main__':
	todo = ListHandler()
	todo.parse(sys.argv)
	todo.update_file()

