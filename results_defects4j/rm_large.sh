#find . -name *\\.txt\\.log -type f -size +100M -exec du -h {} \;
find . -name *\\.txt\\.log -type f -size +100M -exec rm {} \;
