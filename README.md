# taxlot-data

Taking Washington County's public property tax information from individual PDFs for each taxlot into a single table.

The process:
1. Get taxlot information from tables on teh washington county website
2. Open property tax statement pdfs
3. Convert pdf to an image and crop it
4. Use tessesract for character recognition
5. Add data to a dataframe

*Note*: Use `pyinstrument -r html [filename].py` to profile code
