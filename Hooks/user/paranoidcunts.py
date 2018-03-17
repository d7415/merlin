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
from Core.maps import User
from Core.loadable import loadable, route

class paranoidcunts(loadable):
    """List members who are have not set their phone number properly. Optionally sanity-checks phone numbers."""
    alias = "nophone"
    usage = " [galmates] [check] [noemail]"
    
    @route(r"(.*)", access = "admin")
    def execute(self, message, user, params):
        reply = ""
        opts = params.group(1).split()

        # pubphone=F
        Q = session.query(User.name, User.alias)
        if ("galmates" not in opts):
            Q = Q.filter(User.access > 0)
        Q = Q.filter(User.pubphone == False)
        if ("noemail" not in opts):
            Q = Q.filter(User._smsmode.op("IS DISTINCT FROM")('E'))
        Q = Q.order_by(asc(User.name))
        result = Q.all()

        if len(result) > 0:
            printable=map(lambda u_a: "%s%s" % (u_a[0],' ('+u_a[1]+')' if u_a[1] else ''),result)
            reply += "pubphone=F:    "
            reply += ', '.join(printable)

        # No phone number
        Q = session.query(User.name, User.alias)
        if ("galmates" not in opts):
            Q = Q.filter(User.access > 0)
        Q = Q.filter(User.phone == None)
        if ("noemail" not in opts):
            Q = Q.filter(User._smsmode.op("IS DISTINCT FROM")('E'))
        Q = Q.order_by(asc(User.name))
        result = Q.all()

        if len(result) > 0:
            printable=map(lambda u_a: "%s%s" % (u_a[0],' ('+u_a[1]+')' if u_a[1] else ''),result)
            reply += "\nNo phone set:  "
            reply += ', '.join(printable)

        # smsmode=email and no email set
        Q = session.query(User.name, User.alias)
        if ("galmates" not in opts):
            Q = Q.filter(User.access > 0)
        Q = Q.filter(User._smsmode == 'E')
        Q = Q.filter(User.email == None)
        Q = Q.order_by(asc(User.name))
        result = Q.all()

        if len(result) > 0:
            printable=map(lambda u_a: "%s%s" % (u_a[0],' ('+u_a[1]+')' if u_a[1] else ''),result)
            reply += "\nNo email set (and smsmode=Email):  "
            reply += ', '.join(printable)

        if ("check" in opts):
            Q = session.query(User.name, User.alias, User.phone)
            if ("galmates" not in opts):
                Q = Q.filter(User.access > 0)
            Q = Q.order_by(asc(User.name))
            result = Q.all()
            
            res = []
            for [u, a, n] in result:
                if n and (len(n) <= 7) and (n[1:].isdigit()) and (n[0].isdigit() or n[0] == '+'):
                    res.append([u,a,n])
            if len(res) > 0:
                printable=map(lambda u_a_n: "%s%s: %s" % (u_a_n[0],' ('+u_a_n[1]+')' if u_a_n[1] else '',u_a_n[2]),res)
                reply += "\nBad number:    %s" % (', '.join(printable))

        if reply == "":
            reply = "No paranoid cunts found. Congratulations!"
        message.reply(reply)
