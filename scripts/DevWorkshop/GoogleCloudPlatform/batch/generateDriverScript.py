# Example script to generate a file to batch run a bunch of processes

def main():
    outF = open("cloud_driver.sh", "w");

    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j' , 'k' , 'l', 'i', 'm', 'n', 'o', 'p', 'q', 'r',  's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for i, letter in enumerate(letters):
        commandLine = 'nohup python2 -u cloud_read.py 1 %s 100 &> results%s.log &\n' % (letter, i);
        outF.write(commandLine)
    outF.close()

if __name__ == "__main__":
    main()
