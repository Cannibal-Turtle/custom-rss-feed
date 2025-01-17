import feedparser
from feedgen.feed import FeedGenerator
import re

original_feed_url = 'https://siftrss.com/f/eqw6xQQQK8q'
parsed_feed = feedparser.parse(original_feed_url)

# 1) Build a list of (chapter_number_int, main_title, arc_title, entry)
chapter_entries = []
title_pattern = re.compile(r'^(.*?)\s*-\s*Chapter\s*(\d+)\s*-\s*-\s*(.*)$')

for e in parsed_feed.entries:
    match = title_pattern.match(e.title)
    if match:
        main_title = match.group(1).strip()
        chapter_number_str = match.group(2).strip()
        arc_title = match.group(3).strip()
        try:
            chapter_number_int = int(chapter_number_str)
        except ValueError:
            chapter_number_int = 0
    else:
        main_title = e.title
        chapter_number_int = 0
        arc_title = 'N/A'
    
    # Add to our chapter_entries list
    chapter_entries.append((chapter_number_int, main_title, arc_title, e))

# 2) Debug print the original feed order for reference
print("Debug: Original Feed Entries:")
for i, e in enumerate(parsed_feed.entries):
    print(f"  Entry {i+1}: title='{e.title}'")
    if hasattr(e, 'published_parsed') and e.published_parsed:
        print("    published_parsed:", e.published_parsed)
    else:
        print("    NO valid published_parsed!")

# 3) Sort chapter_entries by chapter_number_int descending
chapter_entries.sort(key=lambda x: x[0], reverse=True)

# 4) Build the feed in sorted order
fg = FeedGenerator()
fg.title('Customized Quick Transmigration Feed')
fg.link(href='https://cannibal-turtle.github.io/custom-rss-feed/custom_quick_transmigration_feed.xml', rel='self')
fg.description('A customized RSS feed with separated title, chapter number, and arc title.')

for (chapter_num, main_title, arc_title, entry) in chapter_entries:
    fe = fg.add_entry()
    fe.title(main_title)
    # Put chapter + arc in separate fields or in description
    fe.description(f"Chapter: {chapter_num}")
    fe.category(term=arc_title)  # feedgen >= 1.0.0 uses fe.category()
    fe.link(href=entry.link)

    # If published date is valid, set it
    if hasattr(entry, 'published'):
        fe.pubDate(entry.published)

# 5) Write out the RSS file
new_feed_xml = fg.rss_str(pretty=True)
with open('custom_quick_transmigration_feed.xml', 'wb') as f:
    f.write(new_feed_xml)

print("\nNew RSS feed generated, sorted by descending chapter number, saved to custom_quick_transmigration_feed.xml.")
