"""
    Smithproxy- transparent proxy with SSL inspection capabilities.
    Copyright (c) 2014, Ales Stibal <astib@mag0.net>, All rights reserved.

    Smithproxy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Smithproxy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Smithproxy.  If not, see <http://www.gnu.org/licenses/>.

    Linking Smithproxy statically or dynamically with other modules is
    making a combined work based on Smithproxy. Thus, the terms and
    conditions of the GNU General Public License cover the whole combination.

    In addition, as a special exception, the copyright holders of Smithproxy
    give you permission to combine Smithproxy with free software programs
    or libraries that are released under the GNU LGPL and with code
    included in the standard release of OpenSSL under the OpenSSL's license
    (or modified versions of such code, with unchanged license).
    You may copy and distribute such a system following the terms
    of the GNU GPL for Smithproxy and the licenses of the other code
    concerned, provided that you include the source code of that other code
    when and as the GNU GPL requires distribution of source code.

    Note that people who make modified versions of Smithproxy are not
    obligated to grant this special exception for their modified versions;
    it is their choice whether to do so. The GNU General Public License
    gives permission to release a modified version without this exception;
    this exception also makes it possible to release a modified version
    which carries forward this exception.
    """

import string
import cgi


def print_message(pagename, caption, message, redirect_url=None, redirect_time=5):
    print ("Content-type:text/html\r\n\r\n")

    page = """
        <html>
        <head>
                <title>$pagename</title>
                <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">
                $redirect_meta
                <style media="screen" type="text/css">
                    * {
                    box-sizing: border-box;
                    }
                    
                    *:focus {
                    outline: none;
                    }
                    body {
                    font-family: Arial;
                    background-color: #48617B;
                    padding: 50px;
                    }
                    .login {
                    margin: 20px auto;
                    width: 300px;
                    }
                    .login-screen {
                    background-color: #FFF;
                    padding: 20px;
                    border-radius: 5px
                    }
                    
                    .app-title {
                    text-align: center;
                    color: #777;
                    }
                    
                    .login-form {
                    text-align: center;
                    }
                    .control-group {
                    margin-bottom: 10px;
                    }
                    
                    input {
                    text-align: center;
                    background-color: #ECF0F1;
                    border: 2px solid transparent;
                    border-radius: 3px;
                    font-size: 16px;
                    font-weight: 200;
                    padding: 5px 0;
                    width: 250px;
                    transition: border .5s;
                    }
                    
                    input:focus {
                    border: 2px solid #3498DB;
                    box-shadow: none;
                    }
                    
                    .btn {
                    border: 2px solid transparent;
                    background: #3498DB;
                    color: #ffffff;
                    font-size: 16px;
                    line-height: 25px;
                    padding: 5px 0;
                    text-decoration: none;
                    text-shadow: none;
                    border-radius: 3px;
                    box-shadow: none;
                    transition: 0.25s;
                    display: block;
                    width: 250px;
                    margin: 0 auto;
                    }
                    
                    .btn:hover {
                    background-color: #2980B9;
                    }
                    
                    .login-link {
                    font-size: 12px;
                    color: #444;
                    display: block;
                    margin-top: 12px;
                    }
            </style>    
                
        </head>
        <body>
        <div class="login">
        <div class="login-screen">
        <div class="app-title">        
        $message
        </body> 
        </html> 
        """

    t = string.Template(page)
    meta = ""
    if redirect_url != None:
        meta = "<meta http-equiv=\"Refresh\" content=\"%d; url=%s\">" % (redirect_time, redirect_url)

    print(t.substitute(pagename=cgi.escape(pagename),
                       caption=cgi.escape(caption),
                       message=cgi.escape(message),
                       redirect_meta=meta))

