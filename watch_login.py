import os
import sys
import time
import http.client

from datetime import datetime as dt
from pytz import timezone

# Constants for the script
LOG_PATH = '/path/to/minecraft/logs'
LOG_NAME = 'latest.log'
# Discord Web Hook. If not being used, default to ''
DISCORD_WEBHOOK = ''
TIMEZONE = 'US/Eastern'
MINECRAFT_SERVER_NAME = 'Minecraft Server Name'
# For Log Cleanup. How many days before logs are removed. 0 = never
DAYS_FOR_LOGS = 7
# Prevent logging to terminal
TERM_LOGGING = True

class FileWatch(object):
    def __init__(self):
        self._cached_stamp = None
        self.path = LOG_PATH
        self.filename = self.path + '/' + LOG_NAME
        self.lines = None
        self.discord_webhook = DISCORD_WEBHOOK

    def read_file(self):
        file = open(self.filename)
        lines = file.readlines()
        file.close()

        return lines

    def check_login(self, lines):
        datetime_now = dt.now(timezone(TIMEZONE))
        time_string = datetime_now.strftime("%Y-%m-%d %H:%M")
        for x in range(self.lines, len(lines)):
            if 'logged in with entity' in lines[x]:
                # Found someone logged in. Parse the name
                strings = lines[x].split(' ')
                named_string = strings[3]
                names = named_string.split('[')
                name = names[0]
                if TERM_LOGGING:
                    print('%s  %s has logged in' % (time_string, name))
                if DISCORD_WEBHOOK != '':
                    self.send_to_discord(name)

    def check(self):
        stamp = os.stat(self.filename).st_mtime
        if self._cached_stamp is not None:
            if stamp != self._cached_stamp:
                self._cached_stamp = stamp

                #File Changed.
                lines = self.read_file()
                if len(lines) < self.lines:
                    # File was rotated. Check from
                    # Beginning of file
                    self.lines = 0

                self.check_login(lines)
                self.lines = len(lines)

        else:
            self._cached_stamp = stamp
            # First time reading this file.
            # Record the number of lines in the file
            # and set the last read to the total lines in file
            self.lines = len(self.read_file())

    def delete_old_files(self):
        time_now = time.time()
        datetime_now = dt.now(timezone(TIMEZONE))
        time_string = datetime_now.strftime("%Y-%m-%d %H:%M")
        for filename in os.listdir(self.path):
            f = os.path.join(self.path, filename)
            if os.stat(f).st_mtime < time_now - DAYS_FOR_LOGS * 86400:
                if os.path.isfile(f):
                    if TERM_LOGGING:
                        print('%s  Removing old file: %s' % (time_string, f))
                    os.remove(f)

    def send_to_discord(self, name):
        message = name + ' has logged onto the Minecraft Server ' + MINECRAFT_SERVER_NAME

        formdata = "------:::BOUNDARY:::\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + message + "\r\n------:::BOUNDARY:::--"

        # get the connection and make the request
        connection = http.client.HTTPSConnection("discordapp.com")
        connection.request("POST", self.discord_webhook, formdata, {
            'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
            'cache-control': "no-cache",
            })

        # get the response
        response = connection.getresponse()
        result = response.read()

        # return back to the calling function with the result
        return result.decode("utf-8")


def main():
    file_check = FileWatch()

    while True:
        try:
            time.sleep(1)
            file_check.check()

            now = dt.now(timezone(TIMEZONE))
            if DAYS_FOR_LOGS != 0 and now.hour == 0 and now.minute == 0:
                file_check.delete_old_files()
                time.sleep(60)

        except KeyboardInterrupt:
            if TERM_LOGGING:
                print('\nDone')
            break

        except:
            if TERM_LOGGING:
                print('Unhandled Error: ', sys.exc_info()[0])

if __name__ == "__main__":
    main()
