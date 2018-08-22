import re
import sys
import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QApplication, QDesktopWidget, QMessageBox, QSizePolicy, \
                             QLabel, QGridLayout, QVBoxLayout, QFrame, QTextEdit, QPushButton, QLineEdit)


class DHCP(QWidget):
    

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.data = ''
        self.configs = {}
        self.dictLineEdit = {}

        self.vbox = QVBoxLayout()
        self.gridMain = QGridLayout() 
        self.gridConfigs = QGridLayout()
        self.pathConfigFile = QLineEdit("/etc/dhcp/dhcpd.conf")
    
        label = QLabel( "Config file" )
        self.gridMain.addWidget(label, *(0, 0))
        self.gridMain.addWidget(self.pathConfigFile, *(0, 1), 1, 2)
        
        readButton = QPushButton("Read config")
        saveButton = QPushButton("Save config and Restart DHCP-server")
        readButton.clicked.connect(self.read_config)
        saveButton.clicked.connect(self.save_config)
        self.gridMain.addWidget(readButton, *(1, 1))
        self.gridMain.addWidget(saveButton, *(1, 2))
       
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

    def UIconfig(self):
        
        self.ClearWindow()
        
        row = 0 #gridConfigsLayout rows count
        for items in self.configs.items():
            label = QLabel( str(items[0]) )
            if items[0] == "option domain-name-servers":
                self.gridConfigs.addWidget(label, *(row, 0))
                count = 1
                for line in items[1]:
                    textEdit = QLineEdit( line )
                    self.dictLineEdit[ items[0] + str(count) ] = textEdit
                    self.gridConfigs.addWidget(textEdit, *(row, 1), 1, 2)
                    row += 1
                    count += 1
                    
            # for subnet part in config file
            elif "subnet " in items[0]:
                self.gridConfigs.addWidget( QLabel(items[0]), *(row, 0) )
                row += 1
                self.gridConfigs.addWidget( QLabel("subnet"), *(row, 0) )
                
                textEdit = QLineEdit( items[0].split(' ')[1] )
                self.dictLineEdit[ items[0] ] = textEdit
                self.gridConfigs.addWidget( textEdit, *(row, 1), 1, 2 ) 
                row += 1

                label = QLabel( "netmask" );
                self.gridConfigs.addWidget( label, *(row, 0))
                
                textEdit = QLineEdit( items[1][0] )
                self.dictLineEdit[ "netmask "+items[0] ] = textEdit
                self.gridConfigs.addWidget( textEdit, *(row, 1), 1, 2 )
                row += 1

                for j in range( 1, len(items[1]), 2 ):
                    self.gridConfigs.addWidget( QLabel("range"), *(row, 0) )
                    textEdit = QLineEdit( items[1][j] )
                    key = "range "+items[0]+" "+str(j)
                    self.dictLineEdit[ key ] = textEdit
                    self.gridConfigs.addWidget( textEdit, *(row, 1) )

                    textEdit = QLineEdit( items[1][j+1] )
                    key = "range "+items[0]+" "+str(j+1)
                    self.dictLineEdit[ key ] = textEdit
                    self.gridConfigs.addWidget( textEdit, *(row, 2) )
                    row += 1
                    
            # for hosts part in config file        
            elif "host " in items[0]:
                self.gridConfigs.addWidget( QLabel(items[0]), *(row, 0) )
                row += 1
                self.gridConfigs.addWidget( QLabel("host"), *(row, 0) )

                textEdit = QLineEdit( items[0].split(' ')[1] )
                self.dictLineEdit[ items[0] ] = textEdit
                self.gridConfigs.addWidget( textEdit, *(row, 1), 1, 2 )
                row += 1

                label = QLabel( "hardware ethernet" );
                self.gridConfigs.addWidget( label, *(row, 0))

                textEdit = QLineEdit( items[1][0] )
                key = "hardware ethernet " + items[0]
                self.dictLineEdit[ key ] = textEdit
                self.gridConfigs.addWidget( textEdit, *(row, 1), 1, 2 )
                row += 1

                label = QLabel( "fixed-address" );
                self.gridConfigs.addWidget( label, *(row, 0))

                textEdit = QLineEdit( items[1][1] )
                key = "fixed-address " + items[0]
                self.dictLineEdit[ key ] = textEdit
                self.gridConfigs.addWidget( textEdit, *(row, 1), 1, 2 )
                row += 1

            # for simple configs in config file
            else:
                self.gridConfigs.addWidget(label, *(row, 0))

                textEdit = QLineEdit( str(items[1]) )
                self.dictLineEdit[ label.text() ] = textEdit
                self.gridConfigs.addWidget(textEdit, *(row, 1), 1, 2)
                
            row += 1
            line = QFrame();
            line.setFrameShape(QFrame.HLine);
            line.setFrameShadow(QFrame.Sunken);
            
            self.gridConfigs.addWidget(line, *(row, 0), 1, 3)
            row += 1
            
        self.vbox.addLayout(self.gridConfigs)

        self.resize(1, 1)
        #self.resize(1, 1)

    # delete old Labels and LineEdits if it exist
    def ClearWindow(self):
       if self.gridConfigs.rowCount() > 1:
            while self.gridConfigs.itemAt(0) != None:
                tmp_widget = self.gridConfigs.itemAt(0).widget()
                self.gridConfigs.removeItem(self.gridConfigs.itemAt(0))
                tmp_widget.setParent(None)
       
    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def find_simple_config(self):

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
                    configs_values = []
                    if tmp[1] == "domain-name-servers":                    
                        for i in range(2, len(tmp)):
                            tmp[i] = re.sub('[,;"]', '', tmp[i])
                            configs_values.append(tmp[i])                        
                        self.configs[configs_key] = configs_values
                    else:
                        tmp[2] = re.sub('[,;]', '', tmp[2])
                        self.configs[configs_key] = tmp[2] 
            else:
                tmp[1] = re.sub('[,;]', '', tmp[1])
                self.configs[tmp[0]] = tmp[1]
                #print("find_simple_config = ", tmp[1])


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
            configs_values = []
            if config_type == 'subnet':
                configs_values.append(tmp[3])
                for i in range( 5, len(tmp), 3 ):
                    tmp[i] = re.sub('[,;"]', '', tmp[i])
                    tmp[i+1] = re.sub('[,;"]', '', tmp[i+1])
                    configs_values.append(tmp[i])
                    configs_values.append(tmp[i+1])
            elif config_type == 'hosts':
                configs_values.append(tmp[4])
                configs_values.append(tmp[6])
            self.configs[configs_key] = configs_values
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
                self.data = file_dhcp_config.read()
                text_len = len(self.data)
                self.configs.clear()
                self.find_simple_config()
                self.find_config('subnet')
                self.find_config('hosts')
                self.UIconfig()
                QMessageBox.information(self, "DHCP configurator", "DHCP config file successfully read!", QMessageBox.Ok)

    def save_config(self):
        if self.dictLineEdit:
            try:
                file_dhcp_config = open( self.pathConfigFile.text() , "w")
            except IOError:
                print("Error! DHCP config file does not exist")
                QMessageBox.critical(self, "Error", "DHCP config file does not exist", QMessageBox.Ok)
            else:
                print("DHCP config file open for write")
                with file_dhcp_config:
                    already_write_configs = []
                    _dict = self.dictLineEdit
                    for key in _dict:
                        if key in already_write_configs:# == None:
                            continue
                        
                        if "option domain-name-servers" in key:
                            count = 1
                            file_dhcp_config.write("option domain-name-servers ")
                            tmp_key = '{0}{1}'.format("option domain-name-servers", count)
                            #print("data = {0}".format(tmp_key))
                            
                            while tmp_key in _dict.keys():
                                if count != 1:
                                    file_dhcp_config.write( ", " )
                                    
                                file_dhcp_config.write( _dict[tmp_key].text() )                                
                                already_write_configs.append(tmp_key)
                                count += 1
                                tmp_key = '{0}{1}'.format("option domain-name-servers", count)
                            file_dhcp_config.write(";\n")
                            
                        elif "subnet " in key:
                            count = 1
                            file_dhcp_config.write("\n" + key + " ")
                            
                            tmp_key = '{0} {1}'.format("netmask", key)
                            if tmp_key in _dict.keys():
                               file_dhcp_config.write( tmp_key.split(' ')[0]+" "+_dict[tmp_key].text() + " {\n" )
                               already_write_configs.append(tmp_key)
                               #print("print  = ", tmp_key.split(' ')[0]+" "+_dict[tmp_key].text())

                            tmp_key = '{0} {1} {2}'.format("range", key, count)
                            #print("data = {0}".format(tmp_key))
                            while tmp_key in _dict.keys():
                                tmp_str = "\t" + tmp_key.split(' ')[0] + " " + _dict[tmp_key].text()
                                file_dhcp_config.write( tmp_str )
                                already_write_configs.append(tmp_key)
                                count += 1
                                
                                tmp_key = '{0} {1} {2}'.format("range", key, count)
                                tmp_str = " " + _dict[tmp_key].text() + "\n"
                                file_dhcp_config.write( tmp_str )
                                already_write_configs.append(tmp_key)
                                count += 1
                                tmp_key = '{0} {1} {2}'.format("range", key, count)
                            file_dhcp_config.write( "}\n" )
                            
                        elif "host " in key:
                            count = 1
                            file_dhcp_config.write("\n" + key + " {\n")
                            
                            tmp_key = '{0} {1}'.format("hardware ethernet", key)
                            if tmp_key in _dict.keys():
                               file_dhcp_config.write( "\t" + tmp_key.split(' ')[0] + " " + tmp_key.split(' ')[1] +" "+_dict[tmp_key].text() + ";\n" )
                               already_write_configs.append(tmp_key)
                               #print("print  = ", tmp_key.split(' ')[0]+" "+_dict[tmp_key].text() + ";\n")

                            tmp_key = '{0} {1}'.format("fixed-address", key)
                            if tmp_key in _dict.keys():
                               file_dhcp_config.write( "\t" + tmp_key.split(' ')[0]+" "+_dict[tmp_key].text() + ";\n" )
                               already_write_configs.append(tmp_key)
                               #print("print  = ", tmp_key.split(' ')[0]+" "+_dict[tmp_key].text() + ";\n")
                            file_dhcp_config.write( "}\n" )
                        else:
                            file_dhcp_config.write(key + " " + self.dictLineEdit[key].text() + ";\n")
                print("DHCP config file successfully write")
                if os.system("service isc-dhcp-server restart") == 0:
                    QMessageBox.information(self, "DHCP configurator", "DHCP config file success write\nDHCP-server restart!", QMessageBox.Ok)
                else:
                    QMessageBox.critical(self, "Error", "DHCP config file success write,\n but DHCP-server is not restarted!", QMessageBox.Ok)
        else:
            print("Error! Configuration missing!")
            QMessageBox.critical(self, "Error", "Configuration missing!", QMessageBox.Ok)
                        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = DHCP()
    sys.exit(app.exec_())
