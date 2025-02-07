#!/bin/bash
source /var/www/triumf/venv/bin/activate
python /var/www/triumf/api/bot/bot.py

# chmod +x /var/www/triumf/api/bot/bot.py
# chmod +x /var/www/triumf/run_bot.sh
# crontab -e
# 0 0 * * 0 /var/www/triumf/run_bot.sh  # run every Sunday at midnight