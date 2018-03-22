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
import sys, time, urllib.request, urllib.error, urllib.parse, shutil, os, errno

# ########################################################################### #
# ##############################     NOTICE     ############################# #
# ########################################################################### #
#                                                                             #
# This file is based on excalibur, and is used to provide a standalone set of #
#   tick dumps (without a bot).                                               #
#                                                                             #
# This script is *NOT* part of the normal operation of merlin.                #
#                                                                             #
# ########################################################################### #
# ##############################     CONFIG     ############################# #
# ########################################################################### #

base_url = "http://game.planetarion.com/botfiles/"
alt_base = "http://dumps.dfwtk.com/"
useragent = "Dumper (Python-urllib/%s); Admin/YOUR_IRC_NICK_HERE" % (urllib2.__version__)

# ########################################################################### #
# ########################################################################### #

# From http://www.diveintopython.net/http_web_services/etags.html
class DefaultErrorHandler(urllib.request.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib.error.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result 

class botfile:
    def __init__(self, page):
        self.header = {}
        self.body = []

        # Parse header
        line = page.readline().strip()
        while line:
            [field, value] = line.split(": ",1)
            if value[0] == "'" and value[-1] == "'":
                value = value[1:-1]
            self.header[field] = value
            line = page.readline().strip()

        if "Tick" in self.header:
            if self.header["Tick"].isdigit():
                self.tick = int(self.header["Tick"])
            else:
                raise TypeError("Non-numeric tick \"%s\" found." % self.header["Tick"])
        else:
            raise TypeError("No tick information found.")

        if "Separator" not in self.header:
            self.header["Separator"] = "\t"

        if "EOF" not in self.header:
            self.header["EOF"] = None

        line = page.readline().strip()
        while line != self.header["EOF"]:
            self.body.append(line)
            line = page.readline().strip()

    def __iter__(self):
        return iter(self.body)

def get_dumps(last_tick, etag, modified, alt=False):
    global base_url, alt_base, useragent

    if alt:
       purl = alt_base + str(last_tick+1) + "/planet_listing.txt"
       gurl = alt_base + str(last_tick+1) + "/galaxy_listing.txt"
       aurl = alt_base + str(last_tick+1) + "/alliance_listing.txt"
       furl = alt_base + str(last_tick+1) + "/user_feed.txt"
    else:
       purl = base_url + "planet_listing.txt"
       gurl = base_url + "galaxy_listing.txt"
       aurl = base_url + "alliance_listing.txt"
       furl = base_url + "user_feed.txt"

    # Build the request for planet data
    req = urllib.request.Request(purl)
    if etag:
        req.add_header('If-None-Match', etag)
    if modified:
        req.add_header('If-Modified-Since', modified)
    if useragent:
        req.add_header('User-Agent', useragent)

    opener = urllib.request.build_opener(DefaultErrorHandler())

    pdump = opener.open(req)
    try:
        if pdump.status == 304:
            print("Dump files not modified. Waiting...")
            time.sleep(60)
            return (False, False, False, False)
        elif pdump.status == 404 and last_tick < alt:
            # Dumps are missing from archive. Check for dumps for next tick
            print("Dump files missing. Looking for newer...")
            return get_dumps(last_tick+1, etag, modified, alt)
        else:
            print("Error: %s" % pdump.status)
            time.sleep(120)
            return (False, False, False, False)
    except AttributeError:
        pass

    # Open the dump files
    try:
        req = urllib.request.Request(gurl)
        req.add_header('User-Agent', useragent)
        gdump = opener.open(req)
        if gdump.info().status:
            print("Error loading galaxy listing. Trying again in 2 minutes...")
            time.sleep(120)
            return (False, False, False, False)
        req = urllib.request.Request(aurl)
        req.add_header('User-Agent', useragent)
        adump = opener.open(req)
        if adump.info().status:
            print("Error loading alliance listing. Trying again in 2 minutes...")
            time.sleep(120)
            return (False, False, False, False)
        req = urllib.request.Request(furl)
        req.add_header('User-Agent', useragent)
        udump = opener.open(req)
        if udump.info().status:
            if alt:
                print("Error loading user feed. Ignoring.")
                udump = None
            else:
                print("Error loading user feed. Trying again in 2 minutes...")
                time.sleep(120)
                return (False, False, False, False)
    except Exception as e:
        print("Failed gathering dump files.\n%s" % (str(e),))
        time.sleep(300)
        return (False, False, False, False)
    else:
        return (pdump, gdump, adump, udump)


def checktick(planets, galaxies, alliances, userfeed):
    if not planets.tick:
        print("Bad planet dump")
        time.sleep(120)
        return False
    print("Planet dump for tick %s" % (planets.tick))
    if not galaxies.tick:
        print("Bad galaxy dump")
        time.sleep(120)
        return False
    print("Galaxy dump for tick %s" % (galaxies.tick))
    if not alliances.tick:
        print("Bad alliance dump")
        time.sleep(120)
        return False
    print("Alliance dump for tick %s" % (alliances.tick))

    # As above
    if userfeed:
        if not userfeed.tick:
            print("Bad userfeed dump")
            time.sleep(120)
            return False
        print("UserFeed dump for tick %s" % (userfeed.tick))

    # Check the ticks of the dumps are all the same and that it's
    #  greater than the previous tick, i.e. a new tick
    if not ((planets.tick == galaxies.tick == alliances.tick) and ((not userfeed) or planets.tick == userfeed.tick)):
        print("Varying ticks found, sleeping\nPlanet: %s, Galaxy: %s, Alliance: %s, UserFeed: %s" % (planets.tick, galaxies.tick, alliances.tick, userfeed.tick if userfeed else "N/A"))
        time.sleep(30)
        return False
    return True


def load_config():
    if os.path.isfile("dump_info"):
        info = open("dump_info", "r+")
        last_tick = int(info.readline()[:-1] or 0)
        etag = info.readline()[:-1]
        if etag == "None":
            etag = None
        modified = info.readline()[:-1]
        if modified == "None":
            modified = None
        info.seek(0)
    else:
        info = open("dump_info", "w")
        last_tick = 0
        etag = None
        modified = None
    return (info, last_tick, etag, modified)

def ticker(alt=False):

    t_start=time.time()
    t1=t_start

    (info, last_tick, etag, modified) = load_config()

    while True:
        try:
            # How long has passed since starting?
            # If 55 mins, we're not likely getting dumps this tick, so quit
            if (time.time() - t_start) >= (55 * 60):
                print("55 minutes without a successful dump, giving up!")
                info.close()
                sys.exit()
    
            (pdump, gdump, adump, udump) = get_dumps(last_tick, etag, modified, alt)
            if not pdump:
                continue

            # Get header information now, as the headers will be lost if we save dumps
            etag = pdump.headers.get("ETag")
            modified = pdump.headers.get("Last-Modified")
    
            try:
                os.makedirs("dumps/%s" % (last_tick+1,))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            # Open dump files
            pf = open("dumps/%s/planet_listing.txt" % (last_tick+1,), "w+")
            gf = open("dumps/%s/galaxy_listing.txt" % (last_tick+1,), "w+")
            af = open("dumps/%s/alliance_listing.txt" % (last_tick+1,), "w+")
            uf = open("dumps/%s/user_feed.txt" % (last_tick+1,), "w+")
            # Copy dump contents
            shutil.copyfileobj(pdump, pf)
            shutil.copyfileobj(gdump, gf)
            shutil.copyfileobj(adump, af)
            shutil.copyfileobj(udump, uf)
            # Return to the start of the file
            pf.seek(0)
            gf.seek(0)
            af.seek(0)
            uf.seek(0)
            # Swap pointers
            pdump = pf
            gdump = gf
            adump = af
            udump = uf

            # Parse botfile headers
            try:
                planets   = botfile(pdump)
                galaxies  = botfile(gdump)
                alliances = botfile(adump)
                userfeed = botfile(udump) if udump else None
            except TypeError as e:
                print("Error: %s" % e)
                time.sleep(60)
                continue

            if not checktick(planets, galaxies, alliances, userfeed):
                continue
    
            if not planets.tick > last_tick:
                if planets.tick < last_tick - 5:
                    print("Looks like a new round. Giving up.")
                    return False
                print("Stale ticks found, sleeping")
                time.sleep(60)
                continue
    
            t2=time.time()-t1
            print("Loaded dumps from webserver in %.3f seconds" % (t2,))
            t1=time.time()
    
            if planets.tick > last_tick + 1:
                if not alt:
                    print("Missing ticks. Switching to alternative url....")
                    ticker(planets.tick-1)
                    (info, last_tick, etag, modified) = load_config()
                    continue
                if planets.tick > alt:
                    print("Something is very, very wrong...")
                    continue
            info.write(str(planets.tick)+"\n"+str(etag)+"\n"+str(modified)+"\n")
            info.flush()
            info.seek(0)
            if planets.tick < alt:
                print("Seen:%s Target:%s" %(planets.tick,alt))
                print("Still some ticks missing... (waiting 10 seconds)")
                time.sleep(10)
                ticker(alt)
            break
        except Exception as e:
            print("Something random went wrong, sleeping for 15 seconds to hope it improves: %s" % (str(e),))
            time.sleep(15)
            continue

    info.close()

    t1=time.time()-t_start
    print("Total time taken: %.3f seconds" % (t1,))
    return planets.tick

print("Dumping from %s" % (base_url,))

ticker()
