import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
import time

# python service.py install
# python service.py start


class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'Gneuro_render_service'
    _svc_display_name_ = 'Gneuro_render_service'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Путь к git-bash.exe
        git_bash_path = "C:\\Program Files\\Git\\git-bash.exe"
        
        # Путь к вашему bash-скрипту
        script_path = "/c/project/tg_ai_bot/run_client.sh"
        
        while self.is_alive:
            # Запуск git-bash.exe с вашим скриптом
            command = f'"{git_bash_path}" -c "{script_path}"'
            os.system(command)
            
            # Задержка в 5 минут
            time.sleep(5 * 60)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)
