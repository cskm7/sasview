import wx
from wx import StatusBar as wxStatusB
from wx.lib import newevent
import wx.richtext
import time
from sans.guiframe.gui_style import GUIFRAME_ICON
#numner of fields of the status bar 
NB_FIELDS = 4
#position of the status bar's fields
ICON_POSITION = 0
MSG_POSITION  = 1
GAUGE_POSITION  = 2
CONSOLE_POSITION  = 3
BUTTON_SIZE = 40

CONSOLE_WIDTH = 500
CONSOLE_HEIGHT = 300

class ConsolePanel(wx.Panel):
    """
    """
    def __init__(self, parent, *args, **kwargs):
        """
        """
        wx.Panel.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.msg_txt = wx.richtext.RichTextCtrl(self, size=(CONSOLE_WIDTH-40,
                                                CONSOLE_HEIGHT-60),
                                   style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        
        self.msg_txt.SetEditable(False)
        self.msg_txt.SetValue('No message available')
        self.sizer.Add(self.msg_txt, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(self.sizer)
        
    def set_message(self, status="", event=None):
        """
        """
        status = str(status)
        if status.strip() == "":
            return
        color = (0, 0, 0) #black
        icon_bmp =  wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
                                                 wx.ART_TOOLBAR)
        if hasattr(event, "info"):
            icon_type = event.info.lower()
            if icon_type == "warning":
                color = (0, 0, 255) # blue
                icon_bmp =  wx.ArtProvider.GetBitmap(wx.ART_WARNING,
                                                      wx.ART_TOOLBAR)
            if icon_type == "error":
                color = (255, 0, 0) # red
                icon_bmp =  wx.ArtProvider.GetBitmap(wx.ART_ERROR, 
                                                     wx.ART_TOOLBAR)
            if icon_type == "info":
                icon_bmp =  wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
                                                     wx.ART_TOOLBAR)
        self.msg_txt.Newline()
        self.msg_txt.WriteBitmap(icon_bmp)
        self.msg_txt.BeginTextColour(color)
        self.msg_txt.WriteText("\t")
        self.msg_txt.AppendText(status)
        self.msg_txt.EndTextColour()
        
           
        
class Console(wx.Frame):
    """
    """
    def __init__(self, parent=None, status="", *args, **kwds):
        kwds["size"] = (CONSOLE_WIDTH, CONSOLE_HEIGHT)
        kwds["title"] = "Console"
        wx.Frame.__init__(self, parent=parent, *args, **kwds)
        self.panel = ConsolePanel(self)
        self.panel.set_message(status=status)
        wx.EVT_CLOSE(self, self.Close)
        
        
    def set_multiple_messages(self, messages=[]):
        """
        """
        if messages:
            for status in messages:
                self.panel.set_message(status=status)
                
    def set_message(self, status, event=None):
        """
        """
        self.panel.set_message(status=str(status), event=event)
        
    def Close(self, event):
        """
        """
        self.Hide()
        
