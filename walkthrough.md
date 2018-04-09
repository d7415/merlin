## Simple Merlin Installation Walkthrough
This won't necessarily result in the best merlin installation ever, but it **should** work.  
Any improvements or alternative versions are welcome.

### Starting Point
Debian Stretch (9.3). Minimal installation, with ssh and systemd.
This should also work for Debian Jessie (8.0), but that hasn't been tested for a while.

### Assumptions
* These instructions will require root access.
* We will create a user `merlin` for the bot and website.
* You know how to use `vim`. If you don't like `vim`, feel free to use `nano` or your preferred editor.

## Step One: Install packages
    sudo apt-get install git postgresql python-sqlalchemy python-psycopg2 python-future python-configparser python-django python-jinja2 python-numpy python-matplotlib python-bcrypt nginx logrotate

`git` is used to fetch and update the bot. `postgresql`, `python-sqlalchemy`, `python-psycopg2`, `python-future`, `python-configparser`, `python-django` and `python-jinja2` are basic merlin/arthur dependencies. `python-numpy` and `python-matplotlib` have lots of dependencies, but are needed for graphing in arthur. `python-bcrypt` provides bcrypt support, which is recommended unless you are using FluxBB integration. `nginx` is an alternative to apache, and is my preference. `logrotate` should be automatically installed as a dependency of postgresql, but installing manually won't hurt. It will be used to keep merlin's log files to a manageable size.

## Step Two: Add a new user for merlin
We'll create "merlin" as a normal user. You can rename this if you wish, but you may have to change other steps later in this file. You can run more than one bot with the same user account (in fact, it's easier).  
Note that running a bot as root is a **bad** idea as any security issues will result in compromise of the whole machine.

    sudo useradd -ms /bin/bash merlin

## Step Three: Set up the database
Start the PostgreSQL client as the database superuser

    sudo -u postgres psql

Create the database and user. You'll probably want to choose a different password.

    CREATE DATABASE merlin ENCODING = 'UTF8' TEMPLATE template0;
    CREATE USER merlin WITH PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE merlin TO merlin;
    \q

Capitals are not required, but are used by convention.

Open the new database

    sudo -u postgres psql merlin

Make sure it's owned by the new merlin user

    ALTER SCHEMA public OWNER TO merlin;
    \q

## Step Four: Set up the bot
Login as the bot

    sudo su merlin

Go to the home directory

    cd

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

    vim merlin.cfg

Add your details to git

    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"

Commit your changes. Add a comment. "Config for bot_name" is a good starting point.

    git commit -a

Set up the database tables

    python createdb.py --new

Logout of merlin

    exit

## Step Five: Some permissions...
For another way to achieve this, see `README.Posix`.

Add www-data to merlin's group

    sudo usermod -aG merlin www-data

Grant write permissions to the group where required

    sudo chmod g+w /home/merlin/arthurlog.txt /home/merlin/Arthur/graphs

Make the matplotlib directory, and make sure it is owned by the nginx user.

    sudo mkdir -p /var/www/.matplotlib
    sudo chown www-data:www-data /var/www/.matplotlib

## Step Six: Set up the ticker
Open the crontab file

    sudo vim /etc/crontab

Add a line for excalibur

    1  *    * * *   merlin  python /home/merlin/excalibur.py >> /home/merlin/dumplog.txt 2>&1

## Step Seven: Set up nginx
Open/create a config file for arthur

    sudo vim /etc/nginx/sites-available/arthur

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

    application = call_command("runserver", "8002")

Then alter the proxy_pass line of the nginx config.

Enable the new site...

    cd /etc/nginx/sites-enabled/
    sudo ln -s ../sites-available/arthur
    sudo systemctl reload nginx

## Step Eight: Setup systemd services
Edit the sample unit files, changing `(botname)` to your bot's name - twice in each file. If you are only running one bot, you may wish to remove the "(botname)" parts instead.

    vim /home/merlin/*.service

Copy the newly edited files into place

    sudo cp /home/merlin/*.service /etc/systemd/system/

Then load and enable them

    sudo systemctl daemon-reload
    sudo systemctl enable merlin.service
    sudo systemctl enable arthur.service

## Step Nine: Start the bot!
    sudo systemctl start merlin.service
    sudo systemctl start arthur.service

## Step Ten: Final steps!
You should now have a working bot (merlin), website (arthur) and ticker (excalibur). Talk to the bot, as described in README.md (`!secure`, `!reboot`, `!adduser`, etc)

## Step Eleven (optional): Set up logrotate
Create a new logrotate configuration file for merlin

    sudo vim /etc/logrotate.d/merlin

The file should look something like this

    /home/merlin/*log.txt {
        rotate 1
        size 100k
        compress
        copytruncate
    }

