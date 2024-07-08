# set the default gcloud project
gcloud config set project "<PROJECT_ID>"
# set the default compute zone to london
gcloud config set compute/zone europe-west2-c
# set build region to eu west
gcloud config set builds/region europe-west2

# build remotely (uses Dockerfile)
gcloud builds submit --tag europe-west2-docker.pkg.dev/"<PROJECT_ID>"/sic-soc-docker/app_test:v1 . --region=europe-west2

# deploy the image as app engine (uses app.yaml)
# gcloud app deploy --image-url=europe-west2-docker.pkg.dev/"<PROJECT_ID>"/sic-soc-docker/app_test:v1
# works on port 8080 but cannot write to the file system (problem for custom classification index)

# deploy the image as google run service
gcloud run deploy sic-soc --image europe-west2-docker.pkg.dev/"<PROJECT_ID>"/sic-soc-docker/app_test:v1 \
  --min-instances=0 --max-instances=3 --region=europe-west2 --allow-unauthenticated --memory=4G --port=8080
