import psutil, time, datetime
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from operator import itemgetter
import os

ltpid=[]
ltname=[]
ltcpu=[]
ltmem=[]
ltctime=[]
ltstatus=[]

npid=[]

overall_prop=['System Time','Idle Time','Total Memory','Available Memory','Used Memory','Free Memory','Memory %']
overall_val=[]

def process_data():
    print "process_data"
    
    p = psutil.cpu_times()
    overall_val.append(str(p.system))
    overall_val.append(str(p.idle))

    p = psutil.virtual_memory()
    overall_val.append(str(p.total))
    overall_val.append(str(p.available))
    overall_val.append(str(p.used))
    overall_val.append(str(p.free))
    overall_val.append(str(p.percent))

    for proc in psutil.process_iter():
        ltpid.append(str(proc.pid))
        ltname.append(proc.name())
        
        p = psutil.Process(proc.pid)
        ltmem.append(str(round(float(p.memory_percent()),2)))
        ltctime.append(str(datetime.datetime.fromtimestamp(p.create_time()).strftime("%H:%M:%S")))
        ltstatus.append(str(p.status()))
        ltcpu.append(str(proc.cpu_percent()))

def process_data2():
    print "process_data"    
    global npid
    npid=[]
    for proc in psutil.process_iter():
        npid.append(str(proc.pid))
    
data = {'pid':ltpid, 'name':ltname, 'Cpu (last 1ms)':ltcpu, 'Memory':ltmem, 'Create Time':ltctime, 'Status':ltstatus}

data2 = {'Property':overall_prop, 'Value':overall_val}
        
def cellClick(row,col):
    print "Click on " + str(row) + " " + str(col)
    pid = ltpid[row]
    menu = QMenu()
    suspend = menu.addAction('Suspend')
    resume = menu.addAction('Resume')
    terminate = menu.addAction('Terminate')
    kill = menu.addAction('Kill')
    action = menu.exec_(QCursor.pos())
    if action == suspend:
        psutil.Process(int(pid)).suspend()
    elif action == resume:
        psutil.Process(int(pid)).resume()
    elif action == terminate:
        psutil.Process(int(pid)).terminate()
    elif action == kill:
        psutil.Process(int(pid)).kill()
 
class MyTable(QTableWidget):
    def __init__(self, data, *args):
        print "init"
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setmydata2()
        self.resizeColumnsToContents()
        
        header = self.horizontalHeader()
        header.setStretchLastSection(True)

    def setmydata2(self):
        horHeaders = []
        n = 0
        for key in sorted(self.data, key=itemgetter(-2)):
            horHeaders.append(key)
            m = 0
            for item in self.data[key]:
                if key == 'pid' or key == 'Property':
                    rowPosition = self.rowCount()
                    self.insertRow(rowPosition)
                newitem = QTableWidgetItem(item)
                #to make cells unmodified
                newitem.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(m, n, newitem)
                m += 1
            n += 1
        self.setHorizontalHeaderLabels(horHeaders)
 
def main(args):
    app = QApplication(args)
    tabs = QTabWidget()

    tab1 = QWidget()
    tab2 = QWidget()

    Layout1 = QVBoxLayout()
    Layout2 = QVBoxLayout()

    tabs.resize(500, 600)
    
    process_data()
    table = MyTable(data, 0, 6)
    
    table.cellClicked.connect(cellClick)
    
    Layout1.addWidget(table)
    tab1.setLayout(Layout1)
    
    table2 = MyTable(data2, 0, 2)    
    Layout2.addWidget(table2)
    tab2.setLayout(Layout2)

    print "adding tabs.."
    tabs.addTab(tab1,"Processes")
    tabs.addTab(tab2,"Overall")

    tabs.setWindowTitle("Process Manager")
    
    def process_data1():
        process_data2()
            
        for x in npid:
            if x in ltpid:
                pos = ltpid.index(x)
                newitem3 = QTableWidgetItem(str(psutil.Process(int(x)).cpu_percent()))
                newitem4 = QTableWidgetItem(str(round(float(psutil.Process(int(x)).memory_percent()),2)))
                table.setItem(pos, 4, newitem3)
                table.setItem(pos, 3, newitem4)

            else:                 
                newitem1 = QTableWidgetItem(x)
                newitem5 = QTableWidgetItem(str(datetime.datetime.fromtimestamp(psutil.Process(int(x)).create_time()).strftime("%H:%M:%S")))
                newitem3 = QTableWidgetItem(str(psutil.Process(int(x)).cpu_percent()))
                newitem4 = QTableWidgetItem(str(round(float(psutil.Process(int(x)).memory_percent()),2)))
                newitem6 = QTableWidgetItem(str(psutil.Process(int(x)).status()))
                newitem2 = QTableWidgetItem(str(psutil.Process(int(x)).name()))
                r = table.rowCount()
                table.insertRow(r)
                table.setItem(r, 0, newitem1)
                table.setItem(r, 2, newitem2)
                table.setItem(r, 4, newitem3)
                table.setItem(r, 3, newitem4)
                table.setItem(r, 1, newitem5)
                table.setItem(r, 5, newitem6)
                ltpid.append(x)
                
        for x in ltpid:
            if x not in npid:
                pos = ltpid.index(x)
                table.removeRow(pos)
                ltpid.remove(x)
                
    
    timer = QTimer()
    timer.timeout.connect(process_data1)
    timer.start(2000)
        
    tabs.show()

    sys.exit(app.exec_())
 
if __name__=="__main__":
    main(sys.argv)
