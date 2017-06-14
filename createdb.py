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
import sqlalchemy
from sqlalchemy.exc import DBAPIError, IntegrityError, ProgrammingError
from sqlalchemy.sql import text, bindparam
from Core.config import Config
from Core.db import Base, session
import shipstats

# Edit this if you are migrating from a schema with a different (or no) prefix:
old_prefix = Config.get('DB', 'prefix')
prefix = Config.get('DB', 'prefix')

if len(sys.argv) > 2 and sys.argv[1] == "--migrate":
    round = sys.argv[2]
    if round.isdigit():
        round = "r"+round
    noschema= (len(sys.argv) > 3 and sys.argv[3] == "--noschema")
elif len(sys.argv) > 1 and sys.argv[1] == "--new":
    round = None
else:
    print "To setup a database for a new Merlin install: createdb.py --new"
    print "To migrate without saving previoud round data: createdb.py --migrate temp"
    print "To migrate from an old round use: createdb.py --migrate <previous_round>"
    print "For multiple bots sharing a DB, after the first migration use: createdb.py --migrate <previous_round> --noschema"
    sys.exit()

if round and not noschema:
    print "Moving tables to '%s' schema"%(round,)
    try:
        session.execute(text("ALTER SCHEMA public RENAME TO %s;" % (round,)))
    except ProgrammingError:
        print "Oops! Either you don't have permission to modify schemas or you already have a backup called '%s'" % (round,)
        session.rollback()
        sys.exit()
    else:
        session.commit()
    finally:
        session.close()

print "Importing database models"
from Core.maps import Channel
print "Creating schema and tables"
try:
    session.execute(text("CREATE SCHEMA public;"))
except ProgrammingError:
    print "A public schema already exists, but this is completely normal"
    session.rollback()
else:
    session.commit()
finally:
    session.close()

Base.metadata.create_all()

print "Setting up default channels"
userlevel = Config.getint("Access", "member")
maxlevel = Config.getint("Access", "admin")
gallevel = Config.getint("Access", "galmate")
for chan, name in Config.items("Channels"):
    try:
        channel = Channel(name=name)
        if chan in ["public", "share"]:
            channel.userlevel = gallevel
            channel.maxlevel = gallevel
        else:
            channel.userlevel = userlevel
            channel.maxlevel = maxlevel
        session.add(channel)
        session.flush()
    except IntegrityError:
        print "Channel '%s' already exists" % (channel.name,)
        session.rollback()
    else:
        print "Created '%s' with access (%s|%s)" % (channel.name, channel.userlevel, channel.maxlevel,)
        session.commit()
session.close()

if round:
    print "Migrating data:"
    try:
        print "  - users/friends"
        session.execute(text("INSERT INTO %susers (id, name, alias, passwd, active, access, url, email, phone, pubphone, _smsmode, sponsor, quits, available_cookies, carebears, last_cookie_date, fleetcount) SELECT id, name, alias, passwd, active, access, url, email, phone, pubphone, _smsmode::varchar::smsmode, sponsor, quits, available_cookies, carebears, last_cookie_date, 0 FROM %s.%susers;" % (prefix, round, old_prefix)))
        session.execute(text("SELECT setval('%susers_id_seq',(SELECT max(id) FROM %susers));" % (prefix, prefix)))
        session.execute(text("INSERT INTO %sphonefriends (user_id, friend_id) SELECT user_id, friend_id FROM %s.%sphonefriends;" % (prefix, round, old_prefix)))
        print "  - slogans/quotes"
        session.execute(text("INSERT INTO %sslogans (text) SELECT text FROM %s.%sslogans;" % (prefix, round, old_prefix)))
        session.execute(text("INSERT INTO %squotes (text) SELECT text FROM %s.%squotes;" % (prefix, round, old_prefix)))
        print "  - props/votes/cookies"
        session.execute(text("INSERT INTO %sinvite_proposal (id,active,proposer_id,person,created,closed,vote_result,comment_text) SELECT id,active,proposer_id,person,created,closed,vote_result,comment_text FROM %s.%sinvite_proposal;" % (prefix, round, old_prefix)))
        session.execute(text("INSERT INTO %skick_proposal (id,active,proposer_id,person_id,created,closed,vote_result,comment_text) SELECT id,active,proposer_id,person_id,created,closed,vote_result,comment_text FROM %s.%skick_proposal;" % (prefix, round, old_prefix)))
