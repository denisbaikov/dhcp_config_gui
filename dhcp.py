import re
import sys
import os
import configparser

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QApplication, QDesktopWidget, QMessageBox, QSizePolicy, \
                             QLabel, QGridLayout, QVBoxLayout, QFrame, QTextEdit, QPushButton, QLineEdit)


class DHCP(QWidget):
    

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.data = ''
        self.dictLineEdit = {}
        self.conf = configparser.ConfigParser(comment_prefixes=("#"))

        self.vbox = QVBoxLayout()
        self.gridMain = QGridLayout() 
        self.gridConfigs = QGridLayout()
        self.pathConfigFile = QLineEdit("dhcp.conf")
        self.dhcpServiceName = QLineEdit("dhcpd")
        label = QLabel( "Config file" )
        self.gridMain.addWidget(label, *(0, 0))
        self.gridMain.addWidget(self.pathConfigFile, *(0, 1), 1, 2)

        label = QLabel( "DHCP-server service name" )
        self.gridMain.addWidget(label, *(1, 0))
        self.gridMain.addWidget(self.dhcpServiceName, *(1, 1), 1, 2)
        
        readButton = QPushButton("Read config")
        saveButton = QPushButton("Save config and Restart DHCP-server")
        readButton.clicked.connect(self.read_config)
        saveButton.clicked.connect(self.save_config)
        self.gridMain.addWidget(readButton, *(2, 1))
        self.gridMain.addWidget(saveButton, *(2, 2))
       
        self.vbox.addLayout(self.gridMain)

        self.setLayout(self.vbox)
        
        self.setMinimumWidth(400)
        self.move(0, 0)
        self.setWindowTitle('DHCP Configurator')
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap("icon/main.png")))

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        self.setSizePolicy(sizePolicy)
        self.show()


    def MakeLine(self):
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

        
    def UIconfig(self):

        row =0
        for section in self.conf.sections():
            if section == "simple":
                for item in self.conf.items(section):
                    label = QLabel( str(item[0]) )
                    self.gridConfigs.addWidget(label, *(row, 0))

                    textEdit = QLineEdit( item[1] )
                    self.dictLineEdit[ section + " " + str(item[0]) ] = textEdit
                    self.gridConfigs.addWidget(textEdit, *(row, 1), 1, 2)
                    row += 1
                    self.gridConfigs.addWidget(self.MakeLine(), *(row, 0), 1, 3)
                    row += 1
                    
            elif section == "option domain-name-servers":
                self.gridConfigs.addWidget(QLabel("option domain-name-servers"), *(row, 0))
                row += 1
                for item in self.conf.items(section):
                    label = QLabel( str(item[0]) )
                    self.gridConfigs.addWidget(label, *(row, 0))
                    
                    textEdit = QLineEdit( item[1] )
                    self.dictLineEdit[ section + " " + str(item[0])] = textEdit
                    self.gridConfigs.addWidget(textEdit, *(row, 1), 1, 2)
                    row += 1
                self.gridConfigs.addWidget(self.MakeLine(), *(row, 0), 1, 3)
                row += 1
                    
            elif "subnet " in section:
                self.gridConfigs.addWidget(QLabel(section), *(row, 0))
                row += 1
                flag_first = True
                for item in self.conf.items(section):
                    label = QLabel( str(item[0]) )
                    self.gridConfigs.addWidget(label, *(row, 0))
                    if flag_first == True:
                        textEdit = QLineEdit( item[1] )
                        self.dictLineEdit[ section + " " + str(item[0]) ] = textEdit
                        self.gridConfigs.addWidget(textEdit, *(row, 1), 1, 2)
                        flag_first = None
                    else:                        
                        #print("item[1].split(' ') =>", item[1].split(' '))
                        ranges = item[1].split(' ')[0]
                        ranges = re.sub(',', '', ranges)
                        textEdit = QLineEdit( ranges )
                        self.dictLineEdit[ section + " " + str(item[0]) + "1"] = textEdit
                        self.gridConfigs.addWidget(textEdit, *(row, 1), 1, 1)

                        ranges = item[1].split(' ')[1]
                        ranges = re.sub(',', '', ranges)
                        textEdit = QLineEdit( ranges )
                        self.dictLineEdit[ section + " " + str(item[0]) + "2"] = textEdit
                        self.gridConfigs.addWidget(textEdit, *(row, 2), 1, 1)
                    row += 1
                self.gridConfigs.addWidget(self.MakeLine(), *(row, 0), 1, 3)
                row += 1      
                    
            elif "host " in section:
                self.gridConfigs.addWidget(QLabel(section), *(row, 0))
                row += 1
                for item in self.conf.items(section):
                    label = QLabel( str(item[0]) )
                    self.gridConfigs.addWidget(label, *(row, 0))

                    textEdit = QLineEdit( item[1] )
                    self.dictLineEdit[ section + " " + str(item[0]) ] = textEdit
                    self.gridConfigs.addWidget(textEdit, *(row, 1), 1, 2)
                    row += 1
                self.gridConfigs.addWidget(self.MakeLine(), *(row, 0), 1, 3)
                row += 1  

        self.vbox.addLayout(self.gridConfigs)
        self.resize(1, 1)
        
