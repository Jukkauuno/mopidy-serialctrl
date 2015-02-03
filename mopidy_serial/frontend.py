import pykka
import serial

from mopidy import core

class SerialFrontend(pykka.ThreadingActor, core.coreListener):
	def __init__(self, config, core):
		super(SerialFrontend, self).__init__()
		self.core = core
	
		# Serial setup
		self.ser = serial.Serial((config['serial']['port']), (config['serial']['baud']))
		
		self.current_volume = 0

		# Channel initialization
		self.playlists = None
		self.channel_current = 0
		self.channel_1 = None
		self.channel_2 = None

	def get_channels(self):
		self.playlists = []
		
		for playlist in self.frontend.core.playlists.playlists.get():
			if playlist.name == config['serial']['channel_1']:
				self.channel_1 = playlist
			elif playlist.name == config['serial']['channel_2']:
				self.channel_2 = playlist

	def set_channels(self, channel):
		self.core.tracklist.clear()
		self.core.tracklist.add(uri=channel.uri)
		self.core.playback.play()	

	def main_loop(self):
		self.message = self.ser.readline()

		self.volume, self.channel = self.message.split(',')

		# Set volume
		if self.volume != current_volume:
			self.core.playback.volume = self.volume
			self.current_volume = self.volume
		else:
			self.current_volume = self.current_volume

			
		if self.channel != self.current_channel:
			if self.channel == '1':
				self.set_channels(channel_1)
			elif self.channel == '2':
				self.set_channels(channel_2)
			else:
				self.ser.printline("CHN SET ERR")
