#!/usr/bin/env bash
mode=$1
display_usage()
{
  echo -e "$PROG [-a <dark|light> -t <green|blue|dark-blue> -m <skill_mode> ]"
  echo -e "\n -a sets the overall appearance."
  echo -e " -t sets the colour theme."
  echo -e " -m sets the skill/mode (this can be changed inside the application)"
}
source /home/clive/PycharmProjects/cbot/venv/bin/activate
while getopts "a:t:m:h" options;
do
  case $options in
    a) appearance=" -a ${OPTARG}";;
    t) theme=" -t ${OPTARG}";;
    m) mode=" -m ${OPTARG}";;
    h) display_usage;
       exit 1;;
    *) display_usage;
       exit 1;;
   \?) display_usage;
       exit 1;;
  esac
done

python /home/clive/PycharmProjects/cbot/tk-albert-x.py ${appearance} ${theme} ${mode}