#        session.execute(text("SELECT setval('%sproposal_id_seq',(SELECT max(id) FROM (SELECT id FROM %sinvite_proposal UNION SELECT id FROM %skick_proposal) AS proposals));" % (prefix, prefix, prefix)))
        session.execute(text("INSERT INTO %sprop_vote (vote,carebears,prop_id,voter_id) SELECT vote,carebears,prop_id,voter_id FROM %s.%sprop_vote;" % (prefix, round, old_prefix)))
        session.execute(text("INSERT INTO %scookie_log (log_time,year,week,howmany,giver_id,receiver_id) SELECT log_time,year,week,howmany,giver_id,receiver_id FROM %s.%scookie_log;" % (prefix, round, old_prefix)))
        print "  - smslog"
        session.execute(text("INSERT INTO %ssms_log (sender_id,receiver_id,phone,sms_text,mode) SELECT sender_id,receiver_id,phone,sms_text,mode FROM %s.%ssms_log;" % (prefix, round, old_prefix)))
    except DBAPIError, e:
        print "An error occurred during migration: %s" %(str(e),)
        session.rollback()
        if not noschema:
            print "Reverting to previous schema"
            session.execute(text("DROP SCHEMA public CASCADE;"))
            session.execute(text("ALTER SCHEMA %s RENAME TO public;" % (round,)))
        session.commit()
        sys.exit()
    else:
        session.commit()
    finally:
        session.close()
    if Config.has_section("FluxBB") and Config.getboolean("FluxBB", "enabled"):
        # Get the names of all FluxBB tables.
        tables = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='%s' AND table_name LIKE '%s%%';" % (round, Config.get("FluxBB", "prefix"))))
        for t in tables:
            session.execute(text("CREATE TABLE %s (LIKE %s.%s INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES);" % (t[0], round, t[0])))
            session.execute(text("INSERT INTO %s (SELECT * FROM %s.%s);" % (t[0], round, t[0])))
        # Get the names of all FluxBB sequnces.
        sequences = session.execute(text("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema='%s' AND sequence_name LIKE '%s%%';" % (round, Config.get("FluxBB", "prefix"))))
        for seq in sequences:
            # The group table is different, so deal with that separately.
            if seq[0][-15:] == "groups_g_id_seq":
                session.execute(text("CREATE SEQUENCE %s; SELECT SETVAL('%s', max(g_id)) FROM %s;" % (seq[0], seq[0], seq[0][:-9])))
                session.execute(text("ALTER TABLE %s ALTER COLUMN g_id SET DEFAULT nextval('%s'::regclass);" % (seq[0][:-9], seq[0])))
            else:
                session.execute(text("CREATE SEQUENCE %s; SELECT SETVAL('%s', max(id)) FROM %s;" % (seq[0], seq[0], seq[0][:-7])))
                session.execute(text("ALTER TABLE %s ALTER COLUMN id SET DEFAULT nextval('%s'::regclass);" % (seq[0][:-7], seq[0])))
        session.commit()
        session.close()

    if round == "temp":
        print "Deleting temporary schema"
        session.execute(text("DROP SCHEMA temp CASCADE;"))
        session.commit()
        session.close()

print "Inserting ship stats"
shipstats.main()

if round and not noschema:
    import os, shutil, errno, glob
    if os.path.exists("dumps"):
        if round and round != "temp":
            print "Archiving dump files"
            try:
                os.makedirs("dumps/archive/%s" % round)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            for tdir in glob.glob("dumps/[0-9]*"):
                shutil.move(tdir,"dumps/archive/%s/" % round)
        else:
            print "Not removing dump files. Please remove them manually."
