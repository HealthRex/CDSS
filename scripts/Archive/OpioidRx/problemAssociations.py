import sys;
import datetime;
from scipy import array;
from scipy.stats import chisquare, chi2_contingency;
from medinfo.common.StatsUtil import ContingencyStats;
from medinfo.common.Util import ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;

#DX_COL = "dx_group";
DX_COL = "base_bill_code";
LIMIT_DATE = datetime.datetime(2014,1,1);
DOUBLE_DX = True;
#DOUBLE_DX = False;

def baseQuery():
    query = SQLQuery();
    query.addSelect("count(distinct med.pat_id) as ptCount");
    query.addFrom("stride_order_med as med");
    query.addWhereOp("ordering_datetime","<", LIMIT_DATE );
    return query;

def main(argv):
    medIdsByActiveRx = dict();
    medIdsByActiveRx['Buprenorphine'] = ('125498','114474','212560','114475','114467','114468');
    medIdsByActiveRx['Fentanyl Patch'] = ('2680','27908','125379','27905','27906','540107','540638','540101','27907');
    medIdsByActiveRx['Methadone'] = ('540483','4953','4951','10546','214468','15996','41938','4954','4952');
    medIdsByActiveRx['Hydrocodone'] = ('3724', '4579', '8576', '8577', '8951', '10204', '12543', '13040', '14963', '14965', '14966', '17061', '17927', '19895', '20031', '28384', '29486', '29487', '34505', '34544', '35613', '117862', '204249', '206739');
    medIdsByActiveRx['Hydromorphone'] = ('2458','2459','2464','2465','3757','3758','3759','3760','3761','10224','10225','10226','10227','200439','201094','201096','201098','540125','540179','540666');
    medIdsByActiveRx['Morphine'] = ('5167','5168','5172','5173','5176','5177','5178','5179','5180','5183','6977','10655','15852','20908','20909','20910','20914','20915','20919','20920','20921','20922','29464','30138','31413','36140','36141','79691','87820','89282','91497','95244','96810','112562','112564','115335','115336','126132','198543','198544','198623','201842','201848','205011','206731','207949','208896','540182','540300');
    medIdsByActiveRx['Oxycodone'] = ('5940','5941','6122','6981','10812','10813','10814','14919','16121','16123','16129','16130','19187','26637','26638','27920','27921','27922','27923','28897','28899','28900','31851','31852','31863','31864','92248','126939','200451','203690','203691','203692','203705','203706','203707','204020','204021');

    query = baseQuery();
    totalPatients = float(DBUtil.execute(query)[0][0]);
    
    # print"Total Patients\t%s" % totalPatients

    # print"======= Dx Groups ===========";
    # print"Dx Group\tPt Count\tDx Rate";
    patientsPerDxGroup = dict();
    query = SQLQuery()
    query.addSelect("count(distinct prob.pat_id) as ptCount");
    query.addSelect("prob.%s" % DX_COL );
    query.addFrom("stride_problem_list as prob");
    query.addWhereOp("prob.noted_date","<", LIMIT_DATE );
    query.addGroupBy("prob.%s" % DX_COL );
    if DOUBLE_DX:
        query.addSelect("prob2.%s" % DX_COL );
        query.addFrom("stride_problem_list as prob2");
        query.addWhere("prob.pat_id = prob2.pat_id");
        query.addWhereOp("prob2.noted_date","<", LIMIT_DATE );
        query.addGroupBy("prob2.%s" % DX_COL );
    results = DBUtil.execute(query);
    for row in results:
        patientCount = row[0];
        dxGroup = row[1];
        if DOUBLE_DX:
            dxGroup = (dxGroup,row[2]); # Composite tuple including second diagnosis
        patientsPerDxGroup[dxGroup] = patientCount;

    progress = ProgressDots();
    for activeRx, medIds in medIdsByActiveRx.items():
        query = baseQuery();
        query.addWhereIn("medication_id", medIds );

        # Baseline prescription rates
        rxPtCount = DBUtil.execute(query)[0][0];
        
        # print"====== Rx Counts ======";
        # print"Rx\tPt Count\tRx Rate";
        # print"%s\t%s\t%s" % (activeRx, rxPtCount, (rxPtCount/totalPatients));

        # print"======== Rx-Dx Association ========";
        statIds = ("P-Fisher","P-YatesChi2","oddsRatio","relativeRisk","interest","LR+","LR-","sensitivity","specificity","PPV","NPV",);
        if progress.getCounts() == 0:
            headerCols = ["Rx","Dx","RxDxCount","RxCount","DxCount","Total"];
            if DOUBLE_DX:
                headerCols.insert(2, "Dx2");
            headerCols.extend(statIds);
            headerStr = str.join("\t", headerCols );
            print(headerStr);
        
        # Query out per diagnosis group, but do as aggregate grouped query
        query.addSelect("prob.%s" % DX_COL );
        query.addFrom("stride_problem_list as prob");
        query.addWhere("med.pat_id = prob.pat_id");
        query.addWhereOp("prob.noted_date","<", LIMIT_DATE );
        #query.addWhereIn("prob.%s" % DX_COL, dxKeys );
        query.addGroupBy("prob.%s" % DX_COL );
        if DOUBLE_DX:
            query.addSelect("prob2.%s" % DX_COL );
            query.addFrom("stride_problem_list as prob2");
            query.addWhere("prob.pat_id = prob2.pat_id");
            query.addWhereOp("prob2.noted_date","<", LIMIT_DATE );
            query.addGroupBy("prob2.%s" % DX_COL );
        results = DBUtil.execute(query);
        for row in results:
            rxDxPtCount = row[0];
            dxGroup = row[1];
            if DOUBLE_DX:
                dxGroup = (dxGroup,row[2]); # Composite tuple including second diagnosis
            dxPtCount = patientsPerDxGroup[dxGroup];
            
            conStats = ContingencyStats(rxDxPtCount, rxPtCount, dxPtCount, totalPatients);
            
            dataCells = [activeRx, dxGroup, rxDxPtCount, rxPtCount, dxPtCount, totalPatients];
            if DOUBLE_DX:
                dataCells[1] = dxGroup[0];
                dataCells.insert(2, dxGroup[1]);
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