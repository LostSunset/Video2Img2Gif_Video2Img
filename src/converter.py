"""
影片與圖片轉換核心模組
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import cv2
import imageio
from PIL import Image


class VideoConverter:
    """影片轉換器"""

    @staticmethod
    def video_to_images(
        video_path: str,
        output_dir: str,
        frame_interval: int = 1,
        output_format: str = "png",
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[str]:
        """
        將影片轉換為圖片序列

        Args:
            video_path: 影片檔案路徑
            output_dir: 輸出目錄
            frame_interval: 每幾幀輸出一張圖片（1 = 每幀都輸出）
            output_format: 輸出圖片格式（png, jpg, bmp, webp）
            progress_callback: 進度回調函數 (current_frame, total_frames)

        Returns:
            輸出的圖片路徑列表
        """
        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"無法開啟影片: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        output_files: list[str] = []
        frame_count = 0
        saved_count = 0

        video_name = Path(video_path).stem

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                output_path = os.path.join(
                    output_dir, f"{video_name}_{saved_count:06d}.{output_format}"
                )
                # OpenCV 使用 BGR，需轉換為 RGB 後再存檔
                if output_format.lower() in ("jpg", "jpeg"):
                    cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                elif output_format.lower() == "webp":
                    cv2.imwrite(output_path, frame, [cv2.IMWRITE_WEBP_QUALITY, 95])
                else:
                    cv2.imwrite(output_path, frame)
                output_files.append(output_path)
                saved_count += 1

            frame_count += 1
            if progress_callback:
                progress_callback(frame_count, total_frames)

        cap.release()
        return output_files

    @staticmethod
    def images_to_gif(
        image_paths: list[str],
        output_path: str,
        fps: float = 10.0,
        loop: int = 0,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> str:
        """
        將圖片序列轉換為 GIF

        Args:
            image_paths: 圖片路徑列表
            output_path: 輸出 GIF 路徑
            fps: 每秒幀數
            loop: 循環次數（0 = 無限循環）
            progress_callback: 進度回調函數

        Returns:
            輸出的 GIF 路徑
        """
        if not image_paths:
            raise ValueError("圖片列表不能為空")

        images = []
        total = len(image_paths)

        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path)
            # 確保轉換為 RGB 或 RGBA
            if img.mode not in ("RGB", "RGBA", "P"):
                img = img.convert("RGB")
            images.append(img)
            if progress_callback:
                progress_callback(i + 1, total)

        duration = int(1000 / fps)  # 毫秒
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=loop,
            optimize=True,
        )

        return output_path

    @staticmethod
    def images_to_video(
        image_paths: list[str],
        output_path: str,
        fps: float = 30.0,
        codec: str = "libx264",
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> str:
        """
        將圖片序列轉換為影片

        Args:
            image_paths: 圖片路徑列表
            output_path: 輸出影片路徑
            fps: 每秒幀數
            codec: 編碼器
            progress_callback: 進度回調函數

        Returns:
            輸出的影片路徑
        """
        if not image_paths:
            raise ValueError("圖片列表不能為空")

        total = len(image_paths)

        # 使用 imageio-ffmpeg 來寫入影片
        writer = imageio.get_writer(output_path, fps=fps, codec=codec, quality=8)

        for i, img_path in enumerate(image_paths):
            img = imageio.imread(img_path)
            writer.append_data(img)
            if progress_callback:
                progress_callback(i + 1, total)

        writer.close()
        return output_path

    @staticmethod
    def video_to_gif(
        video_path: str,
        output_path: str,
        frame_interval: int = 1,
        fps: float = 10.0,
        max_width: int | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> str:
        """
        將影片直接轉換為 GIF

        Args:
            video_path: 影片檔案路徑
            output_path: 輸出 GIF 路徑
            frame_interval: 每幾幀取一幀（1 = 每幀都取）
            fps: GIF 播放速度
            max_width: 最大寬度（用於縮小 GIF 尺寸）
            progress_callback: 進度回調函數

        Returns:
            輸出的 GIF 路徑
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"無法開啟影片: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames: list[Image.Image] = []
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                # BGR 轉 RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)

                # 如果指定了最大寬度，進行縮放
                if max_width and img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                frames.append(img)

            frame_count += 1
            if progress_callback:
                progress_callback(frame_count, total_frames)

        cap.release()

        if not frames:
            raise ValueError("無法從影片中提取任何幀")

        duration = int(1000 / fps)
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=True,
        )

        return output_path
