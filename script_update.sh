#!/bin/bash
cd /home/udjango/permacat
git pull
source /home/udjango/permacat/permacatenv39/bin/activate
source .env_variables
pip install -r requirements.txt
python manage.py migrate --settings=bourseLibre.settings.production
python manage.py collectstatic --noinput --settings=bourseLibre.settings.production > /home/udjango/logs/log_collecstatic.log
python manage.py crontab add --settings=bourseLibre.settings.production
sudo systemctl restart nginx
sudo supervisorctl restart permacat_supervisor

