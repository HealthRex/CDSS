import pip;

# If installing on Windows, May need Intel Math Kernel Library
#	Not available through source for Windows installation, 
#	so install from prepared binaries by downloading respective whl that have been precompiled: 
# 	http://www.lfd.uci.edu/~gohlke/pythonlibs/
#pip.main(["install","numpy-1.13.1+mkl-cp27-cp27m-win_amd64.whl"]); 
#pip.main(["install","scipy-0.19.1-cp27-cp27m-win_amd64.whl"]); 
pip.main(["install","numpy"]);
pip.main(["install","scipy"]);

pip.main(["install","psycopg2"]);
pip.main(["install","pandas"]);
pip.main(["install","matplotlib"]);
pip.main(["install","scikit-learn"]);
pip.main(["install","gensim"]);
#pip.main(["install",""]);
#pip.main(["install",""]);
#pip.main(["install",""]);
#

