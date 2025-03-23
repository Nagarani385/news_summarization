def save_report(articles, filename="news_report.txt"):
    """
    Saves extracted articles to a text file, including title, summary, URL, date/time, and sentiment.

    Args:
        articles (list): A list of dictionaries containing article details (title, summary, URL, date/time, and sentiment).
        filename (str, optional): The name of the file where the report will be saved. Defaults to "news_report.txt".

    Returns:
        None
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for article in articles:
                f.write(f"Title: {article['title']}\n")
                f.write(f"Summary: {article['summary']}\n")
                f.write(f"URL: {article['url']}\n")
                f.write(f"Date and Time: {article['date_time']}\n")
                f.write(f"Sentiment: {article['sentiment']}\n")
                f.write("-" * 80 + "\n")

        print(f"Report successfully saved to {filename}")

    except Exception as e:
        print(f"Error while saving report to {filename}: {e}")


def save_final_report(combined_summary, file_name="final_summary.txt"):
    """
    Saves the final combined summary of all articles to a text file.

    Args:
        combined_summary (str): The combined summary of all extracted articles.
        file_name (str, optional): The name of the file where the final summary will be saved. Defaults to "final_summary.txt".

    Returns:
        None
    """
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("Combined Summary ===\n")
            f.write(combined_summary + "\n")

        print(f"Final summary successfully saved to {file_name}")

    except Exception as e:
        print(f"Error while saving final summary to {file_name}: {e}")
