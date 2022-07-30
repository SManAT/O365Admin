
import logging
import threading
import os
import sys
from cryptography.fernet import Fernet
from libs.CmdRunner import CmdRunner
from pathlib import Path


class AzurePS():
    """
    Manage Azure AD
    see https://pypi.org/project/O365/#directory-and-users
    see https://docs.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0&tabs=http#optional-query-parameters
    """
    accounts = []
    errors = False

    def __init__(self, config, scriptPath, console, keyFile, csvFilename):
        self.logger = logging.getLogger('Azure')
        self.rootDir = Path(__file__).parent
        self.config = config
        self.console = console
        self.keyFile = keyFile
        self.csvPath = os.path.join(self.rootDir, "../", csvFilename)

        #delete old CSV File
        if (os.path.exists(self.csvPath) is True):
            os.remove(self.csvPath)

        self.username = self.config['o365']['username']
        self.pasword = self.config['o365']['password']

        self.scriptPath = scriptPath

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True

        self.runner = CmdRunner()

        # Cryptographie
        file = open(self.keyFile, 'rb')
        key = file.read()
        file.close()

        # encrypt
        self.fernet = Fernet(key)

    def getThread(self):
      return self.thread

    def start(self):
      self.thread.start()

    def setType(self, type_):
        """ which type of Thread to execute, see AzureType """
        self.type = type_

    def run(self):
      self.getAccounts()

    def getAccounts(self):
      """ Get all active O365 Accounts """
      self._execute("getO365Users.ps1")

    def loadScript(self, filename):
        """ load a PS Script """
        path = os.path.join(self.scriptPath, filename)
        if (os.path.exists(path) is False):
            self.console.error("Script %s does not exist -abort-" % path)
            sys.exit()
        else:
            with open(path, 'r') as f:
                lines = f.readlines()
            return lines

    def decrypt(self, encMessage):
        """ decrypt a String """
        try:
          return self.fernet.decrypt(str.encode(encMessage)).decode()
        except Exception:
          print("\n")
          self.console.error("Wrong Encryption Key! Create a new one/or hash your password again in config/config.yml ...")
          self.errors = True
          exit()

    def hasErrors(self):
      return self.errors

    def modifyScript(self, lines):
        """
        modify placeholders with decrypted passwords.
        not really save, but a bit ;)
        """
        # get Admin Passwords
        hashstr = self.config["o365"]["password"]
        password = self.decrypt(hashstr)

        erg = []
        for line in lines:
            line = line.replace("{% username %}", self.config["o365"]["username"])
            line = line.replace("{% password %}", password)
            line = line.replace("{% path %}", self.csvPath)
            erg.append(line)
        return erg

    def createCmd(self, arr):
        """ from array to line;line;line """
        erg = ""
        for line in arr:
            # replace line breaks
            line = line.replace('\n', '')

            # no comments
            line = line.strip()
            # delete empty lines
            char = line[:1]
            if char != "#":
                if len(line) != 0:
                    if line[-1:] == "{" or line[-1:] == "|":  # nach { |  darf kein ; sein
                        erg += "%s" % line
                    else:
                        erg += "%s;" % line

        # escape sign, will run inside String
        erg = erg.replace('"', '\\"')
        return erg

    def debugOutput(self, cmd):
      for c in cmd:
        self.console.info(c)

    def debugSave(self, cmd):
      f = open("psDebugging.ps1", "w")
      f.writelines(cmd)
      f.close()

    def _execute(self, psTemplate):
        """ load Code from PS File, replace variables and excute it """
        cmdarray = self.loadScript(psTemplate)
        cmdarray = self.modifyScript(cmdarray)
        cmd = self.createCmd(cmdarray)

        #self.debugOutput(cmdarray)
        #self.debugSave(cmd)

        self.runner.runCmd(cmd)
        if self.runner.getStdout() != "":
          self.console.error("\n" + self.runner.getStderr())
        return self.runner.getStdout()


# Test
#a = Azure()
#a.getAccounts()
