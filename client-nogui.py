#!/usr/bin/python
#coding:utf-8 
from os import execl, path, remove
from sys import executable, argv

from win32ras import SetEntryDialParams, Dial, HangUp, EnumConnections

import config

from time import sleep
from urllib2 import urlopen, URLError

from _winreg import  OpenKey, CloseKey, QueryValueEx, SetValueEx, KEY_WRITE, REG_SZ, HKEY_CURRENT_USER

dir_path = path.realpath(__file__)

RASFILE = '.\\ras.cfg'


class ClientApp():

    session = None
    rasfile = None
    ckp_task = None
    username = ''
    password = ''
    savepass = 0
    
    def __init__(self):
        try:
            print("program initing")
            self.init_config()
            print("init auto boot")
            #self.init_reg()  
            
            print("Connect readying")
            self.connect_ras()

        except: 
            pass    
    def init_config(self):
        rsfile = open(RASFILE,'wb')
        rsfile.write(config.rascfg)
        rsfile.close()
        print "config file write finished"
        
        
    def add_toreg(c):
        reg_content = c
        try:
            akey = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_WRITE)
            SetValueEx(akey, "AutoPPPoe", 0, REG_SZ, reg_content)
        except:
            print "add to reg failed"
            CloseKey(akey)
            pass
        CloseKey(akey)
    
    def check_reg(c):
        lastvalue = c
        try:
            akey = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
            lastvalue = QueryValueEx(akey, "AutoPPPoe")
            
            if str(lastvalue[0]) == c:
                CloseKey(akey)
                return True
            else:
                CloseKey(akey)
                return False
        except:
            CloseKey(akey)
            return False
    def init_reg():
    
        while not  self.check_reg(executable):
            add_toreg(executable)
    


    def check_conn(self):
        """ 检查连接是否成功 """
        if self.session:
            if self.session[0] == 0:
                try:
                    print "ERROR CONENCTION"
                    #print("Error connect Code：%d"%self.session[0])
                    # failed to reconnect
                    sleep(60)                
                    self.restart()
                except:
                    sleep(60)
                    pass

            else:
                try:
                    if self.session[1] > 0:
                        print "ERROR AUTH"
                        #print("Auth Failed code：%d"%self.session[1])
                        # reconnect and check operation
                        sleep(60)
                        self.restart()
                except:
                    sleep(60)
                    pass
                    
                else:
                    print("Auth Success Finished Connect")
                    # wait time for check con 
                    while True:
                        try:
                            urlopen('http://www.hrbeu.edu.cn', timeout = 1)
                            print "check for living"
                            sleep(30)
                            
                        except URLError as err:
                            # reconnect
                            print "Reconnecting ..."
                            self.restart()
        else:
            print "No session builed, reconnecting"
            self.restart()
                
                    

            
    def connect_ras(self):
        """ 认证登录 """
        username = '123456'
        passwd = '000000'
        savepass = 0
        print("Connect building....")

        def _connect():
            try:
                print("_connect started")
                SetEntryDialParams(RASFILE,("pyras", "", "", username, passwd, ""),savepass )
                self.session = Dial(None,RASFILE,("pyras", "", "", username, passwd, ""),None)
            except:
                pass
        print("Connecting......")


        self.disconnect_ras()
        _connect()
        print("Connect finished ")
        self.check_conn()
        
        
        

    def _disconnect_ras(self):
        """ 断开连接 """
        print "disconnecting all session"
        conns = EnumConnections()
        if conns:
            for conn in conns:
                try: HangUp(conn[0])
                except:
                    pass                
        self.session = None
        print "disconnected all sessions"

    def disconnect_ras(self): 
        self._disconnect_ras()

    def exit_handle(self):
        def _exit():
            if path.exists(RASFILE):
                remove(RASFILE)
            
        if self.session:
            self.disconnect_ras()
            _exit()
        else:_exit()    
    def restart(self):
        print "Restarting Service"

        execl(executable, ' ' + dir_path, *argv)

if __name__ == '__main__':

    #RASFILE = '\\'.join(executable.split("\\")[:-1]) + '\\' + RASFILE

    print RASFILE
    client = ClientApp()
    
    client.exit_handle()
    client.restart()


 