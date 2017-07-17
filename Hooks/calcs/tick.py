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
 
from datetime import datetime, timedelta
from Core.loadable import loadable, route
from Core.maps import Updates, GameSetup
import time
from Core.admintools import admin_msg

class tick(loadable):
    access = 2 # Public
    
    @route("")
    def current(self, message, user, params):
        tick = Updates.load()
        if tick is None:
            if time.time() > GameSetup.getint("round_start_time"):
                tdiff = abs(int(GameSetup.getint("round_start_time") - time.time())) / GameSetup.getint("tick_speed") + 1
                message.reply("It *should* be tick %s, but I'm not ticking. Did someone forget to press the magic button?" % tdiff)
                if tdiff > 1:
                    admin_msg("It should be tick %s, but I'm not ticking!" % tdiff)
            else:
                message.reply("Ticks haven't started yet, go back to masturbating.")
        else:
            message.reply(str(tick))
    
    @route("(\d+)")
    def tick(self, message, user, params):
        tick = Updates.load(params.group(1)) or Updates.current_tick()
        if isinstance(tick, Updates): # We have that tick
            message.reply(str(tick))
        elif tick == 0:               # We don't have any ticks
            ticktime = GameSetup.getint("round_start_time") + (int(params.group(1))-1)*GameSetup.getint("tick_speed")
            tdiff = int(ticktime - time.time())
            tdelta = abs(tdiff / 86400)
            retstr  = " %sd" % tdelta if tdelta else ""
            tdelta = (tdiff % 86400) / 3600
            retstr += " %sh" % tdelta if tdelta else ""
            tdelta = (tdiff % 3600) / 60
            retstr += " %sm" % tdelta if tdelta else ""
            retstr = "Tick %s %s expected to happen%s%s%s - %s" % (params.group(1), "is" if tdiff >= 0 else "was", " in" if tdiff >= 0 else "", retstr, " ago" if tdiff < 0 else "", datetime.utcfromtimestamp(float(ticktime)).strftime("%a %d/%m %H:%M UTC"))
            message.reply(retstr)
        else:                         # We have some ticks, but not that one
            diff = int(params.group(1)) - tick
            now = datetime.utcnow()
            tick_speed = GameSetup.getint("tick_speed")
            tdiff = timedelta(seconds=tick_speed*diff)-timedelta(minutes=now.minute%(tick_speed/60))
            retstr  = "%sd " % abs(tdiff.days) if tdiff.days else ""
            retstr += "%sh " % abs(tdiff.seconds/3600) if tdiff.seconds/3600 else ""
            retstr += "%sm " % abs(tdiff.seconds%3600/60) if tdiff.seconds%3600/60 else ""
                
            if diff == 1:
                retstr = "Next tick is %s (in %s" % (params.group(1), retstr)
            elif diff > 1:
                retstr = "Tick %s is expected to happen in %s ticks (in %s" % (params.group(1), diff, retstr)
            elif diff <= 0:
                retstr = "Tick %s was expected to happen %s ticks ago but was not scraped (%s ago" % (params.group(1), -diff, retstr)
            
            ticktime = now + tdiff
            retstr += " - %s)" % (ticktime.strftime("%a %d/%m %H:%M UTC"),)
            message.reply(retstr)
