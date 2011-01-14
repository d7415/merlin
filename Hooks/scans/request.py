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
 
# Request a scan

from sqlalchemy.sql import asc
from sqlalchemy import func, and_
from Core.config import Config
from Core.paconf import PA
from Core.db import session
from Core.maps import Updates, Planet, Galaxy, Request, Intel
from Core.chanusertracker import CUT
from Core.loadable import loadable, route, require_user, user_in, robohci

class request(loadable):
    """Request a scan"""
    alias = "req"
    usage = " <x.y.z> <scantype(s)> [dists] | <id> blocks <amps> | cancel <id> | list | links"
    
    @route(loadable.coord+"\s+(["+"".join(PA.options("scans"))+r"]+)\w*(?:\s+(\d+))?", access = "galmate")
    @user_in("public")
    @require_user
    def execute(self, message, user, params):
        tick = Updates.current_tick()
        # Galaxy Scan
        if params.group(5) is None:

#            Access Control:
#            Uncomment this and change "group" to the lowest group that can request galscans.
#            if not user.is_group():
#                message.alert("Insufficient access for galaxy scans.")
#                return

            galaxy = Galaxy.load(*params.group(1,3))
            if galaxy is None:
                message.alert("No galaxy with coords %s:%s" % params.group(1,3))
                return
            planets = galaxy.planets
            galscan = Config.has_option("Misc", "galscans") and Config.getboolean("Misc", "galscans")
        else:
            planet = Planet.load(*params.group(1,3,5))
            if planet is None:
                message.alert("No planet with coords %s:%s:%s" % params.group(1,3,5))
                return
            planets = [planet]
            galscan = False

        # Scan Quota
        if Config.has_section("ScanQuota"):
            opts = Config.options("ScanQuota") 
            q = []
            for o in opts:
                if int(o) >= user.access:
                    q.append(int(o))
            if q:
                ScanQuota = Config.getint("ScanQuota", str(min(q)))
                reqs = session.query(Request.id).filter(Request.requester_id == user.id).filter(Request.tick == tick).count()
                if (reqs + len(planets) * len(params.group(6).upper())) > ScanQuota:
                    message.reply("This request will exceed your scan quota for this tick (%d scans remaining). " % (ScanQuota - reqs) +\
                                  "Try searching with !planet, !dev, !unit, !news, !jgp, !au.")
                    return

        dists = int(params.group(7) or 0)
        galdists = []

        mergescans = (not galscan) and (Config.has_option("Misc", "maxscans") and len(planets)*len(params.group(6)) > Config.getint("Misc", "maxscans"))

        for planet in planets:
            if galscan or mergescans:
                galdists.append(planet.intel.dists if planet.intel else 0)
                if len(galdists) < len(planets):
                    continue
            types = 0
            for scantype in params.group(6).upper():
                # Reject requests for incoming scans
                if not PA.getboolean(scantype, "request"):
                    message.alert("%s scans cannot be requested." % (PA.get(scantype, "name")))
                    continue
                types += 1
                if galscan or mergescans:
                    # Request the scans
                    for i in range(len(planets)):
                        request = self.request(message, user, planets[i], scantype, galdists[i], galscan or mergescans)
                    # Inform the requester    
                    if galscan and (message.get_chan() != self.scanchan()):
                        message.reply("Requested a Galaxy %s Scan of %s:%s. !request cancel %s:%s to cancel the request." % (request.type, planet.x, planet.y, 
                                                                                                                             request.id-len(planets)+1, request.id))
                    # Check for existing scans
                    scan = planet.scan(scantype)
                    if scan and request.tick - scan.tick < PA.getint(scantype,"expire"):
                        message.reply("%s Scan of %s:%s:%s is already available from %s ticks ago: %s. !request cancel %s if this is suitable." % (
                                                                        scantype, planet.x, planet.y, planet.z, request.tick - scan.tick, scan.link, request.id,))
                        # Cancel requests with a 0-tick old scan, if required
                        if (request.tick == scan.tick):
                            req0age = Config.getint("Misc", "req0agej") if request.scantype == "J" else Config.getint("Misc", "req0age")
                            if req0age == 1:
                               Q = session.query(Request).filter(Request.tick == request.tick).filter(Request.planet_id == request.planet_id)
                               Q = Q.filter(Request.scantype == request.scantype).filter(Request.requester_id == request.requester_id)
                               if Q.count() == 1:
                                   request.active = False
                                   message.reply("Request %s cancelled due to an existing scan. If you really need a newer one, repeat your scan request." % (request.id))
                                   message.privmsg("Cancelled scan request %s due to existing scan" % (request.id), self.scanchan())
                            elif req0age == 0:
                                request.active = False
                                message.reply("Request %s cancelled due to an existing scan." % (request.id))
                                message.privmsg("Cancelled scan request %s due to existing scan" % (request.id), self.scanchan())

                    # Tell the scanners
                    requester = user.name if not Config.getboolean("Misc", "anonscans") else "Anon"
                    if galscan:
                        message.privmsg("[%s:%s] %s requested a Galaxy %s Scan of %s:%s Max Dists(i:%s%s) " % (request.id-len(planets)+1, request.id, requester, 
                                        request.type, planet.x, planet.y, max(galdists), 
                                        "/r:%s" % dists if dists > 0 else "") + Config.get("URL", "reqgscan") % (planet.x, planet.y) , self.scanchan())
                else:
                    request = self.request(message, user, planet, scantype, dists)
                    if message.get_chan() != self.scanchan():
                        message.reply("Requested a %s Scan of %s:%s:%s. !request cancel %s to cancel the request." % (request.type, planet.x, planet.y, planet.z, request.id,))

                    # Check for existing scans
                    scan = planet.scan(scantype)
                    if scan and request.tick - scan.tick < PA.getint(scan.scantype,"expire"):
                        message.reply("%s Scan of %s:%s:%s is already available from %s ticks ago: %s. !request cancel %s if this is suitable." % (
                                                                        scantype, planet.x, planet.y, planet.z, request.tick - scan.tick, scan.link, request.id,))
                        # Cancel requests with a 0-tick old scan, if required
                        if (request.tick == scan.tick):
                            req0age = Config.getint("Misc", "req0agej") if request.scantype == "J" else Config.getint("Misc", "req0age")
                            if req0age == 1:
                               Q = session.query(Request).filter(Request.tick == request.tick).filter(Request.planet_id == request.planet_id)
                               Q = Q.filter(Request.scantype == request.scantype).filter(Request.requester_id == request.requester_id)
                               if Q.count() == 1:
                                   request.active = False
                                   message.reply("Request %s cancelled due to an existing scan. If you really need a newer one, repeat your scan request." % (request.id))
                                   message.privmsg("Cancelled scan request %s due to existing scan" % (request.id), self.scanchan())
                            elif req0age == 0:
                                request.active = False
                                message.reply("Request %s cancelled due to an existing scan." % (request.id))
                                message.privmsg("Cancelled scan request %s due to existing scan" % (request.id), self.scanchan())

            if mergescans:
                message.reply("Requested %d scans. !request cancel %s:%s to cancel the request." % (len(planets) * types, request.id-len(planets)*types+1, request.id))
                message.privmsg("[%s:%s] %s requested %d scans (%s) Max Dists(i:%s%s). !request links for details " % (request.id-len(planets)*types+1, request.id, 
                                requester, len(planets)*types, params.group(6).upper(), max(galdists), "/r:%s" % dists if dists > 0 else ""), self.scanchan())
        session.commit()
    
    @robohci
    def robocop(self, message, request_id, mode):
        request = Request.load(request_id, active=False)
        if request is None:
            return
        
        if mode == "cancel":
            reply = "Cancelled scan request %s" % (request.id,)
            message.privmsg(reply, self.scanchan())
            nicks = CUT.get_user_nicks(request.user.name)
            for nick in nicks:
                message.privmsg(reply, nick)
            return
        
        if mode == "block":
            reply = "Updated request %s dists to %s" % (request.id, request.dists,)
            message.privmsg(reply, self.scanchan())
            nicks = CUT.get_user_nicks(request.user.name)
            for nick in nicks:
                message.privmsg(reply, nick)
            return
        
        user = request.user
        planet = request.target
        
        requester = user.name if not Config.getboolean("Misc", "anonscans") else "Anon"
        dists_intel = planet.intel.dists if planet.intel else 0
        message.privmsg("[%s] %s requested a %s Scan of %s:%s:%s Dists(i:%s%s) " % (request.id, requester, request.type, planet.x,planet.y,planet.z, 
                                                        dists_intel, "/r:%s" % request.dists if request.dists > 0 else "") + request.link, self.scanchan())
    
    def request(self, message, user, planet, scan, dists, gal=False):
        request = Request(target=planet, scantype=scan, dists=dists)
        user.requests.append(request)
        session.commit()
        
        if not gal:
            requester = user.name if not Config.getboolean("Misc", "anonscans") else "Anon"
            dists_intel = planet.intel.dists if planet.intel else 0
            message.privmsg("[%s] %s requested a %s Scan of %s:%s:%s Dists(i:%s%s) " % (request.id, requester, request.type, planet.x,planet.y,planet.z, 
                                                            dists_intel, "/r:%s" % request.dists if request.dists > 0 else "") + request.link, self.scanchan())
        
        return request
    
    @route(r"c(?:ancel)?\s+(\d+(?:[: -]\d+)*)", access = "galmate")
    @require_user
    def cancel(self, message, user, params):
        cancel_ids = []
        reply_ids = []
        noexist = []
        noaccess = []

        for id in params.group(1).split():
            if ':' in id:
                [start,end] = id.split(':')
                cancel_ids += range(int(start), int(end)+1)
            elif '-' in id:
                [start,end] = id.split('-')
                cancel_ids += range(int(start), int(end)+1)
            else:
                cancel_ids.append(int(id))

        for id in cancel_ids:
            id = str(id)
            request = Request.load(id)
            if request is None:
                noexist.append(id)
                continue
            if request.user is not user and not user.is_member() and not self.is_chan(message, self.scanchan()):
                noaccess.append(id)
                continue
            
            request.active = False
            session.commit()

            reply = "Cancelled scan request %s" % (id)
            nicks = CUT.get_user_nicks(request.user.name)
            if message.get_nick() not in nicks:
                for nick in nicks:
                    message.privmsg(reply, nick)
            
            reply_ids.append(id)

        if len(noexist) > 0:
            message.reply("No open request number %s exists (idiot)."%(", ".join(noexist),))
        if len(noaccess) > 0:
            message.reply("Scan requests: %s aren't yours and you're not a scanner!"%(", ".join(noaccess),))
        if len(reply_ids) > 0:
            reply = "Cancelled scan request %s" % (", ".join(reply_ids))
            message.reply(reply)
            if message.get_chan() != self.scanchan():
                message.privmsg(reply, self.scanchan())
        
    
    @route(r"(\d+)\s+b(?:lock(?:s|ed)?)?\s+(\d+)", access = "member")
    def blocks(self, message, user, params):
        id = params.group(1)
        dists = int(params.group(2))+1
        request = Request.load(id)
        if request is None:
            message.reply("No open request number %s exists (idiot)."%(id,))
            return
        if request.user is not user and not user.is_member() and not self.is_chan(message, self.scanchan()):
            message.reply("Scan request %s isn't yours and you're not a scanner!"%(id,))
            return
        
        # Update Intel
        planet = request.target
        if planet.intel is None:
            planet.intel = Intel()
        planet.intel.dists = max(planet.intel.dists, dists)

        request.dists = max(request.dists, dists)
        session.commit()
        
        reply = "Updated request %s dists to %s" % (id, request.dists,)
        message.reply(reply)
        if message.get_chan() != self.scanchan():
            message.privmsg(reply, self.scanchan())
        
        nicks = CUT.get_user_nicks(request.user.name)
        if message.get_nick() not in nicks:
            for nick in nicks:
                message.privmsg(reply, nick)
    
    @route(r"l(?:ist)?", access = "member")
    def list(self, message, user, params):
        Q = session.query(func.count().label('count'), func.max(Request.id).label('max_id'))
        Q = Q.filter(Request.tick > Updates.current_tick() - 5)
        Q = Q.filter(Request.active == True)
        Q = Q.group_by(Request.planet_id, Request.scantype)
        Q = Q.order_by(asc('max_id'))
        SQ = Q.subquery()
        Q = session.query(Request, SQ.c.count).join((SQ, and_(Request.id == SQ.c.max_id)))
        
        if Q.count() < 1:
            message.reply("There are no open scan requests")
            return
        
        message.reply(" ".join(map(lambda (request, count): Config.get("Misc", "reqlist").decode("string_escape") % (request.id, request.target.intel.dists if request.target.intel else "0",
                      "/%s" % request.dists if request.dists > 0 else "", request.scantype, request.target.x, request.target.y, request.target.z,), Q.all())))
    
    @route(r"links? ?(.*)", access = "member")
    def links(self, message, user, params):
        try:
            if params.group(1) == "all":
                i=0
            else:
                i=int(params.group(1))
        except:
            i=5
            
        Q = session.query(func.count().label('count'), func.max(Request.id).label('max_id'))
        Q = Q.filter(Request.tick > Updates.current_tick() - 5)
        Q = Q.filter(Request.active == True)
        Q = Q.group_by(Request.planet_id, Request.scantype)
        Q = Q.order_by(asc('max_id'))
        SQ = Q.subquery()
        Q = session.query(Request, SQ.c.count).join((SQ, and_(Request.id == SQ.c.max_id)))
        
        if Q.count() < 1:
            message.reply("There are no open scan requests")
            return

        message.reply(self.url(" ".join(map(lambda (request, count): Config.get("Misc", "reqlinks").decode("string_escape") % (request.id, 
                      request.target.intel.dists if request.target.intel else "0", "/%s" % request.dists if request.dists > 0 else "", request.link), Q[:i] if i>0 else Q.all())), user))
    
    def scanchan(self):
        return Config.get("Channels", "scans") if "scans" in Config.options("Channels") else Config.get("Channels", "home")
