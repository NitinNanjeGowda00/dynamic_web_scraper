import os
import csv
import json
from typing import List, Dict
from datetime import datetime
from config.settings import OUTPUT_DIR
from src.utils import setup_logger, ensure_directory

logger = setup_logger("exporter")


class DataExporter:
    """Export scraped data to various formats."""
    
    def __init__(self):
        """Initialize exporter."""
        ensure_directory(OUTPUT_DIR)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def to_csv(self, data: List[Dict], filename: str = None) -> str:
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename (without extension)
            
        Returns:
            Path to the created file
        """
        if not data:
            logger.warning("No data to export")
            return None
        
        if filename is None:
            filename = f"quotes_{self.timestamp}"
        
        filepath = os.path.join(OUTPUT_DIR, f"{filename}.csv")
        
        # Flatten tags list to string for CSV
        csv_data = []
        for item in data:
            csv_item = item.copy()
            if 'tags' in csv_item and isinstance(csv_item['tags'], list):
                csv_item['tags'] = ', '.join(csv_item['tags'])
            csv_data.append(csv_item)
        
        # Write CSV
        fieldnames = csv_data[0].keys()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        logger.info(f"Exported {len(data)} records to {filepath}")
        return filepath
    
    def to_json(self, data: List[Dict], filename: str = None) -> str:
        """
        Export data to JSON file.
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename (without extension)
            
        Returns:
            Path to the created file
        """
        if not data:
            logger.warning("No data to export")
            return None
        
        if filename is None:
            filename = f"quotes_{self.timestamp}"
        
        filepath = os.path.join(OUTPUT_DIR, f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(data)} records to {filepath}")
        return filepath