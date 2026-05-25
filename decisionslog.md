# Decisions Log

## ADR-001: GitOps Aracı Olarak ArgoCD seçildi

GitOps özelinde ArgoCD, Flux veya GitHub Actions’u self hosted şekilde localde çalıştırma seçeneklerim vardı.
Local pek uygun bir pratik gibi gelmedi ve Argo dashboardı ve kullanım kolaylığı sebebiyle tercih ettim. Flux daha otomatik ve native olsa da öğrenme eğrisi yüksek ve kalan zamanım için mümkün değildi. Argonun dashboard’ı gerçekten güzel.

## ADR-002: GitHub Actions CI/CD automation için seçildi

Normalde staj yaptığım şirkette Jenkins öğrenmiştim. GitHub Actions’u merak ediyordum. Çok basit bir yapısı var. Tercih etmemin asıl sebebi ise github native olması ve webhook credentials ve token gibi şeylerle uğraştırmadan kolaylıkla entegre edilmesi. GitHub payload’ı kendi parse edebilmesi ve uygulama rahatlığı, ayrıca GitHub’ın kendi cloud’unda makinede çalışması büyük avantaj.

## ADR-003: local’i internete açmak için ngrok tercih edildi

Daha önce deneyimim olması ve kullanım basitliği sebebiyle ngrok tercih ettim, minikube tarafındaki entegrasyonu biraz uğraştırsa da sonuca değdi ve başarılı sonuç aldım.
