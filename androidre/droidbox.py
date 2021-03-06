import subprocess
from subprocess import Popen, PIPE, STDOUT
import fire
import re
import os
import urllib.request
import io

base_dir=os.path.dirname(__file__)

def get_url_file_name():
    from urllib.parse import unquote, urlparse
    from pathlib import PurePosixPath
    return PurePosixPath(
            unquote(urlparse(url).path)).parts[-1]
def download_with_bar(url):
    resp = urllib.request.urlopen(url)
    length = resp.getheader('content-length')
    if length:
        length = int(length)
        blocksize = max(4096, length//100)
    else:
        blocksize = 1000000 # just made something up
    print("total size:","%sMB"%int(length/1024/1024),"block size:","%sByte"%blocksize)
    buf = io.BytesIO()
    size = 0
    while True:
        buf_part = resp.read(blocksize)
        if not buf_part:
            break
        buf.write(buf_part)
        size += len(buf_part)
        if length:
            print('{:.2f}%\r downloading:'.format(int(size/length*100)), end='')
    buf.seek(0)
    print()
    return buf

class ApkTool:
    """
    remember add the android buildtools to env:
    export ANDROID_HOME=/Users/$USER/Library/Android/sdk
    export PATH=${PATH}:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools/30.0.3
    """
    def __init__(self):
        self.apktool=os.path.join(base_dir,"apktool.jar")
    def pull(self):
        """
        pull currently opened apk in android to computer 
        """
        #_stdout=self.__exec_sh("adb shell dumpsys activity top")
        #package_name=re.findall("TASK\s+(.*?)\s+id\=",_stdout)
        _stdout=self.__exec_sh("adb shell dumpsys activity activities | sed -En -e '/Running activities/,/Run #0/p'")
        package_name=re.findall("TaskRecord.*\=(.*?)\s+U\=",_stdout)
        if not package_name or package_name[0]=="null":
            print("can not find package","raw output is:")
            print(_stdout)
            return 
        package_name=package_name[0]
        print("find package name:",package_name)
        _stdout=self.__exec_sh(f'''adb shell dumpsys package {package_name} | grep -A18 "Package \[{package_name}\]"''')
        print(_stdout)
        apk_path=re.findall("codePath\=(.*)",_stdout)[0].strip()
        print("apk path:",apk_path)
        _stdout=self.__exec_sh(f"adb pull {apk_path}/base.apk ./{package_name}.apk",show_output_realtime=True)
    def cpu(self):
        """
        show android architecture 32bit or 64bit?
        """
        _stdout=self.__exec_sh("adb shell getprop  | grep abilist")
        print(_stdout)
    def version(self):
        """
        show android linux kernel version
        """
        _stdout=self.__exec_sh("adb shell cat /proc/version")
        print(_stdout)
    def db(self):
        """
        show is debuggable?
        """
        _stdout=self.__exec_sh("adb shell getprop ro.debuggable")
        print(_stdout)
    def ps(self):
        """
        show android process
        """
        _stdout=self.__exec_sh(f"""adb shell ps""")
        print(_stdout)
    def su(self,*cmd):
        """
        use super user privilege to execute shell command on android
        e.g.
        droidbox su cat /proc/26519/environ
        """
        _stdout=self.__exec_sh(f"""adb shell su -c '{" ".join(cmd)}'""",show_output_realtime=True)
        print(_stdout)
        return _stdout
    def proc_env(self,pid):
        """
        show process  environment by pid
        e.g.
        droidbox proc_env 80
        """
        self.su(fr"cat /proc/{pid}/environ | tr '\000' '\n'""")
    def proc_cwd(self,pid):
        """
        show process currently work directory
        e.g.
        droidbox proc_cwd 80
        """
        self.su(fr"ls -l /proc/{pid}/cwd""")
    def d(self,apk):
        """ensure apktool in env, decode apk:
        e.g. apktools d(ecode) sample.apk  -o outdir
        """
        self.__exec_sh(f"java -jar {self.apktool} d {apk}  -o {apk}_d",show_output_realtime=True)
    def b(self,apk_d):
        """ensure apktool in env, encode apk:
        e.g. apktools b(uild)  inputdir  out.apk
        """
        apk_name=os.path.split(apk_d.strip("_d"))[-1]
        print("output:",apk_name)
        self.__exec_sh(f"java -jar {self.apktool} b {apk_d}  {apk_name}.apk",show_output_realtime=True)
    def sign(self,apk):
        """
        from:https://github.com/appium-boneyard/sign
        java -jar sign.jar my.apk
        """
        sign_jar=os.path.join(base_dir,"sign.jar")
        self.__exec_sh(f"""java -jar {sign_jar} {apk}""",show_output_realtime=True)
    def j2d(self,cls):
        """
        java class byte code  to dex byte code 
        dx --dex --output=Hello.dex Hello.class
        """
        self.__exec_sh("dx --dex --output={cls}.dex {cls}",show_output_realtime=True)
    def ip(self):
        """"show android phone ip"
        """
        self.__exec_sh("""adb shell ip route | awk '{print $9}'""",show_output_realtime=True)
    def sfs(self,frida_server_path=None,arki=""):
        """start frida server on remote mobile phone
        """
        if not frida_server_path:
            f=self.__install("frida")
            req=self.__install("requests")
            f_ver=f.__version__
            url=f"https://github.com/frida/frida/releases/download/{f_ver}/frida-server-{f_ver}-android-arm{arki}.xz"
            print("download url:",url)
            fname=f"frida-server-{f_ver}-android-arm{arki}"
            print("download",fname)
            response =download_with_bar(url)
            import lzma
            print("decompress",fname)
            decompress_data=lzma.decompress(response.read())
            with open(fname,"wb") as f:
                f.write(decompress_data)
            frida_server_path=fname
        name=os.path.split(frida_server_path)[-1]
        print("binary:",name)
        self.__exec_sh(f"adb push {frida_server_path} /data/local/tmp/",show_output_realtime=True)
        print("set x privilege to",name)
        self.su(f"chmod +x /data/local/tmp/{name}")
        print("start ",name)
        self.su(f"/data/local/tmp/{name} 2>&1")
    def wifi(self):
        self.su(f"cat  /data/misc/wifi/*.conf")
    def __install(self,package_name):
        try:
            return __import__(package_name)
        except:
            import os 
            os.system(f"pip install {package_name}")
    def __exec_sh(self,cmd,show_output_realtime=False):
        print(cmd)
        if show_output_realtime:
            p = Popen(cmd, stdout = PIPE, 
            stderr = STDOUT, shell = True)      
            while p.poll() is None:
                line = p.stdout.readline().decode("utf-8")
                print(line)
            p.wait()
            if p.returncode:
                import sys
                sys.exit()
            return 
        out_put=subprocess.run(cmd,shell=True,capture_output=True)
        if  out_put.returncode:
            print("exec cmd fail:",cmd)
            print(out_put.stderr.decode("utf-8"))
            import sys
            sys.exit() 
        return out_put.stdout.decode("utf-8")
def main():
    fire.Fire(ApkTool)
if __name__ == "__main__":
    main()