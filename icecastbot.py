#!/usr/bin/env python

import sys
from voicebot import *
import shout
import time
from subprocess import Popen, PIPE
from threading import Thread, activeCount
from collections import deque
#globals
speech_queue = None
bot_thread = None
ice_thread = None
bot_dead = False

     
class BotThread(Thread):
    def __init__ (self):
        Thread.__init__(self)
        # channel, bot-nick, server, port, owner-nick
        global speech_queue
        
        self.bot = VoiceBot(
            '#auzland',                  #IRC Channel
            'Voicebot',                 #unique nick name for bot
            'irc.0id.net',         #IRC server
            6667,                       #server port
            owner='KpaBap',           #your nick (bot only responds to you)
            speech_queue=speech_queue   #the data structure shared by threads
            )
            
            
    def run(self):
        """docstring for run"""
        self.bot.start()

class IceSource(Thread):
    def __init__(self):
        Thread.__init__(self)
        
        musicflag = 0 ### set to 1 for music or 0 for silence between speech
        
        beep_file = 'morse.aiff.mp3'
        
        self.silence = []
        
        if musicflag == 1:
          self.silence = []
         
          for silchunk in range(1,11):
            silence_file = '%s.mp3' % silchunk
            #print "Read in %s.mp3" % silchunk
            
            
            f = open(silence_file,'rb')
            self.silence.append(f.read())
            f.close()
            
        elif musicflag == 0:
          self.silence.append(open("silence.true.mp3","rb").read())
        
        
        ##print self.silence
        
        
        f = open(beep_file,'rb')
        self.beep = f.read()
        f.close()
        s = shout.Shout()
        s.host = 'irc.00id.net'
        s.port = 8000
        s.user = 'source'
        s.password = '<password>' #the source password as defined in your icecast.xml
        s.mount = "/stream"
        s.format = 'mp3'#'vorbis' | 'mp3'
        # s.protocol = 'http' | 'xaudiocast' | 'icy'
        # s.name = ''
        # s.genre = ''
        # s.url = ''
        # s.public = 0 | 1
        s.audio_info = { 'shout.SHOUT_AI_BITRATE': '48'}
        #  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
        #   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)        
        self.broadcast = s
        self.broadcast.open()
        
    def chunks(self,s, n):
      """Produce `n`-character chunks from `s`."""
      for start in range(0, len(s), n):
          yield s[start:start+n]
        
    def run(self):
        """docstring for run"""
        global speech_queue,bot_thread
        
        cur_chunk = 0
        last_chunk = len(self.silence)
        beep = self.beep               
        while 1:
            
            silence = self.silence[cur_chunk]
            #print "Current chunk is " + str(cur_chunk)
            if activeCount() < 3:
                #the bot thread has died
                return
            if speech_queue:
                s = speech_queue.pop()
                #print s
                command = """echo %s | txt2mp3""" % str(s)
                #print command
                d = Popen(command,shell=True,stdout=PIPE,stderr=PIPE).communicate()[0]
                self.broadcast.send(beep)
                self.broadcast.set_metadata({'song':s})
                self.broadcast.sync()
                self.broadcast.send(d)
                self.broadcast.sync()
                self.broadcast.send(silence)
                self.broadcast.sync()
            else:
                self.broadcast.send(silence)
                self.broadcast.sync()
                #print "Chunk sent"

            if cur_chunk < last_chunk-1:
              cur_chunk+=1
            else:
              cur_chunk=0


def main():
    global speech_queue, bot_thread, ice_thread
    speech_queue = deque()
    bot_thread = BotThread()
    ice_thread = IceSource()
    bot_thread.start()
    ice_thread.start()
    bot_thread.join()



if __name__ == '__main__':
            main()