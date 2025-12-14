# Lucky-Search
Репозиторий проекта "Создание поисковика научной информации" для УрФУ.

## Почему Yandex Cloud и кратко про Terraform

[Yandex Cloud](https://yandex.cloud/ru) - облачный сервис для разработки и развертывания приложений. Мы решили его использовать, тавк как у нас есть опыт работы с ним и [грант](https://yandex.cloud/ru/docs/billing/concepts/bonus-account) на 10 000₽ (за полное прохождение курса "[Инженер облачных сервисов](https://yandex.cloud/ru/training/ycloud)"), который мы использовали для развертывания приложения.
Также новым пользователям даётся грант в размере 4 000₽, котторый также можно использовать для развертывания проекта.

[Terraform](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart) - инструмент для автоматизации развертывания и управления инфраструктурой. С его помощью можно развернуть большую инфраструктуру с одинаковой конфигурациейв в разных облаках.


## Подготовка к работе

Если вы будете разворачивать проект в Yandex Cloud, то для текущей спецификации Terraform требуется (мы опустим такие моменты как регистрация и установка необходимого ПО):

1. Зарегистрировать домен.

Для этого подойдет регистратор дорменов [Рег.ру](https://www.reg.ru/).

2. (Необязательно) Делегировать домен на серверы [Yandex Cloud DNS](https://yandex.cloud/ru/services/dns).

Для удобства, можно [делегировать](https://yandex.cloud/ru/docs/troubleshooting/dns/how-to/delegate-public-zone) домен на серверы Yandex Cloud. Для этого:
    1. Укажите адреса серверов имен Yandex Cloud в NS-записях вашего регистратора:
        - `ns1.yandexcloud.net.`;
        - `ns2.yandexcloud.net`.
    2. [Создайте публичную зону Cloud DNS для вашего домен](https://yandex.cloud/ru/docs/dns/operations/zone-create-public)а.
    3. [Создайте необходимые ресурсные записи](https://yandex.cloud/ru/docs/dns/operations/resource-record-create).
​
3. [Зарезервировать статический IP-адрес для вашего сервера](https://yandex.cloud/ru/docs/vpc/operations/get-static-ip).

4. [Загрузить Docker-образ в реестр Cloud Registry](https://yandex.cloud/ru/docs/cloud-registry/operations/docker/push).

5. [Добавить сертификат от Let's Encrypt®](https://yandex.cloud/ru/docs/certificate-manager/operations/managed/cert-create). Можно также для альтернативы [загрузить свой сертификат](https://yandex.cloud/ru/docs/certificate-manager/operations/import/cert-create).

6. [Создать сервисный аккаунт](https://yandex.cloud/ru/docs/iam/operations/sa/create) и [дать ему роль admin](https://yandex.cloud/ru/docs/iam/operations/sa/assign-role-for-sa). Про роли доступа можно прочитать [тут](https://yandex.cloud/ru/docs/iam/security/##about-access-control).

7. Настроить [Terraform](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart).

Если вы сделали все эти пункты, то вы великорлепны.

---

## Развертывание проекта

> Все дейтвия выполнялись на Ubuntu 20.04

В файле [terraform.tfvars.txt](terraform.tfvars.txt) содержимтся шаблон переменных, которые используются для развертывания проекта.

1. [Получите Oauth-токен](https://yandex.cloud/ru/docs/iam/concepts/authorization/oauth-token) и вставьте его в переменную `ycr_token`.

2. [Получите IAM-токен](https://yandex.cloud/ru/docs/iam/operations/iam-token/create) и вставьте его в переменную `yc_token`.

> Жизнь IAM-токена составляет 12 часов! Потом нужно получать новый токен.

3. В файле [main.tf](main.tf) поменяйте строку:
`ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"` на путь до вашего SSH-ключа, чтобы вы могли подключиться к ВМ.

4. Выполните команду `terraform init`, чтобы инициализировать Terraform.

5. Выполните команду `terraform plan`, чтобы просмотреть, какие ресурсы будут созданы и нет ли проблем с конфигурацией.

6. Выполните команду `terraform apply`, чтобы развернуть проект.

> Обычно время развертывания проекта составляет около 10 минут.

7. Выполните команду `terraform destroy`, чтобы удалить все ресурсы.
