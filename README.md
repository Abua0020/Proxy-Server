# Proxy-Server
Basic Proxy Server for Web Page 
By: Abdulrahman Abu Alhussein 
====================================

Description:
------------
This project is a simple proxy server that fetches web pages for clients. 
The server listens on a specified port and forwards clients to the website, 
it also caches responses for faster responses.

Requirements:
-------------
- Python 3

Usage Instructions:
-------------------
1. download the project file.
2. Run `Server_Proxy.py` using Python:
3. Configure your browser to use the proxy server.
- Host: localhost
- Port: 8888
4. Open a browser and go to any website for example (http://localhost:8888/www.google.com). Then confirm that the proxy server is showing the requests in the terminal.

Screenshots:
------------
I have also added a folder wityh screenshots of the proxy server working with a number of sites.

Notes:
-------------
I used the split_http function to separate the domain from localhost and the port. Which helps route client requests through the proxy.
This function also parses URLs to extract the domain and path correctly, especially for loading images and other resources,
making the server more efficient in handling the requests and caching responses.






