# FastAPI DevOps Case

Bu proje, FastAPI ile yazılmış basit bir backend servisinin test, container, gözlemlenebilirlik, CI/CD ve Kubernetes dağıtım adımlarını gösteren bir DevOps case çalışmasıdır.

## İçerik

- `backend/`: FastAPI uygulaması, testler, Dockerfile, Docker Compose ve Prometheus konfigürasyonu
- `fastapi-chart/`: Uygulamanın Kubernetes üzerinde çalışması için Helm chart
- `.github/workflows/`: Pull request ve `main` branch push akışları için GitHub Actions pipeline dosyaları

## Uygulama Özeti

FastAPI uygulaması [backend/app/main.py](backend/app/main.py) içinde tanımlıdır. Servis aşağıdaki endpoint'leri sunar:

| Endpoint       | Açıklama                                          |
| -------------- | ------------------------------------------------- |
| `GET /ping`    | Basit canlılık kontrolü için `"pong"` döner.      |
| `GET /healthz` | Liveness probe için `{"status": "OK"}` döner.     |
| `GET /readyz`  | Readiness probe için `{"status": "READY"}` döner. |
| `GET /version` | Uygulama versiyonunu döner.                       |
| `GET /metrics` | Prometheus metriklerini yayınlar.                 |

Prometheus metrikleri `prometheus-fastapi-instrumentator` ile otomatik olarak expose edilir.

## Gereksinimler

- Python 3.12+
- Docker ve Docker Compose
- Helm 3
- Kubernetes ortamı, örnek olarak Minikube, Kind veya mevcut bir cluster

## Lokal Kurulum

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Uygulama varsayılan olarak `http://127.0.0.1:8000` adresinde çalışır.

Örnek kontrol:

```bash
curl http://127.0.0.1:8000/ping
curl http://127.0.0.1:8000/healthz
```

## Test

```bash
cd backend
pytest -q
```

Testler [backend/tests/test_main.py](backend/tests/test_main.py) içinde endpoint davranışlarını doğrular.

## Docker ile Çalıştırma

Backend imajını build etmek için:

```bash
docker build -t fastapi-backend:latest ./backend
```

Container olarak çalıştırmak için:

```bash
docker run --rm -p 8000:8000 fastapi-backend:latest
```

## Docker Compose ile Gözlemlenebilirlik

Compose dosyası backend, Prometheus ve Grafana servislerini birlikte ayağa kaldırır:

```bash
cd backend
docker compose up --build
```

Servis adresleri:

- FastAPI: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Prometheus, [backend/prometheus.yaml](backend/prometheus.yaml) içindeki ayara göre backend servisinin `/metrics` endpoint'ini scrape eder.

## Helm ile Kubernetes Dağıtımı

Chart dizini [fastapi-chart](fastapi-chart) altındadır. Geliştirme değerleriyle kurulum:

```bash
helm install fastapi-dev ./fastapi-chart -f fastapi-chart/values-dev.yaml
```

Prod benzeri değerlerle kurulum:

```bash
helm install fastapi-prod ./fastapi-chart -f fastapi-chart/values-prod.yaml
```

Güncelleme için:

```bash
helm upgrade fastapi-dev ./fastapi-chart -f fastapi-chart/values-dev.yaml
```

Kaldırmak için:

```bash
helm uninstall fastapi-dev
```

Chart; `Deployment`, `Service` ve isteğe bağlı `Ingress` kaynaklarını üretir. Liveness ve readiness probe ayarları values dosyalarından yönetilir.

## CI/CD

Proje iki GitHub Actions workflow'u içerir:

- [`.github/workflows/pr.yaml`](.github/workflows/pr.yaml): Pull request açıldığında lint, test, secret scan, Docker build ve Trivy image scan çalıştırır.
- [`.github/workflows/merge.yaml`](.github/workflows/merge.yaml): `main` branch'e push veya `v*` tag push edildiğinde lint, test, secret scan, Docker build, Trivy scan ve GHCR push adımlarını çalıştırır.

Pipeline adımları genel olarak şunları kapsar:

1. Python 3.12 kurulumu
2. Bağımlılıkların yüklenmesi
3. Ruff lint kontrolü
4. Pytest testleri
5. GitLeaks secret taraması
6. Docker image build
7. Trivy güvenlik taraması
8. Merge workflow'unda GHCR'a image push

## Proje Yapısı

```text
.
├── .github/
│   └── workflows/
│       ├── merge.yaml
│       └── pr.yaml
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── tests/
│   │   └── test_main.py
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── README.md
│   ├── docker-compose.yaml
│   ├── prometheus.yaml
│   └── requirements.txt
├── fastapi-chart/
│   ├── templates/
│   │   ├── Deployment.yaml
│   │   ├── Ingress.yaml
│   │   └── Service.yaml
│   ├── Chart.yaml
│   ├── values-dev.yaml
│   └── values-prod.yaml
├── .gitignore
└── README.md
```