class StatusBar(wxStatusB):
    """
    """
    def __init__(self, parent, *args, **kargs):
        wxStatusB.__init__(self, parent, *args, **kargs)
        """
        Implement statusbar functionalities 
        """
        self.parent = parent
        self.parent.SetStatusBarPane(MSG_POSITION)
        #Layout of status bar
        self.SetFieldsCount(NB_FIELDS) 
        self.SetStatusWidths([BUTTON_SIZE, -2, -1, BUTTON_SIZE])
        #display default message
        self.msg_position = MSG_POSITION 
        #save the position of the gauge
        width, height = self.GetSize()
        self.gauge = wx.Gauge(self, size=(width/10, height-3),
                               style=wx.GA_HORIZONTAL)
        self.gauge.Hide()
        #status bar icon
        self.bitmap_bt_warning = wx.BitmapButton(self, -1,
                                                 size=(BUTTON_SIZE,-1),
                                                  style=wx.NO_BORDER)
        console_bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_TOOLBAR,
                                                size = (16,16))
        self.bitmap_bt_console = wx.BitmapButton(self, -1, 
                                 size=(BUTTON_SIZE-5, height-4))
        self.bitmap_bt_console.SetBitmapLabel(console_bmp)
        console_hint = "History of status bar messages"
        self.bitmap_bt_console.SetToolTipString(console_hint)
        self.bitmap_bt_console.Bind(wx.EVT_BUTTON, self._onMonitor,
                                            id=self.bitmap_bt_console.GetId())
        
        self.reposition()
        ## Current progress value of the bar 
        self.nb_start = 0
        self.nb_progress = 0
        self.nb_stop = 0
        self.frame = None
        self.list_msg = []
        self.frame = Console(parent=self)
        if hasattr(self.frame, "IsIconized"):
            if not self.frame.IsIconized():
                try:
                    icon = self.parent.GetIcon()
                    self.frame.SetIcon(icon)
                except:
                    try:
                        FRAME_ICON = wx.Icon(GUIFRAME_ICON.FRAME_ICON_PATH,
                                              wx.BITMAP_TYPE_ICON)
                        self.frame.SetIcon(FRAME_ICON)
                    except:
                        pass
        self.frame.set_multiple_messages(self.list_msg)
        self.frame.Hide()
        self.progress = 0      
        self.timer = wx.Timer(self, -1) 
        self.timer_stop = wx.Timer(self, -1) 
        self.thread = None
        self.Bind(wx.EVT_TIMER, self._on_time, self.timer) 
        self.Bind(wx.EVT_TIMER, self._on_time_stop, self.timer_stop) 
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
    def reposition(self):
        """
        """
        rect = self.GetFieldRect(GAUGE_POSITION)
        self.gauge.SetPosition((rect.x + 5, rect.y - 2))
        rect = self.GetFieldRect(ICON_POSITION)
        self.bitmap_bt_warning.SetPosition((rect.x + 5, rect.y - 2))
        rect = self.GetFieldRect(CONSOLE_POSITION)
        self.bitmap_bt_console.SetPosition((rect.x - 5, rect.y - 2))
        self.sizeChanged = False
        
    def OnIdle(self, event):
        """
        """
        if self.sizeChanged:
            self.reposition()
            
    def OnSize(self, evt):
        """
        """
        self.reposition() 
        self.sizeChanged = True
        
    def get_msg_position(self):
        """
        """
        return self.msg_position
    
    def SetStatusText(self, text="", number=MSG_POSITION, event=None):
        """
        """
        wxStatusB.SetStatusText(self, text, number)
        self.list_msg.append(text)
        icon_bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_TOOLBAR)
        self.bitmap_bt_warning.SetBitmapLabel(icon_bmp)
      
        if self.frame is not None :
            self.frame.set_message(status=text, event=event)
        
    def PopStatusText(self, *args, **kwds):
        """
        Override status bar 
        """
        wxStatusB.PopStatusText(self, field=MSG_POSITION)
      
    def PushStatusText(self, *args, **kwds):
        """
        """
        wxStatusB.PushStatusText(self, field=MSG_POSITION, string=string)
        
    def enable_clear_gauge(self):
        """
        clear the progress bar
        """
        flag = False
        if (self.nb_start <= self.nb_stop) or \
            (self.nb_progress <= self.nb_stop):
            flag = True
        return flag
    
    def _on_time_stop(self, evt): 
        """
        Clear the progress bar
        
        :param evt: wx.EVT_TIMER 
  
        """ 
        count = 0
        while(count <= 100):
            count += 1
        self.timer_stop.Stop() 
        self.clear_gauge(msg="")
        self.nb_progress = 0 
        self.nb_start = 0 
        self.nb_stop = 0
       
    def _on_time(self, evt): 
        """
        Update the progress bar while the timer is running 
        
        :param evt: wx.EVT_TIMER 
  
        """ 
        # Check stop flag that can be set from non main thread 
        if self.timer.IsRunning(): 
            self.gauge.Pulse()
   
    def clear_gauge(self, msg=""):
        """
        Hide the gauge
        """
        self.progress = 0
        self.gauge.SetValue(0)
        self.gauge.Hide() 
         
    def set_icon(self, event):
        """
        Display icons related to the type of message sent to the statusbar
        when available. No icon is displayed if the message is empty
        """
        if hasattr(event, "status"):
            status = str(event.status)
            if status.strip() == "":
                return
        else:
            return
        if not hasattr(event, "info"):
            return 
        msg = event.info.lower()
        if msg == "warning":
            icon_bmp =  wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_TOOLBAR)
            self.bitmap_bt_warning.SetBitmapLabel(icon_bmp)
        if msg == "error":
            icon_bmp =  wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_TOOLBAR)
            self.bitmap_bt_warning.SetBitmapLabel(icon_bmp)
        if msg == "info":
            icon_bmp =  wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
                                                 wx.ART_TOOLBAR)
            self.bitmap_bt_warning.SetBitmapLabel(icon_bmp)
    
    def set_message(self, event):
        """
        display received message on the statusbar
        """
        if hasattr(event, "status"):
            self.SetStatusText(text=str(event.status), event=event)
       
 
    def set_gauge(self, event):
        """
        change the state of the gauge according the state of the current job
        """
        if not hasattr(event, "type"):
            return
        type = event.type
        self.gauge.Show(True)
        if type.lower() == "start":
            self.nb_start += 1
            #self.timer.Stop()
            self.progress += 10
            self.gauge.SetValue(int(self.progress)) 
            self.progress += 10
            if self.progress < self.gauge.GetRange() - 20:
                self.gauge.SetValue(int(self.progress)) 
        if type.lower() == "progress":
            self.nb_progress += 1
            self.timer.Start(1)
            self.gauge.Pulse()
        if type.lower() == "update":
            self.progress += 10
            if self.progress < self.gauge.GetRange()- 20:
                self.gauge.SetValue(int(self.progress))   
        if type.lower() == "stop":
            self.nb_stop += 1
            self.gauge.Show(True)
            if self.enable_clear_gauge():
                self.timer.Stop()
                self.progress = 0
                self.gauge.SetValue(90) 
                self.timer_stop.Start(3) 
                    
    def set_status(self, event):
        """
        Update the status bar .
        
        :param type: type of message send.
            type  must be in ["start","progress","update","stop"]
        :param msg: the message itself  as string
        :param thread: if updatting using a thread status 
        
        """
        self.set_message(event=event)
        self.set_icon(event=event)
        self.set_gauge(event=event)
    
    def _onMonitor(self, event):
        """
        Pop up a frame with messages sent to the status bar
        """
        self.frame.Show(False)
        self.frame.Show(True)
        
        
