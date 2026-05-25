# SECURITY

Bu doküman FastAPI DevOps Case projesi için temel güvenlik notlarını ve secret rotation adımlarını açıklar.

## Güvenlik Yaklaşımı

- Secret değerleri repository'ye commit edilmez.
- `.env` ve `.env.*` dosyaları `.gitignore` ile ignore edilir.
- CI pipeline içinde GitLeaks secret scan çalışır.
- Docker image Trivy ile HIGH ve CRITICAL seviyede taranır.
- Container root olmayan `appuser` kullanıcısı ile çalışır.
- Runtime uygulama şu an zorunlu bir secret veya `.env` dosyası okumaz.

## Mevcut Secret Durumu

Uygulamanın mevcut halinde backend runtime için zorunlu bir secret yoktur.

Kullanılan hassas değerler ve kimlik bilgileri ağırlıklı olarak platform seviyesindedir:

- `GITHUB_TOKEN`: GitHub Actions tarafından sağlanır.
- GHCR yetkileri: GitHub Actions token izinleriyle kullanılır.
- İleride eklenecek API key, database password veya webhook token değerleri GitHub Actions Secrets, Kubernetes Secret veya harici secret manager üzerinden yönetilmelidir.

## Secret Rotation / Sır Rotasyonu

Secret rotasyonu için genel sıra:

1. Rotasyonu yapılacak secret'ı ve kullanım yerlerini belirle.
2. Yeni secret değerini üret.
3. Yeni değeri ilgili secret store'a ekle.
4. Uygulamayı yeni secret ile yeniden başlat veya rollout et.
5. Sağlık kontrollerini ve logları doğrula.
6. Eski secret değerini iptal et veya sil.
7. Değişikliği ve zamanı kayıt altına al.

## GitHub Actions Secret Rotation

Repository secrets GitHub UI üzerinden güncellenebilir:

```text
Repository -> Settings -> Secrets and variables -> Actions
```

Adımlar:

1. Yeni secret değerini oluştur.
2. İlgili repository secret değerini güncelle.
3. CI/CD workflow'u manuel veya yeni commit ile tetikle.
4. Workflow'un başarılı bittiğini doğrula.
5. Eski token veya credential değerini provider tarafında revoke et.

GitHub CLI kullanılıyorsa:

```bash
gh secret set SECRET_NAME
```

Kontrol:

```bash
gh secret list
```

## Kubernetes Secret Rotation

Bu projede mevcut Helm chart içinde Kubernetes Secret template'i yoktur. İleride secret ihtiyacı eklenirse secret değerleri manifest içine düz metin olarak yazılmamalıdır.

Manuel Kubernetes Secret güncelleme örneği:

```bash
kubectl create secret generic fastapi-secret \
  --from-literal=API_KEY=<new-secret-value> \
  --dry-run=client -o yaml | kubectl apply -f -
```

Deployment yeni secret değerini alsın diye rollout restart:

```bash
kubectl rollout restart deployment/fastapi-dev-deployment
kubectl rollout status deployment/fastapi-dev-deployment
```

Doğrulama:

```bash
kubectl get secret fastapi-secret
kubectl logs -f deployment/fastapi-dev-deployment
curl http://127.0.0.1:8080/healthz
```

Eski secret değeri artık kullanılmıyorsa provider tarafında revoke edilir.

## Docker Compose Secret Rotation

Compose ortamında secret `.env` dosyası ile yönetilecekse:

1. `backend/.env` dosyasındaki değeri güncelle.
2. Servisi yeniden oluştur:

```bash
cd backend
docker compose up -d --force-recreate fastapi-backend
```

3. Logları kontrol et:

```bash
cd backend
docker compose logs -f fastapi-backend
```

4. Sağlık kontrolü yap:

```bash
curl http://127.0.0.1:8000/healthz
```

Not: `.env` dosyaları commit edilmemelidir.

## Image ve Dependency Güvenliği

CI pipeline şu kontrolleri uygular:

- Ruff lint
- Pytest
- GitLeaks secret scan
- Docker image build
- Trivy image scan

Lokal Trivy taraması örneği:

```bash
docker build -t fastapi-backend:local ./backend
trivy image --severity HIGH,CRITICAL fastapi-backend:local
```

Bağımlılıklar `backend/requirements.txt` içindedir. Yeni paket eklendiğinde CI pipeline'ın başarıyla çalıştığı doğrulanmalıdır.

## Secret Leak Durumunda Müdahale

Bir secret'ın commit edildiği veya loglara düştüğü fark edilirse:

1. Secret'ı hemen provider tarafında revoke et.
2. Yeni secret üret ve ilgili secret store'a ekle.
3. Uygulamayı restart veya rollout et.
4. GitLeaks ve CI pipeline'ı tekrar çalıştır.
5. Etkilenen servis loglarını ve erişim kayıtlarını incele.
6. Gerekiyorsa Git history temizliği için ayrı incident süreci başlat.

Sadece dosyadan secret'ı silmek yeterli değildir; Git history içinde kalmış olabilir.

## Loglarda Dikkat Edilecekler

- Token, password, API key ve connection string değerleri loglanmamalıdır.
- Hata mesajlarında credential bilgisi döndürülmemelidir.
- Grafana ve Prometheus panellerinde secret içeren label veya annotation kullanılmamalıdır.

## Operasyon Komutları

Restart, rollback ve log inceleme adımları için [RUNBOOK.md](RUNBOOK.md) dosyasına bak.
