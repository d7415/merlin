# Merlin Configuration Overview

## [Connection]
### nick      : Bot
The bot's IRC Nick
### passwd    : password
The bot's password with the IRC services (e.g. P)
### server    : irc.netgamers.org
The IRC server to connect to.
### servpass  : 
The password, if required, to connect to the IRC server.
### port      : 6667
The port to connect to the IRC server.

### antiflood : 2
*Minimum delay between messages in seconds*  
Most public servers will get upset and kill users (or bots) sending too many messages too quickly. One every 2 seconds is considered a good starting point. If you are running merlin on a private server without such flood protection, you can set this to 0.
### \# color     : 12
*Color of all text in mIRC format http://www.mirc.com/colors.html (optional)*  
This option is disabled by default because many users consider it a nuisance. If you want to use this option, be sure to check the `[NoColor]` and `[NoColorChan]` options below.
### maxqueue  : 50
*Warn admins if the message queue exceeds this length*  
The bot will automatically delay sending of messages to avoid flooding and will store them in a prioritised queue. If the queue gets long, there's probably something bad going on. This setting will warn you once every 5 minutes while the queue is too long.
### maxdelay  : 60
*Warn admins if a message takes longer than is to deliver (in whole seconds)*  
Similar to the `maxqueue` setting above, this setting warns you if the delay to an individual message becomes too high. At most, the bot will warn you of such a delay once every 5 minutes.

## [Services]
### nick      : P
The IRC nick of the network services.
### host      : P!cservice@netgamers.org
The full IRC host of the network services.
### login     : P@cservice.netgamers.org
The IRC nick/address used for the login command.
### nickserv  : NS!NickServ@netgamers.org
The full IRC host of the NickServ service, where different to `host`.
### usermask  : users.netgamers.org
The IRC hostmask for +x users should be in the format @registered nick[dot]usermask.

## [NoColor]
*These nicks should never have colors sent to them*  

    P                        : 1
    P@cservice.netgamers.org : 1

The bot will not use colored text when sending messages to these nicks. By default, this is just the services, which will often fail to understand colored messages.

## [NoColorChan]
*These channels should never have colors sent to them. No # or & in front!*  

    someboringchannel        : 1

As with the `[NoColor]` section, the bot will not use colored text when sending messages to these channels. These should be specified without any prefix.

## [Admins]
*multiple admins can be added*  

    pnick     : 1

Admins added here should be chosen carefully and added by their registered services nick. Ideally you, the person running the bot, should be at the top of the list.
Note that anyone added here will have the following privileges:

+ messages will be handled with higher priority
+ notification if the `maxqueue` or `maxdelay` triggers are reached
+ can invite the bot to any channel it knows about
+ can use the `!adduser` command and some others before being added to the bot themselves
+ has access to some extra commands unavailable to "normal" admins
+ will receive responses to CTCP PING and VERSION queries

## [Alliance]
### name      : Alliance
The name of the alliance (should match the name in-game)
### cookies   : 4
if the propsandcookies modules are enabled, users are given this many cookies to give out per day.
### members   : 80
if the propsandcookies modules are enabled, a prop vote cannot be started if there are already this many users.

## [Channels]
*home channel is all that is required at the moment*  
*only special channels need to be defined here*  
*everything else will be stored in the db*  
*Special channels: public, home, scans, def, share*  

    home      : #channel

These channels will be created when createdb.py is run and some have some special parameters. Any channels will be added here, but the special names are:

+ **public**: Added as a public/galchan. Any other channel will be added with userlevel of member and maxlevel of admin.
+ **home**: This is the default channel for most things.`!letmein` will only let users into this channel. It is also the fallback if the `scans` or `def` channels are not set.
+ **scans**: This channel will receive all scan requests.By default, users in this channel can cancel or update the number of distorters on any request.
+ **def**: By default, any defcalls parsed from email notifications will appear here first.
+ **share**: The bot will expect to receive shared scans via this channel. This helps to prevent infinite sharing loops.

