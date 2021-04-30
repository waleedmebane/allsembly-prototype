Allsembly™ Prototype
====================

This is software for creating an online community for anonymous proposal and collaborative evaluation of public policy options, with automated decision support.
It makes use of betting markets and Bayesian networks.
Some additional explanation may be found in misc/notes.md.

Only about half of the major features have been added, so far.

## License

Please find the license terms in the file: LICENSE.txt
The Javascript libraries "d3", "dialog-polyfill", and "simple-jsonrpc-js"
are included with this software in the sub-directory:
web/scripts

Their license terms and copyright notices are in files in the sub-directory:
LICENSE.third-party.  The respective license terms file has its
suffix named after the name of the library.

How to install (for Ubuntu 16.04)
---------------------------------

Dependencies:
 Python >=3.6.5 (tested with Python 3.7.4)
 pip
 Apache2
 openssl
 libapache2-mod-fcgid
 graphviz
 graphviz-dev

 Python packages:
  problog
  ZODB
  pygrphviz
  json-rpc
  Werkzeug
  flup
  RPyC
  persistent
  transaction
  atomic
  readerwriterlock
  argon2-cffi
  cryptography
  typing
  python-daemon

Install Apache2, mod-fcgid, openssl, and graphviz:

`sudo apt-get install apache2 libapache2-mod-fcgid openssl graphviz graphviz-dev`

Next, install Python.  If you are using Ubuntu 16.04, you will need to 
install from source.  With later versions of Ubuntu you may be able
to install using `apt-get install python3`, but it will place Python
in /usr/bin; so you will either have to modify the first line of the
scripts from `#!/usr/local/bin/python3` to `#!/usr/bin/python3` or
place a link in /usr/local/bin (i.e., `sudo ln -si /usr/bin/python3 /usr/local/bin/python3`).

To compile from source, first obtain the source code from:
https://www.python.org/downloads/release/python-374
And then follow the instructions in the README.rst file, which amount to:

    sudo apt-get build-dep python3.5
    ./configure
    make
    make test
    sudo make install

(`*`See the bottom of this file for a tip in case you get an error message
about needing to add a source repository in order to install build
dependencies--the first step listed above.)
(I haven't tested with versions of Python other than 3.7.4, yet.
One dependency, Problog, requires Python >=3.6.5.)


Next, use pip to install the Python packages:

```
sudo python3.7 -m ensurepip
sudo python3.7 -m pip install --upgrade pip
sudo python3.7 -m pip install pygraphviz json-rpc problog ZODB Werkzeug flup RPyC persistent transaction  atomic readerwriterlock argon2-cffi cryptography typing python-daemon
```

Install the Allsembly™ package:

cd to the directory allsembly-prototype

```sudo python3.7 -m pip install .```

OR to install for easy development:

```sudo python3.7 -m pip install --editable .```

Create a new system user named, e.g., "allsembly"
  and give that user permission to read and write /var/allsembly/data

```
sudo adduser --system --no-create-home allsembly
sudo chown allsembly /var/allsembly-prototype/data
```

Make sure the Python scripts have the executable bit set:

```chmod a+x allsembly-prototype/scripts/allsembly*.py```

Add an Allsembly™ user:

This should ideally be done while the Allsembly™ server
  is not running.

```sudo su allsembly -s /bin/bash
allsembly-prototype/scripts/allsembly_add_user.py
```

Follow the prompts.<br />
Then:

```
exit
```

Run the Allsembly™ server:

Before running the server, you may change any configuration settings
  in the server_config.py file.
  
```cd allsembly-prototype/scripts
sudo su allsembly -s /bin/bash
./allsembly-server.py --daemon
exit
```

NOTE: to get it to persist across reboots, you will need a service script
for systemd or initd.  I haven't written one, yet.  Come back to the repo
to check for it later.  Or you can write one consulting your OS documentation.
In the meantime, you could put a line like:
`<directory containing allsembly-server.py and server_config.py>/allsembly-server.py --daemon --user allsembly` into your /etc/rc.local file.
(Replace `<directory containing allsembly-server.py and server_config.py>` with the path where you have put the files, e.g., `/usr/local/bin` or `/home/user/allsembly-prototype/scripts`.)


### Setup and start the Apache web server:

_(You may skip this step and return to it later if you just want to
try out Allsembly.  Go to the section, below: "...development web server".)_

Add an SSL certificate, either by following the directions given by
  your webhosting provider or by using Certbot to install a Let's Encrypt
  certificate: https://certbot.eff.org

Enable mod-fcgi:

```sudo a2enmod fcgid```

Add the following lines to /etc/apache2/apache2.conf:

