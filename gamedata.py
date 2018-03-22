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
 
from future import standard_library
standard_library.install_aliases()
import sys, time
import urllib.request, urllib.error, urllib.parse
from Core.config import Config
from Core.db import session
from Core.maps import Construction, Research, Race, Gov, GameSetup
import json

useragent = "Merlin (Python-urllib/%s); Alliance/%s; BotNick/%s; Admin/%s" % (urllib2.__version__, Config.get("Alliance", "name"), 
                                                                              Config.get("Connection", "nick"), Config.items("Admins")[0][0])

def hook_factory(rclass, gen_mods=False):
    def add_record(dct):
        record = rclass()
        for key in dct:
            setattr(record, key, dct[key])
            if __name__ == '__main__':
                print("%12s%12s" % (key, dct[key]))
        if gen_mods:
            record.gen_mods()
        session.add(record)
    return add_record


def add_setting(dct):
    for key in dct:
        record = GameSetup(key=key,value=dct[key])
        if __name__ == '__main__':
            print("%12s%12s" % (key, dct[key]))
        session.add(record)

def loadfromapi(url,rclass, gen_mods=False):
    # Delete old data
    session.execute(rclass.__table__.delete())
    # Fetch and parse new data
    req = urllib.request.Request(url)
    req.add_header('User-Agent', useragent)
    if url[-8:] == "settings":
        json.load(urllib.request.urlopen(req), object_hook=add_setting)
        add_setting({"timestamp": str(int(time.time()))})
    else:
        json.load(urllib.request.urlopen(req), object_hook=hook_factory(rclass, gen_mods))
    
    session.commit()

def main(api_url = Config.get("URL", "api")):
    loadfromapi(api_url+"?constructions", Construction)
    loadfromapi(api_url+"?research", Research)
    loadfromapi(api_url+"?races", Race)
    loadfromapi(api_url+"?governments", Gov, gen_mods=True)
    loadfromapi(api_url+"?settings", GameSetup)
    session.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(url=sys.argv[1]))
    else:
        sys.exit(main())
