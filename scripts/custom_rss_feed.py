import feedparser
from feedgen.feed import FeedGenerator
import re

def main():
    original_feed_url = 'https://siftrss.com/f/eqw6xQQQK8q'
    parsed_feed = feedparser.parse(original_feed_url)

    # 1) Build a list of (chapter_number_int, main_title, arc_title, entry).
    #    This regex matches strings like:
    #         "Quick Transmigration... - Chapter 158 - - The Disfigured..."
    #    If your feed's title format changes, adjust the regex accordingly.
    title_pattern = re.compile(r'^(.*?)\s*-\s*Chapter\s*(\d+)\s*-\s*-\s*(.*)$')
    chapter_entries = []

    for e in parsed_feed.entries:
        match = title_pattern.match(e.title)
        if match:
            main_title         = match.group(1).strip()
            chapter_number_str = match.group(2).strip()
            arc_title         = match.group(3).strip()
            try:
                chapter_number_int = int(chapter_number_str)
            except ValueError:
                chapter_number_int = 0
        else:
            # If the regex doesn't match, just store chapter=0 and arc=N/A
            main_title         = e.title
            chapter_number_int = 0
            arc_title          = 'N/A'
            # Uncomment to see which titles fail to match:
            # print("NO MATCH:", e.title)

        chapter_entries.append((chapter_number_int, main_title, arc_title, e))

    # 2) Debug print the original feed order (as parsed).
    print("Debug: Original Feed (as parsed by feedparser):")
    for i, item in enumerate(parsed_feed.entries, start=1):
        print(f"  {i:2d}. {item.title}")

    # 3) Sort by chapter_number_int descending (so highest = first).
    chapter_entries.sort(key=lambda x: x[0], reverse=True)

    print("\nDebug: After sorting by descending chapter_number_int:")
    for ch_num, t_main, t_arc, entry_obj in chapter_entries:
        print(f"  Chapter {ch_num} => {t_main}")

    # 4) Create the feed generator.
    fg = FeedGenerator()
    fg.title('Customized Quick Transmigration Feed')
    fg.link(href='https://cannibal-turtle.github.io/custom-rss-feed/custom_quick_transmigration_feed.xml', rel='self')
    fg.description('A customized RSS feed with separated title, chapter number, and arc title.')

    # 5) Add items in the sorted order (largest chapter first => top of XML).
    for (chapter_num, main_title, arc_title, entry) in chapter_entries:
        fe = fg.add_entry()
        fe.title(main_title)
        fe.description(f"Chapter {chapter_num}")
        fe.category(term=arc_title)
        fe.link(href=entry.link)
        if hasattr(entry, 'published'):
            fe.pubDate(entry.published)

    # 6) Write out the RSS file.
    new_feed_xml = fg.rss_str(pretty=True)
    with open('custom_quick_transmigration_feed.xml', 'wb') as f:
        f.write(new_feed_xml)

    print("\nSaved 'custom_quick_transmigration_feed.xml'!")
    print("Open it with Notepad / VS Code (not WordPad) to confirm that")
    print("the FIRST <item> is your highest chapter (e.g., 158).")

if __name__ == "__main__":
    main()
