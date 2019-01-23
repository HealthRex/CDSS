

'''
'''
import os
import pandas as pd
pd.set_option('display.width', 3000)
pd.set_option('display.max_columns', 500)

import stats_utils


'''
Top volume panels.

Top frequent (order in 24h) panels. 
TODO: fix this, < 1 day? <= 1 day?

Choose wisely guideline panels (read from literature)?
'''

# TODO: need update!
TOP_PANELS_AND_COUNTS_BY_VOL = [['LABMGN', 282090], ['LABPT', 149070], ['LABPHOS', 140861], ['LABPTT', 97752], ['LABLACWB', 81693], ['LABCAI', 79497], ['LABK', 49953], ['LABTNI', 35462], ['LABLDH', 30262], ['LABHEPAR', 28083], ['LABUAPRN', 27654], ['LABBLC', 26600], ['LABBLC2', 24669], ['LABNA', 23971], ['LABLIDOL', 20894], ['LABHCTX', 19137], ['LABURNC', 17055], ['LABUA', 16362], ['LABURIC', 15194], ['LABA1C', 14921], ['LABSPLAC', 12427], ['LABPCTNI', 12218], ['LABPLTS', 11576], ['LABLIPS', 11563], ['LABPROCT', 11516], ['LABLAC', 10122], ['LABFIB', 9797], ['LABTSH', 9631], ['LABCK', 8368], ['LABCRP', 8331], ['LABNTBNP', 8127], ['LABTRIG', 6983], ['LABMB', 6396], ['LABCDTPCR', 6280], ['LABOSM', 5838], ['LABRESPG', 5782], ['LABESRP', 5667], ['LABFER', 5413], ['LABALB', 5209], ['LABNH3', 5118], ['LABUSPG', 5050], ['LABFCUL', 4905], ['LABHAP', 4739], ['LABANER', 4574], ['LABFLDC', 4556], ['LABCMVQT', 4376], ['LABBLCTIP', 4095], ['LABFT4', 4061], ['LABTRFS', 4010], ['LABB12', 3984], ['LABBLCSTK', 3970], ['LABPALB', 3906], ['LABUOSM', 3849], ['LABDIGL', 3619], ['LABRETIC', 3297], ['LABCORT', 3198], ['LABHBSAG', 2989], ['LABFE', 2686], ['LABAFBC', 2679], ['LABCA', 2570], ['LABBXTG', 2402], ['LABAFBD', 2321], ['LABUPREG', 2284], ['LABBUN', 2235], ['LABGRAM', 2027], ['LABPTEG', 1942], ['LABCSFTP', 1762], ['LABFOL', 1755], ['LABCSFGL', 1736], ['LABRESP', 1624], ['LABCSFC', 1556], ['LABSTOBGD', 1555], ['LABPCCR', 705], ['LABPCCG4O', 683], ['LABHIVWBL', 73], ['LABSTLCX', 0]]
TOP_PANELS_AND_COUNTS_BY_AVOIDED_VOL = [['LABMGN', 131241.99224268], ['LABK', 40908.462964086], ['LABPHOS', 38567.806173477], ['LABLACWB', 31583.607424191], ['LABBLC2', 22098.085924428], ['LABBLC', 20961.4726608], ['LABURIC', 15194.0], ['LABTNI', 14907.504815014], ['LABLIDOL', 13608.669298696], ['LABPCTNI', 10860.981023707998], ['LABLDH', 9706.447408672], ['LABSPLAC', 9614.741243338], ['LABLAC', 6204.370623486], ['LABUSPG', 5050.0], ['LABPROCT', 4405.2433256879995], ['LABPLTS', 4063.256893088], ['LABLIPS', 3888.0760019960003], ['LABCK', 3763.9788673600005], ['LABUOSM', 3610.8005897010003], ['LABBLCTIP', 3338.2788238799994], ['LABFCUL', 3321.0574856999997], ['LABHBSAG', 2989.0], ['LABDIGL', 2541.283086958], ['LABANER', 2479.960383196], ['LABAFBD', 2321.0], ['LABUPREG', 2284.0], ['LABTRIG', 2048.8365078230004], ['LABAFBC', 1729.262429691], ['LABUAPRN', 1591.597126878], ['LABCSFGL', 1586.9816575759999], ['LABCSFC', 1555.9999999999998], ['LABFLDC', 1449.83191544], ['LABCORT', 1380.8031239339998], ['LABOSM', 1275.99916668], ['LABCDTPCR', 1130.90543324], ['LABMB', 1128.7058808479999], ['LABURNC', 1082.7239178599998], ['LABB12', 996.9512915519999], ['LABPTT', 981.6100414319999], ['LABBUN', 937.1564486550001], ['LABA1C', 862.7588092220001], ['LABFIB', 725.8573297350001], ['LABHAP', 675.964439136], ['LABPCCG4O', 652.048338057], ['LABFE', 519.498567012], ['LABRESP', 368.905280576], ['LABPALB', 229.57315794000002], ['LABCA', 175.36470558], ['LABESRP', 160.25532489600002], ['LABPCCR', 160.253012085], ['LABFER', 138.32970217000002], ['LABALB', 123.013842715], ['LABRETIC', 107.962216824], ['LABBLCSTK', 95.32920021], ['LABCSFTP', 85.824354094], ['LABHIVWBL', 73.00000000000001], ['LABNA', 38.538584207], ['LABSTOBGD', 27.829976505], ['LABHCTX', 14.443019229], ['LABBXTG', 13.916570685999998], ['LABFT4', 10.421728056000001], ['LABNH3', 8.470003392], ['LABGRAM', 3.132921065], ['LABRESPG', 0.0], ['LABPTEG', 0.0], ['LABPT', 0.0], ['LABSTLCX', 0.0], ['LABTRFS', 0.0], ['LABNTBNP', 0.0], ['LABTSH', 0.0], ['LABUA', 0.0], ['LABHEPAR', 0.0], ['LABCAI', 0.0], ['LABCRP', 0.0], ['LABCMVQT', 0.0], ['LABFOL', 0.0]]

