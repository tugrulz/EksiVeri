from setuptools import setup, find_packages, find_namespace_packages

setup(
    name='eksiveri', #todo: chnge
    version='0.1',
    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'beautifulsoup4',
        'Scrapy3'
    ],
    entry_points='''
        [console_scripts]
        authors=soup.author_scraper:scrape_authors_from_csv
        favorites=soup.favorites_scraper:scrape_favorites
        debe=soup.eksispiders:scrape_debe
        entry_scraper=eksispiders.spiders.entry_scraper:run
        entry_sampler=eksispiders.spiders.entry_sampler:run
        topic_scraper=eksispiders.spiders.topic_scraper_final:run
        author_topic_scraper=eksispiders.spiders.author_topic_scraper_final:run
        topic_entry_no=eksispiders.spiders.topic_entry_no_counter:run
        channel=eksispiders.spiders.FinishedScrapers.channel:run
        suggested_topics=eksispiders.spiders.similar_topics_scraper:run
    ''',
)
