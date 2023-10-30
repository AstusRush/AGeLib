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

class HelperTreeItem(QtWidgets.QTreeWidgetItem):
    pass

class HelpTreeWidget(QtWidgets.QTreeWidget):
    """
    This widget is used by the HelpWindow to display an overview of all help pages.
    """
    def __init__(self, parent, helpWindow):
        super(HelpTreeWidget, self).__init__(parent)
        self.HelpWindow = helpWindow
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.itemDoubleClicked.connect(lambda item: self.HelpWindow.selectCategory(item))
        self.itemActivated.connect(lambda item: self.HelpWindow.selectCategory(item)) # triggers with the enter key
    
    def addHelpCategory(self, categoryName, content, subCategories=None, overwrite=False):
        # type: (str,typing.Union[str,QtWidgets.QWidget],typing.Dict[str,typing.Union[str,QtWidgets.QWidget]],bool) -> None
        if self.getCategoryItem(categoryName)[1]:
            if overwrite:
                pass #TODO: Remove the category so that it can be readded
            elif subCategories:
                self.addSubCategories(categoryName, subCategories, overwrite)
                return
            else:
                return
        item = self._prepareItem(categoryName, content)
        self.addTopLevelItem(item)
        if subCategories:
            self.addSubCategories(categoryName, subCategories, overwrite)
    
    def addSubCategories(self, categoryName, subCategories, overwrite=False):
        # type: (str,typing.Dict[str,typing.Union[str,QtWidgets.QWidget]],bool) -> None
        parent_item = self.getCategoryItem(categoryName)
        if not parent_item[1]:
            NC(1,f"Could not find \"{categoryName}\" and can therefore not add subcategories.",win=self.windowTitle(),func="HelpTreeWidget.addSubCategories")
            return
        for k,v in subCategories.items():
            if self.getCategoryItem(k,parent_item[0])[1]:
                if overwrite:
                    pass #TODO: Remove the category so that it can be readded
                else:
                    continue
            item = self._prepareItem(k,v)
            parent_item[0].addChild(item)
    
    def _prepareItem(self, categoryName, content):
        # type: (str,str,typing.Union[str,QtWidgets.QWidget]) -> HelperTreeItem
        item = HelperTreeItem()
        item.setText(0,categoryName)
        if isInstanceOrSubclass(content, QtWidgets.QWidget):
            pass #TODO: Instantiate the widget if necessary and add it to the help list
        elif isinstance(content, str):
            item.setData(0,100, "string")
            item.setData(0,101, content)
        else:
            errMsg = f"Could not register help category \"{categoryName}\" with content of type \"{type(content)}\""
            NC(2,errMsg,win=self.windowTitle(),func="HelpTreeWidget.addHelpCategory")
            item.setData(0,100, "string")
            item.setData(0,101, errMsg)
        return item
    
    def getCategoryItem(self, name, obj=None):
        # type: (str,typing.Union[None,HelperTreeItem]) -> typing.Tuple[HelperTreeItem,bool]
        if not obj: obj = self #TODO: Does not work yet
        l = self.findItems(name, QtCore.Qt.MatchFlag.MatchFixedString|QtCore.Qt.MatchFlag.MatchCaseSensitive|QtCore.Qt.MatchFlag.MatchExactly)
        if l:
            if len(l) > 1:
                NC(2,f"Found multiple categories for the term \"{name}\". Returning only the first.",win=self.windowTitle(),func="HelpTreeWidget.getCategoryItem")
            return l[0], True
        else:
            item = HelperTreeItem()
            item.setText(0,"Category Not Found")
            item.setData(0,100, "string")
            item.setData(0,101, f"Could not find help category \"{name}\"")
            return item, False

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
            self.HelpCategoryListWidget = HelpTreeWidget(self.Splitter, self)
            self.HelpTextDisplay = QtWidgets.QPlainTextEdit(self.Splitter)
            #self.setUIExperiment()
            self.setCentralWidget(self.Splitter)
            help_text = "This is the help window.\nYou can open this window by pressing F1.\nDouble-click an item on the right to display the help page for it."
            self.addHelpCategory(self.windowTitle(),help_text,{"Test":"Test Text"})
            self.addHelpCategory(self.windowTitle(),help_text,{"Test":"Test Text"})
            self.installEventFilter(self)
        except:
            NC(exc=sys.exc_info(),win=self.windowTitle(),func="HelpWindow.__init__")
    
    def setUIExperiment(self):
        self.Test = QtWidgets.QTreeWidget(self.Splitter)
        self.TestItem1 = QtWidgets.QTreeWidgetItem(["Top Level 1",])
        self.TestItem1_1 = QtWidgets.QTreeWidgetItem(["Mid Level 1.1","Mid Level 1.1 2"])
        self.TestItem1_2 = QtWidgets.QTreeWidgetItem(["Mid Level 1.2",])
        self.TestItem2 = QtWidgets.QTreeWidgetItem(["Top Level 2",])
        self.TestItem2_1 = QtWidgets.QTreeWidgetItem(["Mid Level 2.1",])
        self.Test.addTopLevelItem(self.TestItem1)
        self.Test.addTopLevelItem(self.TestItem2)
        self.TestItem1.addChildren([self.TestItem1_1,self.TestItem1_2])
        self.TestItem2.addChild(self.TestItem2_1)
    
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
        self.selectCategory(self.HelpCategoryListWidget.getCategoryItem(category)[0])
    
    def selectCategory(self, item):
        # type: (HelperTreeItem) -> None
        if item.data(0,100).lower() == "string":
            self.HelpTextDisplay.setPlainText(item.data(0,101))
        else:
            self.HelpTextDisplay.setPlainText(f"ERROR\nData of type \"{item.data(100)}\" is not supported yet.")
    
    def addHelpCategory(self, categoryName, content, subCategories=None, overwrite=False):
        # type: (str,typing.Union[str,QtWidgets.QWidget],typing.Dict[str,typing.Union[str,QtWidgets.QWidget]],bool) -> None
        self.HelpCategoryListWidget.addHelpCategory(categoryName, content, subCategories, overwrite)

#endregion Help Window

