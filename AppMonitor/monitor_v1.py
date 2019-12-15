# -*- coding: utf-8 -*-
import frida
import sys
import os
import time
import logging
import analysis
import subprocess
import os
from subprocess import call, PIPE, Popen

logging.basicConfig(level=logging.INFO,
                    format = "%(asctime)s %(message)s",
                    datefmt = '%Y-%m-%d %H:%M',
                    filename = r"D:\PyhonProject\venv\Projects\fridahook\AppMonitor\log.txt",
                    filemode = "w")


class AppMonitor(object):
    def __init__(self):
        pass

    def build_monitor_script(self, dir, topdown = True):
        script = ""
        for root, dirs, files in os.walk(dir, topdown):
            for name in files:
                script += open(os.path.join(root,name)).read()
        return script

    def on_message(self, message, data):
        if message['type'] == 'send':
            logging.info(message['payload'])
        elif message['type'] == 'error':
            logging.info(message['stack'])

    def start_app(self, apkFile, packageName, launcherActivity):
        #install apk
        cmd = "adb install -r " + apkFile
        ret = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if (ret == 1):
            print("[ERROR]: failed install apk")
            sys.exit(1)
        print("successfully installed apk")
        '''
        #launch app
        cmd = "adb shell am start -n " + packageName + "/" + launcherActivity
        ret = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if (ret == 1):
            print("[ERROR]: failed to launch app")
            sys.exit(1)
        print("successfully launched app")
        '''
        #prepare for frida
        # cmd1 = "adb forward tcp:27042 tcp:27042"
        # ret1 = subprocess.call(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def check_apk_install(self, packageName):
        cmd = "adb shell pm list packages -3"
        if packageName in subprocess.getoutput(cmd):
            return True
        return False


    def run(self):
        apkFile = r"E:\app软件破解\未破解\aweme_aweGW_v9.0.0_12535d2.apk"
        app = analysis.Application(apkFile)
        packageName = app.getPackageName()
        launcherActivity = app.getMainActivity()

        # first check app if install
        check_app = self.check_apk_install(packageName)
        if check_app:
            print("[WARNING]: the apk has installed")
            pass
        else:
            #install apk and launch app
            self.start_app(apkFile, packageName, launcherActivity)
            #wait for app
            time.sleep(2)

        pid = None
        device = None
        session = None
        try:
            device = frida.get_usb_device(timeout=5)
            pid = device.spawn([packageName])
            session = device.attach(pid)
        except Exception as e:
            print("[ERROR]: %s" % str(e))
            sys.exit(1)
        print("successfully attached to app")
        script_dir = os.path.join(".", "scripts")
        script_content = self.build_monitor_script(script_dir)
        script = session.create_script(script_content)
        script.on("message", self.on_message)
        script.load()
        device.resume(pid)

        #prevent the python script from terminating
        start = time.process_time()
        while True:
            end = time.process_time()
            if int(end - start) > 300:
                session.detach()
                break

if __name__ == "__main__":
    am = AppMonitor()
    am.run()