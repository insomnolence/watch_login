# watch_login
Simple python script that watches logs for user login, sends info to a discord app, and prunes old log files


Needed a way to let folks know when others were on a local Minecraft Server. Simple python script that runs on the 
system and watches the logs. When someone logs in, it will print it to the terminal and send the info to a Discord
Webhook in order to announce it on Discord channel.

The script also prunes older logs. There are likely better ways for pruning, but just keeping X days from current date 
is good enough for our needs.

It can be easily modified for others' needs. Check out the top of the script for Constants info and modify them for
your needs.
