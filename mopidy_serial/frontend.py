import pykka
import serial
import logging

from mopidy import core

logger = logging.getLogger(__name__)

class SerialFrontend(pykka.ThreadingActor, core.CoreListener):
	def __init__(self, config, core):
		super(SerialFrontend, self).__init__()
		self.core = core
		
		logger.info('Setting serial...')
		
		# Serial setup
		self.ser = serial.Serial((config['serial']['port']), (config['serial']['baud']))
		
		logger.info('Serial set!')

		self.current_volume = 0

		# Channel initialization
		self.playlists = None
		self.channel_current = 0
		self.channel_1 = None
		self.channel_2 = None

		self.main_loop()

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
		
		logger.info('Entered main loop')

		while(1>0):
			self.message = self.ser.readline()

			self.volume, self.channel = self.message.split(',')

			logger.info('Volume:', self.volume)

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

		self.ser.close()
