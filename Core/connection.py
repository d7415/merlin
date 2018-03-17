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
 
# IRC connection

import re
import socket
import time
from Queue import PriorityQueue, Empty
from threading import Thread

from Core.exceptions_ import Reboot
from Core.config import Config
from Core.string import decode, encode, CRLF
from Core.admintools import admin_msg

class connection(object):
    # Socket/Connection handler
    output = PriorityQueue()
    queue_warned = 0
    wait_warned = 0
    quitting = False
    
    def __init__(self):
        # Socket to handle is provided
        self.ping = re.compile(r"PING\s*:\s*(\S+)", re.I)
        self.pong = re.compile(r"PONG\s*:", re.I)
        self.last = time.time()
        self.thread = Thread(target=self.writeout)
        self.thread.start()
    
    def connect(self, nick):
        # Configure socket
        server = Config.get("Connection", "server")
        port = Config.getint("Connection", "port")
        print("%s Connecting... (%s %s)" % (time.strftime("%Y%m%d %H:%M:%S |"), server, port,))
        
        try:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.sock.settimeout(330)
            self.sock.connect((server, port,))
        except:
            print("Error connecting with IPv6. Falling back to IPv4...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(330)
            self.sock.connect((server, port,))
        
        passwd = Config.get("Connection", "servpass")
        if passwd:
            self.write("PASS %s" % (passwd,), 0)
        
        self.write("NICK %s" % (nick,), 0)
        self.write("USER %s 0 * :%s bot. Admin: %s" % (nick, Config.get("Alliance", "name"), Config.items("Admins")[0][0],), 0)
        return self.sock
    
    def attach(self, sock=None, nick=None):
        # Attach the socket
        nick = nick or Config.get("Connection", "nick")
        try:
            self.sock = sock or self.connect(nick)
        except socket.error as exc:
            raise Reboot(exc)
        else:
            self.file = self.sock.makefile('rb', 0)

        # WHOIS ourselves in order to setup the CUT
        # self.write("WHOIS %s" % nick)
        return self.sock, nick
    
    def disconnect(self, line):
        # Cleanly close sockets
        print("%s Disconnecting IRC... (%s)" % (time.strftime("%Y%m%d %H:%M:%S |"),encode(line),))
        try:
            self.write("QUIT :%s" % (line,))
            self.quitting = True
            self.thread.join()
        except Reboot:
            pass
        finally:
            self.close()
        return ()
    
    def write(self, line, priority=10):
        # Write to output queue
        self.output.put((priority, time.time(), line))
        # Warn admins if the queue is too long
        if self.output.qsize() > Config.getint("Connection", "maxqueue"):
            if time.time() > self.queue_warned + 300:
                self.queue_warned = time.time()
                admin_msg("Message output queue length is too long: %s messages" % self.output.qsize())

    def writeout(self):
        # Write to socket/server
        while True:
            try:
                (priority, sent, line) = self.output.get(True, 1)
            except Empty:
                if self.quitting:
                    break
                else:
                    continue
            try:
                while self.last + Config.getfloat("Connection", "antiflood") * (1 + (len(line) > 300) + (priority > 10)) >= time.time():
                    time.sleep(0.5)
                # Warn admins if the wait is too long
                if priority < 10 and time.time() > sent + Config.getint("Connection", "maxdelay"):
                    if time.time() > self.wait_warned + 300:
                        self.wait_warned = time.time()
                        admin_msg("Message output message delay is too long: %.1f seconds" % (time.time() - sent))
                self.sock.send(encode(line) + CRLF)
                self.last = time.time()
                print("%s >> %s" % (time.strftime("%Y%m%d %H:%M:%S |"),encode(line),))
                self.output.task_done()
                if line[:4].upper() == "QUIT":
                    break
            except socket.error as exc:
                raise Reboot(exc)
    
    def read(self):
        # Read from socket
        try:
            line = decode(self.file.readline())
        except socket.error as exc:
            raise Reboot(exc)
        if line:
            if line[-2:] == CRLF:
                line = line[:-2]
            if line[-1] in CRLF:
                line = line[:-1]
            pinging = self.ping.match(line)
            if pinging:
                self.write("PONG :%s" % pinging.group(1), 0)
                #print "%s << PING? PONG!" % (time.strftime("%Y%m%d %H:%M:%S |"),)
            else:
                print("%s << %s" % (time.strftime("%Y%m%d %H:%M:%S |"),encode(line),))
            return line
        else:
            raise Reboot
    
    def fileno(self):
        # Return act like a file
        return self.sock.fileno()
    
    def close(self):
        # And again...
        return self.sock.close()
    
Connection = connection()
