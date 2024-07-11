import requests
import argparse
import sys
import re
import time
import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

class HackedEmails:
    def __init__(self):
        self.api = "https://hacked-emails.com/api"

    def request(self, email):
        url = f"{self.api}?q={email}"
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()

class HIBP:
    def __init__(self):
        self.headers = {'User-Agent': 'Pastepwnd-Compromise-Check', 'api-version': '2'}

    def request(self, url):
        r = requests.get(url, headers=self.headers)
        if "Retry-After" in r.headers:
            print(f"Sleeping for {r.headers['Retry-After']}s to avoid HIBP lockout.")
            time.sleep(int(r.headers["Retry-After"])) # sleep to avoid HTTP 429/Rate Limiting
            r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            return r.json()

    def paste(self, email):
        return f"https://haveibeenpwned.com/api/v2/pasteaccount/{email}"

    def breach(self, domain):
        return f"https://haveibeenpwned.com/api/v2/breaches?domain={domain}"

class Workbench:
    def __init__(self):
        self.cachedurl = "https://webcache.googleusercontent.com/search?q=cache:"

    def format_paste(self, entity, email): # hibp paste      
        title = entity["Title"]
        date = entity["Date"]
        Id = entity["Id"]
        urls = []
        if len(Id) == 8: # pastebin ID
            pastebin = self.create_pastebinurl(Id)
            urls.append(f"<a href='{pastebin}' target='_blank'>Pastebin</a>")
            urls.append(f"<a href='{self.cachedurl}{pastebin}' target='_blank'>Cached View</a>")
        else: # Id is a real URL
            urls.append(f"<a href='{Id}' target='_blank'>Source</a>")
            urls.append(f"<a href='{self.cachedurl}{Id}' target='_blank'>Cached View</a>")

        return [title, email, date, urls]

    def format_breach(self, entity, domain): # hibp breach
        title = entity["Title"]
        date = entity["BreachDate"]
        desc = entity["Description"]
        pwncount = entity["PwnCount"]
        sensitive = entity["IsSensitive"]

        return [title, domain, date, desc, pwncount, sensitive]

    def format_hackedemail(self, breach, email):
        title = breach["title"]
        date = breach["date_created"]
        url = breach["source_url"]
        urls = []
        if url != "#":
            urls.append(f"<a href='{url}' target='_blank'>Source</a>")
            urls.append(f"<a href='{self.cachedurl}{url}' target='_blank'>Cached View</a>")

        return [title, email, date, urls]

    def create_pastebinurl(self, Id):
        return f"https://pastebin.com/raw.php?i={Id}"

class Output:
    def __init__(self):
        pass

    def create_webpage(self, results):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pastepwnd</title>
            <style type="text/css">
                body { font-family: 'Helvetica Neue',Arial, Helvetica,sans-serif; background-color: #eee;}
                table {
                    background-color: #1d1f21;
                    border: 1px solid rgba(34,36,38,.15);
                    border-radius: 2px;
                    color: #fff;
                    text-align: left;
                    border-collapse: collapse;
                    font-size: 12px;
                    margin-bottom: 10px;}
                th, td {padding: 5px; border-bottom: 1px solid #ddd;}
                th {background-color: #f0b128; color: #fff;}
                tr:hover {background-color: #303336;}
                td {border-color: inherit; vertical-align: middle;}
                a {color: #f5ca6f;}
                hr {border-top: 1px solid #636c72 margin: 1.5rem 0};
            </style>
        </head>
        <body>
        <h2>Pastepwnd Breach Detector</h2>
        """

        html+= results
        html += "</body></html>"
        return html

    def create_domain_table(self, results):
        table = """
        <h4>Breaches by Site</h4>
        <table>
        <thead>
        <tr>
        <th>#</th>
        <th>Title</th>
        <th>Target</th>
        <th>Date</th>
        <th>Description</th>
        <th>Compromised Accounts</th>
        <th>Sensitive</th>
        </tr>
        </thead>
        <tbody>
        """
        for key, record in enumerate(results):
            table += f"<tr><td>{key}</td><td>{record[0]}</td><td>{record[1]}</td><td>{record[2]}</td><td>{record[3]}</td><td>{record[4]}</td><td>{record[5]}</td></tr>"
        table += "</tbody></table>"
        return table

    def create_email_table(self, results):
        table = """
        <h4>Breaches by Email</h4>
        <table>
        <thead>
        <tr>
        <th>#</th>
        <th>Title</th>
        <th>Email</th>
        <th>Date</th>
        <th>URLs</th>
        </tr>
        </thead>
        <tbody>
        """
        for key, record in enumerate(results):
            table += f"<tr><td>{key}</td><td>{record[0]}</td><td>{record[1]}</td><td>{record[2]}</td><td>{' | '.join(record[3])}</td></tr>"
        table += "</tbody></table>"
        return table

    def write_file(self, html):
        with open("pastepwnd.html" , "w") as f:
            f.write(html)
        return os.path.abspath("pastepwnd.html")

def main():
    # Telegram bot token (replace with your actual bot token)
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # Command handler for starting the bot
    def start(update: Update, context: CallbackContext) -> None:
        update.message.reply_text("Welcome to Pastepwnd Bot! Send me an email address or domain to check for compromises.")

    # Handler for text messages (email or domain)
    def check_compromise(update: Update, context: CallbackContext) -> None:
        text = update.message.text.strip()

        if re.match(r"[^@]+@[^@]+\.[^@]+", text):  # Check if text is an email
            hibp = HIBP()
            he = HackedEmails()
            workbench = Workbench()
            output = Output()
            results = []

            response = hibp.request(hibp.paste(text))  # hibp request
            if response:
                for entity in response:
                    results.append(workbench.format_paste(entity, text))

            he_response = he.request(text)  # hacked-email.com request
            if he_response:
                for breach in he_response["data"]:
                    results.append(workbench.format_hackedemail(breach, text))

            if results:
                html_result = output.create_email_table(results)
                file_path = output.write_file(output.create_webpage(html_result))

                update.message.reply_text(f"Compromises found for {text}:\nHTML results saved to {file_path}.", parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text(f"No compromises found for {text}.")
        else:
            update.message.reply_text("Invalid input. Please provide a valid email address.")

    # Add command handlers to dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, check_compromise))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
