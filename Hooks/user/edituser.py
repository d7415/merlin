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
 
from Core.config import Config
from Core.db import session
from Core.maps import User, Group, Channel, ChannelAdd
from Core.chanusertracker import CUT
from Core.loadable import loadable, route, require_user

class edituser(loadable):
    """Used to change a user's access or (de)activate them"""
    usage = " <user> (<access>|true|false)"
    access = 1 # Admin
    
    @route(r"(.+)\s+(\S+)", access = "edituser")
    @require_user
    def execute(self, message, user, params):
        
        usernames = params.group(1)
        access = params.group(2).lower()

        if access in self.true:
            access = True
        elif access in self.false:
            access = False
        else:
            g = Group.load(access)
            if not g:
                message.reply("Invalid access group '%s'" % (access,))
                return
    
            if g.admin_only and not user.is_admin:
                message.reply("You may not add a user to the %s group." % (g.name))
                return

        addnicks = {}
        remnicks = []
        remchans = []
        changed = []

        if type(access) in (str, unicode):
            newchanQ = session.query(Channel).join(ChannelAdd).filter(ChannelAdd.group_id == g.id)
            
        for username in usernames.split():
            member = User.load(name=username, active=False)
            if member is None:
                message.alert("No such user '%s'" % (username,))
                return
            
            if type(access) in (str, unicode) and not member.active:
                message.reply("You should first re-activate user %s" %(member.name,))
                return
            
            if member.group.admin_only and not user.is_admin:
                message.reply("You may not change %s's access; they are in the %s group." % (member.name, member.group.name))
                continue

            changed.append(username)

            if type(access) in (str, unicode):
                if member.active == True:
                    oldchanQ = session.query(Channel).join(ChannelAdd).filter(ChannelAdd.group_id == member.group_id)
                    addQ = newchanQ.except_(oldchanQ)
                    remQ = oldchanQ.except_(newchanQ)

                    for chan in addQ.all():
                        try:
                            addnicks[chan.name] += "," + member.name
                        except:
                            addnicks[chan.name] = member.name
                    if remQ.count():
                        remnicks.append(member.name)
                        for chan in remQ.all():
                            message.privmsg("remuser %s %s" % (chan.name, member.name,), Config.get("Services", "nick"))
                            if chan.name not in remchans:
                                remchans.append(chan.name)
                            if Config.getboolean("Misc", "banonrem"):
                                message.privmsg("ban %s *!*@%s.%s GTFO, EAAD"%(chan.name, member.name, Config.get("Services", "usermask"),), Config.get("Services", "nick"))
                member.group_id = g.id
            else:
                if member.active != access and access == True:
                    for chan in member.group.autochannels:
                        try:
                            addnicks[chan.channel.name] += "," + member.name
                        except:
                            addnicks[chan.channel.name] = member.name
                if member.active != access and access == False:
                    for chan in member.group.autochannels:
                        message.privmsg("remuser %s %s" % (chan.channel.name, member.name,), Config.get("Services", "nick"))
                        if chan.channel.name not in remchans:
                            remchans.append(chan.channel.name)
                        if Config.getboolean("Misc", "banonrem"):
                            message.privmsg("ban %s *!*@%s.%s GTFO, EAAD"%(chan.channel.name, member.name, Config.get("Services", "usermask"),), Config.get("Services", "nick"))
                member.active = access
            if not member.active:
                CUT.untrack_user(member.name)
        session.commit()

        if addnicks:
            for chan in g.autochannels:
                channel = chan.channel.name
                if channel in addnicks:
                    message.privmsg("adduser %s %s %s" %(channel, addnicks[channel], chan.level), Config.get("Services", "nick"))
            nicks=[]
            for n in addnicks.values():
                nicks += n.split(",")
            nicks = list(set(nicks))
            nicks.sort()
            message.reply("%s ha%s been added to %s"%(", ".join(nicks), "ve" if len(addnicks) > 1 else "s", ", ".join(addnicks.keys()),))
        if remnicks:
            remchans.sort()
            message.reply("%s ha%s been removed from %s"%(", ".join(remnicks), "ve" if len(remnicks) > 1 else "s", ", ".join(remchans),))
        if changed:
            message.reply("Editted user%s %s access to %s" % ("s" if len(changed) > 1 else "", ", ".join(changed), access,))
