import base64
import curses
import curses.textpad
import numbers
import os
import time
from datetime import datetime

import requests


#curses routines
def start_curses():
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(True)


def stop_curses():
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
  clear()
  main_display()
  refresh()


def lc_write(messages):
  write(localusername, clean_time(time2string(get_time())), messages)
  clear()
  main_display()
  refresh()


def write(author, timestamp, messages):
  if not isinstance(messages, list):
    messages = [messages]
  for message in messages:
    #buffer.append(str(message)[:curses.COLS - 1:])
    firstlinewidth = curses.COLS - len("[%s]<%s> " % (timestamp, author))
    if len(message) > firstlinewidth:
      buffer.append("[%s]<%s> %s" %
                    (timestamp, author, str(message)[0:firstlinewidth:]))
      buffer.append(str(message)[firstlinewidth::])
      #while
      print("no")
    else:
      buffer.append(
          "[%s]<%s> %s" %
          (timestamp, author, str(message)))  #Force sanitize all output


def refresh():
  #while len(buffer) > curses.LINES - 6:
  #  buffer.pop(0)
  if len(buffer) - curses.LINES + reservedlines > 0:
    tempbuffer = buffer[len(buffer) - curses.LINES + reservedlines - yoff::]
  else:
    tempbuffer = buffer
  for i in range(curses.LINES - reservedlines):
    if len(tempbuffer) > i:
      stdscr.addstr(i + headerlen, 0, tempbuffer[i].ljust(curses.COLS))
    else:
      stdscr.addstr(i + headerlen, 0, "".ljust(curses.COLS))
  stdscr.addstr(curses.LINES - ioff, 5, "")  #cursor correction
  center_text("", curses.LINES - boff, "▓")
  stdscr.addstr(curses.LINES - ioff, 0, "[$]: ")


def trycommand(commandtext):
  if commandtext in list(functionmap):
    return True
  else:
    return False  #Not sure how to disable replit catch


def docommand(commandtext, *args):
  return functionmap[commandtext](*args)


def help(*args):
  helplist = [
      "/h, /help ~ Display this text",
      "/c, /connect <username> ~ Connect to server",
      "/j, /join <room> ~ Join a room", "/u, /users ~ Display online users",
      "/r, /rooms ~ Display room info"
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
  #cl_write(result["result"])

  if result["result"] != 0:
    global localroom
    localroom = room
    return "Connected to %s" % room
  elif str(result["result"]) == 0:
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


def rooms(*args):
  r = requests.get("http://glitchtech.top:8/rooms")
  res = r.json()
  roomcount = len(res)
  r = requests.get("http://glitchtech.top:8/users")
  userlist = r.json()
  roomlist = [
      "There are %s rooms open" % roomcount,
      "Room        Last Updated        Users"
  ]
  for room in list(res):
    presentusers = 0
    for user in list(userlist):
      numbercheck = isinstance(userlist[user]["activity"], numbers.Number)
      if not numbercheck and userlist[user]["activity"] == room:
        presentusers += 1
    #time = clean_time(res[room]["lifetime"])
    #Properly store lifetimes serverside first
    time = clean_time(time2string(get_time()))
    roomlist.append("%s%s%s" % (room.ljust(16), time.ljust(20), presentusers))
  return roomlist


def keepalive(userid):
  r = requests.get("http://glitchtech.top:8/keepalive",
                   params={"username": en(userid)})
  result = r.json()
  #{'timestamp': '09:10:23:00:12:02:049792', 'author': 'a', 'message': 'ok'}
  for i in result:
    write(i["author"], clean_time(ltime(i["timestamp"])), i["message"])
  clear()
  main_display()
  refresh()
  return result


#Keep at bottom
functionmap = {
    "c": connect,
    "j": join,
    "h": help,
    "u": users,
    "r": rooms,
    "connect": connect,
    "help": help,
    "join": join,
    "users": users,
    "rooms": rooms
}

#Code entry

#curses setup
stdscr = curses.initscr()
win = curses.newwin(1, curses.COLS - 10, curses.LINES - 2, 4)
count = 2
stdscr.nodelay(True)

start_curses()
buffer = []
timestd = "%m:%d:%y:%H:%M:%S:%f"
localusername = "local"
localroom = "local"
activitychart = {0: "Logged in"}

yoff = 0

ioff = 1
boff = 2
headerlen = 3
reservedlines = headerlen + boff


def update_reservedlines():
  global reservedlines
  reservedlines = headerlen + boff


def clear():
  stdscr.clear()


def clearall():
  stdscr.clear()


def main_display():
  center_text("▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁", 0, "▓", curses.A_REVERSE)
  center_text("[ GlitchChat v0.3 ]", 1, "▓", curses.A_STANDOUT)
  center_text("▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔", 2, "▓", curses.A_REVERSE)


stdscr.refresh()
command = ""
start = time.time()
flag = 0
main_display()
cl_write("Welcome to GlitchChat, type /help to begin")
wipe = True
while True:
  # ----- Key Input handlers -----
  c = stdscr.getch()
  if c == curses.KEY_RESIZE:
    curses.update_lines_cols()
    clear()
    main_display()
    refresh()
  #ping(counter, count)
  if c == 27:  # Codes to escape(esc)
    break  # Exit the while loop
  elif c == curses.KEY_BACKSPACE or c == 127:  #Backspace is encoded as 127/DEL on some devices
    command = command[0:len(command) - 1]
    stdscr.addstr(curses.LINES - ioff, 5, command + " ")
    stdscr.addstr(curses.LINES - ioff, 5,
                  command)  #Wastefully corrects cursor position
  elif c == curses.KEY_UP:
    if yoff < len(buffer) - curses.LINES + reservedlines:
      yoff = yoff + 1
      refresh()
  elif c == curses.KEY_DOWN:
    if yoff > 0:
      yoff = yoff - 1
      refresh()
  elif (c == curses.KEY_ENTER or c == 13 or c
        == 10) and len(command) > 0:  # Accept carriage return and line feed
    stdscr.addstr(curses.LINES - ioff, 5, " " * len(command))
    stdscr.addstr(curses.LINES - ioff, 5, "")  #cursor correction
    ioff = 1
    boff = 2
    update_reservedlines()
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
    if len(command) + 5 >= curses.COLS * ioff:
      ioff += 1
      boff += 1
      update_reservedlines()
      clear()
      main_display()
      refresh()
    stdscr.addstr(curses.LINES - ioff, 5, command)
  # ----- Repeated routine handlers -----
  if time.time() - start > 1 and localusername != "local":
    keepalive(localusername)
    start = time.time()
  # ----- Single routine handlers -----

  stdscr.refresh()
stop_curses()
print("~GlitchChat Client Terminated~")
