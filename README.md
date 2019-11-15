# taxlot-data

Taking Washington County's public property tax information from individual PDFs for each taxlot into a single table.

*Note*: Use `pyinstrument -r html [filename].py` to profile code

**To-Do:**
- A lot, lol.
- But really, uhm...
- Crop PDFs before extracting text
- Parse image_to_string text files, convert to dataframe
- Impliment multi-threading for tesseract operations
- Figure out the fastest way to download and analyze at the same time (Blocks of 10? All PDFs, then all images? Etc.)