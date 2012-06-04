from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr

def __init__():
    pass
    

class VoiceBot(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, owner='', speech_queue=None):
        #TBD error check the var type for deque
        self.speech_queue = speech_queue
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.owner = owner
        self.last_sender = ''
        self.pronounce_dict = {
            'api':'API',
            'lol':'ha ha',
            'lolol':'ha ha',
            'brb':'be right back',
            'thx':'thanks',
            'yeah':'ya',
            
        }
    
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def cleanwords(self,s):
        """cleans each word for better text to speech"""
        #print s
        
        if s.startswith((':','http')):
            if s.startswith('http'):
                return 'weblink'
        if s.lower() in self.pronounce_dict:
            return self.pronounce_dict[s.lower()]
            
        return s
        
    def on_pubmsg(self, c, e):
        #print e.source()
        #print e.arguments()
        sender = e.source().split('!',1)[0]
        if self.last_sender == sender:
            #skip the intro
            speech = e.arguments()[0].replace(':',',',1)
        else:
            self.last_sender = sender
            speech = sender + ', ' + e.arguments()[0].replace(':',',',1)
        speech = speech.replace('_',' ')
        #print speech
        old_words = speech.split()
        new_words = [self.cleanwords(a_word) for a_word in old_words]
        text_to_speak = ' '.join(new_words)
        cmd = 'say "%s"' % text_to_speak
        self.speech_queue.appendleft(text_to_speak)
        return


    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection
        if self.owner and self.owner not in nick:
            c.notice(nick,"you are not my owner")
            return
        if cmd == "disconnect":
            self.broadcast.close()
            self.disconnect()
        elif cmd == "die":
            self.die(msg="")

        else:
            c.notice(nick, "Not understood: " + cmd)
