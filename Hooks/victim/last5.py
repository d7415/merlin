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
from sqlalchemy.sql import asc
from Core.db import session
from Core.maps import Updates, Planet, Alliance, Intel
from Core.loadable import loadable, route

class last5(loadable):
    """Bottom planets by specified criteria"""
    usage = " [alliance] [race] [score|value|size|xp]"
    access = 3 # Member

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
        

        Q = session.query(planet.x, planet.y, planet.z, planet.score, planet.value, planet.size, planet.xp, planet.race, planet_intel.nick)
        Q = Q.join((planet.intel, planet_intel))
        if alliance:
            Q = Q.filter(planet_intel.alliance == alliance)
        if race:
            Q = Q.filter(planet.race == race)
        Q = Q.group_by(planet.x, planet.y, planet.z, planet.score, planet.value, planet.size, planet.xp, planet.race, planet_intel.nick)
        if sortby == "xp":
            Q = Q.order_by(asc(planet.xp))
        elif sortby == "size":
            Q = Q.order_by(asc(planet.size))
        elif sortby == "value":
            Q = Q.order_by(asc(planet.value))
        else:
            Q = Q.order_by(asc(planet.score))
        result = Q.all()
        
        reply = "Bottom%s planets" % (" "+race if race is not None else "")
        if alliance:
            reply+=" in %s"%(alliance.name,)
        reply+=" by %s:\n"%(sortby)
        prev = []
        if alliance:
            i = alliance.members # Not set for some reason... It should be.
        else:
            i = Updates.load().planets
        for x, y, z, score, value, size, xp, race, nick in result[:5]:
            i-=1
            line = "#%s - %s:%s:%s (%s) - Score: %s Value: %s Size: %s XP: %s"%(i,x,y,z,race,score,value,size,xp)
            if nick:
                line = "%s Nick: %s"%(line,nick)
            prev.append(line)
        message.reply(reply+"\n".join(prev))
