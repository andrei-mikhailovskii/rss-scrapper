# You shouldn't change the name of functions or their arguments
# but you can change the content of the initial functions.
from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import xml.etree.ElementTree as ET
import json


class UnhandledException(Exception):
    pass


def parse_channel(channel_elem):
    channel_data = {
        "title": channel_elem.find("title").text,
        "link": channel_elem.find("link").text,
        "description": channel_elem.find("description").text,
        "lastBuildDate":
            channel_elem.find("lastBuildDate").text if channel_elem.find("lastBuildDate") is not None else "",
        "pubDate": channel_elem.find("pubDate").text if channel_elem.find("pubDate") is not None else "",
        "language": channel_elem.find("language").text if channel_elem.find("language") is not None else "",
        "managingEditor":
            channel_elem.find("managingEditor").text if channel_elem.find("managingEditor") is not None else "",
        "categories": [category.text for category in channel_elem.findall("category")],
    }
    return channel_data


def parse_item(item_elem):
    item_data = {
        "title": item_elem.find("title").text if item_elem.find("title") is not None else "",
        "author": item_elem.find("author").text if item_elem.find("author") is not None else "",
        "pubDate": item_elem.find("pubDate").text if item_elem.find("pubDate") is not None else "",
        "link": item_elem.find("link").text if item_elem.find("link") is not None else "",
        "category": item_elem.find("category").text if item_elem.find("category") is not None else "",
        "description": item_elem.find("description").text if item_elem.find("description") is not None else "",
    }
    return item_data


def rss_parser(xml: str, limit: Optional[int] = None, json: bool = False) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json_output: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to a file as separate lines.
    """
    root = ET.fromstring(xml)
    channel_elem = root.find(".//channel")
    item_elems = root.findall(".//item")

    channel_data = parse_channel(channel_elem)

    items_data = [parse_item(item_elem) for item_elem in item_elems]

    if limit is not None:
        items_data = items_data[:limit]

    result = []

    # Format for console output
    result.append(f"Feed: {channel_data['title']}")
    result.append(f"Link: {channel_data['link']}")
    result.append(f"Description: {channel_data['description']}")
    result.append("")

    for key in ["lastBuildDate", "pubDate", "language", "managingEditor"]:
        result.append(f"{key.capitalize()}: {channel_data[key]}")

    if channel_data["categories"]:
        result.append(f"Categories: {', '.join(channel_data['categories'])}")

    result.append("")

    for item_data in items_data:
        result.append(f"Title: {item_data['title']}")
        result.append(f"Author: {item_data['author']}")
        result.append(f"Published: {item_data['pubDate']}")
        result.append(f"Link: {item_data['link']}")
        result.append(f"Category: {item_data['category']}")
        result.append("")
        result.append(item_data['description'])
        result.append("")

    if json:
        # Format for JSON output
        rss_json = {
            "title": channel_data["title"],
            "link": channel_data["link"],
            "description": channel_data["description"],
            "items": items_data,
        }
        return [json.dumps(rss_json, indent=2)]

    return result


def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)

    if args.source is None:
        print("Error: Please provide an RSS URL.")
        return 1

    xml = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()

