# PoC #
Repo for proof of concept exploits and tools.

## BMC\_RSCD\_RCE ##
Unauthenticated remote command execution exploit for BMC Server Automation's RSCD agent. The exploit works against servers affected by CVE-2016-1542 (detected by Nessus).

**This is now a Metasploit module, see exploits/multi/misc/bmc_server_automation_rscd_nsh_rce**

The exploit was created by having Nessus scan a Python script that recorded packets and sent them/junk back to Nessus. With packets captured the data format was trivial to "reverse" to create a semi-working exploit. I later got access to the affected agent software and was able to use a debugger and some fuzzing to iron out the kinks and turn this into a solid RCE exploit.

Check out my blog posts on how I built the exploit for more details:

* ["RCE with BMC Server Automation"](https://nickbloor.co.uk/2018/01/01/rce-with-bmc-server-automation/ "RCE with BMC Server Automation")
* ["Improving the BMC RSCD RCE Exploit"](https://nickbloor.co.uk/2018/01/08/improving-the-bmc-rscd-rce-exploit/ "Improving the BMC RSCD RCE Exploit")

## HP\_Device\_Manager_RCE ##
Unauthenticated remote code execution exploit for HP Device Manager versions 5.0.0 to 5.0.3 (CVE-2020-6926, CVE-2020-6927).

The exploit takes advantage of an unauthenticated Java RMI service which has a Hibernate Query Language injection vulnerability. [ORM injection](https://conference.hitb.org/hitbsecconf2016ams/materials/D2T2%20-%20Mikhail%20Egorov%20and%20Sergey%20Soldatov%20-%20New%20Methods%20for%20Exploiting%20ORM%20Injections%20in%20Java%20Applications.pdf) is used to smuggle a [Postgres SQL injection payload](https://pulsesecurity.co.nz/articles/postgres-sqli) to overwrite the `pg_hba.conf` file on the HP Device Manager server, enabling remote access to the Postgres database that's bundled with HPDM. Once enabled, a backdoor superuser account is used to authenticate to the Postgres database and execute arbitrary operating system commands.

Check out my blog post on how I discovered these vulnerabilities for more details:

* [HP Device Manager CVE-2020-6925, CVE-2020-6926, CVE-2020-6927](https://nickbloor.co.uk/2020/10/05/hp-device-manager-cve-2020-6925-cve-2020-6926-cve-2020-6927/)

While this exploit only works against HPDM 5.x, the unauthenticated Java RMI service is present in all versions of HPDM prior to 5.0.4 and 4.7 service pack 13. The impact of exploiting this service *may* be lower, but there is still an HQLi/SQLi vulnerability, along with the ability to extract configuration (potentially including passwords for other services), and all HPDM account usernames and corresponding MD5 password hashes.

## JNBridge_RCE ##
Unauthenticated remote code execution exploit for insecurely configured JNBridge Java service endpoints. Based on the work of Moritz Bechler ([CVE-2019-7839](https://packetstormsecurity.com/files/153439/Coldfusion-JNBridge-Remote-Code-Execution.html)).

The network protocol implemented by JNBridge is designed solely to facilitate remote code execution for interoperability between Java and .NET applications. Thus, this isn't technically an exploit, just a handy little Python script to execute arbitrary commands against a JNBridge Java endpoint.

Check out my blog post for a walkthrough of my journey from security advisory to producing a full exploit:

* [Reversing JNBridge to Build an n-day Exploit for CVE-2019-7839](https://nickbloor.co.uk/2019/10/12/reversing-jnbridge-to-build-an-n-day-exploit-for-cve-2019-7839/)

## WordPress\_MitM\_ShellDrop ##
This exploit targets insecure automatic update functionality in WordPress to drop a PHP shell on the underlying server. The exploit has been tested successfully up to WordPress 4.9.8, which is the latest version at the date of publishing.

When WordPress checks for updates it attempts a secure HTTPS connection to api.wordpress.org. If this connection fails, for example because an untrusted certificate is presented, then WordPress falls back to using an insecure HTTP connection.

The second issue, is that WordPress trusts translation updates. It won't automatically update plugins, themes, or major core versions, presumably due to the risks of installing new code on the server. It does, however, automatically update translations. Unfortunately WordPress fails to properly validate translation archives so as long as the translation ZIP file contains at least one file with the extension .po, and one file with the extension .mo, WordPress will extract the contents to the underlying server (including the shell inserted in there by the MitM).

I stumbled across these issues by accident but when I reported them (November 2017) the WordPress team basically said WONTFIX because of backwards compatibility. If someone is running WordPress on a server that can't establish an outbound SSL/TLS connection then they should still be able to automatically update WordPress for **security** reasons, they say.

¯\\\_(ツ)\_/¯

Check out my blog post for more details:

* ["POPping WordPress"](https://nickbloor.co.uk/2018/02/28/popping-wordpress/ "POPping WordPress")

## WordPress\_JS\_Snippets ##
Some JS snippets to use for exploiting WordPress XSS vulns.
