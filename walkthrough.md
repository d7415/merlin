## Simple Merlin Installation Walkthrough
This won't necessarily result in the best merlin installation ever, but it **should** work.  
Any improvements or alternative versions are welcome.

### Starting Point
Debian Squeeze (6.0). In this case, the very bare version found on Chicago VPS.  
If you have Wheezy (7.0) or better, you can skip step one and just run `apt-get update` before proceeding.

### Assumptions
Running as root, without sudo installed. If you have sudo you can run `sudo -s` to open a root shell.  
If you don't like `vi`, feel free to use `nano` or your preferred editor.

## Step One: Upgrade from Squeeze
    vi /etc/apt/sources.list
Replace all occurences of "squeeze" with "wheezy"

    apt-get update && apt-get dist-upgrade

## Step Two: Set up the environment
Enable bash auto-completion (press tab to complete commands/filenames)

    vi /etc/bash.bashrc 

Enable colours in bash

    vi ~/.bashrc

## Step Three: Install packages
    apt-get install vim-nox bash-completion screen git postgresql python-sqlalchemy python-psycopg2 python-django python-jinja2 python-numpy python-matplotlib python-bcrypt nginx logrotate

`vim-nox` and  `bash-completion` just make life nicer. `screen` is used to keep the bot running after you logout. `git` is used to fetch and update the bot. `postgresql`, `python-sqlalchemy`, `python-psycopg2`, `python-django` and `python-jinja2` are basic merlin/arthur dependencies. `python-numpy` and `python-matplotlib` have lots of dependencies, but are needed for graphing in arthur. `python-bcrypt` provides bcrypt support, which is recommended unless you are using FluxBB integration. `nginx` is an alternative to apache, and is my preference. `logrotate` should be automatically installed as a dependency of postgresql, but installing manually won't hurt. It will be used to keep merlin's log files to a manageable size.

## Step Four: Add a new user for merlin
We'll create "merlin" as a normal user. You can rename this if you wish, but you may have to change other things further down the line. You can run more than one bot with the same username (in fact, it's easier).  
Note that running a bot as root is a **bad** idea as any security issues will result in compromise of the whole machine.

    useradd -ms /bin/bash merlin

## Step Five: Set up the database
Become the database superuser

    su postgres

Start the PostgreSQL client

    psql

Create the database and user. You'll probably want to choose a different password.

    CREATE DATABASE merlin ENCODING = 'UTF8' TEMPLATE template0;
    CREATE USER merlin WITH PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE merlin TO merlin;
    \q

Capitals are not required, but are used by convention.

Open the new database

    psql merlin

Make sure it's owned by the new merlin user

    ALTER SCHEMA public OWNER TO merlin;
    \q

Logout of postgres user

    exit

## Step Six: Set up the bot
Login as the bot

    su merlin

Go to the home directory

    cd /home/merlin

Delete user files (they'll be recreated automatically)

    rm .*

Clone the git repository

    git clone https://github.com/d7415/merlin.git .

Create log files

    touch dumplog.txt errorlog.txt arthurlog.txt scanlog.txt

Checkout the branch you want. Replace source_branch with any branch or tag name. For more details see [Branches](https://github.com/d7415/merlin/wiki/Branches)

    git checkout source_branch

Create a branch for your bot

    git checkout -b my_branch

Edit merlin.cfg. If necessary, you should also add any other bots to excalibur.py  
For more details, `less README.md`

    vi merlin.cfg

Add your details to git

    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"

Commit your changes. Add a comment. "Config for bot_name" is a good starting point.

    git commit -a

Set up the database tables

    python createdb.py --new

Logout of merlin

    exit

## Step Seven: Some permissions...
For another way to achieve this, see `README.Posix`.

Add www-data to merlin's group

    usermod -aG merlin www-data

Grant write permissions to the group where required

    chmod g+w arthurlog.txt Arthur/graphs

Make the matplotlib directory, and make sure it is owned by the nginx user.

    mkdir -p /var/www/.matplotlib
    chown www-data:www-data /var/www/.matplotlib

## Step Eight: Set up the ticker
Open the crontab

    vi /etc/crontab

Add a line for excalibur

    1  *    * * *   merlin  python /home/merlin/excalibur.py >> /home/merlin/dumplog.txt 2>&1

## Step Nine: Set up nginx
Open/create a config file for arthur

    vi /etc/nginx/sites-available/arthur

Once you're done, it should look like this

    server {
        listen 80;
        server_name arthur.your-domain.com;
        access_log /var/log/nginx/arthur.log;
        error_log /var/log/nginx/arthur_err.log;
        root /home/merlin/Arthur/;

        location /static/ {
            alias /home/merlin/Arthur/static/;
            expires 30d;
        }

        location /media/ {
            alias /home/merlin/Arthur/static/;
            expires 30d;
        }

    #    Uncomment this section to enable sharing of dump files
    #    location /dumps/ {
    #        alias /home/merlin/dumps/;
    #        autoindex on;
    #    }

    #    Uncomment this section to point arthur.your-domain.com/forum/ at a FluxBB installation at /var/www/fluxbb/
    #    location /forum/ {
    #        alias /var/www/fluxbb/;
    #        index index.php;
    #    }

        location /favicon.ico {
            alias /home/merlin/Arthur/static/favicon.ico;
            expires 30d;
        }

        location /robots.txt {
            alias /home/merlin/Arthur/static/robots.txt;
            expires 30d;
        }

        location / {
            proxy_pass http://127.0.0.1:8000;
        }
    }

If you have more than one arthur running, you will need to specify different ports to run on. To do this, edit arthur.py, and add a port number to the last line, e.g.

    application = django.core.management.commands.runserver.Command().execute("8002")

Then alter the proxy_pass line of the nginx config.

Enable the new site...

    cd /etc/nginx/sites-enabled/
    ln -s ../sites-available/arthur .
    /etc/init.d/nginx restart

## Step Ten: Start the bot!
    cd /home/merlin
    screen
    su merlin
    python merlin.py

Press `ctrl+a, c` to start a new window in screen.

    su merlin
    python arthur.py

If required, repeat for IMAPPush.py, etc

## Step Eleven: Final steps!
You should now have a working bot (merlin), website (arthur) and ticker (excalibur). Talk to the bot, as described in README.md (`!secure`, `!reboot`, `!adduser`, etc)

## Step Twelve (optional): Set up logrotate
As root, create a new logrotate configuration file for merlin

    vi /etc/logrotate.d/merlin

Once you're done, the file should look something like this

    /home/merlin/*log.txt {
        rotate 1
        size 100k
        compress
        copytruncate
    }

