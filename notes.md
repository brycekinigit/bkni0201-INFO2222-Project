# Notes

## To Do:

[] Login
[] Friends list (will need a new db table for friend relations)
[] Adding friends
[] Friend request approval/denial
[] Server cannot read messages (This and next *might* be covered by TLS/SSL)
[] Server cannot modify messages (MAC)
[] Message history stored encrypted in database using user password to decrypt
[] Store passwords properly with hash and salt
[] Session Tokens

## Misc.

We need to find out how exactly messages are sent. Peer to peer is vulnerable to impersonation, and seems to be how the template is. Server-side would only allow connection if both sides authenticate

When a user logs in, the server sends a rendered version of the home page. The home page can then use some jevascript functions to send info to the server, which it passes on to the other client

## Current vulnerabilities

- Anyone can put any username into address bar and access any other user
- Xss
- All users enter one big room, and cannot see who else is in.
- Might be possible to change javascript to send whatever to whoever from whoever

## Sources

https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/
https://docs.cherrypy.dev/en/latest/basics.html#config
https://iomarmochtar.wordpress.com/2016/05/04/using-https-on-cherrypy/
https://gist.github.com/rafaelhdr/96547498b515f6c0b7f8383f49a8aa5c
