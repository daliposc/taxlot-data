import pandas as pd

i = 100
while i <= 1100:
    df = pd.read_csv(f'data/assessments/old/hillsboro_assessment_and_taxation_{i}.csv', sep='|', index_col=0, dtype={'prop_class':str,'code_area':str})
    # df.loc[df['assessed_val'] == 0, 'taxes_2018'] = 0
    # df.loc[df['assessed_val'] == 0, 'taxes_2019'] = 0
    # df.loc[df['prop_account_id'] == 'tlid', 'prop_account_id'] = ''
    df.loc[df['lot_size'] == "ATTR_ERR: Acres: N/A ", 'lot_size'] = ''
    with open(f'data/assessments/hillsboro_assessment_and_taxation_{i}.csv', 'w') as f:
        f.write(df.to_csv(sep='|', line_terminator='\n'))
    i += 100