# Script para desarrollo con Tailwind CSS y Django

Write-Host "Iniciando desarrollo con Tailwind CSS..." -ForegroundColor Green

# Función para limpiar procesos
function Cleanup {
    Write-Host "Terminando procesos..." -ForegroundColor Yellow
    if ($tailwindJob) { Stop-Job $tailwindJob; Remove-Job $tailwindJob }
    if ($djangoJob) { Stop-Job $djangoJob; Remove-Job $djangoJob }
    exit
}

# Capturar Ctrl+C
[Console]::TreatControlCAsInput = $false
[Console]::CancelKeyPress += {
    param($sender, $e)
    $e.Cancel = $true
    Cleanup
}

try {
    # Iniciar Tailwind en modo watch
    Write-Host "Iniciando Tailwind CSS en modo watch..." -ForegroundColor Cyan
    $tailwindJob = Start-Job -ScriptBlock { npm run build-css-watch }
    
    # Esperar un momento
    Start-Sleep -Seconds 3
    
    # Iniciar Django
    Write-Host "Iniciando servidor Django..." -ForegroundColor Cyan
    $djangoJob = Start-Job -ScriptBlock { python manage.py runserver }
    
    Write-Host "Desarrollo iniciado:" -ForegroundColor Green
    Write-Host "- Tailwind CSS: Observando cambios en archivos CSS" -ForegroundColor White
    Write-Host "- Django: http://127.0.0.1:8000/" -ForegroundColor White
    Write-Host "Presiona Ctrl+C para terminar ambos procesos" -ForegroundColor Yellow
    
    # Mantener el script corriendo y mostrar output
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Mostrar output de los jobs si hay alguno
        if ($tailwindJob.State -eq "Running") {
            $tailwindOutput = Receive-Job $tailwindJob -Keep
            if ($tailwindOutput) {
                Write-Host "[Tailwind] $tailwindOutput" -ForegroundColor Magenta
            }
        }
        
        if ($djangoJob.State -eq "Running") {
            $djangoOutput = Receive-Job $djangoJob -Keep
            if ($djangoOutput) {
                Write-Host "[Django] $djangoOutput" -ForegroundColor Blue
            }
        }
        
        # Verificar si algún job ha terminado
        if ($tailwindJob.State -ne "Running" -or $djangoJob.State -ne "Running") {
            Write-Host "Uno de los procesos ha terminado." -ForegroundColor Red
            break
        }
    }
}
finally {
    Cleanup
}