# delete old Labels and LineEdits if it exist
    def ClearWindow(self):
       if self.gridConfigs.rowCount() > 1:
            while self.gridConfigs.itemAt(0) != None:
                tmp_widget = self.gridConfigs.itemAt(0).widget()
                self.gridConfigs.removeItem(self.gridConfigs.itemAt(0))
                tmp_widget.setParent(None)

                
    def find_simple_config(self):
        self.conf.add_section('simple')
        for str in self.data.split('\n'):
            
            if len( str ) < 2:
                continue

            if str[0]=="#":
                continue

            index_current_str = self.data.find(str)
            if self.data[ 0:index_current_str ].rfind('{') != -1:
                continue
                #print(self.data.find(str))
            
            tmp = str.split(' ')

            if tmp[0] == "subnet":
                continue;
            
            if len( tmp ) > 2:
                if tmp[0] == "option":
                    configs_key = tmp[0]                
                    configs_key += ' ' + tmp[1] 
                    if tmp[1] == "domain-name-servers":
                        self.conf.add_section('option domain-name-servers')
                        for i in range(2, len(tmp)):
                            tmp[i] = re.sub('[,;"]', '', tmp[i])
                            self.conf.set('option domain-name-servers', "{0}{1}".format("server", i-1), tmp[i])
                    else:
                        tmp[2] = re.sub('[,;]', '', tmp[2])
                        self.conf.set('simple', configs_key, tmp[2] )
            else:
                tmp[1] = re.sub('[,;]', '', tmp[1])
                self.conf.set( 'simple', tmp[0], tmp[1] )


    def find_config(self, config_type):
        
        search_str = ''
        if config_type == 'subnet':
            search_str = "^subnet.*?(\d+).netmask.*?(\d+)."
        elif config_type == 'hosts':
            search_str = "^host."
            
        match = re.search(search_str, self.data, flags=re.MULTILINE)
        while match:
            tmp_data = self.data[ match.start() : ]
            tmp_data = tmp_data[ 0:tmp_data.find('}') ]

            clear_start = match.start()
            clear_end = self.data.find('}')+1

            tmp_data = re.sub( r'\s+|\n|\r|\t+|\s+', ' ', tmp_data )
            tmp_data = re.sub( r'\s+{+|;+', '', tmp_data )

            tmp = tmp_data.split(' ')

            configs_key = tmp[0]               
            configs_key += ' ' + tmp[1]
            self.conf.add_section(configs_key)
            if config_type == 'subnet':
                self.conf.set(configs_key, 'netmask', tmp[3])
                count = 1
                for i in range( 5, len(tmp), 3 ):
                    tmp[i] = re.sub('[,;"]', '', tmp[i])
                    tmp[i+1] = re.sub('[,;"]', '', tmp[i+1])
                    self.conf.set(configs_key, "range{0}".format(count), "{0}, {1}".format(tmp[i], tmp[i+1]))
                    count += 1
            elif config_type == 'hosts':
                self.conf.set(configs_key, 'hardware ethernet', tmp[4])
                self.conf.set(configs_key, 'fixed-address', tmp[6])
            self.data = self.data[ 0:clear_start-1 ] + self.data[ clear_end: ]
            match = re.search(search_str, self.data, flags=re.MULTILINE)

    def read_config(self):
        try:
            file_dhcp_config = open( self.pathConfigFile.text() , "r")
        except IOError:
            print("Error! DHCP config file does not exist")
            QMessageBox.critical(self, "Error", "DHCP config file does not exis", QMessageBox.Ok)
            self.ClearWindow()
        else:
            print("DHCP config file read")
            with file_dhcp_config:
                self.data = ''
                self.dictLineEdit = {}
                self.ClearWindow()
                self.conf.clear()
        
                self.data = file_dhcp_config.read()
                text_len = len(self.data)
                self.find_simple_config()
                self.find_config('subnet')
                self.find_config('hosts')
                self.UIconfig()
                QMessageBox.information(self, "DHCP configurator", "DHCP config file successfully read!", QMessageBox.Ok)


    def save_config(self):
        if len(self.conf.sections()) == 0:
             print("Error! Configuration missing!")
             QMessageBox.critical(self, "Error", "Configuration missing!", QMessageBox.Ok)
             return
        try:
             file_dhcp_config = open( self.pathConfigFile.text() , "w")
        except IOError:
             print("Error! DHCP config file does not exist")
             QMessageBox.critical(self, "Error", "DHCP config file does not exist", QMessageBox.Ok)
        else:
             print("DHCP config file open for write")        
             with file_dhcp_config: 
                  for section in self.conf.sections():
                       if section == "simple":
                            for item in self.conf.items(section):
                                 value = section + " " + item[0]
                                 file_dhcp_config.write("{0} {1};\n".format(item[0], self.dictLineEdit[value].text()))
                                 
                       elif section == "option domain-name-servers":
                            file_dhcp_config.write("\noption domain-name-servers ")
                            flag_first = True
                            for item in self.conf.items(section):
                                 value = section + " " + item[0]
                                 if flag_first == None:
                       	              file_dhcp_config.write(", {0}".format(self.dictLineEdit[value].text()))
                                 else:
                       	              file_dhcp_config.write("{0}".format(self.dictLineEdit[value].text()))
                       	              flag_first = None
                            file_dhcp_config.write(";\n")
                            
                       elif re.sub('[0-9. ]', '', str(section)) == "subnet":
                            flag_first = True
                            for item in self.conf.items(section):
                                 if flag_first == True:
                                      value = section + " " + item[0]
                                      file_dhcp_config.write( "\n{0} netmask {1} {2}\n".format(section, self.dictLineEdit[value].text(), "{") )
                                      flag_first = None
                                 else:
                                      value = section + " " + item[0] + str(1)
                                      file_dhcp_config.write(" range {0} ".format(self.dictLineEdit[value].text()) )
                                      value = section + " " + item[0] + str(2)
                                      file_dhcp_config.write( self.dictLineEdit[value].text() + "\n" )
                            file_dhcp_config.write("};\n")
                       elif "host " in section:
                            file_dhcp_config.write( "\n{0} {1}\n".format(section, "{") )
                            for item in self.conf.items(section):
                                parametr = section + " " + item[0]
                                value = self.dictLineEdit[parametr].text()
                                file_dhcp_config.write( "   {0} {1}\n".format(item[0], value) )
                            file_dhcp_config.write( "}\n" )

                  print("DHCP config file successfully write")
                  if os.system("service {0} restart".format(self.dhcpServiceName.text())) == 0:
                       QMessageBox.information(self, "DHCP configurator", "DHCP config file success write\nDHCP-server restart!", QMessageBox.Ok)
                  else:
                       QMessageBox.critical(self, "Error", "DHCP config file success write,\n but DHCP-server is not restarted!", QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DHCP()
    sys.exit(app.exec_())

