import random
'''
--------------------------------------------------
sample() is an inbuilt function of random module 
in Python that returns a particular length list 
of items chosen from the sequence i.e. list, tuple, 
string or set
--------------------------------------------------
Used for random sampling without replacement
--------------------------------------------------
x denotes: 
    expects: 
        - list 
        - cases that you want to randomize 

y denotes:
    - list of boolean values that indicate whether or not 
          the recommender is turned on 

n denotes:
    - the number of times you want to sample without replacement
    - should equal the length of x and y (should I make this explicit?) 

Purpose of Script:
    - writing a function that accepts a list of physician cases and randomly orders them
    - making it reproducible (can run again) (may need to review documentation on seed) 
    
Learning Points to Incorporate: 
    - more test driven development
    - functional programming versus Object Oriented Programming 
    - Less Script-Like   
----------------------------------------------------        
'''


def testRandomizeCase(x, y):
    assert type(x) == list
    assert len(x) == len(y)


def randomizeCase(x,y):
    # set the seed 
    random.seed(a=1)
    # initialize an empty list 
    output = []
    # construct for loop for number of physicians in your study
    for _ in range(50):
        a = random.sample(x, 5)
        b = random.sample(y, 4)
        #c = [] 
        #c.append("True")
        output.append((a,b))
    return(output)

# p1 denotes the cases represented by letters in an alphabet     
cases = ['Fever B','Headache','Palpitations', 'Hematemesis', 'Shortness of Breath']

# TRUE or FALSE (True means recommender is turned on) 
booleanList = [True,True, False, False]

# running script: 
t = randomizeCase(cases, booleanList)
# assumes first case recommender is on
print t[0]
print t[1]
print t[2]
