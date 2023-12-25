#! /bin/bash
while getopts f:o: opt; do
  case $opt in
   f)
     spec_path=$OPTARG
     ;;
   o)
     out_dir=$OPTARG
     ;;
   \?)
     echo "Invalid option -$OPTARG" >&2
     exit 1
     ;;
   :)
     echo "Option -$OPRTARG requires an arguement." >&2
     exit 1
     ;;
   esac
done

sources=()

if ! [ -z "$spec_path" ]; then
  spec_sources=$(spectool -S  "$spec_path" | awk -F ': ' '{print $2}')
  for source in $spec_sources; do
   if [[ $source == http:* ]]; then
     sources+="$source"
   fi
   if [[ $source == ^https:* ]]; then
     sources+="$source"
   fi
  done
fi

echo ">>>>>>>>>>"

if [ -z "$out_dir" ]; then
  out_dir=$(pwd)
fi

proxy="https://cache-proxy.test.osinfra.cn/download"

for source in "${sources[@]}"; do
  obs_source=$proxy/$source
  wget $obs_source -p $out_dir
  base_name=`basename $source`
  if [ ! -f "$out_dir/$base_name" ]; then
    echo "Failed to download from cache-proxy.Start downloading from the official website."
    wget $source -P $out_dir
  fi
done

