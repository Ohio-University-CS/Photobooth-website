from PIL import Image
import os

# Layout configurations - define rows, cols for each layout
LAYOUTS = {
    # layouts
    "4x1" : {"cols": 4, "rows": 1},
    "2x2" : {"cols": 2, "rows": 2},
    "1x4" : {"cols": 1, "rows": 4},
    "1x3" : {"cols": 1, "rows": 3},
    "4x2" : {"cols": 4, "rows": 2}, 
}


def create_strip(photo_paths: list, layout: str, output_path: str) -> str:
    pass
    
