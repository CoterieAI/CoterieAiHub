export EMAIL_HOST="smtp.sendgrid.net"
export EMAIL_HOST_USER="apikey"
export EMAIL_HOST_PASSWORD="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"
export EMAIL_PORT="587"
export FROM_EMAIL="ogunwedeemmanuel@gmail.com"
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export JWT_SECRET="3facc3d340090665088c0507c8272f6309f98c97ab3e2e0c"
export KAFKA_API_URL="35.202.207.9:15012"
export PROJECT_ID="coterieai-project"
export ZONE="us-central1-c"
export CLUSTER_ID="coterie-dev-cluster"
export MYSQL_CLOUD_INSTANCE="coterieai-project:us-central1:coterie"
export GOOGLE_APPLICATION_CREDENTIALS="./credentials/coterieai-pnoroject-2dbda6f3219a.json"
# export DB_NAME="django_db"
# export DB_USER="root"
# export DB_PASSWORD="12345678"
#chmod +x ./cloud_sql_proxy.exe
#./cloud_sql_proxy -instances=coterieai-project:us-central1:cote=tcp:3307 -credential_file="./credentials/coterieai-project-2dbda6f3219a.json"

# chmod +x ./cloud_sql_proxy

# mkdir -p cloudsql

# ./cloud_sql_proxy -instances=$MYSQL_CLOUD_INSTANCE=tcp:3306 -credential_file=$GOOGLE_APPLICATION_CREDENTIALS  &

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
