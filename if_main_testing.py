import get_wash_co_site_info
import pandas as pd

##Call a function from an imported python file that I made
df = pd.read_csv("data/taxlots_hillsboro_sql_table_export.csv")
tlid_df = get_wash_co_site_info.get_webpage("1N228AA00400")
print(tlid_df)