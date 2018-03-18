Merlin
========
Merlin is the Copyright &copy; 2012 of Robin K. Hansen, Elliot Rosemarine, Andreas Jacobsen.  
This version was modified and added to by Martin Stone 2012-2015.  
Please read the included LICENSE.

Here Be Dragons
----------------------------
This version of merlin breaks database and config compatibility with ellonweb's original branch, and pretty much anything not forked from here. Additionally, it breaks compatibility with itself occasionally (well, actually quite frequently...).

If you run into trouble, it may be worth checking the [See Also](#see-also) section below, which contains some more detail and a step-by-step walkthrough.

For further support, use github or (preferably) try #munin on netgamers IRC. 

Installation Requirements
----------------------------
Requirements (tested on):

+ Git 
+ Python 2.7.*
+ PostgreSQL 9.1
+ psycopg2 2.4.5
+ SQLAlchemy 0.7.8
+ configparser 3.3.0

Additional Arthur requirements: 

+ nginx (Apache 2.2 + mod_wsgi should be fine)
+ Django 1.4+
+ Jinja2 2.6

Additional Graphing requirements: 

+ numpy 1.1
+ matplotlib 1.0

Additional POSIX environment (e.g. Linux) requirements:
Create and chmod 777 these directories:

+ /var/www/.matplotlib
+ /merlin/Arthur/graphs

Create and chmod 666 these files:

+ /merlin/dumplog.txt
+ /merlin/errorlog.txt
+ /merlin/scanlog.txt
+ /merlin/arthurlog.txt

>Note that these sort of permissions are potentially insecure and can cause a stale graphing cache. For more information, refer to README.Posix.

Quick Installation Instructions
----------------------------
Use Git to download the code and create a branch to track your changes:

	git clone git://github.com/d7415/merlin.git
	cd merlin
	git checkout -b <your_branch_name> acl-stable
	
After making changes to the code/config, you should store your changes:

	git add <name_of_changed_files>
	git commit -m <short_description_of_changes>
	
To update the code to the latest available source:

	git checkout acl-stable
	git pull
	git rebase acl-stable <your_branch_name>
	
This will re-apply your changes on top of the latest source. If you made some incompatible changes you might need to modify your change!

If you would like to contribute to merlin see [Setting up git](http://help.github.com/set-up-git-redirect)

Postgres Setup
----------------------------
All of the data your bot uses is stored in a postgresql database, see [Postgres Docs](http://www.postgresql.org/docs/)
or the relevant documentation for your OS/Distro.

For merlin your database needs to be in UTF-8 encoding          
		
	CREATE DATABASE <your_database_name> ENCODING = 'UTF8' TEMPLATE template0;

Preparing merlin
----------------------------
Inspect and modify merlin.cfg in an editor as required.

>Note Graphing can be completely disabled in the config, look for - graphing  : and append "cached", "enabled", or "disabled" depending on which you want!
       
Run createdb.py. This will create all the neccessary tables for you, as well as configuring the bot to join your alliance's main channel and downloading the shipstats from PA. Linux users, there is no shebang line so you will need to run: 
		
	python createdb.py

Inspect and modify /Hooks/\_\_init\_\_.py as needed. This controls which groups of commands will be enabled. Add a # character to the beginning of a line to disable a module. Many alliances will want to disable the prop/cookie package.
       
Merlin Access Settings
----------------------------
All of Merlin's functionality is stored in /Hooks/

Merlin's system hooks use the list of admins defined in merlin.cfg to control access. System hooks can be identified by the system modifier:@system(..)

Access control for other commands is set using !grant, !revoke (and !show) for specifiy groups, which in turn can be controlled using !addgroup, !editgroup, !remgroup. Use the bot's !help command for more details.

If a command is executed in a channel Merlin first checks the channel's min and max levels. If the channel's max level is higher than the command's requirement the command is denied. If the user's access level or the channel's min level match or exceed the requirement the command is executed.

If you want to limit a command to use in a specific channel or in PM, you can use this modifier on the execute method of the hook  @channel("home")

This can be changed to any channels defined in merlin.cfg or simply "PM",or you can specify the specific channel.

Running Merlin
----------------------------
Run merlin.py. Again, there is no shebang line.

	python merlin.py
		
Now add yourself to the bot using !adduser:
        
	!adduser <your_pnick> admin

You may also want to !secure the bot. You should do this each round and then 

	!reboot

Any time you make changes to any of Merlin's code, you will need to use 
		
	!reload 

Configuring Excalibur
----------------------------
You need to use a task scheduler to run excalibur.py one minute after every tick. If you're using crontab, you might use a command like this, which uses the supplied excalibur.sh

	1 * * * * python /path/to/merlin/excalibur.py >> /path/to/merlin/dumplog.txt 2>&1

excalibur.py will need updating if you want to use the same excalibur for more than one bot.

Configuring Apache and running Arthur
----------------------------
At the bottom of your httpd.conf, add the following lines
            
	WSGIScriptAlias / /path/to/merlin/arthur.wsgi
    <Directory /path/to/merlin/>
        <Files arthur.wsgi>
            Order allow,deny
            Allow from all
        </Files>
    </Directory>
    
    Alias /static/ /path/to/merlin/Arthur/static/
    <Directory /path/to/merlin/Arthur/static/>
        Order allow,deny
        Allow from all
    </Directory>
    
    Alias /graphs/ /path/to/merlin/Arthur/graphs/
    <Directory /path/to/merlin/Arthur/graphs/>
        Order allow,deny
        Allow from all
        ErrorDocument 404 /draw
    </Directory>
       
Make sure you edit all the paths!

Open the arthur.wsgi file and edit the two paths in that file. Open Arthur/__init__.py and edit the path in that file.

Arthur Access Settings
----------------------------
All of Arthur's functionality is stored in /Arthur/

Arthur's hooks use a similar but simpler access model to Merlin. The hooks all have an access level defined at the class level, similar to Merlin's default route access.

These can be edited manually, provide fine-grained control over access and the items in the dynamic menu. The recommended method of controlling Arthur access is with the "arthur_intel", "arthur_scans" and "arthur_attacks" privileges, which can be granted using !grant.

Anyone with an active user account is able to login to the website. This means galmates as well as members, though obviously there is very little for galmates to see! You have the option of making tools open for public use or the opposite, restricting what your members can see.

Updating for a new round
----------------------------
You should disable your task scheduler from running Excalibur when the round is over, it is not guaranteed to function correctly during havoc.
Make sure you have the latest source code! (see #4)
Run createdb.py with the --migrate switch and the old round number. For example, just before the start of round 37:
            
    python createdb.py --migrate 36
       
This will store the old database in an alternate schema for archiving, and copy your user list (among other things) to a new schema.
The migration tool will automatically pull the ship stats from PA. If the stats change before tick start or if you want to load beta stats, you can run shipstats.py manually:
            
    python shipstats.py [optional_url_to_stats]

Avoid running this midround, it will delete stored unit/au scans.
Don't forget to enable your task scheduler again once ticks start!

See Also
----------------------------
Other useful sources:

+ Installation walkthrough: [walkthrough.md](walkthrough.md)
+ Command list: [commandlist.md](commandlist.md)
+ A more detailed description of merlin.cfg entries: [config-desc.md](config-desc.md)
+ Posix tips: [README.Posix](README.Posix)
+ Branch explanation on the wiki: <https://github.com/d7415/merlin/wiki/Branches>

Extra Features and Requirements
----------------------------
Some features require extra configuration. Details below.

### IMAP Support
IMAP support allows the bot to parse notification emails from Planetarion. The bot can then announce incoming or recalled fleets, request scans for incoming fleets and forward the messages to the user's email address.

This feature has been tested in two environments. The first is where the alliance has a domain or subdomain. The account specified in the [imap] section of merlin.cfg should be a wildcard address so that it can receive notifications for all users. Users must then set their notification email address in-game to pnick-def@alliance.com. The "-def" is a configurable suffix for notification email addresses. If this is set, the bot will forward any emails to pnick@alliance.com but will not check their contents or trigger defcalls. The suffix allows users to have their own inboxes without the bot listening, or to have a forwarding address through the bot.

Alternatively, the feature can be used with a single address, so long as the provider will collect all mail for username+something@domain in the same inbox. GMail is known to behave in this way. In this case, it is recommended to set the defsuffix to blank in the [imap] section of merlin.cfg to avoid confusion. Set the singleaddr option to True and users should use username+pnick@domain as their notifications email address in-game.

To listen for new emails:

    python IMAPPush.py

If this proves unstable, these crontab lines will kill and restart the process every hour

    39 *    * * *   root    kill `ps aux | grep IMAPPush.py | grep -v grep | sed -r 's/merlin[ tab]+([0-9]+).*/\1/g'`
    40 *    * * *   merlin  /path/to/merlin/imappush.sh
Where the bot is run as user "merlin" and stored in /path/to/merlin/. imappush.sh should contain

    #!/bin/bash
    cd /path/to/merlin/
    python IMAPPush.py >> IMAPLog.txt


### Importing "Last 1000 scans"
Planetarion allows alliance members to "List scan ids of last 1000 scans". If this is saved to a file called "1000scans.txt", 1000scans.py will parse them into the bot using user ID #1. By default this loads at one scan every 2 seconds to minimise server RAM usage (~40mb in testing). If your server has lots of RAM, the time.sleep() can be changed to a lower number or removed entirely..


### WhatsApp Support
WhatsApp support allows the use of WhatsApp with the !sms command.

##### Requirements
You will need a phone number to receive the confirmation SMS and create a WhatsApp account. The bot will need its own account (and number) because two devices cannot be logged in at the same time.

##### Dependencies
This function requires the yowsup library, by Tarek Galal.
The git repository will already point to the latest known-good version of the library. To install:  

    git submodule init
    git submodule update

The second of these can also be used to update to a newer version when the upstream repository (this one) updates. If you encounter a fatal "reference is not a tree" error, try

    git submodule sync
    git submodule update

##### Config Items
"login" is your full, international phone number, including the country code but without the leading + or 00.

"password" is more tricky. Register the bot's number using the yowsup cli and this [guide](https://github.com/tgalal/yowsup/wiki/yowsup-cli#registration). Once you have been given a password it must be base64 decoded before saving as "password" in merlin.cfg. In python:

    "your password".decode("base64")

### Twilio Support
Merlin can now use [Twilio](https://www.twilio.com) for SMS and voice calling.

First, [install](https://www.twilio.com/docs/python/install) the twilio-python library. Then sign up on their website and add the details to merlin.cfg. You can send test messages/calls to your own phone for free with a trial account, but you will have to upgrade to send to others. SMS will be sent using Twilio when the user's smsmode is set to Twilio.

The !call command will initiate a call to a user and hang up after the number of seconds set in the timeout setting in the Twilio section of merlin.cfg. If the user answers and the warn setting is True, a message will be played identifying the bot and telling the user to stop wasting credit.

Unfortunately Twilio does not have an API call to check account balance, so there is no !showmethemoney support at this time.

### FluxBB Integration
Merlin can integrate with FluxBB, creating user accounts and updating passwords when the arthur password is updated in !pref.

Notes:

+ FluxBB must be set up to use the same database as merlin, and the merlin user must have SELECT, UPDATE and INSERT privileges to the FluxBB users table.
+ To avoid conflicts, FluxBB should be set up using the table prefix option. This can then be set in merlin.cfg.
+ Passwords updated from within FluxBB will not be updated on arthur.

### Multiple Bots on One Database
This version of merlin allows multiple bots to share a single ticker, saving bandwidth, disk space and processing power.

Notes:

+ Each bot must have its own prefix set in merlin.cfg
+ The ticker (excalibur.py) called by cron should refer to *all* merlin.cfg paths.
+ Only one ticker should be used. If more than one are called, only the first will work each tick.
+ When migrating data for a new round, do *not* use the "temp" option. This will erase settings for all but the current bot.
+ When migrating data for a new round, migrate the first bot normally. For each other bot, use the "--noschema" option, i.e. `python createdb.py --migrate 36 --noschema`

### Botfile saving
To save the PA botfiles every tick, change `savedumps` to `True` in excalibur.py and make sure that the merlin folder itself, or a subdirectory called "dumps", is writable by the account running excalibur.

To share the dumps with others, add a section to your Apache or nginx config, e.g.

##### Apache

    Alias /dumps/ /path/to/merlin/dumps/
    <Directory /path/to/merlin/dumps/>
        Options +Indexes
        Order allow,deny
        Allow from all
    </Directory>
    
##### nginx

    location /dumps/ {
        alias /path/to/merlin/dumps/;
        autoindex on;
    }

Note: If you are using one excalibur for multiple bots, the dump files will only be saved for the "main" bot. To share these, use the "main" merlin path in all dump-related Apache/nginx config.
