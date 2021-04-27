<?xml version="1.0" encoding="UTF-8"?>
<!--
 Copyright © 2021 Waleed H. Mebane

   This file is part of Allsembly™ Prototype.

   Allsembly™ Prototype is free software: you can redistribute it and/or
   modify it under the terms of the Lesser GNU General Public License,
   version 3, as published by the Free Software Foundation and the
   additional terms directly below this notice.

   Allsembly™ Prototype is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   Lesser GNU General Public License for more details.

   You should have received a copy of the Lesser GNU General Public
   License along with Allsembly™ Prototype.  If not, see
   <https://www.gnu.org/licenses/>.

   Additional terms:

   Without his or her specific prior written permission, neither may the names
   of any author of or contributor to this software be used to endorse products
   derived from this software nor may his or her names, image, or likeness be
   used to promote products derived from this software.

   Nothing in this license shall be interpreted as granting any license to
   any of the trademarks of any of the authors of or contributors to this
   software.
-->
<!--
This implements the client side of logging in to the Allsembly server.
Implementing it as an XSL template simplifies what the CGI has to do,
but will also make it easy to do localization in the future by including
(using "xsl-include") an XML file that contains the strings to use.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="/">
	<html lang="en">
<head>
    <meta charset="utf-8" />
    <style>
        form {
            margin 0 auto;
            width 250px
        }
    </style>
</head>
<body>

        <xsl:for-each select="BadAuth">
            <p style="color:red">Incorrect UserId or Password</p>
        </xsl:for-each>
        <xsl:for-each select="MissingUserId">
            <p style="color:red">Missing UserId</p>
        </xsl:for-each>
        <xsl:for-each select="MissingPassword">
            <p style="color:red">Missing Password</p>
        </xsl:for-each>

    <form action="/cgi-bin/allsembly_demo.py" method="POST">
        <p>
        <label>UserId: </label>
        <input name="userid"/>
        </p>
        <p>
        <label>Password: </label>
        <input name="password" type="password"/>
        </p>
        <p>
        <button type="submit">Submit</button>
        </p>
    </form>
</body>
</html>
	</xsl:template>
</xsl:stylesheet>