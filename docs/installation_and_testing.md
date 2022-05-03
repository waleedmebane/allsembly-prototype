Installation and Testing
========================

## License

Please find the license terms in the file: LICENSE.txt.
The license is LGPLv3-only with three additional terms: 1) disallowing using the
authors' names and likenesses; 2) declining to grant license to use trademarks; 
and 3) providing additional permission for static linking.

The Javascript libraries "d3", "dialog-polyfill", and "jquery"
are included with this software in the sub-directory:
web/scripts

Their license terms and copyright notices are in files in the sub-directory:
LICENSE.third-party.  The respective license terms file has its
suffix named after the name of the library.  They are under permissive,
BSD and MIT, license terms.

How to install (for Ubuntu 16.04 or Ubuntu 18.04)
---------------------------------

Dependencies:
 Python >=3.7 (tested with Python 3.9.5)
 pip
 Apache2
 mod_wsgi
 graphviz
 graphviz-dev

 Python packages:
  problog
  ZODB
  pygraphviz
  RPyC
  persistent
  transaction
  atomic
  readerwriterlock
  typing
  python-daemon
  django

Install Apache2 and graphviz:

```
sudo apt-get update
sudo apt-get install apache2 graphviz graphviz-dev apache2-dev
```

The apache2-dev package might not be necessary if you install Python and
mod_wsgi from Ubuntu packages rather than using the method in the 
instructions below.  The mod_wsgi package needs to be one that was built
for the version of Python it will be used with.

Next, install Python.  If you are using Ubuntu 16.04 or 18.04, you will need to 
install from source.  With later versions of Ubuntu you may be able
to install using `apt-get install python3` (you need a Python version >=3.7), 
but it will place Python in /usr/bin; so you will either have to modify the 
first line of the scripts from `#!/usr/local/bin/python3` to 
`#!/usr/bin/python3` or place a link in /usr/local/bin (i.e., 
`sudo ln -si /usr/bin/python3 /usr/local/bin/python3`).  If you install
Python using apt, then also install libapache2-mod-wsgi using apt as
`apt-get install libapache2-mod-wsgi`; otherwise, install mod_wsgi using
pip as described below.

To compile from source, first obtain the source code from:
https://www.python.org/downloads/release/python-395
And then follow the instructions in the README.rst file, which amount to:

    sudo apt-get build-dep python3.5
    ./configure --enable-optimizations --enable-shared LDFLAGS=-Wl,-rpath=/usr/local/lib
    make
    sudo make install

The configure options, except --enable-optimization, which is optional,
are needed for Python to work well with mod_wsgi.
(`*`See the bottom of this section for a tip in case you get an error message
about needing to add a source repository in order to install build
dependencies--the first step listed above.)


Next, install pip:

```
sudo python3.9 -m ensurepip
sudo python3.9 -m pip install --upgrade pip
```

#### Install the Allsembly™ package:

