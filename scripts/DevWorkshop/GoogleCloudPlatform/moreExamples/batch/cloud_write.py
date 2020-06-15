def main():
    t = []
    f = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j' , 'k' , 'l', 'i', 'm', 'n', 'o', 'p', 'q', 'r',  's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for i  in letters:
        t.append((str('nohup python2 -u cloud_read.py ' + str(1) + " " + i)))
    for j in range(1,27):
        f.append(str(' 100') + ' &> results' + str(j) + '.log  &')
    z = [x + y for x,y in zip(t,f)]
    outF = open("cloud_log.sh", "w")
    for line in z:
      # write line to output file
      outF.write(line)
      outF.write("\n")
    outF.close()

if __name__ == "__main__":
    main()
