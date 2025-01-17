import feedparser
import PyRSS2Gen
from datetime import datetime, timezone
import re
import logging
import xml.dom.minidom

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

    # Use the original dragonholic.com feed URL
    original_feed_url = 'https://dragonholic.com/feed/manga-chapters/'
    parsed_feed = feedparser.parse(original_feed_url)

    # 1) Define regex patterns
    link_pattern = re.compile(r'/chapter-(\d+)/?$')
    # Adjust the title pattern if needed based on the original feed's title structure
    title_pattern = re.compile(r'^(.*?)\s*[-–—]+\s*Chapter\s*(\d+)\s*[-–—]+\s*(.*)$')

    chapter_entries = []

    # 2) Extract chapter information from the original feed
    for e in parsed_feed.entries:
        print(f"\nProcessing entry:")
        print(f"Title: {e.title}")
        print(f"Link: {e.link}")
        print(f"Published: {e.published if hasattr(e, 'published') else 'No published date'}")
        print(f"GUID: {e.guid if hasattr(e, 'guid') else 'No GUID'}")

        # Implement title filtering
        if "Quick Transmigration: The Villain Is Too Pampered and Alluring" not in e.title:
            logging.info(f"Skipping entry not matching title filter: {e.title}")
            continue  # Skip entries that don't include the desired title

        link_match = link_pattern.search(e.link)
        title_match = title_pattern.match(e.title)

        if link_match and title_match:
            chapter_number_int = int(link_match.group(1))
            main_title = title_match.group(1).strip()
            # Remove leading hyphens and spaces from arc_title
            arc_title = re.sub(r'^[-–—]+\s*', '', title_match.group(3).strip())
            logging.debug(f"Matched Entry: Chapter {chapter_number_int}, Title: {main_title}, Arc: {arc_title}")
        else:
            # Detailed debugging
            if not link_match:
                logging.warning(f"Link did not match for entry: {e.link}")
            if not title_match:
                logging.warning(f"Title did not match for entry: {e.title}")
            continue  # Skip entries that don't match both patterns

        chapter_entries.append((chapter_number_int, main_title, arc_title, e))

    if not chapter_entries:
        logging.error("No valid chapters found. Exiting script.")
        return

    # 3) Debug: Print original feed order
    logging.info("Debug: Original Feed Order:")
    for i, (ch_num, _, _, _) in enumerate(chapter_entries, start=1):
        logging.info(f"  {i:2d}. Chapter {ch_num}")

    # 4) Sort chapters in descending order based on chapter number
    sorted_chapter_entries = sorted(chapter_entries, key=lambda x: x[0], reverse=True)

    # 5) Debug: Print sorted feed order
    logging.info("\nDebug: Sorted Feed Order (Descending):")
    for i, (ch_num, _, _, _) in enumerate(sorted_chapter_entries, start=1):
        logging.info(f"  {i:2d}. Chapter {ch_num}")

    # 6) Create RSS items using PyRSS2Gen
    rss_items = []
    for (chapter_num, main_title, arc_title, entry) in sorted_chapter_entries:
        logging.info(f"Adding Chapter {chapter_num} to feed")

        # Handle 'published' date
        try:
            pub_date_str = entry.published
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
        except (ValueError, AttributeError) as ex:
            logging.warning(f"Failed to parse published date for entry: {entry.title}. Error: {ex}")
            pub_date = datetime.now(timezone.utc)  # Use current time as fallback

        # Handle 'guid' and 'category'
        guid_value = entry.guid if hasattr(entry, 'guid') else entry.link
        category_value = arc_title if arc_title else 'N/A'

        # Create RSSItem
        rss_item = PyRSS2Gen.RSSItem(
            title=main_title,
            link=entry.link,
            description=f"Chapter {chapter_num}",
            guid=PyRSS2Gen.Guid(guid_value, isPermaLink=False),
            categories=[category_value],
            pubDate=pub_date
        )
        rss_items.append(rss_item)

    # 7) Create RSS feed using PyRSS2Gen
    rss = PyRSS2Gen.RSS2(
        title='Customized Feed',
        link='https://cannibal-turtle.github.io/custom-rss-feed/custom_feed.xml',
        description='A customized RSS feed with separated title, chapter number, and arc title.',
        lastBuildDate=datetime.now(timezone.utc),
        items=rss_items
    )

    # 8) Generate XML string
    rss_xml_str = rss.to_xml(encoding='utf-8')

    # 9) Pretty-print the XML using xml.dom.minidom
    dom = xml.dom.minidom.parseString(rss_xml_str)
    pretty_xml_as_string = dom.toprettyxml(indent="  ", encoding="utf-8").decode('utf-8')

    # 10) Write the pretty-printed XML to file
    output_file = 'custom_feed.xml'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)

    logging.info(f"\nSaved '{output_file}' successfully!")
    logging.info("Open it with a code editor to confirm that the first <item> is your highest chapter (e.g., 159).")

if __name__ == "__main__":
    main()
