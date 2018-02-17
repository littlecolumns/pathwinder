import os
import sys
import wx
import wx.adv
from wx.lib.wordwrap import wordwrap
from wx.lib.agw import ultimatelistctrl as ULC
from system_tools import BashFile, PathRetriever

class MainFrame(wx.Frame):
  """"""

  #----------------------------------------------------------------------
  def __init__(self):
    """Constructor"""
    wx.Frame.__init__(self, None, title="Easy Bash PATH Editor", size=(600, 400))
    panel = MainPanel(self)

    # Setting up the menu.
    self.menu_bar  = wx.MenuBar()
    self.help_menu = wx.Menu()
    
    self.help_menu.Append(wx.ID_ABOUT,   "&About")
    self.menu_bar.Append(self.help_menu, "&Help")
    
    self.SetMenuBar(self.menu_bar)
    self.Bind(wx.EVT_MENU, self.show_about, id=wx.ID_ABOUT)

    self.Show()

  def show_about(self, event):
    info = wx.adv.AboutDialogInfo()
    info.Name = "Easy Bash PATH Editor"
    info.Version = "0.1"
    info.WebSite = (
      "https://github.com/jsoma/easy-bash-path-editor",
      "Easy Bash PATH Editor"
    )
    info.Developers = ["Jonathan Soma"]
    info.Description = wordwrap(
        "Edit your PATH pretty easily in OS X.\n"
        "Icon by Vectors Market at flaticon.com",
        350, wx.ClientDC(self))
    wx.adv.AboutBox(info)


class MainPanel(wx.Panel):
  """"""

  #----------------------------------------------------------------------
  def __init__(self, parent):
    """Constructor"""
    wx.Panel.__init__(self, parent)

    font = self.GetFont()
    font.SetPointSize(14)
    self.SetFont(font)
    self.items = []
    self.path_retriever = PathRetriever()

    sizer = wx.BoxSizer(wx.VERTICAL)

    self.edit_profile = wx.Button(self, -1, 'Edit raw')
    self.edit_profile.Bind(wx.EVT_BUTTON, self.open_editor)

    self.add_path_button = wx.Button(self, -1, 'Add folder')
    self.add_path_button.Bind(wx.EVT_BUTTON, self.add_path_click)

    box = wx.BoxSizer(wx.HORIZONTAL)
    box.Add(self.edit_profile, flag=wx.RIGHT, border=5)
    box.Add(self.add_path_button, flag=wx.RIGHT, border=5)
    sizer.Add(box, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=15)

    self.create_list()
    box = wx.BoxSizer(wx.HORIZONTAL)
    box.Add(self.list, 1, flag=wx.EXPAND | wx.ALL, border=15)
    sizer.Add(box, 1, wx.EXPAND)

    self.save_button = wx.Button(self, -1, 'Save')
    self.save_button.Bind(wx.EVT_BUTTON, self.save_click)

    self.refresh_button = wx.Button(self, -1, 'Refresh')
    self.refresh_button.Bind(wx.EVT_BUTTON, self.update_path_list)

    box = wx.BoxSizer(wx.HORIZONTAL)

    box.Add(self.refresh_button, flag=wx.RIGHT, border=5)
    box.Add(self.save_button)

    sizer.Add(box, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, border=15)

    # checkbox = wx.CheckBox(self, wx.ID_ANY, "Create backup")
    # checkbox.SetValue(True)
    
    # box = wx.BoxSizer(wx.HORIZONTAL)
    # box.Add(checkbox, flag=wx.ALIGN_CENTER_VERTICAL)

    # sizer.Add((-1, 5))
    # sizer.Add(box, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=15)

    self.SetSizer(sizer)

  def update_path_list(self, event=None):
    self.list.DeleteAllItems()

    paths = self.current_path_list()
    self.items = [PathRow(path, self.list) for path in paths]
    self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
    self.list.SetColumnWidth(1, 475)

  def create_list(self):
    font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

    self.list = PathTable(self)

    self.list.InsertColumn(0, "Keep?")
    self.list.InsertColumn(1, "Directory")
    self.update_path_list()

  def current_path_list(self):
    self.path_retriever.update()
    return self.path_retriever.shell_paths

  def open_editor(self, event):
    os.system("open ~/.bash_profile")

  def enable_save(self):
    self.save_button.Enable()

  def disable_save(self):
    self.save_button.Disable()

  def save_click(self, event):
    self.save_changes()
    dialog = wx.MessageDialog(self, 
      "Changes saved!", 
      "Notice", 
      wx.OK)
    dialog.ShowModal()
    dialog.Destroy()

  def save_changes(self):
    self.disable_save()

    removals = [item for item in self.items if not item.checked()]

    profile = BashFile()
    # Performs backup automatically
    profile.remove_paths(removals)

    self.update_path_list()
    self.enable_save()
  
  def add_path_click(self, evt):
    TYPE_IT = "Type it"
    FILE_BROWSER = "File browser"

    dialog = wx.SingleChoiceDialog(
                self, "How will you enter it?", 'Select an option',
                [TYPE_IT, FILE_BROWSER], 
                wx.CHOICEDLG_STYLE
                )

    picker_text = wx.TextEntryDialog(self, "Please enter the folder name")
    picker_browse = wx.DirDialog(self, "Find your directory", style=wx.DD_DEFAULT_STYLE)

    if dialog.ShowModal() != wx.ID_OK:
      dialog.Destroy()
      return
    
    path = None
    if dialog.GetStringSelection() == TYPE_IT:
      if picker_text.ShowModal() == wx.ID_OK:
        path = picker_text.GetValue()
    elif dialog.GetStringSelection() == FILE_BROWSER:
      if picker_browse.ShowModal() == wx.ID_OK:
        path = picker_browse.GetPath()

    dialog.Destroy()
    picker_text.Destroy()
    picker_browse.Destroy()
    
    if path is not None:
      print("Going to add", path)
      profile = BashFile()
      profile.add_path_string(path)
      self.update_path_list()

class PathRow():

  def __init__(self, path, list_ctrl):
    self.path = path
    self.list_ctrl = list_ctrl

    self.checkbox = wx.CheckBox(list_ctrl, wx.ID_ANY, "" )
    self.checkbox.SetValue(True)

    self.list_ctrl.InsertStringItem(path.index, "")
    self.list_ctrl.SetItemWindow(path.index, 0, self.checkbox, expand=True)
    self.list_ctrl.SetStringItem(path.index, 1, path.directory)

  def checked(self):
    return self.checkbox.GetValue()

  def removal_string(self):
    return self.path.removal_string()

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, self.path)


class PathTable(ULC.UltimateListCtrl):

  def __init__(self, parent):
    ULC.UltimateListCtrl.__init__(self, parent, agwStyle=
      wx.LC_REPORT 
      | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
