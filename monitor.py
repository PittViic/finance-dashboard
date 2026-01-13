import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MonitorExtrato(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        elif event.src_path.endswith('.csv'):
            print(f"NOVO EXTRATO DETECTADO: {event.src_path}")
            print("Atualizando base de dados...")
            # Aqui você poderia adicionar lógica para mover o arquivo,
            # enviar um email de alerta ou inserir num banco SQL.

if __name__ == "__main__":
    path = "extratos"
    event_handler = MonitorExtrato()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"Monitorando a pasta '{path}' por novos CSVs...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()