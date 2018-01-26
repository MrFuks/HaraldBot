'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import sys
import irc.bot
import requests
import json
import multiprocessing
import time
import string

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        print(json.dumps(r, indent=4, sort_keys=True))
        self.channel_id = r['users'][0]['_id']

        chatters = requests.get('https://tmi.twitch.tv/group/user/' + channel + '/chatters').json()
        print(json.dumps(chatters,indent=4, sort_keys=True))

        p = multiprocessing.Process(target=TwoPool ,args=(channel,))
        p.start()
        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)


    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        print(e)
        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):

        print(e.source.split("!")[0])
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        else:
            cmd = parseInput(e.arguments[0])
            self.do_command(e,cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection

        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            #print(json.dumps(r, indent=4, sort_keys=True))
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

        # Provide basic information to viewers for specific commands
        elif cmd == "raffle":
            message = "This is an example bot, replace this text with your raffle text."
            c.privmsg(self.channel, message)
        elif cmd == "schedule":
            message = "This is an example bot, replace this text with your schedule text."
            c.privmsg(self.channel, message)

        elif ":" in cmd:
            c.privmsg(self.channel,"chuj nie " + cmd)
            time.sleep(2)
            c.privmsg(self.channel,"mentalnie te gre wygralem")
            time.sleep(2)
            c.privmsg(self.channel,"bo miales chujowy build")
            time.sleep(2)
            c.privmsg(self.channel,"/timeout " + e.source.split("!")[0] + " 30")
        # The command was not recognized
        else:
            pass

    def test(self, message):
        print(message)

def main():
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username  = sys.argv[1]
    client_id = sys.argv[2]
    token     = sys.argv[3]
    channel   = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

def TwoPool(channel):
    while True:
        time.sleep(3)
        try:
            chatters = requests.get('https://tmi.twitch.tv/group/user/' + channel + '/chatters').json()
        except:
            pass
        #print(json.dumps(chatters,indent=4, sort_keys=True))

def parseInput(message):

    for m in message.split(' '):
        if ':' in m:
            try:
                a, b = m.strip(string.ascii_letters).split(':')
                if (int(a) > int(b)) and isHaraldRaging():
                    return a+":"+b
            except:
                pass
        if '-' in m:
            try:
                a, b = m.strip(string.ascii_letters).split('-')
                if (int(a) > int(b)) and isHaraldRaging():
                    return a+":"+b
            except:
                pass


    return "pass"

def isHaraldRaging():
    return True

if __name__ == "__main__":
    main()
