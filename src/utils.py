import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import logging

class ScraperUtils:
    """
    Utilidades para el mantenimiento del scraper
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.download_path = self.base_path / 'descargas'
        self.log_path = self.base_path / 'logs'
        self.state_file = self.base_path / 'scraper_state.json'
        
    def cleanup_old_files(self, days_old: int = 30):
        """Limpiar archivos antiguos"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        cleaned_files = []
        
        # Limpiar descargas antiguas
        for file_path in self.download_path.glob('*.zip'):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                file_path.unlink()
                cleaned_files.append(str(file_path))
        
        # Limpiar logs antiguos
        for file_path in self.log_path.glob('*.log'):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                file_path.unlink()
                cleaned_files.append(str(file_path))
        
        print(f"Archivos limpiados: {len(cleaned_files)}")
        return cleaned_files
    
    def reset_scraper_state(self):
        """Resetear el estado del scraper"""
        if self.state_file.exists():
            backup_name = f"scraper_state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy(self.state_file, self.base_path / backup_name)
            self.state_file.unlink()
            print(f"Estado reseteado. Backup guardado como: {backup_name}")
        else:
            print("No hay estado para resetear")
    
    def get_download_stats(self):
        """Obtener estadísticas de descargas"""
        if not self.state_file.exists():
            print("No hay datos de descargas")
            return
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_files = len(data)
        total_size = 0
        
        # Calcular estadísticas
        dates = []
        for filename, info in data.items():
            dates.append(datetime.fromisoformat(info['fecha_descarga']))
            # Intentar extraer tamaño
            size_str = info.get('info', {}).get('tamaño', '0')
            # Simplificado: asumir MB si no está especificado
            if 'MB' in size_str:
                total_size += float(size_str.replace(' MB', '').replace(',', '.'))
        
        if dates:
            first_download = min(dates)
            last_download = max(dates)
        else:
            first_download = last_download = None
        
        print(f"""
=== ESTADÍSTICAS DE DESCARGAS ===
Total de archivos: {total_files}
Tamaño aproximado: {total_size:.1f} MB
Primera descarga: {first_download}
Última descarga: {last_download}
=================================""")
    
    def check_missing_files(self):
        """Verificar archivos registrados vs archivos físicos"""
        if not self.state_file.exists():
            print("No hay estado para verificar")
            return
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            registered_files = set(json.load(f).keys())
        
        physical_files = set(f.name for f in self.download_path.glob('*.zip'))
        
        missing_physical = registered_files - physical_files
        missing_registered = physical_files - registered_files
        
        if missing_physical:
            print("Archivos registrados pero no encontrados físicamente:")
            for f in missing_physical:
                print(f"  - {f}")
        
        if missing_registered:
            print("Archivos físicos pero no registrados:")
            for f in missing_registered:
                print(f"  - {f}")
        
        if not missing_physical and not missing_registered:
            print("✅ Todos los archivos están sincronizados")
    
    def generate_full_report(self):
        """Generar reporte completo"""
        if not self.state_file.exists():
            print("No hay datos para el reporte")
            return
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Crear DataFrame
        rows = []
        for filename, info in data.items():
            row = {
                'archivo': filename,
                'fecha_descarga': info['fecha_descarga'],
                'tamaño': info.get('info', {}).get('tamaño', 'N/A'),
                'fecha_original': info.get('info', {}).get('fecha', 'N/A'),
                'archivos_contenidos': info.get('info', {}).get('archivos', 'N/A'),
                'apudactas': info.get('info', {}).get('apudactas', 'N/A'),
                'existe_fisicamente': (self.download_path / filename).exists()
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Guardar reporte
        report_file = self.base_path / f"reporte_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(report_file, index=False)
        
        print(f"Reporte completo generado: {report_file}")
        return str(report_file)


def main():
    """Menú principal de utilidades"""
    utils = ScraperUtils()
    
    while True:
        print("\n=== UTILIDADES DEL SCRAPER ===")
        print("1. Ver estadísticas de descargas")
        print("2. Verificar archivos faltantes")
        print("3. Generar reporte completo")
        print("4. Limpiar archivos antiguos")
        print("5. Resetear estado del scraper")
        print("0. Salir")
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == '1':
            utils.get_download_stats()
        elif choice == '2':
            utils.check_missing_files()
        elif choice == '3':
            utils.generate_full_report()
        elif choice == '4':
            days = input("¿Días de antigüedad para limpiar? (default: 30): ").strip()
            days = int(days) if days else 30
            utils.cleanup_old_files(days)
        elif choice == '5':
            confirm = input("¿Estás seguro de resetear el estado? (s/N): ").strip().lower()
            if confirm == 's':
                utils.reset_scraper_state()
        elif choice == '0':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida")


if __name__ == "__main__":
    main()
