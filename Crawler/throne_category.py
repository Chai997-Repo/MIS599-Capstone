import scrapy

class BlogSpider(scrapy.Spider):
    name = 'got_spider'
    allowed_domains = [
        "gameofthrones.fandom.com",
        "imdb.com",
        "studiobinder.com",
        "reddit.com",
        "transcripts.foreverdreaming.org"
    ]
    
    start_urls = [
        'https://gameofthrones.fandom.com/wiki/Transcripts',
        "https://www.imdb.com/title/tt1837863/quotes/",
        "https://www.studiobinder.com/blog/game-of-thrones-script-screenplay-pdf-download/",
        "https://www.reddit.com/r/asoiaf/comments/7o1uhw/spoilers_main_political_changes_in_westeros_in/",
        "http://transcripts.foreverdreaming.org/viewforum.php?f=67"
    ]

    def parse(self, response):
        self.logger.info(f"Parsing URL: {response.url}")
        
        if "fandom.com" in response.url:
            dialogues = response.css('div.dialogue::text').getall()
            characters = response.css('div.dialogue b::text').getall()
            for character, dialogue in zip(characters, dialogues):
                yield {
                    'Character': character.strip(),
                    'Dialogue': dialogue.strip()
                }

        elif "imdb.com" in response.url:
            quotes = response.css('.sodatext::text').getall()
            for quote in quotes:
                yield {
                    'Dialogue': quote.strip()
                }

        elif "studiobinder.com" in response.url:
            scripts = response.css('a::attr(href)').re(r'.*\.pdf$')
            for script in scripts:
                yield {
                    'Script Link': script.strip()
                }

        elif "reddit.com" in response.url:
            discussions = response.css('.md p::text').getall()
            for discussion in discussions:
                if discussion.strip():
                    yield {
                        'Discussions': discussion.strip()
                    }

        elif "foreverdreaming.org" in response.url:
            threads = response.css('a.topictitle::attr(href)').getall()
            for thread in threads:
                yield response.follow(thread, callback=self.parse_script)
         # Handle pagination
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Following next page: {next_page_url}")
            yield response.follow(url=next_page_url, callback=self.parse_script)

    def parse_script(self, response):
        self.logger.info(f"Parsing script page: {response.url}")
        
        lines = response.css('.postbody::text').getall()
        for line in lines:
            clean_line = line.strip()
            if clean_line:
                yield {
                    'Dialogue': clean_line
                }

        USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0 Safari/537.36'
        CONCURRENT_REQUESTS = 32
        DOWNLOAD_DELAY = 0.25
        RETRY_ENABLED = True
        RETRY_TIMES = 3
        RETRY_HTTP_CODES = [403, 404]