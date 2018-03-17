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
 
from sqlalchemy.sql import desc
from sqlalchemy.sql.functions import count
from Core.db import session
from Core.maps import Request, User, Scan, Updates
from Core.loadable import loadable, route

class topscanners(loadable):
    """List top scanners in the last x ticks. Shows requested scans by default. Use the "all" option to show all parsed scans."""
    usage = " [<age> <number>] [all]"
    access = "admin"
    alias = "topscan"
    
    @route(r"(all)?")
    def nooptions(self, message, user, params):
        tick=Updates.current_tick()
        self.execute(message, tick, 5, params.group(1) is not None)

    @route(r"([0-9]+)\s+([0-9]+)\s*(all)?")
    def withoptions(self, message, user, params):
        self.execute(message, int(params.group(1)), int(params.group(2)), params.group(3) is not None)


    def execute(self, message, age, num, showall):
        reply = ""
        tick=Updates.current_tick()

        totals = session.query(Scan.scanner_id, count('*').label('s_count'))
        if not showall:
            totals = totals.join((Request, Scan.id == Request.scan_id))
        totals = totals.filter(Scan.tick >= ((tick-age) if age > 0 else 0)).group_by(Scan.scanner_id).subquery()

        Q = session.query(User.name, User.alias, totals.c.s_count)
        Q = Q.outerjoin((totals, User.id == totals.c.scanner_id))
        Q = Q.filter(totals.c.s_count > 0)
        Q = Q.order_by(desc(totals.c.s_count))
        result = Q.all()
        if len(result) < 1:
            message.reply("No scans found in the last %d ticks" % (age))
            return
        printable=map(lambda name_alias_c: "%s%s: %s" % (name_alias_c[0],' ('+name_alias_c[1] +')' if name_alias_c[1] else '', name_alias_c[2]),result[:num])
        reply += ', '.join(printable)
        message.reply(reply)
