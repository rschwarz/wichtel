#! /usr/bin/env python3

"""
A helper script to draw giftees in a random and secret fashion.
Participants are notified by email.
"""

import argparse
from email.mime.text import MIMEText
import getpass
import random
import smtplib

_MESSAGE = """Hallo {0}, wir machen darum keinen Bogen,
auch dein Name wurde gezogen,
Freue dich, aber bedenke,
für {1} besorgst du die Geschenke.
Es gibt nicht jedes Jahr das selbe,
wenn du nichts weißt, bring Socken, gelbe.
"""


def parse(config):
    """Read name/address list and return dictionary"""
    addresses = {}
    tabus = {}
    for line in config:
        line = line.strip()
        if line:
            tokens = line.split(":")
            name = tokens[0]
            address = tokens[1]
            addresses[name] = address
            tabus[name] = [t for t in tokens[2:] if t]
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


def send(srv, recipient, address, giftee, args):
    """Send _MESSAGE to address using server."""
    msg = MIMEText(_MESSAGE.format(recipient, giftee))
    msg["Subject"] = "Weihnachtswichteln"
    msg["To"] = ", ".join([address, args.cc])
    msg["From"] = args.sender
    srv.sendmail(args.sender, [address, args.cc], msg.as_string())


def main(args):
    with open(args.participants) as participants_file:
        participants, tabus = parse(participants_file)

    match = matching(tabus)

    if args.dryrun:
        for k, v in match.items():
            print(f"{k:15s} --> {v}")
        return

    if args.pw is None:
        args.pw = getpass.getpass()

    srv = smtplib.SMTP(args.host)
    srv.starttls()
    srv.login(args.user, args.pw)
    for name in participants:
        send(srv, name, participants[name], match[name], args)
    srv.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.add_argument(
        "participants",
        help="Colon-separated (name:email:tabus).",
    )
    parser.add_argument("--host", help="SMTP host.")
    parser.add_argument("--user", help="SMPT user (sender).")
    parser.add_argument("--pw", help="SMPT user's password (optional).")
    parser.add_argument("--sender", help="Sender email address.")
    parser.add_argument("--cc", help="CC address for all mails.")
    parser.add_argument(
        "--dryrun", action="store_true", help="Don't send mails, just print matching."
    )

    args = parser.parse_args()
    main(args)
