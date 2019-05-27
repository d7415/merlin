from __future__ import print_function
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

# Script by Martin Stone
 
from Core.db import session
from Core.maps import Group, Access
from Core.callbacks import Callbacks

print("Looking for new commands and subcommands...")
def addaccess(name, access):
    command = Access.load(name)
    if command:
        return

    print("Adding %s" % (name))
    command = Access(name=name)
    session.add(command)
    if access == 2:
        command.groups.append(session.merge(Group.load(id=2)))
        command.groups.append(session.merge(Group.load(id=3)))
        command.groups.append(session.merge(Group.load(id=4)))
    elif access == 3:
        command.groups.append(session.merge(Group.load(id=3)))
        command.groups.append(session.merge(Group.load(id=4)))
    elif access != 1:
        command.groups.append(session.merge(Group.load(id=access)))


for callback in Callbacks.callbacks['PRIVMSG']:
    if not callback.access:
        continue
    addaccess(callback.name, callback.access)
    session.commit()
    try:
       if callback.subcommands:
           i = 0
           while i < len(callback.subcommands):
               addaccess(callback.subcommands[i], callback.subaccess[i])
               i += 1
    except:
        session.rollback()
    else:
        session.commit()

session.close()
print("Done!")
