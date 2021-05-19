import subprocess
import fire
import re
class ApkTool:
    def pull(self):
        """
        pull currently opened apk in android to computer 
        """
        _stdout=self.__exec_sh("adb shell dumpsys activity top")
        package_name=re.findall("TASK\s+(.*?)\s+id\=",_stdout)
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
        _stdout=self.__exec_sh(f"adb pull {apk_path}/base.apk ./{package_name}.apk")
        print(_stdout)
    def cpu(self):
        """
        show android architecture 32bit or 64bit?
        """
        _stdout=self.__exec_sh("adb shell getprop  | grep abilist")
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
        _stdout=self.__exec_sh(f"""adb shell su -c {" ".join(cmd)}""")
        print(_stdout)
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
    def __exec_sh(self,cmd):
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