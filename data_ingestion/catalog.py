import os
import json
from datetime import datetime
from typing import List, Optional

class SceneCatalog:
    """
    Nature: Metadata Manager.
    Aim: Tracks downloaded files and prevents redundant downloads (Cache Management).
    Application: A local JSON database that maps 'Date + Region' to 'Local File Path'.
    """
    def __init__(self, catalog_path: str = "data/catalog.json"):
        self.catalog_path = catalog_path
        self.db = self._load_db()

    def _load_db(self):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, 'r') as f:
                return json.load(f)
        return {"scenes": []}

    def register_scene(self, scene_id: str, file_path: str, timestamp: str, bbox: List[float]):
        """Registers a new download in the local index."""
        entry = {
            "scene_id": scene_id,
            "path": file_path,
            "acquired_at": timestamp,
            "bbox": bbox,
            "processed": False
        }
        self.db["scenes"].append(entry)
        self._save_db()

    def find_cached_scene(self, target_date: str, bbox: List[float]) -> Optional[str]:
        """
        Aim: Checks if we already have this image before calling the API.
        """
        for scene in self.db["scenes"]:
            if scene["acquired_at"] == target_date and scene["bbox"] == bbox:
                return scene["path"]
        return None

    def _save_db(self):
        with open(self.catalog_path, 'w') as f:
            json.dump(self.db, f, indent=4)