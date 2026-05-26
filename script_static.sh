#!/bin/bash
cd /home/udjango/permacat
git pull
source /home/udjango/permacat/permacatenv39/bin/activate
source .env_variables
python manage.py collectstatic -c --noinput --settings=bourseLibre.settings.production > /home/udjango/logs/log_collecstatic.log
sudo systemctl restart nginx
sudo supervisorctl restart permacat_supervisor

