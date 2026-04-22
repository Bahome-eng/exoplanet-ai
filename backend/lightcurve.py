# backend/lightcurve.py

import os
import lightkurve as lk
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import pandas as pd
import logging
import io
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class LightcurveGenerator:
    def __init__(self, dataset_path: str = None):
        self.dataset_path = dataset_path or os.path.abspath(
            os.path.join(BASE_DIR, "../data/koi_data.csv")
        )
        self.df = None
        self.load_dataset()

    def load_dataset(self):
        try:
            self.df = pd.read_csv(
                self.dataset_path,
                comment="#",
                on_bad_lines="skip"
            )
            self.df.columns = [str(c).strip() for c in self.df.columns]
            logger.info(f"Loaded Kepler dataset with {len(self.df)} rows")
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise

    def get_kepid_from_kepoi_name(self, kepoi_name: str) -> Optional[int]:
        try:
            matching_rows = self.df[self.df["kepoi_name"].astype(str) == str(kepoi_name)]
            if matching_rows.empty:
                logger.warning(f"No matching row found for kepoi_name: {kepoi_name}")
                return None

            kepid = matching_rows["kepid"].iloc[0]
            logger.info(f"Found kepid {kepid} for kepoi_name {kepoi_name}")
            return int(kepid)

        except Exception as e:
            logger.error(f"Error getting kepid for {kepoi_name}: {str(e)}")
            return None

    def retrieve_lc(self, kepid: int) -> Tuple[bool, bytes, str]:
        try:
            kepler_id = f"KIC {kepid}"
            file_name = f"{kepid}.png"

            logger.info(f"Generating lightcurve for kepid: {kepid}")

            lcs = lk.search_lightcurve(
                kepler_id,
                exptime="long",
                author="Kepler",
                limit=1
            ).download_all()

            if not lcs:
                logger.warning(f"No lightcurve data found for {kepler_id}")
                return False, None, None

            lc_raw = lcs.stitch()
            lc_clean = lc_raw.remove_outliers()

            plt.figure(figsize=(4, 3), dpi=100)
            plt.title(f"Light Curve for KIC {kepid}", fontsize=10, fontweight="bold")
            plt.xlabel("Time (days)", fontsize=8)
            plt.ylabel("Normalized Flux", fontsize=8)

            time_values = lc_clean.time.value
            flux_values = lc_clean.flux.value if hasattr(lc_clean.flux, "value") else lc_clean.flux

            if len(time_values) > 1000:
                step = len(time_values) // 1000
                time_values = time_values[::step]
                flux_values = flux_values[::step]

            plt.plot(time_values, flux_values, lw=0.5, color="#4a9eff", alpha=0.8)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, dpi=150, bbox_inches="tight", facecolor="white", format="png")
            plt.close()

            image_data = buffer.getvalue()
            buffer.close()

            del lcs, lc_raw, lc_clean, time_values, flux_values

            logger.info(f"Lightcurve generated for kepid: {kepid}")
            return True, image_data, file_name

        except Exception as e:
            logger.error(f"Error generating lightcurve for kepid {kepid}: {str(e)}")
            return False, None, None

    def generate_lightcurve_for_kepoi(self, kepoi_name: str) -> Tuple[bool, bytes, str, int]:
        try:
            kepid = self.get_kepid_from_kepoi_name(kepoi_name)
            if kepid is None:
                return False, None, None, None

            try:
                success, image_data, filename = self.retrieve_lc(kepid)
                if success and image_data:
                    return success, image_data, filename, kepid
            except Exception as e:
                logger.warning(f"Full lightcurve generation failed for {kepoi_name}: {str(e)}")

            logger.info(f"Using fallback simple lightcurve for {kepoi_name}")
            from simple_lightcurve import generate_simple_lightcurve
            success, image_data, filename = generate_simple_lightcurve(kepid)
            return success, image_data, filename, kepid

        except Exception as e:
            logger.error(f"Error generating lightcurve for {kepoi_name}: {str(e)}")
            return False, None, None, None


lightcurve_generator = LightcurveGenerator()


def generate_lightcurve(kepoi_name: str) -> Tuple[bool, bytes, str, int]:
    return lightcurve_generator.generate_lightcurve_for_kepoi(kepoi_name)