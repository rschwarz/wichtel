#! /usr/bin/env python2
# -*- coding: utf-8 -*- 

'''
A helper script to draw giftees in a random and secret fashion.
Participants are notified by email.
'''

import fileinput
import getpass
import random
import smtplib

_MESSAGE = '''Content-Type: text/plain; charset="utf-8"
Subject: Weihnachtswichteln

Hallo {0}, Freund der Wichtelei,
auch dieses Jahr bist du dabei.
Kümmre dich jetzt schon im Advent
um ein wunderschön Präsent.
Für {1} bist du der Bote.
Wenn du nichts weißt, bring Socken, rote.
'''

_HOST = 'mail.com'
_USER = 'user@mail.com'
_PW = None # prompt

_SENDER = _USER
_MASTER = _USER

def parse():
    '''Read name/address list and return dictionary'''
    addresses = {}
    tabus = {}
    for line in fileinput.input():
        line = line.strip()
        if line:
            tokens = line.split(':')
            name = tokens[0]
            address = tokens[1]
            addresses[name] = address
            tabus[name] = tokens[2:]
    return addresses, tabus

def matching(names, tabus):
    '''Find a bijective map without fixed points.'''
    def all_different(source, image):
        '''Check whether source map has fixed point.'''
        return all([x != y for x, y in zip(source, image)])

    def count_isolated_transpositions(source, image):
        '''Check whether a, b exist, with a -> b and b -> a'''
        count = 0
        f = dict(zip(source, image))
        for s, i in zip(source, image):
            if f[i] == s:
                count += 1
        return count

    def good_matching(source, image):
        '''Check if matching satisfies our constraints'''
        if not all_different(source, image):
            return False
        if count_isolated_transpositions(source, image) > 0:
            return False
        return all(y not in tabus[x]
                   for x, y in zip(source, image))

    giftees = list(names)
    while not good_matching(names, giftees):
        random.shuffle(giftees)
    return dict(zip(names, giftees))

def send(srv, recipient, address, giftee):
    '''Send _MESSAGE to address using server.'''
    srv.sendmail(from_addr=_SENDER,
                 to_addrs=[address, _MASTER],
                 msg=_MESSAGE.format(recipient, giftee))

if __name__ == '__main__':
    participants, tabus = parse()
    match = matching(participants.keys(), tabus)

    if _PW is None:
        _PW = getpass.getpass()

    srv = smtplib.SMTP(_HOST)
    srv.login(_USER, _PW)
    for name in participants:
        send(srv, name, participants[name], match[name])
    srv.quit()
