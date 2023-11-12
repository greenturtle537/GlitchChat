# Glitch Chat
*Brought to you by Glitch Technologies.*
A http-driven communication protocol that uses a central server to relay new messages between connected users.

# Usage
**You can try out Glitch Chat with replit.com right now, in your browser. Just go to
https://replit.com/@greenturtle537/GlitchChat?v=1
and hit the play button**

To use GlitchChat on you machine, you will need python and the pip installer. You will also need to install the requests package.

```
pip import requests
python client/main.py
```
Once the client is running, you can type /help to get more information.



# Server
The majority of the code in this repository is designed to run the backend of GlitchChat. 
While we support push requests, it is important that any extensions to the software do not conflict with the provided client(So update the client in the same request). 
It also MUST be compatibile with Python 3.9. Third-party packages are allowed, but not recommended.
Please note that the .gitignore exists for the security of the local server files, and do not attempt to remove files.

# Client
Code under /client is not a part of the local server. 
It is a TUI interface for communicating and testing the capabilities of the server. 
Feel free to submit quality of life features as I will not be prioritizing its development going forward. 
Third party packages must be compatible with early versions of Python3, and are therefore also not recommended.
We do plan on releasing dedicated executables for Windows later on, so try to keep it compatible.

**Need more docs? Check the Wiki tab!!!**
