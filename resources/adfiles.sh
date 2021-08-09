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
      echo ""
    fi
  done
  echo ""
  echo Push
  echo ""
  git push
  echo ""
fi
echo "Done"
echo ""
git status
echo ""

