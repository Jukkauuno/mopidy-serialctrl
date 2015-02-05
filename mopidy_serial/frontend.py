import pykka
import serial
import logging
import pygame
import os
import atexit

from pygame.locals import *

from mopidy import core

logger = logging.getLogger(__name__)

class SerialFrontend(pykka.ThreadingActor, core.CoreListener):
	def __init__(self, config, core):
		super(SerialFrontend, self).__init__()
		self.core = core
		self.pygame = pygame
		
		self.running = 1
		
		self.pygame.init()
		self.pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), 'static.mp3'))
		self.pygame.mixer.music.play(-1)		

		logger.info('Setting serial...')
		
		# Serial setup
		self.ser = serial.Serial((config['serial']['port']), (config['serial']['baud']))
		
		logger.info('Serial set!')

		self.old_message = None

		self.current_volume = 0

		# Channel initialization
		self.playlists = None
		self.current_channel = None
		self.channel_1 = None
		self.channel_2 = None
		
		self.channel_1_name = config['serial']['channel_1']
		self.channel_2_name = config['serial']['channel_2']

	#def on_start(self):
		#self.get_channels()

	def playlists_loaded(self):
		logger.info('Getting playlists...')
		
		for playlist in self.core.playlists.playlists.get():
			logger.info('Playlist name: ' + playlist.name)
			if self.channel_1_name in playlist.name:
				logger.info('Channel 1 found: ' + playlist.name)
				self.channel_1 = playlist
			elif self.channel_2_name in playlist.name:
				logger.info('Channel 2 found: ' + playlist.name)
				self.channel_2 = playlist
		
		logger.info('Playlists loaded!')	
		self.main_loop()

	def set_channels(self, channel):
		logger.info('Setting channel...')
		logger.info('Trying to play: ' + channel.uri)
		self.core.tracklist.add(uri=channel.uri)
		logger.info('Playlist: ' + channel.name + ' loaded...')
		self.core.tracklist.shuffle()
		self.core.playback.play()
		logger.info('Should play...')	

	def main_loop(self):
		
		logger.info('Entered main loop')

		self.buffer = ''

		while(self.running == 1):
			
			#logger.info('Reading serial message...')
			
			if '\n' in self.buffer:
				pass
			else:
				self.buffer += self.ser.read(1)

			self.buffer += self.ser.read(self.ser.inWaiting())
			if '\n' in self.buffer:
				self.message, self.buffer = self.buffer.split('\n')[-2:]
			
			#logger.info('Serial message: ' + self.message)

			if self.message is not None and self.message != self.old_message:
				self.old_message = self.message

				logger.info('Message: ' + self.message)
				
				try:	
					self.volume, self.channel = self.message.split('/')
					logger.info('Message splitted to volume and channel!')
				except:
					logger.info('Could not split the message :(')
					pass

				logger.info('Volume: '+ self.volume)
				logger.info('Channel: ' + self.channel)

				# Set volume
				if self.volume != self.current_volume:
					self.core.playback.volume = self.volume
					self.current_volume = self.volume
				else:
					self.current_volume = self.current_volume
			
				if self.channel != self.current_channel:
					self.current_channel = self.channel
					if '1' in self.channel:
						self.core.playback.stop()
						self.core.tracklist.clear()
						self.pygame.mixer.music.stop()
						logger.info('Launching channel 1: ' + self.channel_1.name)
						self.set_channels(self.channel_1)
					elif '2' in self.channel:
						self.core.playback.stop()
						self.core.tracklist.clear()
						self.pygame.mixer.music.play(-1)
						#self.set_channels(self.channel_2)
					else:
						self.core.playback.stop()
						self.core.tracklist.clear()
						self.pygame.mixer.music.play(-1)

		
	def exit_handler():
		logger.info('Starting exit routine...')
		self.running = 0
		logger.info('Main loop terminated...')
		self.ser.close()
		logger.info('Serial connection closed. Good bye.')

	atexit.register(exit_handler)
