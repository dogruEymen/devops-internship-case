# RUNBOOK

Bu doküman FastAPI DevOps Case projesi için temel operasyon adımlarını açıklar: yeniden başlatma, geri alma ve log inceleme.

## Kapsam

Uygulama üç farklı şekilde çalıştırılabilir:

- Lokal Python: `uvicorn`
- Lokal stack: Docker Compose ile FastAPI, Prometheus ve Grafana
- Kubernetes: Helm chart ve Argo CD ile GitOps deployment

## Hızlı Sağlık Kontrolü

Lokal uygulama:

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
curl http://127.0.0.1:8000/version
```

Kubernetes port-forward sonrası:

```bash
kubectl port-forward svc/fastapi-dev-service 8080:80
curl http://127.0.0.1:8080/healthz
```

Pod ve rollout durumu:

```bash
kubectl get pods
kubectl get deploy
kubectl rollout status deployment/fastapi-dev-deployment
```

## Restart / Yeniden Başlatma

### Lokal Python

Terminalde çalışan `uvicorn` sürecini durdur:

```bash
CTRL+C
```

Tekrar başlat:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Compose

Sadece FastAPI servisini yeniden başlat:

```bash
cd backend
docker compose restart fastapi-backend
```

Tüm stack'i yeniden başlat:

```bash
cd backend
docker compose down
docker compose up --build
```

Prometheus veya Grafana için:

```bash
cd backend
docker compose restart prometheus
docker compose restart grafana
```

### Kubernetes / Helm

Deployment rollout restart:

```bash
kubectl rollout restart deployment/fastapi-dev-deployment
kubectl rollout status deployment/fastapi-dev-deployment
```

Prod release için release adına göre:

```bash
kubectl rollout restart deployment/fastapi-prod-deployment
kubectl rollout status deployment/fastapi-prod-deployment
```

Helm values değişikliği sonrası upgrade:

```bash
helm upgrade fastapi-dev ./fastapi-chart -f fastapi-chart/values-dev.yaml
```

### Argo CD

Argo CD Application sync:

```bash
argocd app sync fastapi-backend
argocd app wait fastapi-backend
```

CLI yoksa Kubernetes üzerinden Application durumunu kontrol et:

```bash
kubectl get application fastapi-backend -n argocd
kubectl describe application fastapi-backend -n argocd
```

## Rollback / Geri Alma

### Docker Compose

Compose ortamında rollback için önceki çalışan image tag'i ile tekrar çalıştır:

```bash
cd backend
docker compose down
docker image ls fastapi-backend
docker run --rm -p 8000:8000 fastapi-backend:<onceki-tag>
```

Compose dosyasında sabit image tag kullanılmaya başlanırsa ilgili tag'e dönüp stack'i tekrar başlat:

```bash
cd backend
docker compose up --build
```

### Helm

Release geçmişini görüntüle:

```bash
helm history fastapi-dev
```

Önceki revision'a dön:

```bash
helm rollback fastapi-dev <revision>
helm status fastapi-dev
```

Prod release için:

```bash
helm history fastapi-prod
helm rollback fastapi-prod <revision>
helm status fastapi-prod
```

### Kubernetes Rollout

Deployment rollout geçmişi:

```bash
kubectl rollout history deployment/fastapi-dev-deployment
```

Bir önceki ReplicaSet'e dön:

```bash
kubectl rollout undo deployment/fastapi-dev-deployment
kubectl rollout status deployment/fastapi-dev-deployment
```

Belirli revision'a dön:

```bash
kubectl rollout undo deployment/fastapi-dev-deployment --to-revision=<revision>
```

### Argo CD / GitOps

GitOps yaklaşımında kalıcı rollback için repository'de çalışan son iyi commit veya image tag'e geri dönülür.

1. Son çalışan image tag veya Helm values değişikliğini belirle.
2. `fastapi-chart/values-prod.yaml` içindeki `image.tag` değerini önceki çalışan tag'e al.
3. Değişikliği commit ve push et.
4. Argo CD sync bekle veya manuel sync çalıştır:

```bash
argocd app sync fastapi-backend
argocd app wait fastapi-backend
```

Kısa süreli acil geri dönüş için Kubernetes rollout undo kullanılabilir, fakat Argo CD self-heal açık olduğu için Git'teki hedef durum değişmezse Argo CD cluster'ı tekrar Git'teki versiyona çekebilir.

## Logs / Log Bakma

### Lokal Python

`uvicorn` logları uygulamanın çalıştığı terminalde görünür.

### Docker Compose

FastAPI logları:

```bash
cd backend
docker compose logs -f fastapi-backend
```

Prometheus logları:

```bash
cd backend
docker compose logs -f prometheus
```

Grafana logları:

```bash
cd backend
docker compose logs -f grafana
```

Son satırları görmek için:

```bash
cd backend
docker compose logs --tail=100 fastapi-backend
```

### Kubernetes

Pod listesini al:

```bash
kubectl get pods -l app=fastapi-dev-fastapi
```

Deployment üzerinden log takip et:

```bash
kubectl logs -f deployment/fastapi-dev-deployment
```

Önceki container restart logları:

```bash
kubectl logs deployment/fastapi-dev-deployment --previous
```

Pod event ve probe hatalarını incele:

```bash
kubectl describe deployment fastapi-dev-deployment
kubectl describe pod <pod-name>
```

Ingress ve Service kontrolü:

```bash
kubectl get ingress
kubectl describe ingress fastapi-dev-ingress
kubectl get svc
kubectl describe svc fastapi-dev-service
```

### Argo CD

Application durumu:

```bash
argocd app get fastapi-backend
argocd app history fastapi-backend
```

Kubernetes üzerinden:

```bash
kubectl describe application fastapi-backend -n argocd
```

## Incident Sonrası Kontrol Listesi

- `/healthz` ve `/readyz` başarılı mı?
- Pod'lar `Running` ve `Ready` durumda mı?
- Rollout tamamlandı mı?
- Prometheus `/metrics` endpoint'ini scrape ediyor mu?
- Grafana dashboard veya alarmlarda hata devam ediyor mu?
- Değişiklik Git ve Helm values tarafında doğru state'e sahip mi?