class SPageStatusbar(wxStatusB):
    def __init__(self, parent, timeout=None, *args, **kwds):
        wxStatusB.__init__(self, parent, *args, **kwds)
        self.SetFieldsCount(1) 
        self.timeout = timeout
        width, height = parent.GetSizeTuple()
        self.gauge = wx.Gauge(self, style=wx.GA_HORIZONTAL, 
                              size=(width, height/10))
        rect = self.GetFieldRect(0)
        self.gauge.SetPosition((rect.x , rect.y ))
        if self.timeout is not None:
            self.gauge.SetRange(int(self.timeout))
        self.timer = wx.Timer(self, -1) 
        self.Bind(wx.EVT_TIMER, self._on_time, self.timer) 
        self.timer.Start(1)
        self.pos = 0
       
    def _on_time(self, evt): 
        """
        Update the progress bar while the timer is running 
        
        :param evt: wx.EVT_TIMER 
  
        """ 
        # Check stop flag that can be set from non main thread 
        if self.timeout is None and self.timer.IsRunning(): 
            self.gauge.Pulse()
            
        
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = wx.Frame(None, wx.ID_ANY, 'test frame')
    #statusBar = StatusBar(frame, wx.ID_ANY)
    statusBar = SPageStatusbar(frame)
    frame.SetStatusBar(statusBar)
    frame.Show(True)
    #event = MessageEvent()
    #event.type = "progress"
    #event.status  = "statusbar...."
    #event.info = "error"
    #statusBar.set_status(event=event)
    app.MainLoop()

