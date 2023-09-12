from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import base64
from urllib.parse import urlparse
from datetime import datetime
from timer import RepeatedTimer
import numbers

timestd = "%m:%d:%y:%H:%M:%S:%f"

hostName = "glitchtech.top"
serverPort = 8


def in_index(mylist, target):
  for i in mylist:
    if i == target:
      return True
  return False


def base64_decode(string):
  a = 4
  b = len(string) % a
  c = 4 - b
  d = b"=" * c
  e = string + d
  return base64.urlsafe_b64decode(e)


def de(input_str):
  return base64.urlsafe_b64decode(input_str.replace('~', '=')).decode("utf-8")


def jwrite(file, out_json, operation="w+"):
  outfile = open(file, operation)
  json.dump(out_json, outfile, indent=2)
  outfile.close()


def jload(file):
  jfile = open(file)
  jdict = json.load(jfile)
  jfile.close()
  return jdict


def get_query(query):
  keys = []
  values = []
  for qc in query.split("&"):
    pair = qc.split("=")
    keys.append(pair[0])
    values.append(pair[1])
  return dict(zip(keys, values))


def time2string(time):
  return datetime.strftime(time, timestd)


def get_time():
  return datetime.now()


def clean_time(time):
  return time[0:17:1]


def string2time(string):
  return datetime.strptime(string, timestd)


def chat(author, message):
  obj = {
    "timestamp": time2string(get_time()),
    "author": author,
    "message": message
  }
  return obj


def cleaner():
  users = jload("users.json")
  rooms = jload("rooms.json")
  print(users)
  for user in list(users):
    alive = users[user]["keepalive"]
    dif = get_time() - string2time(alive)
    timeout = dif.total_seconds()
    if timeout >= 5:
      users.pop(user)
      jwrite("users.json", users)
  print(rooms)
  for room in list(rooms):
    if rooms[room]["lifetime"]:
      dif = get_time() - string2time(rooms[room]["lifetime"])
      timeout = dif.total_seconds()
      if timeout >= 5:
        rooms.pop(room)


def login(username, password):
  logins = jload("creds.json")
  ret = {"res": 0, "name": "noname"}
  if username in logins['users']:
    ret["res"] = 1
    if password == logins['users'][username]['Password']:
      ret["name"] = logins['users'][username]['Name']
      ret["res"] = 2
      if logins['users'][username]['Admin']:
        ret["res"] = 3
  return ret


class ChessServer(BaseHTTPRequestHandler):

  def do_GET(self):
    p = self.path.split("?")[0]
    # Refer to p[0] for get path
    query = urlparse(self.path).query
    query_components = {}
    if len(query) > 0:
      query_components = get_query(query)
    self.send_response(200)
    self.send_header("Content-type", "text/json")
    self.end_headers()

    if p == "/connect":
      # Result 0: Username already in use
      # Result 1: Connected

      #username = de(query_components["username"])
      username = de(query_components["username"])
      userjson = jload("users.json")
      res = {"result": 0}
      # Number activities are hardcoded as follows
      # 0 = Logged in
      # Interpret strings as chat room signatures
      if not username in userjson.keys():
        userjson[username] = {
          "keepalive": time2string(get_time()),
          "activity": 0
        }
        jwrite("users.json", userjson)
        res["result"] = 1

      self.wfile.write(bytes(json.dumps(res), "utf-8"))

    if p == "/makeroom":
      room = query_components["room"]
      roomsjson = jload("rooms.json")
      res = {"result": 0}
      if not room in roomsjson.keys():
        roomsjson[room] = {
          "lifetime": False,
          "filter": False,
          "length": 50,
          "owner": False,
          "editable": True,
          "motd": "This is a room",
          "refresh": True
          "refreshlen": 10
        }
        jwrite("rooms.json", roomsjson)
        list = []
        list.append(chat("SYSTEM", "%s room created" % room))
        jwrite("rooms/%s.json" % room, list)
        res["result"] = jload("rooms/%s.json" % room)
      self.wfile.write(bytes(json.dumps(res), "utf-8"))

    if p == "/users":
      self.wfile.write(bytes(json.dumps(jload("users.json")), "utf-8"))

    if p == "/time":
      self.wfile.write(
        bytes(json.dumps({"result": time2string(get_time())}), "utf-8"))

    if p == "/rooms":
      self.wfile.write(bytes(json.dumps(jload("rooms.json")), "utf-8"))

    if p == "/message":
      # Result 0 indicates "User/Room not found"
      # Result 1 indicates success
      username = de(query_components["username"])
      message = de(query_components["message"])
      userjson = jload("users.json")
      if username in userjson and not isinstance(
          userjson[username]["activity"], numbers.Number):
        activeroom = jload("rooms/%s.json" % userjson[username]["activity"])
        chatitem = chat(username, message)
        activeroom.append(chatitem)
        jwrite("rooms/%s.json" % userjson[username]["activity"], activeroom)
        self.wfile.write(bytes(json.dumps({"result": 1}), "utf-8"))
      else:
        self.wfile.write(bytes(json.dumps({"result": 0}), "utf-8"))

    if p == "/join":
      # Result 0 indicates "User/Room not found"
      # Result 1 indicates success
      # Else message log
      username = de(query_components["username"])
      room = de(query_components["room"])
      userjson = jload("users.json")
      roomsjson = jload("rooms.json")
      if username in userjson and room in roomsjson:
        userjson[username]["activity"] = room
        jwrite("users.json", userjson)
        #self.wfile.write(bytes(json.dumps(userjson), "utf-8")) Cannot remember if this was for debugging
        if roomsjson[room]["refresh"]:
          activeroom = jload("rooms/%s.json" % room)
          self.wfile.write(bytes(json.dumps(activeroom), "utf-8"))
        else:
          self.wfile.write(bytes(json.dumps({"result": 1}), "utf-8"))
      else:
        self.wfile.write(bytes(json.dumps({"result": 0}), "utf-8"))

    if p == "/keepalive":
      username = de(query_components["username"])
      userjson = jload("users.json")
      newmsgs = []
      if username in userjson:
        lastvisit = string2time(userjson[username]["keepalive"])
        userjson[username]["keepalive"] = time2string(get_time())
        if not isinstance(userjson[username]["activity"], numbers.Number):
          activeroom = jload("rooms/%s.json" % userjson[username]["activity"])
          for i in activeroom:
            dif = string2time(i["timestamp"]) - lastvisit
            if dif.total_seconds() > 0:
              newmsgs.append(i)
        jwrite("users.json", userjson)
        self.wfile.write(bytes(json.dumps(newmsgs), "utf-8"))
      else:
        self.wfile.write(
          bytes(json.dumps({"result": "Not logged in"}), "utf-8"))

  def do_POST(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    # POST requests requiring decode should be put here
    decode = []
    if in_index(decode, self.path):
      query = post_data.decode("utf-8")
      query_components = {}
      if len(query) > 0:
        query_components = get_query(query)
    self.send_response(200)
    self.send_header("Content-type", "text/json")
    self.end_headers()
    if self.path == "/addpost":
      self.wfile.write(bytes(json.dumps({"success": 1}), "utf-8"))


if __name__ == "__main__":
  webServer = HTTPServer((hostName, serverPort), ChessServer)
  rt = RepeatedTimer(1, cleaner)  # it no auto-starts, yes need of rt.start()
  rt.start()
  try:
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
      webServer.serve_forever()
    except KeyboardInterrupt:
      pass
  finally:
    rt.stop()

  webServer.server_close()
  print("Server stopped.")
