
# Установка
windows power shell
#Проверяем запущенные сессии
wsl -l -v
#Устанавливаем убунту как сессию по-умолчанию
wsl --set-default Ubuntu
#Обновляем все программы
sudo apt update && sudo apt upgrade -y
# 2. Установка необходимых утилит
sudo apt install -y \
    curl \
    wget \
    git \
    nano \
    htop \
    net-tools \
    gnupg \
    software-properties-common \
    apt-transport-https \
    ca-certificates
# 3. Настройка времени (важно для 1С!)
sudo timedatectl set-timezone Europe/Moscow


# Регулярная работа

##Проверяем запущенные сессии
wsl -l -v
##Запускаем Ubuntu
wsl -d Ubuntu
##Запускаем docker wsl
wsl -d docker-desktop
exit # выходим из среды docker-desktop, она остаётся запущенной.


