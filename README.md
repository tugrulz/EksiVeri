# EksiVeri
A comprehensive Ekşisözlük scraper. Designed for computational social science.

## Install
Clone or download the repository and run 
    
    pip install .
in the home directory.
## Usage
### Author Scraper
Scrapes a given authors page. (todo: explain more throughly)

Usage: 

    authors [OPTIONS] INPUT_CSV OUTPUT_FOLDER AUTHOR_COLUMN_NAME ENTRY_CROP_LENGTH

Options:
  --nrows INTEGER  Only scrape the first nrow many authors. Reads all the
                   authors in the input file if -1 or unspecified  [default:
                   -1]

  --help           


### Favorites
to do: breef explaination

Usage: 
    
    favorites [OPTIONS] INPUT_PATH OUTPUT_PATH ENTRY_ID_COLUMN_NAME

Options:

  --max_threads INTEGER  Maximum number of threads to use. Optimal value might
                         change from system to system.  [default: 10]

  --help                 


arguments: input_path output_path entry_id_column_name max_number_of_threads(optional)
* input_path: path of the input csv file which contains the  entry ids in one of the columns.
* output_path: path for the output csv file.
* max_number_of_threads: Optional. An integer greater than zero. Determines the maximum number of concurrent requests to be sent.

### Debe Scraper
Usage: 

    debe [OPTIONS] [%d.%m.%Y|%d-%m-%Y] [%d.%m.%Y|%d-%m-%Y] OUTPUT_PATH

Options:

  --help  

### Entry Scraper

Scrapes entries from a csv file that contains entry ids and writes the scrape info to three csv files, one containing brief info about each entry,
one that contains the entry id and the whole entry content and one with the links included in the entry.

run: 

    entry_scraper [OPTIONS] TAG_NAME [FILE_NAME] [COL_NO] [CONTENT_LIMIT] 

Options:

  --help
    
arguments: single_entry(optional) file_name col_no content_limit tag_name
* single_entry: Entry id of the desired input. If it is given instead of scraping the entries in a file, only this entry will be scraped. None by default.
* file_name: the name of the csv file that contains entry ids. entry_id_list.csv by default.
* col_no: the column number that contians the entry ids. 0 by default.
* content_limit: The limit of the entry content to be used for the brief info file. By default 280 characters.
* tag_name: the tag of the data set, to be used to name three output files. Naming example: tag_name.csv, tag_name_long.csv, tag_name_links.csv

###

### Random Entry Scraper

Scrapes entries with random ids from the given interval and writes the scrape info to three csv files, one containing brief info about each entry, one that contains the entry id and the whole entry content and one with the links included in the entry.

run: 

    entry_sampler [OPTIONS] [CONTENT_LIMIT] START_ENTRY END_ENTRY SAMPLE_SIZE
    
arguments: content_limit start_entry end_entry sample_size
* content_limit: The limit of the entry content to be used for the brief info file. By default 280 characters.
* start_entry: The start entry id of the interval.
* end_entry: The end entry id of the interval.
* sample_size: A random sample of this size will be retrieved from the interval
###

### Topic Scraper

Scrapes all the entries from a given topic link in a file. It can scrape just a specific page if indicated. It can also scrape the most liked entries overall, or most liked entries that day.

run: 

    topic_scraper [OPTIONS] [FILE_NAME] [COL_NO] [CONTENT_LIMIT] [0|1|2]

Options:

  --page_no INTEGER RANGE  If a specific page is wanted to be scrape, it can
                           be given here.  [default: -1]

  --help                   
    
arguments: single_topic (optional) file_name col_no content_limit page_no(optional) sukela(optional)
* single_topic: Topic name or link to be scraped. If a topic link or url is given, instead of scraping the topics from a file, only this topic will be scraped. None by default.
* file_name: the name of the csv file that contains topic links. topic_links_list.csv by default.
* col_no: the column number that contians the topic links. 0 by default.
* content_limit: The limit of the entry content to be used for the brief info file. By default 280 characters.
* page_no: If a specific page is wanted to be scrape, it can be given here.
* sukela: If 0, scrapes all entries in order of date, if 1, scrapes entries in order of overall likes, if 2, scrapes entries that were liked that day.

###

### Author Topic Scraper

Scrapes the entries of a topic related to an author in eksi.

run: 

    author_topic_scraper [OPTIONS] [FILE_NAME] [COL_NO] [CONTENT_LIMIT]
    
Options:

  --help
    
arguments: single_author(optional) file_name col_no content_limit page_no sukela
* single_author: Author nick to be scraped. If an author nick is given, instead of scraping the author nicks from a file, only this athor's topic will be scraped. None by default.
* file_name: the name of the csv file that contains author nicks. author_nicks_list.csv by default.
* col_no: the column number that contians the author nicks. 0 by default.
* content_limit: The limit of the entry content to be used for the brief info file. By default 280 characters.

###

### Topic Entry Number Scraper

Scrapes the number of entries in a given topic.

run: 

    topic_entry_no [OPTIONS] [FILE_NAME] [COL_NO]
    
Options:

  --help
    
arguments: single_topic(optional) file_name(optional) col_no(optional) 
* single_topic: Topic name or link to be scraped. If a topic link or url is given, instead of scraping the topics from a file, only this topic will be scraped. None by default.
* file_name: the name of the csv file that contains topic links. topic_links_list.csv by default.
* col_no: the column number that contians the topic links. 0 by default.

###

### Topic Channel Scraper

Scrapes the channels associated with a topic.

run: 

    channel [OPTIONS] [FILE_NAME] [COL_NO]
    
Options:

  --help
    
arguments: single_topic(optional) file_name(optional) col_no(optional)
* single_topic: Topic name or link to be scraped. If a topic link or url is given, instead of scraping the topics from a file, only this topic will be scraped. None by default.
* file_name: the name of the csv file that contains topic links. topic_links_list.csv by default.
* col_no: the column number that contians the topic links. 0 by default.

###

### Suggested Topics Scraper

Scrapes the name, entry no and link of the topics associated with given keywords.

run: 

    suggested_topics [OPTIONS] [SINGLE_KEYWORD] [FILE_NAME] [COL_NO]
    
Options:

  --help

arguments: single_keyword(optional) file_name(optional) col_no(optional)
* single_topic: A keyword that will be used to find topics that contain that keyword. If this is given, only this keyword is searched. None by default.
* file_name: the name of the csv file that contains topic links. topic_links_list.csv by default.
* col_no: the column number that contians the topic links. 0 by default.

###