```
FcgidIOTimeout 1800

Alias "/cgi-bin/" "/usr/local/apache2/cgi-bin/"
<Location "/cgi-bin">
SetHandler fcgid-script
Options +ExecCGI
Require all granted
#Optionally uncomment the lines below to limit the number of bytes
# that can be sent in a single request to the FastCGI scripts in 
# this directory.
#LimitRequestBody 64000
#LimitXMLRequestBody 64000
</Location>
```

Make the directory /usr/local/apache2/cgi-bin/:

```sudo mkdir -p /usr/local/apache2/cgi-bin/```

Copy the FastCGI script into that directory:

```sudo cp -i allsembly-prototype/scripts/allsembly_demo.py /usr/local/apache2/cgi-bin/```

Move the web files to the web root:

```sudo mkdir -p /var/www/html/allsembly
sudo cp -ir allsembly-prototype/web/* /var/www/html/allsembly
```

Restart the Apache server:

```sudo apachectl restart```

Open a web browser and navigate to https://\<your-server-hostname\>/cgi-bin/allsembly_demo.py
Enter the userid and password of the user you created in a previous step.


### Try out Allsembly™ using the development web server.
Create a directory to store the SSL certificate:

`mkdir ~/allsembly_test_cert`

Create a self-signed SSL certificate.  You only need to do this step once.
(Replace '\<your-linux-userid\>' below with your own userid.)

```
python3.7
Python 3.7.4 (default, Apr 22 2021, 18:55:44) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from werkzeug.serving import make_ssl_devcert
>>> make_ssl_devcert('/home/<your-linux-userid>/allsembly_test_cert/', host='localhost')
('/home/<your-linux-userid>/allsembly_test_cert/.crt', '/home/<your-linux-userid>/allsembly_test_cert/.key')
>>> quit()
```

Start the development server:

allsembly-prototype/scripts/allsembly_dev_demo.py -c '/home/<your-linux-userid>/allsembly_test_cert/' -w 'allsembly-prototype/web/'

That will start a server running on locahost port 8443.
If you are running the server on a remote machine, use the -s or --host option 
to give the IP address of the server.  You should also create your SSL 
certifcate with host='\<your-server-hostname\>' in the previous step, e.g.: 
`make_ssl_devcert('/home/\<your-linux-userid\>/allsembly_test_cert/', host='waleedmebane.com')`.

Your firewall might block ports other than 80 and 443.  If so, you can run the server with the option -p 443, but you also have to run it as root (using sudo) since access to ports <=1024 is privileged.

Open your browser and go to https://localhost:8443 or https://\<your-server-hostname\>:\<your-server-port-number\> 
Your browser will warn you that the connection is not secure since you are
using a self-signed certificate.  Click the appropriate button to bypass the
warning.
Enter the userid and password of the user you created in a previous step.


NOTE: When building Python3.7.4 from source code, you might get an error
message on the first step of installing build dependencies.
In that case, you might have to uncomment a line beginning with "deb-src"
near the top of your /etc/apt/sources.list file and then run 
`sudo apt-get update` to populate the cache.

How to run the tests
--------------------

The tests may be run using pytest (See https://pytest.org).

With pytest installed, simply run pytest from the main directory of the
distribution by typing `pytest`.  It will automatically discover the tests 
(which are in the subdirectory "tests"), run them, and report the results.

pytest may be installed with `python3.7 -m pip install pytest`.

Misc
----

NOTE: This project is uses typed Python.  The mypy settings are in the
file setup.cfg.  It uses all of the settings from mypy --strict
(as of mypy version 0.812) except --disallow-subclassing-any, which
is not used (especially) since some classes subclass "Persistent" in order
to take advantage of the ZODB database.

The modules may be type-checked using the following command from the
command line from within the main directory of the project:
`mypy allsembly/*.py`.  It should report no errors.

For more information about mypy or about optional type-checking in Python,
see http://mypy-lang.org.

Mypy may be installed with: `python3.7 -m pip install mypy`.

Settings for Pylint (see https://pylint.org) are also in the setup.cfg file.
With Pylint installed, the modules may be linted by running Pylint from the 
command line as follows:
`pylint --rcfile=setup.cfg allsembly`.

The Pylint settings in setup.cfg correspond to:
`pylint --disable=all -enable F,E,W --disable=python3`.
This will report many warnings, mostly about unused variables and two
errors about imports.  The errors are false positives as far as I can
tell.  The module is successfully using the imported class (OOBTree).
I plan to attend to the warnings.
I also look at the output of the refactoring module even though it 
is disabled in setup.cfg, and I plan to implement some of its refactoring
recommendations.
