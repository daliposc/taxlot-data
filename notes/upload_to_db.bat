ogr2ogr -f PostgreSQL PG:"dbname=property user=postgres" hillsboro_assessment_and_taxation_0.csv -nln hillsboro_real_property -nlt NONE -overwrite -lco PRECISION=NO -lco COLUMN_TYPES="prop_class=TEXT","code_area=TEXT" -oo AUTODETECT_TYPE=TRUE -oo EMPTY_STRING_AS_NULL=TRUE
for /l %%x in (100,100,32400) do (
    echo %%x
    ogr2ogr -f PostgreSQL PG:"dbname=property user=postgres" hillsboro_assessment_and_taxation_%%x.csv -nln hillsboro_real_property -nlt NONE -append -oo AUTODETECT_TYPE=TRUE -oo EMPTY_STRING_AS_NULL=TRUE
)