import re

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QLabel, QGridLayout, QFrame, \
                             QVBoxLayout, QApplication, QDesktopWidget, QTextEdit, QPushButton, QLineEdit)

#data = ''
#configs = {}

class DHCP(QWidget):
    
    data = ''
    configs = {}
    dict_LineEdit = {}
    
    def __init__(self):
        super().__init__()

        self.read_config()
        self.initUI()


    def initUI(self):       

        #lableList = {}
        #textEdit = QTextEdit()

        grid = QGridLayout()
        #self.setLayout(grid)        

        ii = 0
        jj = 0
        for items in DHCP.configs.items():
            lable = QLabel()            
            lable.setText( str(items[0]) )
            if items[0] == "option domain-name-servers":
                grid.addWidget(lable, *(ii, 0))
                count = 1
                for line in items[1]:
                    print(line)
                    textEdit = QLineEdit( line )
                    self.dict_LineEdit[ items[0] + str(count) ] = textEdit
                    grid.addWidget(textEdit, *(ii, 1), 1, 2)
                    ii += 1
                    count += 1
                    
            # for subnet part in config file
            elif "subnet " in items[0]:
                grid.addWidget( QLabel(items[0]), *(ii, 0) )
                ii += 1
                grid.addWidget( QLabel("subnet"), *(ii, 0) )
                
                textEdit = QLineEdit( items[0].split(' ')[1] )
                self.dict_LineEdit[ items[0] ] = textEdit
                grid.addWidget( textEdit, *(ii, 1), 1, 2 )                
                
                ii += 1

                lable = QLabel( "netmask" );
                grid.addWidget( lable, *(ii, 0))
                
                textEdit = QLineEdit( items[1][0] )
                self.dict_LineEdit[ "netmask "+items[0] ] = textEdit
                grid.addWidget( textEdit, *(ii, 1), 1, 2 )
                ii += 1

                for j in range( 1, len(items[1]), 2 ):
                    grid.addWidget( QLabel("range"), *(ii, 0) )
                    textEdit = QLineEdit( items[1][j] )
                    key = "range "+items[0]+" "+str(j)
                    self.dict_LineEdit[ key ] = textEdit
                    grid.addWidget( textEdit, *(ii, 1) )

                    textEdit = QLineEdit( items[1][j+1] )
                    key = "range "+items[0]+" "+str(j+1)
                    self.dict_LineEdit[ key ] = textEdit
                    grid.addWidget( textEdit, *(ii, 2) )
                    ii += 1
                    
            # for hosts part in config file        
            elif "host " in items[0]:
                grid.addWidget( QLabel(items[0]), *(ii, 0) )
                ii += 1
                grid.addWidget( QLabel("host"), *(ii, 0) )

                textEdit = QLineEdit( items[0].split(' ')[1] )
                self.dict_LineEdit[ items[0] ] = textEdit
                grid.addWidget( textEdit, *(ii, 1), 1, 2 )
                ii += 1

                lable = QLabel( "hardware ethernet" );
                grid.addWidget( lable, *(ii, 0))

                textEdit = QLineEdit( items[1][0] )
                key = "hardware ethernet " + items[0]
                self.dict_LineEdit[ key ] = textEdit
                grid.addWidget( textEdit, *(ii, 1), 1, 2 )
                ii += 1

                lable = QLabel( "fixed-address" );
                grid.addWidget( lable, *(ii, 0))

                textEdit = QLineEdit( items[1][1] )
                key = "fixed-address " + items[0]
                self.dict_LineEdit[ key ] = textEdit
                grid.addWidget( textEdit, *(ii, 1), 1, 2 )
                ii += 1
            else:
                grid.addWidget(lable, *(ii, 0))

                textEdit = QLineEdit( str(items[1]) )
                self.dict_LineEdit[ lable.text() ] = textEdit
                grid.addWidget(textEdit, *(ii, 1), 1, 2)
                
            ii += 1
            line = QFrame();
            line.setFrameShape(QFrame.HLine);
            line.setFrameShadow(QFrame.Sunken);
            
            grid.addWidget(line, *(ii, 0), 1, 3)
            ii += 1


        readButton = QPushButton("Read config")
        saveButton = QPushButton("Save config")
        saveButton.clicked.connect(self.save_config)
        grid.addWidget(readButton, *(ii, 1))
        grid.addWidget(saveButton, *(ii, 2))

        self.setLayout(grid)
        self.resize(400, 400)
        #self.center()
        self.move(0, 0)
        self.setWindowTitle('dhcp configuration')
        print(self.configs)

        #for key in self.dict_LineEdit:
        #    print ("{0} => {1}".format(key, self.dict_LineEdit[key].text()))
        #print(dict_LineEdit)
        #print(dict_LineEdit.get("option subnet-mask").text())

        
        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def find_simple_config(self):

        for str in self.data.split('\n'):
            if len( str ) < 2:
                continue
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
                        tmp[2] = re.sub('[,;"]', '', tmp[2])
                        self.configs[configs_key] = tmp[2] 
            else:
                tmp[1] = re.sub('[,;"]', '', tmp[1])
                self.configs[tmp[0]] = tmp[1]


    def find_config(self, parametr):
        
        search_str = ''
        if parametr == 'pools':
            search_str = "^subnet.*?(\d+).netmask.*?(\d+)."
        elif parametr == 'hosts':
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
            if parametr == 'pools':
                configs_values.append(tmp[3])
                for i in range( 5, len(tmp), 3 ):
                    tmp[i] = re.sub('[,;"]', '', tmp[i])
                    tmp[i+1] = re.sub('[,;"]', '', tmp[i+1])
                    configs_values.append(tmp[i])
                    configs_values.append(tmp[i+1])
            elif parametr == 'hosts':
                configs_values.append(tmp[4])
                configs_values.append(tmp[6])
            self.configs[configs_key] = configs_values
            self.data = self.data[ 0:clear_start-1 ] + self.data[ clear_end: ]
            match = re.search(search_str, self.data, flags=re.MULTILINE)

    def read_config(self):
        try:
            file_dhcp_config = open("dhcp.conf" , "r")
        except IOError:
            print("Error! DHCP config file does not exist")
        else:
            print("DHCP config file read")
            with file_dhcp_config:
                self.data = file_dhcp_config.read()
                text_len = len(self.data)
                self.find_simple_config();
                self.find_config('pools')
                self.find_config('hosts')

    def save_config(self):
        if self.dict_LineEdit:
            try:
                file_dhcp_config = open("dhcp.conf_new" , "w")
            except IOError:
                print("Error! DHCP config file does not exist")
            else:
                print("DHCP config file open for write")
                with file_dhcp_config:
                    already_write_configs = []
                    _dict = self.dict_LineEdit
                    for key in _dict:
                        if key in already_write_configs:# == None:
                            continue
                        
                        if "option domain-name-servers" in key:
                            count = 1
                            file_dhcp_config.write("option domain-name-servers ")
                            tmp_key = '{0}{1}'.format("option domain-name-servers", count)
                            print("data = {0}".format(tmp_key))
                            
                            while tmp_key in _dict.keys():
                                file_dhcp_config.write( _dict[tmp_key].text()+", " )
                                already_write_configs.append(tmp_key)
                                count += 1
                                tmp_key = '{0}{1}'.format("option domain-name-servers", count)
                        elif "subnet " in key:
                            print("subnet")
                        elif "host" in key:
                            print("host")
                        else:
                            file_dhcp_config.write(key + " " + self.dict_LineEdit[key].text())
                        file_dhcp_config.write(";\n")
                        print("AAAA")
                        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = DHCP()
    sys.exit(app.exec_())
 




        

        
