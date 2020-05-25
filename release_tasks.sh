python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable || :
python manage.py test --settings=rebalanceamento_acoes.settingsDev