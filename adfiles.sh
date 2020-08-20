#!/bin/sh

default=updated
if	[ -z "$1" ];	then
  echo -e "\nUsage $0 file1 file2 ...\n"
  exit
else
  for i in "$@"
  do
    target=${i%/}
    if [[ -f "$target" ]] ; then
      echo ""
      echo Add "$i"
      echo ""
      git add "$i"
      echo ""
      read -p "message: [$default] ": var
      var=${var:-$default}
      echo $var
      git commit -m "$var"
    fi
  done
  echo ""
  echo Done
  echo ""
  echo Push
  git push
fi
echo""
git status
echo ""

