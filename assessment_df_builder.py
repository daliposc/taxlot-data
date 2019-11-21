import logging
import site_reader
import pandas as pd

def main():
    logging.basicConfig(filename='log.log', format='%(asctime)s: %(message)s', level=logging.INFO)
    taxlots_df = pd.read_csv('data/hillsboro_taxlots.csv')
    assessment_df = pd.DataFrame()
    tlid_count = 0
    for index, row in taxlots_df.iterrows():
        if tlid_count > 33300:
            logging.info(f'--Assessing {taxlots_df.loc[index].tlid} TLID {tlid_count} --')
            assessment_df = assessment_df.append(site_reader.get_asessment_report(taxlots_df.loc[index].tlid), ignore_index=True)
            logging.info(f'Asessment {tlid_count} rows appended to assessment dataframe.')
            print('tlid:', taxlots_df.loc[index].tlid, '| total taxlots:', tlid_count)
            if tlid_count % 100 == 0:
                logging.info(f'----Writing data to "data/assessments/hillsboro_assessment_and_taxation_{tlid_count}.csv"----')
                with open('data/assessments/hillsboro_assessment_and_taxation_{}.csv'.format(tlid_count), 'w') as f:
                    print(assessment_df.info(verbose=True))
                    f.write(assessment_df.to_csv(sep='|', line_terminator='\n'))
                    assessment_df = pd.DataFrame()
                logging.info('----Data successfully written----')
        tlid_count += 1
    
    logging.info(f'----Writing (the last bit of) data to "data/assessments/hillsboro_assessment_and_taxation_{tlid_count}.csv"----')
    with open('data/assessments/hillsboro_assessment_and_taxation_{}.csv'.format(tlid_count), 'w') as f:
        print(assessment_df.info(verbose=True))
        f.write(assessment_df.to_csv(sep='|', line_terminator='\n'))
        assessment_df = pd.DataFrame()
        logging.info('----Data successfully written!!!----')

if __name__ == '__main__':
    main()