## [Scans]
### quota     : 1
This is the the maximum number of scan requests a user with basic `request` access can make per tick.
### highquota : 5
This is the the maximum number of scan requests a user with `req_highquota` access can make per tick. Users with `req_noquota` access are exempt.
### anonscans : False
If True, nicks will not be shown in scan requests.
### showurls  : False
*show scan URLs in "delivered to..." messages.*
If True, the scan URL will be included in the "delivered to" messages, as well as in the message to the requester.  
### galscans  : True
*present gal scan requests as a link to the "galaxy scan" page instead of indiviudal requests*  
If True, when a user requests a scan for a whole galaxy it will link to the in-game "Galaxy Scan" page, with the galaxy preselected. The scan type and individual planets will have to be selected manually, but it reduced the number of clicks and cleans up the scans channel.
### maxscans  : 5
*more than this many scans in a single request command will be summarized.*  
If a users requests more than this many scans in one command, the output will show as a single message indicating the number and types of scans along with the highest number of distorters in the set.
### showscanner : True
When presenting a requested scan to a user, tell them who provided the scan, if known.
### reqlist   : [%s: (%s%s) %s %s:%s:%s] 
### reqlinks  : [%s (%s%s): %s]
*These patterns will be filled with ID, dists, type, coords for !request list, and ID, dists and link for !request links. Use \x03 to begin a color code, \x0F to reset to default client colors.*  
This allows advanced users to set a custom format for scan requests in `!request list` and `!request links`. The order of the items cannot be changed.
### reqexpire : 24
*Scan requests expire after this many ticks.*  
Scan requests will not be filled if they are older than this many ticks. This can prevent nuisance messages if someone happens to paste a scan you requested several days or weeks earlier.
### req0age   : 1
### req0agej  : 2
*0: Disallow requests where a scan exists with the same tick.*  
*1: Allow the request, but make the user repeat it first.*  
*2: Just request it, even if one exists.*  
This enables "clever" behaviour where the bot will ignore, ask for confirmation or allow multiple requests of the same type on the same planet in the same tick. The behaviour for JGP requests is handled separately because these are more likely to change during a tick.
### shareto   : 
The bot will send the URL of any scans it sees to this nick or channel, for sharing. This feature is primarily designed to allow scan pooling with the public #Scans bot. If you want to join the scan pool with the #Scans bot, speak to mPulse or Pit.

## [Misc]
### acl       : True
This is used internally to determine whether the bot is using the `legacy` or `acl` branch.
### errorlog  : errorlog.txt
General error log for merlin.
### scanlog   : scanlog.txt
Scan parser log.
### arthurlog : arthurlog.txt
Log for Arthur (web interface).
### debuglog  : 
*Logs *all* traffic sent to stdout, including all conversations the bot sees. For privacy reasons, this is disabled by default and is the recommended value.*  
If enabled, this log will record every message sent to or received by merlin. This includes every command sent and everything said in any channel where the bot is. This has potential privacy concerns, so is disabled by default and recommended to stay that way.
### excalibur : stdout
Log for excalibur (the ticker). By default, this goes to stdout and the `excalibur.sh` script handles logging.
### maillogs  : 
*Email logs to admin (see below)*  
*Add letters to select which logs to email: e = errorlog; a = arthurlog; s = scanlog; d = dumplog (excaliburlog)*  
*Note that an email is sent for each line, so scanlog and dumplog will create many email messages for each entry.*  
This will send an email to the address below for each line of a selected file logged. As such, scanlog and dumplog will result in a **lot** of email. Even errorlog is likely to send many emails for a single error.
### logmail   : 
*Email address for maillogs. separate multiple addresses with a space.*  
*Make sure that the smtp settings below are correct. If using the localhost mailer, it may be possible to use usernames in place of full email addresses.*  
If `maillogs` is enabled above, the emails will be sent to this address.
### catchup   : True
*Whether to allow "catch-up" from the altdumps botfiles archive specified below.*
This will avoid missed ticks by collecting them from an archive on another server.
### autoreg   : False
If True, users are automatically added as galmates.
### usercache : join
*"rapid", "join" or blank*  
If set to rapid or join, the bot keeps track of IRC nicks and their associated registered nicks.
### robocop   : 12345
*local TCP/IP port to use*  
This allows different parts of the bot to talk to each other. It **must** be different where two bots are operating on the same machine.
### sms       : combined
*"clickatell", "googlevoice", or "combined". Note that the "email" smsmode requires "combined" here.*  
Configuration for various smsmodes is later in the file. For the most part, this should be left as `combined` to allow for other smsmodes.
### graphing  : cached
*"cached", "enabled", or "disabled"*  
This controls graphing in Arthur.
### banonrem  : False
*Ban users on !remuser as well as removing them from P*  
If True, `!remuser` will ban users from channels when removing them from the services access list.
### remself   : False
*Bot will remove itself from P's access list for a channel when !remchan is used.*  
If True, the bot will remove its own channel access when `!remchan` is used.
### defage    : 24
*mydef can be this old before the bot starts pestering people. Set to 0 to disable.*  
If a user's mydef is older than this number of ticks, every time they join a channel with the bot in it will send them a notice telling them to update it.
### globaldef : False
*defcalls are sent to *all* channels, not just home or def.*  
If this is enabled, defcalls (using the email parser or `!defcall`) will be sent to all registered channels (other than public/galchans), rather than just the `home` or `def` channels.
### autoscans : A
### scanage   : 2
*defcalls will autorequest autoscans (in format PDUNJA) when stored scans are older than scanage.*  
*Leave autoscans blank to disable this feature.*  
When the bot receives an email notification of new incoming fleets it will request scans of any types specified in `autoscans` if the stored versions are older than `scanage` ticks.
### attscans  : 
*!attack will autorequest attscans (in format PDUNJA) when scans are older than the current tick.*  
The bot will request these types of scan when `!attack` is used to set up a new attack if the stored versions are older than the current tick.
### attwaves  : 3
*Default number of waves for !attack.*  
The `!attack` command will produce this number of waves.
### attactive : 12
*Attack is active this many ticks before land tick.*  
Attacks are considered active and shown on the website this many ticks before the land tick.
### attjgp    : 4
*Show JGPs on arthur this many ticks this many ticks before land tick.*  
### tellmsg   : False
*!tell uses NOTICE by default. Set to True to use PRIVMSG instead.*  
Specify how to pass `!tell` messages to users.
### findsmall : True
*Find new small (one-planet) alliances each tick.*
If True, excalibur will look for new one-planet alliances each tick, find the relevant planet and add the intel automatically.
### bcrypt    : False
*Use bcrypt instead of SHA1 for passwords. This will break FluxBB integration and requires the Python bcrypt library.*
If True, use bcrypt for passwords instead of SHA1. This is a much more suitable algorithm for storing passwords, but is incompatible with FluxBB integration and requires the python bcrypt library which is not usually installed by default.

