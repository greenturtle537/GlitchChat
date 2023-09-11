import requests
import os
import time
import curses
import curses.textpad
from datetime import datetime
import numbers
import base64


#curses routines
def start_curses(instance):
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(True)


def stop_curses(instance):
  curses.nocbreak()
  stdscr.keypad(False)
  curses.echo()
  curses.endwin()


# misc routines
def cls():
  os.system('cls' if os.name == 'nt' else 'clear')


def base64_encode(s):
  return base64.urlsafe_b64encode(s).strip(b"=")


def en(input):
  return base64.urlsafe_b64encode(bytes(input, "utf-8")).replace(b'=', b'~')


def center_text(text, y, pad="", attr=curses.A_NORMAL):
  length = len(text)
  stdscr.addstr(y, 0, pad * curses.COLS, attr)
  num = round((curses.COLS / 2) - (length / 2))
  stdscr.addstr(y, num, text, attr)


def datetime_from_utc_to_local(utc_datetime):  # Borrowed function
  now_timestamp = time.time()
  offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
    now_timestamp)
  return utc_datetime + offset


def time2string(time):
  return datetime.strftime(time, timestd)


def ltime(time):
  dif = get_time() - string2time(time)
  newtime = string2time(time) + dif
  return time2string(newtime)


def get_time():
  return datetime.now()


def clean_time(time):
  return time[9:17:]


def string2time(string):
  return datetime.strptime(string, timestd)


def cl_write(messages):
  write("CLIENT", clean_time(time2string(get_time())), messages)


def lc_write(messages):
  write(localusername, clean_time(time2string(get_time())), messages)


def write(author, timestamp, messages):
  if not isinstance(messages, list):
    messages = [messages]
  for message in messages:
    #buffer.append(str(message)[:curses.COLS - 1:])
    buffer.append(
      "[%s]<%s> %s" %
      (timestamp, author, str(message)))  #Force sanitize all output
  refresh(yoff)


def refresh(y=0):
  #while len(buffer) > curses.LINES - 6:
  #  buffer.pop(0)
  if len(buffer) - curses.LINES + 6 > 0:
    tempbuffer = buffer[len(buffer) - curses.LINES + 6 - yoff::]
  else:
    tempbuffer = buffer
  for i in range(curses.LINES - 6):
    if len(tempbuffer) > i:
      stdscr.addstr(i + 3, 0, tempbuffer[i].ljust(curses.COLS))
    else:
      stdscr.addstr(i + 3, 0, "".ljust(curses.COLS))
  stdscr.addstr(curses.LINES - 2, 5, "")  #cursor correction
  stdscr.refresh()


def trycommand(commandtext):
  if commandtext in list(functionmap):
    #functionmap[commandtext]()
    return True
  else:
    return False


def docommand(commandtext, *args):
  return functionmap[commandtext](*args)


def help(*args):
  helplist = [
    "/help ~ Display this text", "/connect <username> ~ Connect to the server",
    "/join <room> ~ Join a room", "/users ~ Display online users"
  ]
  return helplist


# requests routines
def connect(*args):
  username = args[0][0]
  if username == "local":
    return "This username is reserved"
  r = requests.get("http://glitchtech.top:8/connect",
                   params={"username": en(username)})
  result = r.json()
  if result["result"] == 1:
    global localusername
    localusername = username
    return "Connected as %s" % localusername
  else:
    return [
      "This username is already in use",
      "Please wait a few seconds before trying again"
    ]


def join(*args):
  if localusername == "local":
    return "Connect to the server first"
  room = args[0][0]
  r = requests.get("http://glitchtech.top:8/join",
                   params={
                     "username": en(localusername),
                     "room": en(room)
                   })
  result = r.json()
  if result["result"] == 1:
    global localroom
    localroom = room
    return "Connected to %s" % room
  elif result["result"] == 0:
    return "User/Room not found"


