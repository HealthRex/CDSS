

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
TOP_PANELS_AND_COUNTS_BY_VOL = [['LABMGN', 329148], ['LABPT', 176593], ['LABPHOS', 165710], ['LABPTT', 114423], ['LABCAI', 94642], ['LABLACWB', 94077], ['LABK', 56785], ['LABTNI', 42049], ['LABLDH', 35325], ['LABHEPAR', 32554], ['LABUAPRN', 31754], ['LABBLC', 31579], ['LABBLC2', 29343], ['LABNA', 27405], ['LABLIDOL', 24076], ['LABHCTX', 22416], ['LABURNC', 20309], ['LABUA', 20083], ['LABURIC', 18320], ['LABA1C', 17682], ['LABSPLAC', 14871], ['LABPCTNI', 14578], ['LABLIPS', 13496], ['LABPLTS', 12462], ['LABPROCT', 12141], ['LABTSH', 11387], ['LABFIB', 10916], ['LABCRP', 10248], ['LABLAC', 10159], ['LABCK', 9705], ['LABNTBNP', 9701], ['LABTRIG', 8492], ['LABMB', 8340], ['LABCDTPCR', 7774], ['LABOSM', 6909], ['LABESRP', 6577], ['LABALB', 6561], ['LABFER', 6367], ['LABFCUL', 6200], ['LABRESPG', 6064], ['LABANER', 6004], ['LABNH3', 5976], ['LABUSPG', 5688], ['LABFLDC', 5636], ['LABHAP', 5602], ['LABPALB', 5300], ['LABCMVQT', 5182], ['LABBLCTIP', 4894], ['LABFT4', 4821], ['LABTRFS', 4791], ['LABBLCSTK', 4722], ['LABB12', 4624], ['LABUOSM', 4440], ['LABDIGL', 4304], ['LABRETIC', 3801], ['LABCORT', 3694], ['LABHBSAG', 3427], ['LABGRAM', 3286], ['LABAFBC', 3252], ['LABBXTG', 3033], ['LABAFBD', 2888], ['LABCA', 2882], ['LABRESP', 2815], ['LABFE', 2739], ['LABUPREG', 2673], ['LABBUN', 2547], ['LABPTEG', 2295], ['LABCSFTP', 2157], ['LABCSFGL', 2129], ['LABFOL', 2111], ['LABSTOBGD', 1996], ['LABCSFC', 1889], ['LABPCCG4O', 1148], ['LABPCCR', 811], ['LABHIVWBL', 629], ['LABSTLCX', 0]]
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
    show_top_volume_panels()