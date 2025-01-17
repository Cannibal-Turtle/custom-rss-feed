import feedparser
from feedgen.feed import FeedGenerator
import re

# URL of the original RSS feed
original_feed_url = 'https://siftrss.com/f/eqw6xQQQK8q'

# Fetch and parse the original feed
parsed_feed = feedparser.parse(original_feed_url)

# Initialize the new feed
fg = FeedGenerator()
fg.title('Customized Quick Transmigration Feed')
fg.link(href='https://cannibal-turtle.github.io/custom-rss-feed/custom_quick_transmigration_feed.xml', rel='self')  # Update with your GitHub Pages URL
fg.description('A customized RSS feed with separated title, chapter number, and arc title.')

# Regex pattern to extract components
# Adjusted regex to account for possible variations in title formatting
title_pattern = re.compile(r'^(.*?)\s*[-–—]\s*Chapter\s*(\d+)\s*[-–—]+\s*(.*)$')

for entry in parsed_feed.entries:
    # Apply regex to the title
    match = title_pattern.match(entry.title)
    if match:
        main_title = match.group(1).strip()
        chapter_number = match.group(2).strip()
        arc_title = match.group(3).strip()
    else:
        # Fallback if pattern doesn't match
        main_title = entry.title
        chapter_number = 'N/A'
        arc_title = 'N/A'

    # Create a new entry in the new feed
    fe = fg.add_entry()
    fe.title(main_title)
    fe.link(href=entry.link)
    fe.pubDate(entry.published)
    fe.description(f"Chapter: {chapter_number}\nArc: {arc_title}")
    # Add category using the updated method
    fe.category(term=arc_title)

# Generate the RSS feed XML
new_feed_xml = fg.rss_str(pretty=True)

# Save the new feed to a file
with open('custom_quick_transmigration_feed.xml', 'wb') as f:
    f.write(new_feed_xml)

print("New RSS feed has been generated successfully.")
