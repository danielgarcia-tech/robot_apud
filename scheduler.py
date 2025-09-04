import schedule
import time
import logging
from datetime import datetime
import os
import sys

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.apudacta_scraper import ApudActaScraper
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ScheduledScraper:
    """
    Gestor de programación para el scraper de ApudActa
    """
    
    def __init__(self):
        self.execution_time = os.getenv('EXECUTION_TIME', '09:00')
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging para el scheduler"""
        log_path = os.getenv('LOG_PATH', './logs')
        os.makedirs(log_path, exist_ok=True)
        
        log_filename = f"{log_path}/scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - SCHEDULER - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_scraper(self):
        """Ejecutar el scraper"""
        try:
            self.logger.info("=== EJECUTANDO SCRAPER PROGRAMADO ===")
            
            scraper = ApudActaScraper()
            scraper.run_daily_scraping()
            
            # Generar reporte
            report_file = scraper.generate_report()
            if report_file:
                self.logger.info(f"Reporte generado: {report_file}")
            
            self.logger.info("=== SCRAPER COMPLETADO ===")
            
        except Exception as e:
            self.logger.error(f"Error ejecutando scraper programado: {e}")
    
    def start_scheduler(self):
        """Iniciar el programador"""
        self.logger.info(f"Iniciando programador - Ejecución diaria a las {self.execution_time}")
        
        # Programar la tarea diaria
        schedule.every().day.at(self.execution_time).do(self.run_scraper)
        
        # También permitir ejecución manual inmediata si se pasa argumento
        if len(sys.argv) > 1 and sys.argv[1] == '--now':
            self.logger.info("Ejecutando inmediatamente por solicitud manual")
            self.run_scraper()
        
        # Loop principal del programador
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Revisar cada minuto
                
        except KeyboardInterrupt:
            self.logger.info("Programador detenido por el usuario")
        except Exception as e:
            self.logger.error(f"Error en el programador: {e}")


def main():
    """Función principal"""
    print("=== APUDACTA SCRAPER SCHEDULER ===")
    print("Presiona Ctrl+C para detener")
    print("Usa --now como argumento para ejecutar inmediatamente")
    print("=" * 40)
    
    scheduler = ScheduledScraper()
    scheduler.start_scheduler()


if __name__ == "__main__":
    main()