## [Updates]
### notify-users:
*Users to be notified of new updates. Space-separated pnicks. Should be a subset of [Admins].*
*Empty will use the first user in the [Admins] section. Remove "updatenotifier" from Hooks/\__init__.py to disable.*
### notify-repo: d7415
*Filter updates by repo author name. Space separated.*
### notify-allow: Pit
*Allow updates from these pnicks. Space separated.*
### notify-channel: #merlin-updates
*Join this channel to receive updates. If you are forking merlin and would like voice, contact Pit.*
### notify-branch: acl-stable
*Filter notifications by branch, e.g. acl, acl-stable, master, legacy-stable. Also allows these keywords: all, stable. Space separated list.*
*Non-stable branches may require DB structure updates and should only be applied by advanced users, but there is no harm in being notified of them.*
### notify-level: bugfix major forks
*Filter notifications by level. Space separated list. Options are:*

+ *major:   Patches required for the bot to function correctly, or at all.*
+ *bugfix:  Patches fixing bugs in the code.*
+ *minor:   Minor changes, e.g. formatting, typos, documentation changes.*
+ *feature: New features.*
+ *all:     Any of the above levels*
+ *forks:   New merlin forks when they are first added to the update channel*

## [DB]

    # Postgres
    driver    : psycopg2
    dbms      : postgresql

Use the values for PostreSQL. MySQL is no longer officially supported.
### username  : merlin
Database username.
### password  : password
Database password.
### host      : localhost
Database host. If your database is hosted on a different machine, specify it here. Otherwise leave as localhost.
### port      : 5432

    # Default ports:
    #   Postgres Normal: 5432
    #   Postgres Alt:    5433

The port used by your SQL Server. The ports listed in the comment are the default ports, so should work most of the time.
### database  : merlin
The database name.
### URL       : %(dbms)s+%(driver)s://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s
This is a URL used by SQL Alchemy to connect to the database. It is generated using the preceding configuration options, so shouldn't need changing manually.
### prefix    : ally_
*Prefix for using multiple bots in one database. If you are upgrading an existing merlin and do not need this feature, change to blank.*  
This is a prefix added to all alliance-specific tables in the database. The primary purpose of this is to allow multiple bots to run on the same server with minimum replication. If this is a new installation, it's a good idea to use an abbreviated form of your alliance name here. Leave the trailing underscore (_) for readability.

