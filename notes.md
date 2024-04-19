# Notes

## To Do

[x] Login
[x] Friends list (will need a new db table for friend relations)
[] Adding friends
[~] Friend request approval/denial
[] Server cannot read messages (This and next are NOT covered by HTTPS)
[] Server cannot modify messages (MAC)
[] Message history stored encrypted in database using user password to decrypt
[] Store passwords properly with hash and salt
[x] Session Tokens
[] Make sure that no XSS is possible (ankit on ed said it's possible in scaffold)
[] Do report

## Misc

## Current vulnerabilities

- User can be logged in on multiple devices

## Sources

https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/
https://docs.cherrypy.dev/en/latest/basics.html#config
https://iomarmochtar.wordpress.com/2016/05/04/using-https-on-cherrypy/
https://gist.github.com/rafaelhdr/96547498b515f6c0b7f8383f49a8aa5c
