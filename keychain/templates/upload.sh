set -e
keypath="{{keypath}}"
if [[ $keypath = "" ]]
then
  if [ -e "$HOME/.ssh/id_dsa.pub" ]
  then
    keypath="$HOME/.ssh/id_dsa.pub"
  elif [ -e "$HOME/.ssh/id_rsa.pub" ]
  then
    keypath="$HOME/.ssh/id_rsa.pub"
  else
    echo "Unable to find a public key." 
    echo "Specify a path with 'keypath' parameter in URL."
    exit 1
  fi
fi
curl -s -X PUT -F key="@$keypath" "{{url_root}}{{email}}/{{keyname}}"

