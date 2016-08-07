# Search
Script that searches one or more named input files (standard input if no files are specified, or the file name '-' is given) for lines containing a match to a regular expression pattern.

Script accepts list of optional parameters that are mutually exclusive:
- -u ( --underscore ) which prints '^' under the matching text
- -c ( --color ) which highlight matching text [1]
- -m ( --machine ) which generate machine readable output format: file_name:no_line:start_pos:matched_text

To use this script you can write command into terminal like this:
```
python search.py -u -c -m "pattern" /path/to/file /path/to/file2
```
