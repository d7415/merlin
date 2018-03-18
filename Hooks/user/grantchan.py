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
 
# Module by Martin Stone

from Core.db import session
from Core.maps import Group, Channel, ChannelAdd
from Core.loadable import loadable, route, require_user
from Core.config import Config

class grantchan(loadable):
    """Grant groups access to channels. Multiple groups and channels should be comma separated. If no level is specified, groups will be added at level 24."""
    usage = " <access groups> <commands> [level]"
    access = 1 # Admin
    alias = "gchan"
    
    @route(r"(\S+)\s+(\S+)(?:\s+(\d+))?", access = "grantchan")
    @require_user
    def execute(self, message, user, params):
        
        groups = params.group(1).lower().split(",")
        channels = params.group(2).lower().split(",")
        if params.group(3):
            level = int(params.group(3))
            if level < 1 or level > 498:
                message.reply("Invalid access level: %d" % level)
                return
        else:
            level = 24

        exists = {}

        for group in groups:
            g = Group.load(group)
            if not g:
                message.reply("Invalid access group '%s'." % (group,))
                session.rollback()
                return
            if g.admin_only and not user.is_admin:
                message.reply("You don't have access to change the %s group." % (group,))
                session.rollback()
                return
            for channel in channels:
                c = Channel.load(channel)
                if not c:
                    message.reply("Invalid channel '%s'." % (channel,))
                    session.rollback()
                    return
                newchan = True
                for chan in g.autochannels:
                    if chan.channel == c:
                        newchan = False
                        try:
                            exists[group] += ", %s" % (channel)
                        except:
                            exists[group] = channel
                        break
                if newchan:
                    session.add(ChannelAdd(channel_id=c.id, group_id=g.id, level=level))
                    nicks = []
                    for u in g.users:
                        nicks += [u.name]
                    message.privmsg("adduser %s %s %s" %(channel, ",".join(nicks), level), Config.get("Services", "nick"))
        session.commit()

        message.reply("access to %s granted to %s%s" % (", ".join(channels), ", ".join(groups), " except..." if len(exists) else "."))
        for group in exists:
            message.reply("Group %s already has access to: %s" % (group, exists[group]))