TOP_PANELS_AND_COUNTS_IN_1DAY = [['LABMETB', 139576], ['LABMGN', 135115], ['LABCBCD', 63426], ['LABLACWB', 60781], ['LABPTT', 59468], ['LABPHOS', 56710], ['LABPT', 55978], ['LABCAI', 52599], ['LABK', 40257], ['LABHEPAR', 21786], ['LABNA', 20816], ['LABTNI', 20105], ['LABLIDOL', 17706], ['LABHCTX', 10312], ['LABLDH', 9003], ['LABURIC', 7526], ['LABLAC', 6105], ['LABSPLAC', 5099], ['LABFIB', 4658], ['LABUSPG', 4430], ['LABCK', 3875], ['LABOSM', 3602], ['LABMB', 2987], ['LABUA', 2002], ['LABPCTNI', 1748], ['LABPROCT', 1355], ['LABLIPS', 1241], ['LABBLC', 1239], ['LABANER', 1206], ['LABAFBC', 1091], ['LABCA', 1084], ['LABA1C', 1003], ['LABBUN', 955], ['LABALB', 954], ['LABBLC2', 936], ['LABNH3', 917], ['LABFCUL', 881], ['LABURNC', 832], ['LABCORT', 801], ['LABUAPRN', 758], ['LABPLTS', 724], ['LABTRIG', 664], ['LABPTEG', 635], ['LABCRP', 626], ['LABUOSM', 600], ['LABRESPG', 566], ['LABTSH', 535], ['LABAFBD', 502], ['LABNTBNP', 486], ['LABBXTG', 461], ['LABFLDC', 450], ['LABDIGL', 422], ['LABHAP', 404], ['LABFER', 348], ['LABESRP', 317], ['LABRETIC', 213], ['LABHBSAG', 210], ['LABGRAM', 194], ['LABFT4', 193], ['LABBLCTIP', 191], ['LABRESP', 173], ['LABCMVQT', 157], ['LABPALB', 133], ['LABB12', 125], ['LABTRFS', 115], ['LABBLCSTK', 73], ['LABCSFTP', 66], ['LABCSFC', 65], ['LABCSFGL', 64], ['LABCDTPCR', 62], ['LABFE', 49], ['LABPCCG4O', 47], ['LABSTOBGD', 44], ['LABFOL', 36], ['LABUPREG', 21], ['LABPCCR', 12], ['LABHIVWBL', 3], ['LABSTLCX', 0]]
TOP_PANELS_AND_COUNTS_IN_1TO3DAYS = [['LABMETB', 105169], ['LABMGN', 104168], ['LABCBCD', 96547], ['LABPHOS', 59456], ['LABPT', 54376], ['LABCAI', 14790], ['LABLDH', 13654], ['LABPTT', 13595], ['LABLACWB', 6053], ['LABURIC', 5318], ['LABBLC', 5018], ['LABBLC2', 4450], ['LABK', 3911], ['LABHCTX', 3712], ['LABPLTS', 3379], ['LABPROCT', 2757], ['LABTRIG', 2669], ['LABUAPRN', 2229], ['LABFIB', 2178], ['LABHEPAR', 2081], ['LABUA', 1948], ['LABDIGL', 1797], ['LABCRP', 1788], ['LABTNI', 1626], ['LABLIPS', 1536], ['LABURNC', 1469], ['LABSPLAC', 1363], ['LABALB', 1316], ['LABCK', 1285], ['LABHAP', 1234], ['LABNH3', 1147], ['LABPALB', 1015], ['LABRESPG', 956], ['LABNA', 861], ['LABCMVQT', 733], ['LABBLCTIP', 618], ['LABBLCSTK', 618], ['LABESRP', 616], ['LABLAC', 535], ['LABNTBNP', 527], ['LABLIDOL', 500], ['LABA1C', 488], ['LABCA', 462], ['LABMB', 453], ['LABFER', 408], ['LABFLDC', 366], ['LABRETIC', 349], ['LABUOSM', 288], ['LABGRAM', 276], ['LABTSH', 275], ['LABCSFGL', 253], ['LABRESP', 250], ['LABCSFTP', 245], ['LABCSFC', 243], ['LABFCUL', 239], ['LABAFBC', 218], ['LABOSM', 203], ['LABCORT', 201], ['LABFT4', 183], ['LABBUN', 166], ['LABANER', 113], ['LABTRFS', 102], ['LABPTEG', 86], ['LABB12', 80], ['LABUSPG', 74], ['LABAFBD', 66], ['LABFE', 60], ['LABCDTPCR', 53], ['LABSTOBGD', 47], ['LABBXTG', 46], ['LABHBSAG', 39], ['LABPCTNI', 29], ['LABFOL', 22], ['LABUPREG', 5], ['LABHIVWBL', 1], ['LABPCCR', 1], ['LABSTLCX', 0], ['LABPCCG4O', 0]]

