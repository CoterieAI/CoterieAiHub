gcloud iam service-accounts add-iam-policy-binding --role roles/iam.workloadIdentityUser --member "serviceAccount:****-****.svc.id.goog[default/coterieai]" *****@***-project.iam.gserviceaccount.com

kubectl create secret generic -n **** db-secret --from-literal=username=*** --from-literal=password=*** --from-literal=database=***

kubectl create secret generic -n *** django-secret --from-literal=username=**** --from-literal=password=**** --from-literal=database=***

kubectl annotate serviceaccount *** iam.gke.io/gcp-service-account=****@****-***.iam.gserviceaccount.com -n ***

kubectl create secret generic cloudsql-oauth-credentials --from-file=credentials.json=<path/to/serviceaccountKey.json>

