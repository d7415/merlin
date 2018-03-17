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
 
from sqlalchemy.sql import asc
from Core.db import session
from Core.maps import Group, Updates
from Core.loadable import loadable, route

class members(loadable):
    """List all members, in format nick (alias). Optionally include coordinates, mydef age, tick of last mydef update."""
    usage = " [coords] [defage] [mydef] [galmates] [showempty]"
    access = 1 # Admin
    
    @route(r"(.*)", access = "members")
    def execute(self, message, user, params):
        reply = ""
        tick=Updates.current_tick()
        opts = params.group(1).split()

        for g in session.query(Group).order_by(asc(Group.name)).all():
            if ("galmates" not in opts) and (g.id == 2):
                continue;
            if len(g.users) < 1 and "showempty" not in opts:
                continue
            printable=map(lambda u: "%s%s%s%s%s" % (u.name,' ('+u.alias+')' if u.alias else '',
                " (%d:%d:%d)" % (u.planet.x, u.planet.y, u.planet.z) if "coords" in opts and u.planet is not None else '', 
                " (%s)" % ((u.fleetupdated or 0)-tick) if "defage" in opts else '',
                " (%s)" % (u.fleetupdated or 0) if "mydef" in opts else ''),g.users)
            reply += "%s:  %s\n" % (g.name, ', '.join(printable))
        message.reply(reply[:-1])
