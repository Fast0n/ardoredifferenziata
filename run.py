import json
import logging
import time
from datetime import date, timedelta

import holidays
import requests
import schedule
from pid.decorator import pidfile
from telegram.ext import Updater

from settings import CHAT_ID, TOKEN, bin_, location, type_, url_api

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def job(bot, addDayDebug=0):
    # get present day and add one day
    EndDate = date.today() + timedelta(days=2 + addDayDebug)

    it_holidays = holidays.country_holidays('IT', subdiv='RC')

    if EndDate.weekday() != 0 and not EndDate in it_holidays:
        waste = ''
        response_api = requests.request(
            "GET",
            url_api,
            data=url_api,
        )
        data = json.loads(response_api.text)
        # create the message to be sent on Telegram
        for a in range(len(data["data"])):
            for b in range(len(data["data"][a])):
                if b == EndDate.weekday() and data["data"][a][b + 1] != "":
                    waste += f"*{type_[str(data['data'][a][1]).replace('*', '').capitalize()]}*{bin_[str(data['data'][a][1]).replace('*', '').capitalize()]}\n"

        link_waste = 'https://i.postimg.cc/13X6VZj1/DIFFERENZIATA2.jpg'
        message = f"*Buonasera { location.replace('-', ' ').capitalize()} 🌆*\n*E' arrivato il momento di portare fuori:*\n\n{waste}_Esporre entro le ore 01:00 del giorno di raccolta\nFonte: [Comune di Ardore]({link_waste})_"
        bot.send_photo(chat_id=CHAT_ID, caption=message,
                       parse_mode="MarkdownV2", photo=open('DIFFERENZIATA2.jpg', 'rb'))

        # print actualy date
        print(str(date.today()))
        return


@ pidfile(pidname='/tmp/ArdoreDifferenziata.pid')
def main():
    print("--- Starting ArdoreDifferenziata ---")
    # Setup bot
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    schedule.every().day.at("21:00").do(dispatcher.run_async(job, updater.bot))

    while True:
        schedule.run_pending()
        time.sleep(30)  # wait 30 seconds


if __name__ == "__main__":
    main()
