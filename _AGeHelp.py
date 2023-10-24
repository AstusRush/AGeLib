#region General Import
from ._import_temp import *
#endregion General Import

#region Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeAWWF import *
from ._AGeWindows import *
#endregion Import

#region Help Widgets

class HelperCategoryItem(QtWidgets.QListWidgetItem):
    pass

class HelpCategoryListWidget(ListWidget):
    """
    This widget is used by NotificationsWidget to display all notifications.
    """
    def __init__(self, parent, helpWindow):
        super(HelpCategoryListWidget, self).__init__(parent)
        self.HelpWindow = helpWindow
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.itemDoubleClicked.connect(lambda item: self.HelpWindow.selectCategory(item))
    
    def addHelpCategory(self, categoryName, content, overwrite=False):
        if False: #TODO: Check if the category is already registered
            if overwrite:
                pass #TODO: Overwrite the category
            else:
                return
        if isInstanceOrSubclass(content, QtWidgets.QWidget):
            pass #TODO: Instantiate the widget if necessary and add it to the help list
        elif isinstance(content, str):
            item = HelperCategoryItem()
            item.setText(categoryName)
            item.setData(100, "string")
            item.setData(101, content)
            self.addItem(item)
        else:
            NC(2,f"Could not register help category \"{categoryName}\" with content of type \"{type(content)}\"",win=self.windowTitle(),func="HelpCategoryListWidget.addHelpCategory")
    
    def getCategoryItem(self, name):
        l = self.findItems(name, QtCore.Qt.MatchFlag.MatchFixedString|QtCore.Qt.MatchFlag.MatchCaseSensitive|QtCore.Qt.MatchFlag.MatchExactly)
        if l:
            if len(l) > 1:
                NC(2,f"Found multiple categories for the term \"{name}\". Returning only the first.",win=self.windowTitle(),func="HelpCategoryListWidget.getCategoryItem")
            return l[0]
        else:
            item = HelperCategoryItem()
            item.setText("Category Not Found")
            item.setData(100, "string")
            item.setData(101, f"Could not find help category \"{name}\"")
            return item

#endregion Help Widgets
#region Help Window
class HelpWindow(AWWF):
    def __init__(self,parent = None):
        try:
            # Init
            super(HelpWindow, self).__init__(parent, initTopBar=False)
            self.TopBar.init(IncludeFontSpinBox=True,IncludeErrorButton=True,IncludeAdvancedCB=True)
            self.setWindowTitle("Help Window")
            self.StandardSize = (900, 500)
            self.resize(*self.StandardSize)
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogHelpButton))
            
            self.Splitter = QtWidgets.QSplitter(self)
            self.HelpCategoryListWidget = HelpCategoryListWidget(self.Splitter, self)
            self.HelpTextDisplay = QtWidgets.QPlainTextEdit(self.Splitter)
            self.setCentralWidget(self.Splitter)
            self.addHelpCategory(self.windowTitle(),"This is the help window.\nYou can open this window by pressing F1.\nDouble-click an item on the right to display the help page for it.")
            self.installEventFilter(self)
        except:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="HelpWindow.__init__")
    
    def eventFilter(self, source, event):
        # type: (QtWidgets.QWidget, QtCore.QEvent|QtGui.QKeyEvent) -> bool
        if event.type() == 6: # QtCore.QEvent.KeyPress
            if event.key() == QtCore.Qt.Key_F1:
                App().showWindow_Help(self.windowTitle())
                return True
        return super(HelpWindow, self).eventFilter(source, event) # let the normal eventFilter handle the event
    
    def showCategory(self, category = ""):
        if category=="": category = "No Category"
        self.show()
        App().processEvents()
        self.positionReset()
        App().processEvents()
        self.activateWindow()
        #NC(3,category)
        self.selectCategory(self.HelpCategoryListWidget.getCategoryItem(category))
    
    def selectCategory(self, item):
        if item.data(100).lower() == "string":
            self.HelpTextDisplay.setPlainText(item.data(101))
        else:
            self.HelpTextDisplay.setPlainText(f"ERROR\nData of type \"{item.data(100)}\" is not supported yet.")
    
    def addHelpCategory(self, categoryName, content, overwrite=False):
        self.HelpCategoryListWidget.addHelpCategory(categoryName, content, overwrite)

#endregion Help Window

