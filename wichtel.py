#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A helper script to draw giftees in a random and secret fashion.
Participants are notified by email.
"""

import fileinput
import getpass
import random
import smtplib

_MESSAGE = """Content-Type: text/plain; charset="utf-8"
Subject: Weihnachtswichteln

Hallo {0}, Freund der Wichtelei,
auch dieses Jahr bist du dabei.
Kümmre dich jetzt schon im Advent
um ein wunderschön Präsent.
Für {1} bist du der Bote.
Wenn du nichts weißt, bring Socken, rote.
"""

_HOST = "mail.com"
_USER = "user@mail.com"
_PW = None  # prompt

_SENDER = _USER
_MASTER = _USER


def parse():
    """Read name/address list and return dictionary"""
    addresses = {}
    tabus = {}
    for line in fileinput.input():
        line = line.strip()
        if line:
            tokens = line.split(":")
            name = tokens[0]
            address = tokens[1]
            addresses[name] = address
            tabus[name] = tokens[2:]
    return addresses, tabus


def all_different(source, image):
    """Check whether source map has fixed point."""
    return all([x != y for x, y in zip(source, image)])


def has_isolated_transposition(source, image):
    """Check whether a, b exist, with a -> b and b -> a"""
    f = dict(zip(source, image))
    for s, i in zip(source, image):
        if f[i] == s:
            return True
    return False


def matches_tabus(source, image, tabus):
    """Check whether any is matched to a tabu."""
    return any(y in tabus[x] for x, y in zip(source, image))


def good_matching(source, image, tabus):
    """Check if matching satisfies our constraints"""
    if not all_different(source, image):
        return False
    if has_isolated_transposition(source, image):
        return False
    if matches_tabus(source, image, tabus):
        return False
    return True


def matching(tabus):
    """Find a bijective map without fixed points."""
    names = list(tabus.keys())
    giftees = list(names)
    while not good_matching(names, giftees, tabus):
        random.shuffle(giftees)
    return dict(zip(names, giftees))


def send(srv, recipient, address, giftee):
    """Send _MESSAGE to address using server."""
    srv.sendmail(
        from_addr=_SENDER,
        to_addrs=[address, _MASTER],
        msg=_MESSAGE.format(recipient, giftee),
    )


if __name__ == "__main__":
    participants, tabus = parse()
    match = matching(tabus)

    if _PW is None:
        _PW = getpass.getpass()

    srv = smtplib.SMTP(_HOST)
    srv.login(_USER, _PW)
    for name in participants:
        send(srv, name, participants[name], match[name])
    srv.quit()
