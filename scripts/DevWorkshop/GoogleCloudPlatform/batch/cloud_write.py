t = []
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j' , 'k' , 'l', 'i', 'm', 'n', 'o', 'p', 'q', 'r',  's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
for i  in letters:
  t.append((str('nohup python2 -u cloud_read10.py ' +  i + str(' 100') + ' &> results.log  &')))

outF = open("cloud_log.sh", "w")
for line in t:
  # write line to output file
  outF.write(line)
  outF.write("\n")
outF.close()
