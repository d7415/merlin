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
 
from sqlalchemy.sql.functions import count
from Core.db import session
from Core.maps import Galaxy, Planet, Alliance, Intel
from Core.loadable import loadable, route

class bumchums(loadable):
    """Pies"""
    usage = " <alliance> [alliance] [number]"
    
    @route(r"(\S+)(?:\s+([A-Za-z].*?))?(?:\s+(\d+))?", access = "galmate")
    def execute(self, message, user, params):
        
        alliance = Alliance.load(params.group(1))
        if alliance is None:
            message.reply("No alliance matching '%s' found"%(params.group(1),))
            return
        if params.group(2):
            alliance2 = Alliance.load(params.group(2))
            if alliance2 is None:
                message.reply("No alliance matching '%s' found"%(params.group(2),))
                return
        bums = int(params.group(3) or 2)
        Q = session.query(Galaxy.x, Galaxy.y, count())
        Q = Q.join(Galaxy.planets)
        Q = Q.join(Planet.intel)
        Q = Q.filter(Galaxy.active == True)
        Q = Q.filter(Planet.active == True)
        if params.group(2):
            R = Q.filter(Intel.alliance==alliance2)
            R = R.group_by(Galaxy.x, Galaxy.y)
            R = R.having(count() >= bums)
        Q = Q.filter(Intel.alliance==alliance)
        Q = Q.group_by(Galaxy.x, Galaxy.y)
        Q = Q.having(count() >= bums)
        prev = []
        if params.group(2):
            for x1, y1, c1 in Q.all():
                for x2, y2, c2 in R.all():
                    if x1 == x2 and y1 == y2:
                        prev.append("%s:%s (%s,%s)"%(x1, y1, c1, c2))
            if len(prev) < 1:
                message.reply("No galaxies with at least %s bumchums from %s and %s"%(bums,alliance.name,alliance2.name))
                return
            reply="Galaxies with at least %s bums from %s and %s: "%(bums,alliance.name, alliance2.name)+ ' | '.join(prev)
        else:
            result = Q.all()    
            if len(result) < 1:
                message.reply("No galaxies with at least %s bumchums from %s"%(bums,alliance.name,))
                return
            prev=[]
            for x, y, chums in result:
                prev.append("%s:%s (%s)"%(x, y, chums))
            reply="Galaxies with at least %s bums from %s: "%(bums,alliance.name)+ ' | '.join(prev)
        message.reply(reply)
