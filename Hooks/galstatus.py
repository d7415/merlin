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
 
import re
import traceback
from sqlalchemy.exc import IntegrityError
from Core.db import session
from Core.maps import Updates, Planet, FleetScan
from Core.loadable import system
from Core.string import scanlog
from time import asctime

statusre=re.compile(r"(\d+):(\d+):(\d+)\*?\s+(\d+):(\d+):(\d+)\*?\s+(R|A|D)\s+(.*?)\s+((Xan|Ter|Cat|Zik|Etd)\s+)?(\d+)\s+(\d+)")

@system('PRIVMSG')
def catcher(message):
    try:
        m = statusre.search(message.get_msg().replace("\x02",""))
        if m:
            parse(message, m)
    except Exception, e:
        print "Exception in galstatus: "+e.__str__()
        traceback.print_exc()

class parse(object):
    def __init__(self, message, m):

        scanlog(asctime())
        try:
            pnick = "(%s)" % message.get_pnick()
        except:
            pnick = ""
        scanlog("Galaxy status from %s%s" % (message.get_nick(), pnick))

        target_x=m.group(1)
        target_y=m.group(2)
        target_z=m.group(3)

        owner_x=m.group(4)
        owner_y=m.group(5)
        owner_z=m.group(6)



        mission=m.group(7)
        fleetname=m.group(8)
#        race=m.group(10)
        fleetsize=m.group(11)
        eta=m.group(12)

        if mission == "A":
            mission = "Attack"
        elif mission == "D":
            mission = "Defend"
        elif mission == "R":
            mission = "Return"

        target=Planet.load(target_x,target_y,target_z)
        if target is None:
            return

        owner=Planet.load(owner_x,owner_y,owner_z)
        if owner is None:
            return

        curtick=Updates.current_tick()
        landing_tick = int(eta) + int(curtick)

        scanlog("%s:%s:%s %s:%s:%s '%s' %s %s eta %s" % (owner_x,owner_y,owner_z,target_x,target_y,target_z,fleetname,fleetsize,mission,eta))

        fleet = FleetScan(owner=owner, target=target, fleet_size=fleetsize, fleet_name=fleetname, landing_tick=landing_tick, mission=mission)
        fleet.in_cluster = owner_x == target_x
        fleet.in_galaxy = fleet.in_cluster and owner_y == target_y
        try:
            session.add(fleet)
            session.commit()
        except IntegrityError,e:
            session.rollback()
            print "Exception in galstatus: "+e.__str__()
            scanlog("Exception in galstatus: "+e.__str__())
            traceback.print_exc()

        self.report_incoming(message,target,owner,fleet)

    def report_incoming(self, message, target, owner, fleet):
        i=target.intel
        if i is None:
            scanlog("planet %s:%s:%s not in intel" % (target.x,target.y,target.z))
            return
        reply="%s reports: " % (message.get_nick(),)
        if i.nick:
            reply+=i.nick + " -> "
        reply+=" (xp: %s" % (owner.calc_xp(target),)

        # munin has some commented code here for associating with a defcall

        if i.relay and i.reportchan and message.get_chan() != i.reportchan:
            reply+=") "
            reply+=message.get_msg().replace("\x02","")
            message.privmsg(reply,i.reportchan)
        else:
            scanlog("planet not set to relay (%s) or report (%s) or report is source (%s)" % (i.relay,i.reportchan,message.get_chan()))
