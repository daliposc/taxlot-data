import site_reader
import pandas as pd

taxlots_df = pd.read_csv('data/hillsboro_taxlots.csv')
assessment_df = pd.DataFrame()
row_count = 0
for index, row in taxlots_df.iterrows():
    if row_count % 100 == 0:
        with open('data/assessments/tlid_assessments_{}.txt'.format(row_count), 'w') as f:
            print(assessment_df.to_csv())
            f.write(assessment_df.to_csv(sep='|', line_terminator='\n'))
            assessment_df = pd.DataFrame()
    assessment_df = assessment_df.append(site_reader.get_asessment_report(taxlots_df.loc[index].tlid), ignore_index=True)
    row_count += 1