while true; do
    curl -s http://www.reddit.com/r/random | grep -oE "/r/[A-Za-z0-9]+" | sort | uniq | sed 's/\/r\///g' 
done
