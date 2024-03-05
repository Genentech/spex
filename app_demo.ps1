# Этот файл предназначен для демонстрационных целей.

# Важное сообщение
$alert = @"
IMPORTANT:
Don't forget to set environment variables HOST_DATA_STORAGE
(it should be a path on your local machine)

The script awaits that you will do it in the ./set_env.local.ps1 file
content of file for example:
`$env:HOST_DATA_STORAGE="C:\path\to\your\data"
"@

# Попытка загрузить переменные среды из файла
$envFile = "./set_env.local.ps1"
if (Test-Path $envFile) {
    . $envFile
} else {
    Write-Host "ERROR: set_env.local.ps1 not found"
    exit
}

# Проверка на наличие переменной среды HOST_DATA_STORAGE
if ([string]::IsNullOrEmpty($env:HOST_DATA_STORAGE)) {
    Write-Host $alert
    exit 1
}

# Изменение прав доступа к папке redis и скрипту build.sh не требуется в Windows
# PowerShell автоматически обрабатывает права доступа

# Выбор файла docker-compose
$DOCKER_COMPOSE_FILE = "docker-compose-demo.yml"

switch ($args[0]) {
    "up" {
        Write-Host "Up..."
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
    }
    "down" {
        Write-Host "Down..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
    }
    "stop" {
        Write-Host "Stopping..."
        docker-compose -f $DOCKER_COMPOSE_FILE stop
    }
    "start" {
        Write-Host "Starting..."
        docker-compose -f $DOCKER_COMPOSE_FILE start
    }
    "rm" {
        Write-Host "Removing..."
        docker-compose -f $DOCKER_COMPOSE_FILE rm -f -s -v
    }
    default {
        Write-Host "Usage: .\${0} {up|down|stop|start|rm}"
        Write-Host @"
up - up the microservices (similar: docker-compose up -d)
down - down the microservices (similar: docker-compose down)
stop - stop the microservices (similar: docker-compose stop)
start - start the microservices (similar: docker-compose start)
rm - remove the microservices (similar: docker-compose rm -f -s -v)
"@
    }
}
