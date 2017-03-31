# ./new_instance.sh PROJ_NAME ORG_NAME PORT
echo "starting $1 for $2 on localhost:$3"
mkdir -p containers
rm -r containers/$1
cp -r template containers/$1
cd containers/$1
rm .env
rm -r venv
touch .env
echo "ORG_NAME=$2" >> .env
echo "COMPOSE_PROJECT_NAME=$1" >> .env
echo "EXTERNAL_PORT=$3" >> .env

# unfinished config stuff
echo "MAIL_USERNAME=hack4impact-sendgrid" >> .env
echo "MAIL_PASSWORD=$MAIL_PASSWORD" >> .env
echo "ADMIN_EMAIL=contact@hack4impact.org" >> .env
echo "ADMIN_PASSWORD=password" >> .env
echo "SECRET_KEY=$4" >> .env

docker-compose rm web db redis
docker-compose up -d
