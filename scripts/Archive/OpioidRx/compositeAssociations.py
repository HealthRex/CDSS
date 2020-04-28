import sys;
import datetime;
from scipy import array;
from scipy.stats import chisquare;
from medinfo.common.StatsUtil import ContingencyStats;
from medinfo.common.Util import ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;

# Composite results from problemAssociations.py when seeing Rx associated with 2 Dx

def main(argv):
    
    # Initial pass to get single diagnosis baselines by looking for 2x Dx combos where Dx1 = Dx2
    countByDx = dict();
    countByRxDx = dict();
    associationFile = open(argv[1]);
    associationFile.readline(); # Dump header row
    for line in associationFile:
        line.strip();
        chunks = line.split("\t");
        rx = chunks[0];
        dx1 = chunks[1];
        dx2 = chunks[2];
        if dx1 == dx2:
            rxDxCount = int(chunks[3]);
            rxCount = int(chunks[4]);
            dxCount = int(chunks[5]);
            countByRxDx[(rx,dx1)] = rxDxCount;
            countByDx[dx1] = dxCount;
        
    # Second pass to now do stats for combo diagnoses, to see if prescription shows difference between 1 or both diagnoses        
    statIds = ("P-Fisher","P-YatesChi2","oddsRatio","relativeRisk","interest","LR+","LR-","sensitivity","specificity","PPV","NPV",);
    headerCols = ["Rx","Dx1","Dx2","RxDx1Dx2Count","RxDx1Count","RxDx2Count","RxCount","Dx1Dx2Count","Total","E(RxDx1Dx2Count)","E(RxDx2Dx1Count)","E(Dx1Dx2Count)","P-Chi2-Obs:Exp",];
    headerCols.extend(statIds);
    headerStr = str.join("\t", headerCols );
    print(headerStr);

    associationFile = open(argv[1]);
    associationFile.readline(); # Dump header row
    progress = ProgressDots();
    for line in associationFile:
        line.strip();
        chunks = line.split("\t");
        rx = chunks[0];
        dx1 = chunks[1];
        dx2 = chunks[2];
        rxDx1Dx2Count = int(chunks[3]);
        rxDx1Count = countByRxDx[(rx,dx1)];
        rxDx2Count = countByRxDx[(rx,dx2)];
        rxCount = int(chunks[4]);
        dx1Count = countByDx[dx1];
        dx2Count = countByDx[dx2];
        dx1dx2Count = int(chunks[5]);
        totalCount = float(chunks[6]);  # Floating point to auto-convert float divisions later

        conStats = ContingencyStats(rxDx1Dx2Count, rxCount, dx1dx2Count, totalCount);
        
        # Expected vs. observed Rx rates dependent on presence of Dx1Dx2 combination based one whether Rx rates per diagnosis are independent of combination
        observed = array \
            ([  (rxDx1Dx2Count),           (dx1dx2Count-rxDx1Dx2Count),
                (rxCount-rxDx1Dx2Count),   (totalCount-dx1dx2Count-rxCount+rxDx1Dx2Count),
            ]);
        
        # Expected rates based on assumption that diagnoses occur independently of one another
        expectedRxDx1Dx2 = (rxDx1Count*dx2Count/totalCount);
        expectedRxDx2Dx1 = (rxDx2Count*dx1Count/totalCount);
        expectedDx1Dx2 = (dx1Count*dx2Count/totalCount);
        expected = array \
            ([   (expectedRxDx1Dx2),            (expectedDx1Dx2-expectedRxDx1Dx2),
                (rxCount-expectedRxDx1Dx2),    (totalCount-expectedDx1Dx2-rxCount+expectedRxDx1Dx2),
            ]);

        (chi2ObsExp, pChi2ObsExp) = chisquare(observed, expected);
        
        dataCells = [rx, dx1, dx2, rxDx1Dx2Count, rxDx1Count, rxDx2Count, rxCount, dx1dx2Count, totalCount, expectedRxDx1Dx2, expectedRxDx2Dx1, expectedDx1Dx2, pChi2ObsExp];
        for statId in statIds:
            try:
                dataCells.append( conStats[statId] );
            except ZeroDivisionError:
                dataCells.append( None );
        for i, value in enumerate(dataCells):
            dataCells[i] = str(value);  # String conversion to allow for concatenation below
        dataStr = str.join("\t", dataCells );
        print(dataStr);
        progress.update();
    progress.printStatus();

if __name__ == "__main__":
    main(sys.argv);