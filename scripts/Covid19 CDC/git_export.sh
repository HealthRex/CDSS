while read filename; do git add $filename; done < "export_list.txt"
git status
git commit -m "update " 
git push origin master
