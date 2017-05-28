# This file is part of Merlin.
# Merlin is the Copyright (C)2008,2009,2010 of Robin K. Hansen, Elliot Rosemarine, Andreas Jacobsen.

# Individual portions may be copyright by individual contributors, and
# are included in this collective work with permission of the copyright
# owners.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
 
# Help for new scanners.

# Module by Martin Stone

from Core.config import Config
from Core.chanusertracker import CUT
from Core.loadable import loadable, route
from Core.messages import NOTICE_REPLY

class scannerhelp(loadable):
    """Help for scanners"""
    alias = "scanhelp"
    usage = " [nick]"
    access = 4 # Scanner
    subcommands = ["scanhelp_target"]
    subaccess = [1]

    helptext = """When a request comes in, it looks like this...
[123] %s requested a Planet Scan of 1:1:1 Dists(i:17) https://game.planetarion.com/waves.pl?id=1&x=1&y=1&z=1
or...
[123] %s requested a Planet Scan of 1:1:1 Dists(i:17/r:35) https://game.planetarion.com/waves.pl?id=1&x=1&y=1&z=1
The "Dists(i:17)" is the number of distorters I think the planet has, based on blocked scanners or from dev scans. The real number may be higher, or possibly lower if some distorters have been destroyed.
The "r:35" in the second example means that the user requesting the scan thinks that the planet has at least 35 distorters.
If you don't have as many amplifiers as the planet has distorters, it's probably not worth wasting your resources trying.
The URL at the end will take you straight to the waves page in-game and will do the scan. You can then copy the URL of the scan (from the "Scan Link" on the page or from your address bar) and paste it in PM to me or in any channel where I can see it.
 
To list open requests, use ".req l" (.request list) for a list in an abbreviated format: [123: (17/35) P 1:1:1]
Alternatively, ".req links" will give a list of scan URLs to click on: [123 (17/35): http://game.planetarion.com/waves.pl?id=1&x=1&y=1&z=1]
If you get blocked, you can use the "blocks" subcommand. "!req 123 b 20" would indicate that you were blocked doing the example above (the request ID, 123, is in the square brackets) and you have 20 amplifiers.
 
If you have any problems, ask. Scanners are often idle, but usually helpful when they're around!
Thanks for scanning for %s!""" % ("Anon" if Config.getboolean("Scans", "anonscans") else Config.items("Admins")[0][0], "Anon" if Config.getboolean("Scans", "anonscans") else Config.items("Admins")[0][0], Config.get("Alliance", "name"))
    
    @route(r"(.*)")
    def execute(self, message, user, params):
        if params.group(1):
            if not self.check_access(message, "scanhelp_target"):
                message.alert("Insufficient access to send the help to %s." % params.group(1))
                return
            from Hooks.scans.request import request
            if not CUT.nick_in_chan(params.group(1),request().scanchan()):
                message.alert("%s does not appear to be in the scanner channel. Aborting." % params.group(1))
                return
            if message.reply_type() == NOTICE_REPLY:
                message.notice(self.helptext, params.group(1), 2)
            else:
                message.privmsg(self.helptext, params.group(1), 2)
        else:
            message.reply(self.helptext, 2)
