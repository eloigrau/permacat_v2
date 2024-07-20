#!/bin/bash
cd /home/udjango/permacat
git pull
source /home/udjango/permacat/permacatenv37/bin/activate
pip install -r requirements_2.txt
python manage.py migrate --settings=bourseLibre.settings.production
python manage.py collectstatic --noinput --settings=bourseLibre.settings.production
python manage.py crontab add --settings=bourseLibre.settings.production
sudo systemctl restart nginx
sudo supervisorctl restart permacat_supervisor

