# <This file is used to quickstart the server from my machine>
#Reconfigure python3.6 to your binary name I think
echo "Ignore warning if first time running"
pkill glitchchat.py
rm nohup.out
echo "Hit ctrl-c once nohup gets rolling"
nohup python3.6 main.py &
echo "Now running main.py"