def message(msg):
  #cl_write(en(msg))
  r = requests.get("http://glitchtech.top:8/message",
                   params={
                     "username": en(localusername),
                     "message": en(msg)
                   })
  result = r.json()
  if result["result"] == 1:
    return msg
  else:
    return "User/Room not found"


def users(*args):
  r = requests.get("http://glitchtech.top:8/users")
  res = r.json()
  usercount = len(res)
  userlist = [
    "There are %s users online" % usercount,
    "Username        Last Updated        Activity"
  ]
  for user in list(res):
    if isinstance(res[user]["activity"], numbers.Number):
      activity = activitychart[res[user]["activity"]]
    else:
      activity = res[user]["activity"]
    time = clean_time(res[user]["keepalive"])
    userlist.append("%s%s%s" % (user.ljust(16), time.ljust(20), activity))
  return userlist


def keepalive(userid):
  r = requests.get("http://glitchtech.top:8/keepalive",
                   params={"username": en(userid)})
  result = r.json()
  #{'timestamp': '09:10:23:00:12:02:049792', 'author': 'a', 'message': 'ok'}
  for i in result:
    write(i["author"], clean_time(ltime(i["timestamp"])), i["message"])
  return result


#Keep at bottom
functionmap = {"connect": connect, "help": help, "join": join, "users": users}

#Code entry

#curses setup
stdscr = curses.initscr()
win = curses.newwin(1, curses.COLS - 10, curses.LINES - 2, 4)
count = 2
stdscr.nodelay(True)

start_curses(stdscr)
buffer = []
timestd = "%m:%d:%y:%H:%M:%S:%f"
localusername = "local"
localroom = "local"
activitychart = {0: "Logged in"}

yoff = 0

center_text("▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁", 0, "▓", curses.A_REVERSE)
center_text("| GlitchChat v0.2 |", 1, "▓", curses.A_STANDOUT)
center_text("▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔", 2, "▓", curses.A_REVERSE)

center_text("", curses.LINES - 3, "▓")
stdscr.addstr(curses.LINES - 2, 0, "[$]: ")

stdscr.refresh()
command = ""
start = time.time()
flag = 0
cl_write("Welcome to GlitchChat, type /help to begin")
while True:
  # ----- Key Input handlers -----
  c = stdscr.getch()
  #ping(counter, count)
  if c == 27:  # Codes to escape(esc)
    break  # Exit the while loop
  elif c == curses.KEY_BACKSPACE or c == 127:  #Backspace is encoded as 127/DEL on some devices
    command = command[0:len(command) - 1]
    stdscr.addstr(curses.LINES - 2, 5, command + " ")
    stdscr.addstr(curses.LINES - 2, 5,
                  command)  #Wastefully corrects cursor position
  elif c == curses.KEY_UP:
    if yoff < len(buffer) - curses.LINES + 6:
      yoff = yoff + 1
      refresh()
  elif c == curses.KEY_DOWN:
    if yoff > 0:
      yoff = yoff - 1
      refresh()
  elif (c == curses.KEY_ENTER or c == 13 or c
        == 10) and len(command) > 0:  # Accept carriage return and line feed
    stdscr.addstr(curses.LINES - 2, 5, " " * len(command))
    stdscr.addstr(curses.LINES - 2, 5, "")  #cursor correction

    if command[0] == "/":
      commandls = command.split("/")
      commandls = commandls[1].split(" ")
      if trycommand(commandls[0]):
        commandout = docommand(commandls[0], commandls[1::])
        cl_write(commandout)
    elif localroom != "local":
      message(command)
    else:
      lc_write(command)

    command = ""
  elif c > 31 and c <= 126:
    command = command + chr(c)
    stdscr.addstr(curses.LINES - 2, 5, command)
  # ----- Repeated routine handlers -----
  if time.time() - start > 1 and localusername != "local":
    keepalive(localusername)
    start = time.time()
  # ----- Single routine handlers -----

  stdscr.refresh()
stop_curses(stdscr)
print("~GlitchChat Client Terminated~")
