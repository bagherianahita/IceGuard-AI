from scipy import ndimage
from typing import List, Dict

def cluster_detections(mask: np.ndarray) -> List[Dict]:
    """
    Aim: Group individual bright pixels into single 'Iceberg' objects.
    Nature: Segmentation & Clustering.
    Application: Prevents one large iceberg from being counted as 50 separate small ones.
    """
    labeled_array, num_features = ndimage.label(mask)
    objects = ndimage.find_objects(labeled_array)
    
    icebergs = []
    for i, obj in enumerate(objects):
        # Calculate size (area)
        size = np.sum(mask[obj])
        
        # Calculate centroid (center point)
        center_y = (obj[0].start + obj[0].stop) / 2
        center_x = (obj[1].start + obj[1].stop) / 2
        
        icebergs.append({
            "internal_id": f"ice_{i:03d}",
            "pixel_coords": (center_x, center_y),
            "area_pixels": float(size),
            "confidence": 0.85 # Placeholder confidence
        })
    
    return icebergs