data_folderpath = 'data-Stanford-panel-10000-episodes'

def show_top_volume_panels():
    data_filepath = os.path.join(data_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')
    df = pd.read_csv(data_filepath, keep_default_na=False)

    # TODO: does tot_vol include 2014_1stHalf?
    if '2014 1stHalf count' in df.columns.values.tolist():
        df['total_cnt'] = df[[x+' count' for x in stats_utils.DEFAULT_TIMEWINDOWS[1:]]].sum(axis=1)
        df.drop('2014 1stHalf count', axis=1).to_csv(data_filepath, index=False)

    top_panels_and_cnts_by_vol =  df[['lab', 'total_cnt']].drop_duplicates().sort_values('total_cnt', ascending=False).values.tolist()
    print ', '.join(str(x) for x in top_panels_and_cnts_by_vol)

def show_top_avoided_volume_panels(target_PPV=0.95):
    data_filepath = os.path.join(data_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')
    df = pd.read_csv(data_filepath, keep_default_na=False)

    # TODO: does tot_vol include 2014_1stHalf?
    if '2014 1stHalf count' in df.columns.values.tolist():
        df['total_cnt'] = df[[x + ' count' for x in stats_utils.DEFAULT_TIMEWINDOWS[1:]]].sum(axis=1)
        df.drop('2014 1stHalf count', axis=1).to_csv(data_filepath, index=False)

    df = df[df['targeted_PPV_fixTrainPPV']==target_PPV]
    df['avoided_cnt'] = (df['true_positive']+df['false_positive']) * df['total_cnt']
    top_panels_and_cnts_by_avoidable_vol = df[['lab', 'avoided_cnt']].drop_duplicates().sort_values('avoided_cnt',
                                                                                        ascending=False).values.tolist()
    print ', '.join(str(x) for x in top_panels_and_cnts_by_avoidable_vol)

def show_top_order_in_1day_panels():
    data_filepath = os.path.join(data_folderpath, 'Fig2_Order_Intensities', 'Order_Intensities_panel.csv')
    df = pd.read_csv(data_filepath, keep_default_na=False)
    top_panels_and_cnts_in_1day = df[['lab', '< 1 day']].drop_duplicates().sort_values('< 1 day', ascending=False).values.tolist()
    print ', '.join(str(x) for x in top_panels_and_cnts_in_1day)

def show_top_order_in_1to3day_panels():
    data_filepath = os.path.join(data_folderpath, 'Fig2_Order_Intensities', 'Order_Intensities_panel.csv')
    df = pd.read_csv(data_filepath, keep_default_na=False)
    top_panels_and_cnts_in_1to3days = df[['lab', '1-3 days']].drop_duplicates().sort_values('1-3 days',
                                                                                       ascending=False).values.tolist()
    print ', '.join(str(x) for x in top_panels_and_cnts_in_1to3days)

if __name__ == '__main__':
    show_top_order_in_1day_panels()