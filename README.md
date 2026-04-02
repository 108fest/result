1) Поднять ВМ (ubuntu/debian)
2) Клонировать репозиторий 
```sh
git clone https://github.com/108fest/result.git
```
3) Предустановить:
    - [docker](https://docs.docker.com/engine/install/ubuntu/)
    - wireguard:
```sh
sudo apt update && sudo apt install wireguard -y
```
4) Добавить в hosts содержимое файла [hosts](./hosts.txt)
5) Поднять compose:
```sh
docker compose -f compose.yml up -d
```
