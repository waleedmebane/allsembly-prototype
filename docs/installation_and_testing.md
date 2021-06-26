Installation and Testing
========================

## License

Please find the license terms in the file: LICENSE.txt.
The license is LGPLv3-only with two additional terms, disallowing using the
authors' names and likenesses and declining to grant license to use trademarks.

The Javascript libraries "d3", "dialog-polyfill", and "simple-jsonrpc-js"
are included with this software in the sub-directory:
web/scripts

Their license terms and copyright notices are in files in the sub-directory:
LICENSE.third-party.  The respective license terms file has its
suffix named after the name of the library.  They are under permissive,
BSD and MIT, license terms.

How to install (for Ubuntu 16.04 or Ubuntu 18.04)
---------------------------------

Dependencies:
 Python >=3.7 (tested with Python 3.7.4 and Python 3.7.10)
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

Next, install Python.  If you are using Ubuntu 16.04 or 18.04, you will need to 
install from source.  With later versions of Ubuntu you may be able
to install using `apt-get install python3` (you need a Python version >=3.7), 
but it will place Python in /usr/bin; so you will either have to modify the 
first line of the scripts from `#!/usr/local/bin/python3` to 
`#!/usr/bin/python3` or place a link in /usr/local/bin (i.e., 
`sudo ln -si /usr/bin/python3 /usr/local/bin/python3`).

To compile from source, first obtain the source code from:
https://www.python.org/downloads/release/python-374
And then follow the instructions in the README.rst file, which amount to:

    sudo apt-get build-dep python3.5
    ./configure
    make
    make test
    sudo make install

(`*`See the bottom of this section for a tip in case you get an error message
about needing to add a source repository in order to install build
dependencies--the first step listed above.)


Next, use pip to install the Python packages:

```
sudo python3.7 -m ensurepip
sudo python3.7 -m pip install --upgrade pip
sudo python3.7 -m pip install pygraphviz json-rpc problog ZODB Werkzeug flup RPyC persistent transaction  atomic readerwriterlock argon2-cffi cryptography typing python-daemon
```

Install the Allsembly™ package:

Clone or download the [source code repository](https://github.com/waleedmebane/allsembly-prototype) 
files into a directory, "allsembly-prototype". <br />
cd to the directory allsembly-prototype, then:

```sudo python3.7 -m pip install .```

OR to install for easy development:

```sudo python3.7 -m pip install --editable .```

Create a new system user named, e.g., "allsembly"
  and give that user permission to read and write /var/allsembly-prototype/data 

```
sudo adduser --system --no-create-home allsembly
sudo mkdir -p /var/allsembly-prototype/data
sudo chown allsembly /var/allsembly-prototype/data
```

Make sure the Python scripts have the executable bit set:

```chmod a+x allsembly-prototype/scripts/allsembly*.py```

Add an Allsembly™ user:

This should ideally be done while the Allsembly™ server
  is not running.

```
sudo su allsembly -s /bin/bash
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
  
```
cd allsembly-prototype/scripts
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

```
sudo mkdir -p /var/www/html/allsembly
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

```allsembly-prototype/scripts/allsembly_dev_demo.py -c '/home/<your-linux-userid>/allsembly_test_cert/' -w 'allsembly-prototype/web/'```

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


*NOTE: When building Python3.7.4 from source code, you might get an error
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

pytest may be installed with `python3.7 -m pip install pytest`.

