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
 
import sys
import urllib2
from sqlalchemy.sql import text
from Core.config import Config
from Core.db import false, session
from Core.maps import Ship
import json

useragent = "Merlin (Python-urllib/%s); Alliance/%s; BotNick/%s; Admin/%s" % (urllib2.__version__, Config.get("Alliance", "name"), 
                                                                              Config.get("Connection", "nick"), Config.items("Admins")[0][0])
def add_ship(dct):
    ship = Ship()
    for key in dct.keys():
        if dct[key] != "-":
            if key == "class":
                k = key + "_"
            elif key[:4] == "init":
                k = "init"
            elif key[:6] == "target":
                k = "t" + key[-1]
            else:
                k = key
            if k == "race" and dct[k][:4] == "The ":
                setattr(ship, k, dct[key][4:])
            else:
                setattr(ship, k, dct[key])
    ship.total_cost = int(ship.metal) + int(ship.crystal) + int(ship.eonium)
    session.add(ship)
    if __name__ == '__main__':
        print "%12s%12s%12s%12s" % (ship.name, ship.class_, ship.race, ship.type,)

def main(url = Config.get("URL", "ships")):
    # Remove old stats
    session.execute(Ship.__table__.delete())
    session.execute(text("SELECT setval('ships_id_seq', 1, :false);", bindparams=[false]))

    # Fetch and parse new stats
    req = urllib2.Request(url)
    req.add_header('User-Agent', useragent)
    json.load(urllib2.urlopen(req), object_hook=add_ship)
    
    session.commit()
    session.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(url=sys.argv[1]))
    else:
        sys.exit(main())
