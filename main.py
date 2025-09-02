from download_leaderboard_exports import download_leaderboard_exports
from process_leaderboard import process_leaderboard

if __name__ == "__main__":
    urls = [
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-1-8-eg4lmf/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-2-8-HQ2TOo/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-3-8-RlWFKF/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-4-8-JXwQbn/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-5-8-YCJzg4/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-6-8-kpRQ7X/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-7-8-0hdute/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-8-8-AlorJX/leaderboard"
    ]
    #download_leaderboard_exports(urls)
    process_leaderboard()