Clone or download the [source code repository](https://github.com/waleedmebane/allsembly-prototype) 
files into a directory, "allsembly-prototype". <br />
cd to the directory allsembly-prototype, then:

```sudo python3.9 -m pip install .```

OR to install for easy development:

```sudo python3.9 -m pip install --editable .```

Create a new system user named, e.g., "allsembly"
  and give that user permission to read and write /var/allsembly-prototype/data 

```
sudo adduser --system --no-create-home allsembly
sudo mkdir -p /var/allsembly-prototype/data
sudo chown allsembly /var/allsembly-prototype/data
```

Make sure the server script has the executable bit set:

```chmod a+x allsembly-prototype/scripts/allsembly-server.py```

Create the user database:

```
cd allsembly-prototype
python3.9 manage.py migrate
```

#### Add an Allsembly™ user:

```
python3.9 manage.py shell
Python 3.9.5 (default, Jul 19 2021, 01:21:38) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('username', '', 'password')
>>> exit()
```

Replace "username" and "password", above, with your desired username
and password.

#### Run the Allsembly™ server:
  
```
cd allsembly-prototype/scripts
sudo ./allsembly-server.py --daemon --user allsembly
```

NOTE: to get it to persist across reboots, you will need a service script
for systemd or initd.  See allsembly-prototype/scripts/allsembly.service
for an example.  Modify the path on the line starting with "ExecStart="
to point to the location of allsembly-server.py on your system.  You 
then need to copy the service script into the appropriate system
location: /etc/systemd/system/; and run
the command to enable the service: `sudo systemctl enable allsembly.service`.
Alternatively, you could put a line like:
`<directory containing allsembly-server.py>/allsembly-server.py --daemon --user allsembly` into your /etc/rc.local file.
(Replace `<directory containing allsembly-server.py>` with the path where you have put the file, e.g., `/usr/local/bin` or `/home/user/allsembly-prototype/scripts`.)


### Setup and start the Apache web server:
(NOTE: you can try out Allsembly™ using the web server build into
Django.  Consult the Django documentation for details.  Basically,
you can execute `python3 manage.py runserver` from the allsembly-prototype
directory; then connect to http://127.0.0.1:8000.  You can skip setting
up Apache and return to it later when you desire a production quality 
web service.)

#### Setup SSL (Recommended)
Add an SSL certificate, either by following the directions given by
  your webhosting provider or by using Certbot to install a Let's Encrypt
  certificate: https://certbot.eff.org

#### Enable mod-wsgi:

```
sudo python3.9 -m pip install mod_wsgi
sudo sh -c 'mod_wsgi-express module-config > /etc/apache2/mods-available/wsgi.load'
sudo a2enmod wsgi
```

Add the following lines to the bottom of /etc/apache2/apache2.conf:

```
WSGIDaemonProcess wsgipgroup user=<user> python-path="/home/<user>/allsembly-prototype"
WSGIProcessGroup wsgipgroup
```
Replace ```/home/<user>``` with the path into which you have cloned or
copied the allsembly-prototype repository, and replace ```<user>``` in
```user=<user>``` with the name of a user that has read and execute 
permisions, as appropriate, in the django-site and django-app directories,
or the owner of those directories.  You may use any name for the name
of the process group.


Add the following lines between of your virtual host's VirtualHost 
open/close tags (e.g., `<Virtualhost ...>...</VirtualHost>`), which may
be in one of your configuration files in /etc/apache2/sites-enabled, 
such as /etc/apache2/sites-enabled/000-default.conf or
/etc/apache2/sites-enabled/default-ssl.conf (if you have SSL configured):

```
Alias "/static/" "/home/<user>/allsembly-prototype/web/scripts/"
WSGIScriptAlias "/allsembly" "/home/<user>/allsembly-prototype/django_site/wsgi.py"
<Directory /home/<user>/allsembly-prototype/django_site>
  <Files wsgi.py>
    Require all granted
  </Files>
</Directory>
<Directory /home/<user>/allsembly-prototype/web/scripts>
  Require all granted
</Directory>
```

Replace ```/home/<user>``` with the path into which you have cloned or
copied the allsembly-prototype repository.

Restart the Apache server:

```sudo apachectl restart```

Add your hostname and/or IP address to the list of allowed hosts in the
Django settings file by editing allsembly-prototype/django_site/settings.py
changing ```ALLOWED_HOSTS = []``` to ```ALLOWED_HOSTS = ['hostname']```.
Replace "hostname" with your hostname, e.g., "waleedmebane.com".

You will likely wish to **set ```DEBUG = False```** in the 
allsembly-prototype/django_site/settings.py file before making a
public-facing deployment, but ```DEBUG = True``` is useful while checking
that one's installation and configuration is correct. 

Open a web browser and navigate to https://\<your-server-hostname\>/allsembly <br />
Enter the userid and password of the user you created in a previous step.


*NOTE: When building Python3.9.5 from source code, you might get an error
message on the first step of installing build dependencies.
In that case, you might have to uncomment a line beginning with "deb-src"
near the top of your /etc/apt/sources.list file and then run 
`sudo apt-get update` to populate the cache.

How to install for other platforms
----------------------------------

The software has only been tested with Ubuntu 16.04 and 18.04; 
however, I believe that the only platform specific parts are the `--daemon` 
option, the `--user` option and platform specific file paths.  These should
work on many other Unix-like or Unix operating systems.  So it might
work with MacOS.  The allsembly-server.py script might run under Windows
if you set all of the file options with Windows-specific pathnames and
skip the options `--daemon` and `--user`.  I believe the first line 
beginning "#!" has no effect on Windows, and it, instead, uses the file
extension to determine which application (i.e., the Python interpreter) to
use to load the file according to its registry of file types.
You might try putting the script in the Windows startup folder or check 
your Windows Server OS documentation for appropriate ways to cause it to 
run at startup and to restrict its privileges.  There might be a RunAs 
option on the script's properties window.

How to run the tests
--------------------

The tests may be run using pytest (See https://pytest.org).

With pytest installed, simply run pytest from the main directory of the
distribution by typing `pytest`.  It will automatically discover the tests 
(which are in the subdirectory "test"), run them, and report the results.

pytest may be installed with `python3.9 -m pip install pytest`.

