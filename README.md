# wash-co-taxlot-data

Taking Washington County's public property tax information from seperate webpages and individual PDFs and putting it all into a single, logical table. Because even though the data is public, it's difficult to access.

The process:
1. Get taxlot information from tables on the washington county website
2. Open property tax statement pdfs
3. Convert pdf to an image and crop it
4. Use tessesract for character recognition
5. Add data to a dataframe

CSV's are in the "/data/assessments" folder. The entire script took about 8 hours to run, largely due to service request timeouts. Each website table takes about 1.5 seconds to download and scrape, and optical content recognition using Google's Tesseract engine takes about 2 seconds per pdf, for a total of 3.5 seconds per property tax account. Sometimes there are multiple property tax accounts per taxlot. `pyinstrument -r html [filename].py` was used to profile the code.

There is a public facing ArcREST server with Metro Taxlot data here: 

https://services1.arcgis.com/CaytfvK0buqDpHgu/ArcGIS/rest/services/Taxlots_all/FeatureServer/6

With ogr2ogr, the taxlot geometries can be downloaded and stored in a SpatiaLite database:

```
ogr2ogr -f SQLite taxlots_all_Wash_Cnty.sqlite "https://services1.arcgis.com/CaytfvK0buqDpHgu/ArcGIS/rest/services/Taxlots_all/FeatureServer/6/query?where=%22COUNTY%22%3D%27W%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=true&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pgeojson&token="
```
