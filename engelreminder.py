#!/usr/bin/env python2

import requests
import pjsua as pj
import sys

def marytts(host, port, data):
    r = requests.post("http://{}:{}/process".format(host, port), data)

    r.raise_for_status()

    return r.content

maryttsOptions = {
    "INPUT_TEXT": "Hi, This is a reminder that your shift as angel starts in 10 minutes at 17:00 to 19:00. Thanks for your help and have fun!",
    "INPUT_TYPE": "TEXT",
    "OUTPUT_TYPE": "AUDIO",
    "LOCALE": "en_US",
    #"AUDIO": "AU_STREAM",
    "AUDIO": "WAVE_FILE",
    "VOICE": "cmu-slt-hsmm"
}

with open("speech.wav", "wb") as f:
    f.write(marytts("localhost", 59125, maryttsOptions))

# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        print "Call is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

    # Notification when call's media state has changed.
    def on_media_state(self):
        global lib
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            player = lib.create_player("speech.wav")
            player_slot = lib.player_get_slot(player)
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            #lib.conf_connect(call_slot, 0)
            #lib.conf_connect(0, call_slot)
            lib.conf_connect(player_slot, call_slot)
            print "Hello world, I can talk!"

class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    def on_incoming_call(self, call):
        call.hangup(501, "Sorry, not ready to accept calls yet")

    def on_reg_state(self):
        print "Registration complete, status=", self.account.info().reg_status, \
              "(" + self.account.info().reg_reason + ")"

lib = pj.Lib()

lib.init()

transport = lib.create_transport(pj.TransportType.UDP)

lib.start()

acc_cfg = pj.AccountConfig(domain="voip.eventphone.de", username="4567", password="password", registrar="sip:voip.eventphone.de")

my_cb = MyAccountCallback()
acc = lib.create_account(acc_cfg, cb=my_cb)

acc.make_call("sip:7654@voip.eventphone.de", MyCallCallback())

print "Press <ENTER> to quit"
input = sys.stdin.readline().rstrip("\r\n")

# Shutdown the library
#lib.player_destroy(player)
lib.destroy()
lib = None
