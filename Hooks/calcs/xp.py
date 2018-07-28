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
 
from Core.paconf import PA
from Core.maps import Planet
from Core.loadable import loadable, route, require_planet

class xp(loadable):
    """Calculates XP gain from stealing asteroids. Does not consider XP round_factor."""
    usage = " <x:y:z> [a:b:c]"
    access = 2 # Public
    
    @route(r"%s\s+%s"%((loadable.planet_coord,)*2))
    def planet(self, message, user, params):
        target = Planet.load(*params.group(1,3,5))
        if target is None:
            message.alert("No planet with coords %s:%s:%s" % params.group(1,3,5))
            return
        attacker = Planet.load(*params.group(6,8,10))
        if attacker is None:
            message.alert("No planet with coords %s:%s:%s" % params.group(6,8,10))
            return
        
        self.execute(message, target, attacker)
    
    @route(loadable.planet_coord)
    @require_planet
    def me(self, message, user, params):
        target = Planet.load(*params.group(1,3,5))
        if target is None:
            message.alert("No planet with coords %s:%s:%s" % params.group(1,3,5))
            return
        attacker = user.planet
        
        self.execute(message, target, attacker)
    
    def execute(self, message, target, attacker):
        reply="Target "

        reply+="%s:%s:%s (%s|%s) "%(target.x,target.y,target.z,
                                 self.num2short(target.value),self.num2short(target.score))
        reply+="| Attacker %s:%s:%s (%s|%s) "%(attacker.x,attacker.y,attacker.z,
                                            self.num2short(attacker.value),self.num2short(attacker.score))

        reply+="| Bravery: %.2f " % (attacker.bravery(target),)

        cap=target.maxcap(attacker)
        xp=attacker.calc_xp(target)
        reply+="| Roids: %s | XP: %s | Score: %s" % (cap,xp,xp*PA.getint("numbers", "xp_value"))
        message.reply(reply)
