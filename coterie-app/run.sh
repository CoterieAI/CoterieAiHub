export EMAIL_HOST="smtp.sendgrid.net"
export EMAIL_HOST_USER="apikey"
export EMAIL_HOST_PASSWORD="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"
export EMAIL_PORT="587"
export FROM_EMAIL="ogunwedeemmanuel@gmail.com"
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export JWT_SECRET="3facc3d340090665088c0507c8272f6309f98c97ab3e2e0c"
export KAFKA_API_URL="https://coterieai-producer-main-zl7x2jvd3a-uc.a.run.app"
export PROJECT_ID="coterieai-project"
export ZONE="us-central1-c"
export CLUSTER_ID="clust"
export MYSQL_CLOUD_INSTANCE="coterieai-project:us-central1:cote"
export GOOGLE_APPLICATION_CREDENTIALS="./credentials/coterieai-project-2dbda6f3219a.json"

#chmod +x ./cloud_sql_proxy.exe
#./cloud_sql_proxy -instances=coterieai-project:us-central1:cote=tcp:3307 -credential_file="./credentials/coterieai-project-2dbda6f3219a.json"

chmod +x ./cloud_sql_proxy.exe
./cloud_sql_proxy.exe -instances=$MYSQL_CLOUD_INSTANCE=tcp:3306 -credential_file=$GOOGLE_APPLICATION_CREDENTIALS  &

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000