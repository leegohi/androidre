# androidre

NAME

    droidbox

SYNOPSIS

    droidbox COMMAND

COMMANDS

    COMMAND is one of the following:

     cpu

       show android architecture 32bit or 64bit?

     proc_cwd

       show process currently work directory e.g. droidbox proc_cwd 80

     proc_env

       show process  environment by pid e.g droidbox proc_env 80

     ps

       show android process

     pull

       pull currently opened apk in android to computer

     su
     
       use super user privilege to execute shell command on android e.g. droidbox su cat /proc/26519/environ