## [Arthur]
### public    : True
The website can be accessed by anyone, without logging in. This does not affect member-only functions such as intel, scans and the member list.
### showdumps : False
If true, a link is shown to the dumps directory. Further instructions on dump/botfile saving can be found in [README.md](https://github.com/d7415/merlin#botfile-saving)
### secretkey : 
*Generate a secretkey with:*  
`python -c 'import random; print "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])'`
*NB: Django 1.5+ will refuse to start if this is blank.*  
This string is used by Django to hash some data. Version 1.5+ will get upset if you don't set it, so best get it done now, even if you're using an older version. You'll only forget.

## [URL]
### arthur    : http://localhost:8000/
URL for Arthur (the web interface).
### game      : http://game.planetarion.com
URL for the game. This should only need to change for special rounds or beta.
### ships     : %(game)s/manual.pl?page=stats
The ship stats page of the manual.
### dumps     : %(game)s/botfiles
Where to find the botfiles / tick dumps
### altdumps  : http://dumps.dfwtk.com/%s
An archive of tick dumps, so that we can catch up if we start mid-round or miss some.
### planets   : %(dumps)s/planet_listing.txt
### galaxies  : %(dumps)s/galaxy_listing.txt
### alliances : %(dumps)s/alliance_listing.txt
### alt_plan  : %(altdumps)s/planet_listing.txt
### alt_gal   : %(altdumps)s/galaxy_listing.txt
### alt_ally  : %(altdumps)s/alliance_listing.txt
The individual botfiles. 3 for normal, 3 for the archive.
### viewscan  : %(game)s/showscan.pl?scan_id=%%s
### viewgroup : %(game)s/showscan.pl?scan_grp=%%s
Scan links, for viewing wihtout logging in.
### reqscan   : %(game)s/waves.pl?id=%%s&x=%%s&y=%%s&z=%%s
Waves page.
### reqgscan  : %(game)s/waves.pl?gal_scan_x=%%s&gal_scan_y=%%s&action=load_gal#tab2
Galaxy Scan page.
### bcalc     : %(game)s/bcalc.pl?
PA Battle Calc.

## [alturls]

    ip : http://146.185.135.215
    # game : http://game.planetarion.com
    # r56 : http://r56.planetarion.com
    # tof : http://twistoffate.planetarion.com
    # ranul : http://pa.ranultech.co.uk
    # ranulgame : http://game.ranultech.co.uk
    # p45 : http://p45.planetarion.com

IP for accessing Planetarion if you're having DNS issues.

##[arthururls]
*Section for any URLs arthur may run from, to keep Django happy. No "http", no "/", no port numbers.*
###local : 127.0.0.1

## [clickatell]

    user      : 
    pass      : 
    api       : api_key

Clickatell configuration.

## [googlevoice]
    user      : 
    pass      : 
    api       : api_key

Google Voice configuration.

## [Twilio]
    sid       :
    auth_token:
    number    :
    timeout   : 10
    warn      : True
    # timeout is in seconds to wait for an answer.
    # If warn is True, anyone answering will be told that it's the bot and to stop wasting credit.

Twilio configuratoin

## [WhatsApp]

    login     : 
    password  : 

WhatsApp configuration. See [README.md](https://github.com/d7415/merlin#whatsapp-support).

## [smtp]
### user      : 
SMTP username, for sending emails. Leave blank for local mail.
### pass      : 
SMTP password, for sending emails. Leave blank for local mail.
### host      : localhost
SMTP hostname.
### port      : 0
SMTP port. Usually 25 for an external server over SMTP. 0 for the local mail system.
### frommail  : planetarion@yourdomain.com
From address. Preferably one you can view mail for.

## [imap]
### user      : 
IMAP username for the email notifications parser (see [README.md](https://github.com/d7415/merlin#imap-support) for details).
### pass      : 
*If you don't specify a password here, IMAPPush.py will prompt for it.*  
IMAP password. If not specified here, it will be requested at runtime.
### host      : imap.gmail.com
IMAP server.
### ssl       : True
Should the bot connect via SSL? This should be set to True wherever SSL is available.
### bounce    : 
*Address to warn if user not found*  
If a lookup fails in the email parser, it will bounce to this address with a warning.
### forwarding: True
If False, no mail will be forwarded. Notifications will still be send on after parsing so long as SMTP settings are configured.
### defsuffix : -def
This is used to differentiate PA notifications from other email.
### singleaddr: False
*Allows using a normal gmail account or similar, using address+pnick@gmail.com. In this mode, a blank defsuffix is recommended.*  
This changes the parser to look for username+pnick@domain rather than pnick-suffix@domain. More details in [README.md](https://github.com/d7415/merlin#imap-support).

## [FluxBB]
### enabled   : False
*enabled:  Enables FluxBB integration.*  
Enable FluxBB integration. This includes automatically creating accounts and adding a link to Arthur. See [README.md](https://github.com/d7415/merlin#fluxbb-integration) for further details.
### url       : 
*url:      URL for FluxBB installation.*  
FluxBB's URL.
### prefix    : fluxbb_
*prefix:   Table prefix for FluxBB.*  
FluxBB allows setting a prefix for all its tables. This is very useful for preventing conflicts and to see at a glance what is part of the bot and what is part of the forums.
### memgroup  : 4
*memgroup: ID of the default FluxBB usergroup for members. Set to 0 to disable adding members (Will still update existing accounts).*  
When auto-adding members to FluxBB, add them to this group.
### galgroup  : 3
*galgroup: ID of the default FluxBB usergroup for galmates. Set to 0 to disable adding galmates (Will still update existing accounts).*  
When auto-adding galmates to FluxBB, add them to this group.

