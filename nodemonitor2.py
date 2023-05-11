#!/usr/bin/env python
import wx
import wx.lib.buttons as buttons
from jenkinsapi.jenkins import Jenkins
import webbrowser

MiBYTE = 1024 * 1024
GiBYTE = 1024 * 1024 * 1024
PROFILE = ""
REGION = "--region eu-west-1"
headers = ['name', 'online', 'idle', 'executors']
patterns = [
    ('BUSY', lambda text: style(text, fg='white', bg='green')),
    ('IDLE', lambda text: style(text, fg='white', bg='red')),
    ('OFFLINE', lambda text: style(text, fg='white', bg='black')),
    ('ONLINE', lambda text: style(text, fg='white', bg='green')),
]
jenkins_url = 'https://jenkins.infra.optibrium.com'
cmd = "curl https://jenkins.infra.optibrium.com/computer/api/json"
# ref: https://stackoverflow.com/questions/69316536/how-to-check-if-an-executor-is-running-in-jenkins


class NodeMonitor(wx.Frame):
    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(NodeMonitor, self).__init__(*args, **kw)
        self.SetInitialSize(wx.Size(130, 280))

        # create a panel in the frame
        self.pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.names, self.full_names = self.get_node_names()
        self.flags = []
        # q length text
        self.qlen = wx.StaticText(self.pnl, pos=wx.Point(10,5), label='???', style=wx.ALIGN_CENTER)
        # create node items
        x = 10
        y = 30
        yinc = 30
        for i in range(0,len(self.names)):
            btn = buttons.GenButton(self.pnl, i, self.names[i], pos=(x,y+(i*yinc)))
            btn.SetSize(100,20)
            btn.BackgroundColour = wx.BLUE
            btn.ForegroundColour = wx.WHITE
            self.Bind(wx.EVT_BUTTON, self.OnNodeCLick, id=btn.Id)
            self.flags.append(btn)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.node_status, self.timer)
        self.timer.Start(milliseconds=15000)
        self.node_status((None))

    def findButton(self,name):
        flag = [x for x in self.flags if x.Label == name]
        return flag[0]

    def OnNodeCLick(self, event):
        if event.Id == 0:
            # can't get url for built in node, ignore
            pass
        else:
            btnurl = "{j}/computer/{n}/".format(n=self.full_names[event.Id], j=jenkins_url)
            webbrowser.open((btnurl))

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)


    def get_node_names(self):
        server = Jenkins(jenkins_url, username='ci-admin', password='fhp4MxzyE2r8aLMiR7i7AARl')
        names = []
        full_names = []
        for n in server.get_nodes().keys():
            nc = server.get_node(n)
            names.append(nc._data['displayName'].split(' ')[0])
            full_names.append(nc._data['displayName'])
        return names, full_names


    def node_status(self, event):
        self.pnl.SetBackgroundColour(wx.BLACK)
        self.pnl.Refresh(eraseBackground=True)
        server = Jenkins(jenkins_url, username='ci-admin', password='fhp4MxzyE2r8aLMiR7i7AARl')
        active_names = []
        queue = server.get_queue()
        self.qlen.LabelText = "Queue: {d}".format(d=len(queue))
        for n in server.get_nodes().keys():
            nc = server.get_node(n)
            # could add test ofr enable/disable and do more colors
            if nc._data['offline']:
                idl = wx.BLACK
                ox = wx.LIGHT_GREY
            else:
                if nc._data['idle']:
                    idl = (200,200,200)
                    ox =  (128,128,128)
                else:
                    idl = wx.GREEN
                    ox = wx.WHITE
            exe = nc._data['executors']
            # exe1 = nc.get_num_executors()
            btn = self.findButton(nc._data['displayName'].split(' ')[0])
            btn.SetBackgroundColour(idl)
            btn.SetForegroundColour(ox)
            btn.Refresh(eraseBackground=True)
        self.pnl.SetBackgroundColour(wx.LIGHT_GREY)
        self.pnl.Refresh(eraseBackground=True)
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = NodeMonitor(None, title='Jenkins')
    frm.Show()
    app.MainLoop()
