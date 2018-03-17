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
 
from sqlalchemy.sql import desc
from Core.config import Config
from Core.db import session
from Core.maps import Updates, User, Ship, UserFleet
from Core.loadable import loadable, route

class finddef(loadable):
    """Search mydef for ships by target class and, optionally, ship class or target level."""
    usage = " [<class>] <target class> [t1|t2|t3]"
    
    @route(r"(\S+)\s+(\S+)\s+[tT]([1-3])", access = "member")
    def tclass(self, message, user, params):
        self.execute(message, params.group(2), params.group(1), [int(params.group(3))])

    @route(r"(\S+)\s+[tT]([1-3])", access = "member")
    def tonly(self, message, user, params):
        self.execute(message, params.group(1), trange=[int(params.group(2))])

    @route(r"(\S+)\s+([^tT]\S+)", access = "member")
    def shipclass(self, message, user, params):
        self.execute(message, params.group(2), params.group(1))

    @route(r"(\S+)", access = "member")
    def anyclass(self, message, user, params):
        self.execute(message, params.group(1))

    def execute(self, message, target, shipclass=None, trange=[1,2,3]):
        
        target=self.tconvert(target)
        if not target:
            message.reply("invalid ship class")
            return
        if shipclass:
            shipclass=self.tconvert(shipclass)
        replies = []
        tick = Updates.current_tick()
        for t in trange:
            result = self.getships(target, shipclass, t)
            if len(result) > 0:
                replies.append("%sFleets targetting %s T%s: "%(shipclass+" " if shipclass else "",target,t))
                replies.append( ", ".join(map(lambda (u, x, s): "   %s(%s) %s: %s %s"%(u.name,u.fleetupdated-tick,u.fleetcount,self.num2short(x.ship_count),s.name),result)))
        if replies == []:
            replies.append("There are no planets with free %sfleets targetting %s %s"%(shipclass+" " if shipclass else "",target,"T"+trange[0] if trange != [1,2,3] else ""))
        message.reply("\n".join(replies))

    def getships(self, target, shipclass=None, target_level=1):

        Q = session.query(User, UserFleet, Ship)
        Q = Q.join(User.fleets)
        Q = Q.join(UserFleet.ship)
        Q = Q.filter(User.active == True)
        Q = Q.filter(User.access >= Config.getint("Access", "member"))
        if shipclass:
            Q = Q.filter(Ship.class_ == shipclass)
        if target_level == 3:
            Q = Q.filter(Ship.t3 == target)
        elif target_level == 2:
            Q = Q.filter(Ship.t2 == target)
        else:
            Q = Q.filter(Ship.t1 == target)
        Q = Q.filter(User.fleetcount > 0)
        Q = Q.order_by(desc(UserFleet.ship_count))
        return Q.all()

    def tconvert(self, target):
        if target.lower()[0:2] == "fi":
            return "Fighter"
        elif target.lower()[0:2] == "co":
            return "Corvette"
        elif target.lower()[0:2] == "fr":
            return "Frigate"
        elif target.lower()[0:2] == "de":
            return "Destroyer"
        elif target.lower()[0:2] == "cr":
            return "Cruiser"
        elif target.lower()[0:2] in ["bs","ba"]:
            return "Battleship"
        else:
            return None
