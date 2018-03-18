# This file is part of Merlin/Arthur.
# Merlin/Arthur is the Copyright (C)2009,2010 of Elliot Rosemarine.

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
 
from sqlalchemy import or_
from sqlalchemy.sql import asc, desc
from Core.config import Config
from Core.db import session
from Core.maps import Updates, Planet, User, Group, PhoneFriend, Channel
from Arthur.context import menu, render
from Arthur.loadable import loadable, load
bot = Config.get("Connection","nick")

@menu(bot, "Members")
@load
class members(loadable):
    access = "members"
    def execute(self, request, user, sort=None):
        
        order =  {"name"  : (asc(User.name),),
                  "sponsor" : (asc(User.sponsor),),
                  "access" : (asc(User.group_id),desc(User.carebears),asc(User.name),),
                  "carebears" : (desc(User.carebears),),
                  "planet" : (asc(Planet.x),asc(Planet.y),asc(Planet.z),),
                  "defage" : (asc(User.fleetupdated),),
                  }
        nogroups = sort is not None
        if sort not in order:
            sort = "name"
        order = order.get(sort)
        
        members = []
        Q = session.query(User.name, User.alias, User.sponsor, User.group_id, User.carebears, Planet, User.fleetupdated,
                          User.phone, User.pubphone, or_(User.id == user.id, User.id.in_(session.query(PhoneFriend.user_id).filter_by(friend=user))))
        Q = Q.filter(User.group_id != 2)
        Q = Q.filter(User.active == True)
        Q = Q.outerjoin(User.planet)
        for o in order:
            Q = Q.order_by(o)

        if nogroups:
            members.append(("All members", Q.all(),))
        else:
            for g in session.query(Group).filter(Group.id != 2).order_by(asc(Group.name)).all():
                members.append((g.name, Q.filter(User.group_id == g.id).all(),))
        
        return render("members.tpl", request, accesslist=members)

@menu(bot, "Galmates")
@load
class galmates(loadable):
    access = "members"
    def execute(self, request, user, sort=None):
        
        order =  {"name"  : (asc(User.name),),
                  "sponsor" : (asc(User.sponsor),),
                  "access" : (desc(User.access),),
                  "planet" : (asc(Planet.x),asc(Planet.y),asc(Planet.z),),
                  }
        if sort not in order:
            sort = "name"
        order = order.get(sort)
        
        Q = session.query(User.name, User.alias, User.sponsor, User.access, Planet,
                          User.phone, User.pubphone, User.id.in_(session.query(PhoneFriend.user_id).filter_by(friend=user)))
        Q = Q.filter(User.group_id == 2)
        Q = Q.filter(User.active == True)
        Q = Q.outerjoin(User.planet)
        for o in order:
            Q = Q.order_by(o)
        
        return render("galmates.tpl", request, members=Q.all())

@menu(bot, "Channels")
@load
class channels(loadable):
    access = "channels"
    def execute(self, request, user, sort=None):
        
        order =  {"name"  : (asc(Channel.name),),
                  "userlevel" : (desc(Channel.userlevel),),
                  "maxlevel" : (desc(Channel.maxlevel),),
                  }
        nogroups = sort is not None
        if sort not in order:
            sort = "name"
        order = order.get(sort)
        
        channels = []
        Q = session.query(Channel.name, Channel.userlevel, Channel.maxlevel)
        for o in order:
            Q = Q.order_by(o)

        if nogroups:
            channels.append(("All", Q.all(),))
        else:
            for g in session.query(Group).filter(Group.id != 2).order_by(asc(Group.name)).all():
                channels.append((g.name, Q.filter(Channel.userlevel == g.id).all(),))

        return render("channels.tpl", request, accesslist=channels)
