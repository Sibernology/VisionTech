# VisionTech
Kamera Tabanlı Uzaktan Kontrol Sistemi

Bu proje; bilgisayar kamerasını kullanarak el hareketleriyle işletim sistemini, fareyi ve medya oynatıcılarını uzaktan yönetmeyi sağlayan bir bilgisayarlı görü (Computer Vision) uygulamasıdır. Proje, popüler kültürdeki fütüristik el hareketleriyle kontrol mekanizmalarını temel alarak, bilgisayarı dokunmadan yönetebileceğimiz işlevsel bir araç sunmayı amaçlar.

Uygulama Linux (X11) ortamı için optimize edilmiş olup tamamen açık kaynaklı ve yeni özellikler eklenmeye müsait bir mimariye sahiptir.
Özellikler

   Yüz Bulanıklaştırma: Gizlilik amacıyla kameradaki yüzleri otomatik olarak tespit eder ve gerçek zamanlı olarak bulanıklaştırır (Gaussian Blur).

   Akıllı Fare Kontrolü: İşaret ve orta parmağınız yan yanayken elinizi hareket ettirerek fare imlecini yönetebilirsiniz. Baş parmağınızı açıp kapatarak sol tıklama (click) yapabilirsiniz.

   Ses Seviyesi Yönetimi: Avucunuzu tamamen açıp elinizi kameraya yaklaştırarak veya uzaklaştırarak sistem sesini dinamik olarak artırıp azaltabilirsiniz.

   Medya Kontrolü: Belirli parmak kombinasyonlarıyla oynatılan medyayı duraklatabilir, sonrakine veya öncekine geçebilirsiniz.

   Zaman Ayarlı Ekran Görüntüsü: Elinizi sıkı bir yumruk yapıp 1 saniye boyunca tuttuğunuzda otomatik olarak ekran görüntüsü alınır.

   Görsel Yardım Menüsü: İki elinizi de yukarı kaldırıp avuçlarınızı açtığınızda ekranda hangi hareketin ne işe yaradığını gösteren bir kılavuz menüsü açılır.

Kullanılan Teknolojiler ve Kütüphaneler
Yazılım ve Kütüphaneler

    Python 3

    OpenCV: Kamera görüntüsünü almak, işlemek ve ekranda arayüz oluşturmak için.

    MediaPipe: El hatlarını (landmark) ve yüzü yüksek doğrulukla tespit etmek için.

    NumPy: Görüntü matrisleri ve koordinat dönüşümleri için.

Linux Sistem Araçları (Bağımlılıklar)

Sistem komutlarının yürütülmesi için arka planda şu araçlar çağrılmaktadır:

    xdotool (Fare hareketleri ve tıklama için)

    pactl (Sistem ses kontrolü için)

    scrot (Ekran görüntüsü kaydetmek için)

    playerctl (Medya oynatıcı kontrolü için)

🚀 Çalıştırma ve Kurulum Alternatifleri

Projenin gereksinim duyduğu sistem araçlarının ana makinenizi etkilememesi ve çevre birimlerinin (Kamera, Ekran, Ses) izole bir şekilde çalışabilmesi için Docker kullanılması önerilir. Alternatif olarak yerel makinenizde Virtual Environment (venv) de oluşturabilirsiniz.
Seçenek A: Docker ile Çalıştırma (Önerilen)

Docker konteynerinin X11 ekran sunucusuna, kameraya ve ses sürücülerine erişebilmesi için aşağıdaki komutu terminalde çalıştırmanız yeterlidir.

Not: Komuttaki /dev/video1 parametresi varsayılan kamera indeksinize göre (/dev/video0 vb.) değişiklik gösterebilir. Ayrıca $HOME/Desktop/goruntuisleme_python dizinini kendi proje yolunuza göre güncelleyiniz.

Bash

# Docker'ı yükle (eğer yüklü değilse) 

 # 1. Önce sistem paketlerini güncelle
    sudo apt update

# 2. Gerekli yardımcı araçları kur
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 3. Docker'ın resmi GPG anahtarını ekle
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 4. Docker reposunu sistemine tanıt
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.dist.d/docker.list > /dev/null

# 5. Listeyi tekrar güncelle ve asıl Docker paketlerini kur
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io



# Docker'ın yerel ekran sunucusuna erişimine izin verin
    sudo xhost +local:docker > /dev/null 2>&1


    
# VE SON OLARAK PROJEYİ ÇALIŞTIRIN
# Konteyneri çevre birimi izinleriyle birlikte başlatın
    sudo docker run -it --rm \
    --device=/dev/video1 \
    -e DISPLAY=$DISPLAY \
    -e PULSE_SERVER=unix:/run/user/1000/pulse/native \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /run/user/1000/pulse:/run/user/1000/pulse \
    -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
    -v $HOME/Desktop/goruntuisleme_python:/app \
    gesture-control


Seçenek B: Yerel Makinede (venv) Kurulum

Projeyi doğrudan yerel makinenizde çalıştırmak isterseniz, sistem bağımlılıklarının çakışmaması adına bir sanal ortam (venv) oluşturabilirsiniz.

  Bağımlılıkları yerel sisteminize yükleyin:
    
   
'''   
Bash

    sudo apt install xdotool scrot playerctl text-utils python3-venv

    Proje dizininde sanal ortamı oluşturun ve aktif edin:
    Bash

    python3 -m venv venv
    source venv/bin/activate

    Gerekli Python paketlerini kurun ve projeyi başlatın:
    Bash

    pip install opencv-python mediapipe numpy
    python main.py

(Çıkış yapmak için klavyeden q tuşuna basabilirsiniz.)

💡 Gelecek Planları (Fikir Aşaması)

Bu proje şu an için yerel bilgisayarı kontrol etmeye odaklansa da, mevcut altyapısı bir Akıllı Ev Sistemine dönüştürülmeye oldukça uygundur.

Gelecekte projeyi daha da ileri taşımak için bir ESP32 geliştirme kartı ve röle modülü sisteme entegre edilebilir. Python kodunda el hareketleri algılandığında, bu komutlar yerel ağ (IP) üzerinden ESP32'ye iletilebilir. Böylece sadece kameraya el sallayarak odanızdaki lambayı, vantilatörü veya diğer elektronik cihazları uzaktan açıp kapatabileceğiniz akıllı bir ev ekosistemi oluşturabilirsiniz.
