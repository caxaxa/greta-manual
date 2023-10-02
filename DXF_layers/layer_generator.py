import numpy as np
from osgeo import gdal
import ezdxf
import cv2

# Setting color indices for DXF
RED_COLOR = 1  # Red
BLACK_COLOR = 7  # Black

class GeoImageProcessor:
    def __init__(self, geotiff_path, dxf_path):
        # Opening the GeoTIFF file and getting its geotransform details.
        self.tif_dataset = gdal.Open(geotiff_path)
        self.geotransform = self.tif_dataset.GetGeoTransform()

        #preparing hotspot set to avoid double counting
        self.used_hotspots = set()
        # Reading the DXF file for drawing and annotating.
        self.dwg = ezdxf.readfile(dxf_path)
        self.msp = self.dwg.modelspace()

    def _convert_to_geo_coordinates(self, contour):
        """Convert contour's image coordinates to geospatial coordinates."""
        return [((pt[0][0]) * self.geotransform[1] + self.geotransform[0],
                (pt[0][1]) * self.geotransform[5] + self.geotransform[3]) for pt in contour]

    def draw_contour(self, contour, layer_name, color=BLACK_COLOR):
        """Draw the contour on the DXF file."""
        geo_contour = self._convert_to_geo_coordinates(contour)
        geo_contour.append(geo_contour[0])
        self.msp.add_lwpolyline(geo_contour, dxfattribs={'layer': layer_name, 'color': color})

    def draw_and_fill_contour(self, contour, layer_name, color=None):
        """Draw and fill the contour on the DXF file."""
        geo_contour = self._convert_to_geo_coordinates(contour)
        self.draw_contour(contour, layer_name, color)
        hatch = self.msp.add_hatch(dxfattribs={'layer': layer_name, 'color': color})
        hatch.paths.add_polyline_path(geo_contour)
        hatch.set_solid_fill(color=color)

    def annotate_contour(self, contour, label, layer_name):
        """Add annotation (text) to the center of the contour."""
        center_x = sum(pt[0] for pt in contour) / len(contour)
        center_y = sum(pt[1] for pt in contour) / len(contour)
        self.msp.add_text(label, dxfattribs={'layer': layer_name, 'insert': (center_x, center_y), 'height': 1})

    def is_panel_affected(self, panel, hotspots, tracker):
        x, y, w, h = cv2.boundingRect(tracker)
        test_panel = np.array([((pt[0][0] + x), (pt[0][1] + y)) for pt in panel])
        offsets = [(0, 0), (5, 0), (-5, 0), (0, 3), (0, -3)]
        for hotspot_idx, hotspot in enumerate(hotspots):
            # Check if hotspot has already been used
            if hotspot_idx in self.used_hotspots:
                continue

            M = cv2.moments(hotspot)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                for dx, dy in offsets:
                    if cv2.pointPolygonTest(test_panel, (cx + dx, cy + dy), False) >= 0:
                        self.used_hotspots.add(hotspot_idx)  # Add this hotspot to the used set
                        return True
        return False


    def detect_and_annotate_panels(self, tracker, tracker_idx, new_mask, hotspots):
        """Detect individual solar panels within a tracker and annotate them."""
        x, y, w, h = cv2.boundingRect(tracker)
        tracker_roi = new_mask[y:y+h, x:x+w]
        inverted_tracker_roi = cv2.bitwise_not(tracker_roi)
        panels = detect_contours(inverted_tracker_roi)
        panels = sorted(panels, key=lambda c: cv2.boundingRect(c)[1])

        for panel_jdx, panel in enumerate(panels):
            panel_geo_contour = [((pt[0][0] + x) * self.geotransform[1] + self.geotransform[0],
                                  (pt[0][1] + y) * self.geotransform[5] + self.geotransform[3]) for pt in panel]
            label = f"{tracker_idx+1}-{panel_jdx+1}"

            # Check if the panel is affected by hotspots.
            if self.is_panel_affected(panel, hotspots, tracker):
                self.msp.add_lwpolyline(panel_geo_contour, dxfattribs={'layer': 'GRETA - Máscara dos Trackers'})
                self.msp.add_lwpolyline(panel_geo_contour, dxfattribs={'layer' : 'GRETA - Trackers Afetados', 'color': RED_COLOR})
                self.annotate_contour(panel_geo_contour, label, 'GRETA - Número das Placas')
                self.annotate_contour(panel_geo_contour, label, 'GRETA - Trackers Afetados')
            else:
                self.annotate_contour(panel_geo_contour, label, 'GRETA - Número das Placas')
                self.msp.add_lwpolyline(panel_geo_contour, dxfattribs={'layer': 'GRETA - Máscara dos Trackers'})
    def save(self, path):
        """Save changes to the DXF file."""
        self.dwg.saveas(path)

def detect_contours(mask):
    """Detect contours from a binary mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours
