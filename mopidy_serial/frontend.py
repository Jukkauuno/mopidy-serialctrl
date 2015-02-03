import pykka, serial, time

from mopidy import core

class SerialFrontend(pykka.ThreadingActor, core.coreListener):
	def __init__(self, config, core):
		super(SerialFrontend, self).__init__()
		self.core = core


