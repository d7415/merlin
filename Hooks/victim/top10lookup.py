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
#
# Module by Martin Stone
 
from sqlalchemy.orm import aliased
from sqlalchemy.sql import desc
from Core.db import session
from Core.maps import Planet, Alliance, Intel
from Core.loadable import loadable, route

class top10lookup(loadable):
    """Top planets by specified criteria. Results in !lookup format."""
    usage = " [alliance] [race] [score|value|size|xp]"
    access = "member"
    alias = "top10l"

    @route(r"")
    def nogroup(self, message, user, params):
        self.execute(message)

    @route(r"(\S+)")
    def onegroup(self, message, user, params):
        opt = params.group(1).lower()
        if opt in ["score","value","size","xp"]:
            self.execute(message, sortby=opt)
        elif opt in ["good"[:len(opt)], "bad"[:len(opt)], "pretty"[:len(opt)]]:
            self.execute(message, race=opt)
        else:
            alliance = Alliance.load(opt)
            if alliance is None:
                message.reply("No alliance or user matching '%s' found" % (params.group(1),))
            else:
                self.execute(message, alliance=alliance)

    @route(r"(.*)")
    def groups(self, message, user, params):
        opts=params.group(1).lower().split()
        
        alliance=None
        sortby="score"
        race=None

        for opt in opts:
            if opt in ["score","value","size","xp"]:
                sortby=opt
            elif opt in ["good"[:len(opt)], "bad"[:len(opt)], "pretty"[:len(opt)]]:
                if opt[0] == "g":
                    race="Good"
                elif opt[0] == "b":
                    race="Bad"
                elif opt[0] == "p":
                    race="Prty"
            else:
                alliance=Alliance.load(opt)
                if alliance is None:
                    message.reply("No alliance or user matching '%s' found" % (params.group(1),))
        self.execute(message, alliance=alliance, race=race, sortby=sortby)

    def execute(self, message, alliance=None, race=None, sortby="score"):
        planet = aliased(Planet)
        planet_intel = aliased(Intel)
        

        Q = session.query(planet.x, planet.y, planet.z, planet_intel.nick)
        Q = Q.outerjoin((planet.intel, planet_intel))
        if alliance:
            Q = Q.filter(planet_intel.alliance == alliance)
        if race:
            Q = Q.filter(planet.race == race)
        if sortby == "xp":
            Q = Q.order_by(desc(planet.xp))
        elif sortby == "size":
            Q = Q.order_by(desc(planet.size))
        elif sortby == "value":
            Q = Q.order_by(desc(planet.value))
        else:
            Q = Q.order_by(desc(planet.score))
        result = Q.all()
        
        reply = "Top%s planets" % (" "+race if race is not None else "")
        if alliance:
            reply+=" in %s"%(alliance.name,)
        reply+=" by %s:\n"%(sortby)
        prev = []
        i=0
        for x, y, z, nick in result[:10]:
            i+=1
            line = "#%2s %12s%s"%(i, "["+nick+"] " if nick else "", Planet.load(x,y,z))
            prev.append(line)
        message.reply(reply+"\n".join(prev))
