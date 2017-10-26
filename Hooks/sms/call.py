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

from Core.config import Config
from Core.maps import User
from Core.loadable import loadable, route, require_user
if Config.get("Twilio", "sid"):
    from twilio.rest import Client

class call(loadable):
    """Calls the user's phone."""
    usage = " <nick>"
    
    @route(r"(\S+)", access = "member")
    @require_user
    def execute(self, message, user, params):
        if not Config.get("Twilio", "sid"):
            message.reply("Twilio support not configured. Tell the admin. If you are the admin, configure Twilio or disable !call to prevent this message.")
            return

        rec = params.group(1)
        receiver=User.load(name=rec,exact=False,access="member") or User.load(name=rec)
        if not receiver:
            message.reply("Who exactly is %s?" % (rec,))
            return
        if receiver.smsmode == "Retard":
            message.reply("I refuse to talk to that incompetent retard. Check %s's mydef comment and use !phone show to try sending it using your own phone." %(receiver.name,))
            return 

        if not (receiver.pubphone or user in receiver.phonefriends or user.is_admin()):
            message.reply("%s's phone number is private or they have not chosen to share their number with you. No call made." % (receiver.name,))
            return

        phone = self.prepare_phone_number(receiver.phone)
        if not phone or len(phone) <= 7:
            message.reply("%s has no phone number or their phone number is too short to be valid (under 6 digits). No call made." % (receiver.name,))
            return

        client = Client(Config.get("Twilio", "sid"), Config.get("Twilio", "auth_token"))
        if Config.getboolean("Twilio", "warn"):
            url="http://twimlets.com/echo?Twiml=%3CResponse%3E%3CSay%20voice%3D%22alice%22%20language%3D%22en-GB%22%20%3EHello.%20This%20is%20" +\
                Config.get("Connection", "nick") + ".%20Stop%20wasting%20our%20credit!%3C%2FSay%3E%3CHangup%2F%3E%3C%2FResponse%3E&",
        else:
            url="http://twimlets.com/echo?Twiml=%3CResponse%3E%3CHangup%2F%3E%3C%2FResponse%3E&",
        tw = client.api.account.calls.create(to=phone, from_=Config.get("Twilio", "number"), url=url, timeout=Config.getint("Twilio", "timeout"))

        if tw.sid:
            message.reply("Successfully called %s." % (receiver.name))
        else:
            message.reply("Error: Failed to get call ID from Twilio server.")
        
    def prepare_phone_number(self,text):
        if not text:
            return text
        s = "".join([c for c in text if c.isdigit()])
        return "+"+s.lstrip("00")
