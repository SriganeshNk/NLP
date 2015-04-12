from jpype import *


def run():
    print 'Thread started'
    try:
        print repr(java.awt.Frame)
        javax.swing.JFrame("Test Frame").setVisible(True)
        shutdownGuiEnvironment()
    except JException, ex:
        print ex


startJVM(getDefaultJVMPath())

setupGuiEnvironment(run)
