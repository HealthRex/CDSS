        
def kappaStat( contingencyTable ):
    """Calculate Cohen's kappa statistic for inter-rater agreement.
    contingencyTable expected to be a 2D table (2D list)
    representing the counts of mutually exclusive categorical responses for
    two different raters.
    
    http://en.wikipedia.org/wiki/Kappa_statistic
    
    >>> from util import kappaStat;
    >>> contingencyTable = [ [20,5], [10,15] ];
    >>> kappaStat( contingencyTable );
    (0.3999999999999999, 0.7, 0.5)

    """

    # Count up total sums first
    rowSums = [0]*len(contingencyTable);
    colSums = [0]*len(contingencyTable);
    tableSum = 0.0; # Floating point number to automate subsequent conversions
    
    for i, row in enumerate(contingencyTable):
        for j, datum in enumerate(row):
            rowSums[i] += datum;
            colSums[j] += datum;
            tableSum += datum;
            
    # Second pass to estimate chance/random agreement based on total row/col sums
    agreeSum = 0;
    chanceSum = 0.0;
    
    for i, row in enumerate(contingencyTable):
        for j, datum in enumerate(row):
            if i == j:
                agreeSum += datum;
                chanceSum += (rowSums[i]/tableSum)*(colSums[j]/tableSum);

    agreeRate = agreeSum / tableSum;
    
    kappa = (agreeRate - chanceSum) / (1 - chanceSum);
    
    return (kappa, agreeRate, chanceSum);
    