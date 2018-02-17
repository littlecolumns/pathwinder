import os
import datetime
import pty
import threading
from shutil import copyfile
from pathlib import Path
from subprocess import Popen, PIPE
from select import select

class BashFile:

  def __init__(self):
    self.filepath = os.path.expanduser("~/.bash_profile")
    self.assure_exists()
    pass

  def assure_exists(self):
    Path(self.filepath).touch()

  def backup(self):
    backup_dir = os.path.expanduser('~/.path_editor_backups')
    try:
      os.makedirs(backup_dir)
    except FileExistsError:
      pass
    
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.bak") 
    filepath = os.path.join(backup_dir, filename)
    profile_path = os.path.expanduser('~/.bash_profile')

    copyfile(profile_path, filepath)

  # Removals are ShellPaths
  # Append removals to the end of ~/.bash_profile
  def remove_paths(self, removals, backup=True):
    if backup:
      self.backup()

    with open(self.filepath, "a") as profile:
      for removal in removals:
        profile.write(removal.removal_string())

  def add_path_string(self, path, backup=True):
    if backup:
      self.backup()

    line_note = "# Easy Bash PATH Editor added: %s\n" % path
    line_path = "export PATH=\"%s:$PATH\"\n" % path

    with open(self.filepath, "a") as profile:
      profile.write("\n")
      profile.write(line_note)
      profile.write(line_path)

class ShellPath():

  def __init__(self, directory, index):
    self.directory = directory
    self.index = index

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, self.directory)

  def removal_string(self):
    return '\n%s\nexport PATH=$(%s)\n' % (self.removal_note(), self.sed_command())

  def sed_regex(self):
    # Remove all of the regex-y things
    cleaned_dir = self.directory.replace("/","\\/").replace(".","\\.")

    # (:|^) - colon or beginning of line
    # (:|$) - colon or end of line
    return '(:|^)%s(:|$)' % cleaned_dir

  def sed_command(self):
    # Replaces text with a :
    # Replaces ALL instances
    return 'sed -E "s/%s/:/g" <<< $PATH' % self.sed_regex()

  def removal_note(self):
    return '# Easy Bash PATH Editor removed: %s' % self.directory


class PathRetriever:

  def __init__(self):
    self.paths = []
    self.shell_paths = []

  def update(self):
    try:
      master, slave = pty.openpty()
      p = Popen(['/bin/bash', '-l'], stdin=slave, stdout=PIPE, stderr=PIPE, universal_newlines=True)
      pin = os.fdopen(master, 'w')

      pin.write("echo $PATH\n")

      path_str = None
      while not path_str:
          rs = select([p.stdout], [], [])[0]
          for r in rs:
              if r is p.stdout:
                  path_str = p.stdout.readline().strip()

      paths = path_str.strip().split(":")
      self.paths = [path for path in paths if path != ""]
    except:
      self.paths = []
    self.shell_paths = [ShellPath(path, i) for i, path in enumerate(paths)]
