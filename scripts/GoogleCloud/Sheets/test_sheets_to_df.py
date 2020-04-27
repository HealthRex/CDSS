from pathlib import Path

from scripts.GoogleCloud.Sheets.sheets_to_df import GoogleSheetsConnect


def test_creating_df_from_sheets(json_path, sheet_id, range_name):
    p = Path(json_path)
    assert p.exists(), json_path + ' does not exist.'

    sheet_connect = GoogleSheetsConnect(json_path)

    sheet_result = sheet_connect.get_sheet(sheet_id, range_name)

    df = sheet_connect.get_df(sheet_result, verbose=True, first_line_header=False)

    print(df)

    return


if __name__ == '__main__':
    json = input('Enter json_path: ')

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    SAMPLE_RANGE_NAME = 'Class Data!A2:E'

    test_creating_df_from_sheets(json, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)