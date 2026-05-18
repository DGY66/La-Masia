from __future__ import annotations

import queue
import threading
from pathlib import Path
from typing import Callable

import customtkinter as ctk


LOGO_DIR = Path(__file__).parent / "assets" / "espn_logos"
LOGO_URL = "https://a.espncdn.com/i/teamlogos/soccer/500/{team_id}.png"


class ESPNLogoManager:
    def __init__(self, logo_dir: Path = LOGO_DIR) -> None:
        self.logo_dir = logo_dir
        self.logo_dir.mkdir(parents=True, exist_ok=True)
        self._image_cache: dict[tuple[int, tuple[int, int]], ctk.CTkImage] = {}
        self._loading: set[tuple[int, tuple[int, int]]] = set()
        self._results: queue.Queue[tuple[Callable[[ctk.CTkImage], None], ctk.CTkImage, tuple[int, tuple[int, int]]]] = queue.Queue()
        self._lock = threading.Lock()

    def start_ui_pump(self, master) -> None:
        self._master = master
        self._drain_queue()

    def _drain_queue(self) -> None:
        try:
            while True:
                callback, image, key = self._results.get_nowait()
                with self._lock:
                    self._image_cache[key] = image
                    self._loading.discard(key)
                callback(image)
        except queue.Empty:
            pass

        if hasattr(self, "_master") and self._master.winfo_exists():
            self._master.after(60, self._drain_queue)

    def get_placeholder(self, size: tuple[int, int]) -> ctk.CTkImage:
        image_lib = self._require_pillow()
        image = image_lib.new("RGBA", size, (48, 58, 92, 255))
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)

    def has_cached_logo(self, team_id: int) -> bool:
        png_path = self.logo_dir / f"{team_id}.png"
        return png_path.exists() and png_path.stat().st_size > 0

    def get_logo_image(self, team_id: int, size: tuple[int, int]) -> ctk.CTkImage:
        image_lib = self._require_pillow()
        key = (team_id, size)
        cached = self._image_cache.get(key)
        if cached is not None:
            return cached

        png_path = self.logo_dir / f"{team_id}.png"
        if not png_path.exists():
            raise FileNotFoundError(f"Missing cached logo for team_id={team_id}")

        try:
            pil_image = image_lib.open(png_path).convert("RGBA")
        except Exception:
            png_path.unlink(missing_ok=True)
            raise

        pil_image = pil_image.resize(size, image_lib.Resampling.LANCZOS)
        image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
        self._image_cache[key] = image
        return image

    def load_logo_async(
        self,
        team_id: int,
        size: tuple[int, int],
        callback: Callable[[ctk.CTkImage], None],
    ) -> None:
        key = (team_id, size)

        with self._lock:
            cached = self._image_cache.get(key)
            if cached is not None:
                callback(cached)
                return
            if key in self._loading:
                return
            self._loading.add(key)

        png_path = self.logo_dir / f"{team_id}.png"
        if png_path.exists() and png_path.stat().st_size > 0:
            try:
                image = self.get_logo_image(team_id, size)
            except Exception:
                png_path.unlink(missing_ok=True)
            else:
                with self._lock:
                    self._loading.discard(key)
                callback(image)
                return

        threading.Thread(
            target=self._load_worker,
            args=(team_id, size, callback),
            daemon=True,
        ).start()

    def _load_worker(
        self,
        team_id: int,
        size: tuple[int, int],
        callback: Callable[[ctk.CTkImage], None],
    ) -> None:
        key = (team_id, size)
        try:
            self._ensure_logo_cached(team_id)
            image = self.get_logo_image(team_id, size)
        except Exception:
            image = self.get_placeholder(size)
        self._results.put((callback, image, key))

    def _ensure_logo_cached(self, team_id: int) -> Path:
        requests_lib = self._require_requests()
        png_path = self.logo_dir / f"{team_id}.png"
        if png_path.exists():
            if png_path.stat().st_size > 0:
                return png_path
            png_path.unlink(missing_ok=True)

        response = requests_lib.get(LOGO_URL.format(team_id=team_id), timeout=10)
        response.raise_for_status()
        png_path.write_bytes(response.content)
        return png_path

    @staticmethod
    def _require_requests():
        try:
            import requests
        except ModuleNotFoundError as exc:
            raise RuntimeError("requests is not installed") from exc
        return requests

    @staticmethod
    def _require_pillow():
        try:
            from PIL import Image
        except ModuleNotFoundError as exc:
            raise RuntimeError("Pillow is not installed") from exc
        return Image
