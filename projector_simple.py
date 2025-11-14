"""
简单的投影显示方案：保存高亮图片到文件
用户可以用任何图片查看器打开并全屏显示
"""

import cv2
import numpy as np
import os
from typing import Tuple

class ProjectorSimple:
    def __init__(self, image_path: str, output_dir="./projector_output"):
        """
        初始化简单投影显示
        image_path: 书架照片路径
        output_dir: 输出目录
        """
        self.image_path = image_path
        self.output_dir = output_dir
        self.current_highlight = None
        self.highlight_duration = 5.0
        self.highlight_start_time = None
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 加载原始图片
        self.original_image = None
        self.load_image(image_path)
        
        print(f"✅ 简单投影模式已初始化")
        print(f"   高亮图片将保存到: {output_dir}/highlight.jpg")
        print(f"   可以用任何图片查看器打开并全屏显示")
    
    def load_image(self, image_path: str):
        """加载图片"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            print(f"📸 原始图片尺寸: {img.shape[1]}x{img.shape[0]}")
            
            # 保持原始尺寸（或调整到合适大小）
            # 投影仪通常是1920x1080，但我们可以保持原图比例
            self.original_image = img.copy()
            self.width = img.shape[1]
            self.height = img.shape[0]
            
            print(f"✅ 成功加载图片: {image_path}")
        except Exception as e:
            print(f"❌ 加载图片失败: {e}")
            self.original_image = None
    
    def highlight_book(self, position: Tuple[float, float, float, float], 
                       book_name: str = "", points: list = None):
        """
        高亮显示书籍并保存图片
        position: (x, y, width, height) 归一化坐标 (0-1) - 用于兼容性
        book_name: 书籍名称
        points: 四点定位数据 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] - 归一化坐标 (0-1)，如果提供则优先使用
        """
        import time
        
        if self.original_image is None:
            print("❌ 图片未加载")
            return
        
        # 优先使用四点定位
        use_points = points is not None and len(points) == 4
        
        if use_points:
            # 使用四点定位
            print(f"\n📍 使用四点定位:")
            print(f"   四点数据: {points}")
            
            # 转换为像素坐标
            pixel_points = []
            for p in points:
                px = int(p[0] * self.width)
                py = int(p[1] * self.height)
                pixel_points.append([px, py])
            
            # 计算边界框（用于书名位置）
            xs = [p[0] for p in pixel_points]
            ys = [p[1] for p in pixel_points]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            x, y, w, h = x_min, y_min, x_max - x_min, y_max - y_min
            
            print(f"   图片尺寸: {self.width}x{self.height}")
            print(f"   像素坐标: {pixel_points}")
            print(f"   边界框: ({x}, {y}, {w}, {h})")
        else:
            # 使用矩形定位（兼容旧格式）
            # 转换为像素坐标
            # 注意：position存储的是 (center_x, center_y, width, height) 归一化坐标
            # 需要转换为左上角坐标用于绘制
            center_x = position[0] * self.width
            center_y = position[1] * self.height
            w = int(position[2] * self.width)
            h = int(position[3] * self.height)
        
            # 计算左上角坐标
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)
        
            # 调试信息
            print(f"\n📍 使用矩形定位:")
            print(f"   归一化坐标: {position}")
            print(f"   图片尺寸: {self.width}x{self.height}")
            print(f"   高亮区域: ({x}, {y}, {w}, {h})")
            pixel_points = None
        
        # 确保坐标在范围内
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        w = min(w, self.width - x)
        h = min(h, self.height - y)
        
        # 创建显示图片
        frame = self.original_image.copy()
        
        # 将背景设为半透明黑色（60%透明度，可以看到书架）
        # 60%透明度 = 40%不透明度，所以背景应该是原图的40%亮度
        overlay = cv2.addWeighted(frame, 0.4, np.zeros_like(frame), 0.6, 0)
        
        # 高亮区域填充白色（60%透明度，可以看到书架）
        white_overlay = overlay.copy()
        if use_points:
            # 使用四点绘制多边形
            pts = np.array(pixel_points, np.int32)
            cv2.fillPoly(white_overlay, [pts], (255, 255, 255))
        else:
            # 使用矩形
            cv2.rectangle(white_overlay, (x, y), (x + w, y + h), (255, 255, 255), -1)
        
        # 将白色区域以60%透明度叠加（原图60% + 白色40%）
        overlay = cv2.addWeighted(overlay, 0.6, white_overlay, 0.4, 0)
        
        # 显示书名（固定宽度400，最多3行）
        if book_name:
            # 固定背景框大小（所有书名都使用相同大小）
            center_x = x + w // 2
            box_width = 600  # 固定宽度：600像素
            box_height = 180  # 固定高度：足够3行显示
            box_x = center_x - box_width // 2
            box_y = max(50, y - box_height - 60)  # 在白色块上方至少60像素
            
            # 确保不超出图片边界
            box_x = max(10, min(box_x, self.width - box_width - 10))
            box_y = max(10, min(box_y, self.height - box_height - 10))
            
            # 固定字体大小
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            thickness = 3
            max_lines = 3
            line_spacing = 8
            padding = 15  # 内边距
            
            # 可用宽度和高度（固定背景框内的可用空间）
            available_width = box_width - padding * 2
            
            # 分割长文本为多行（最多3行）
            words = book_name.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                (text_width, _), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
                
                if text_width <= available_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        if len(lines) >= max_lines:
                            break
                    current_line = word
            
            if current_line and len(lines) < max_lines:
                lines.append(current_line)
            
            # 如果超过3行，缩小字体以适应
            if len(lines) > max_lines:
                # 尝试缩小字体
                for scale in [1.2, 1.0, 0.8, 0.6]:
                    test_thickness = max(1, int(scale * 2))
                    test_lines = []
                    test_current_line = ""
                    
                    for word in words:
                        test_line = test_current_line + " " + word if test_current_line else word
                        (text_width, _), _ = cv2.getTextSize(test_line, font, scale, test_thickness)
                        
                        if text_width <= available_width:
                            test_current_line = test_line
                        else:
                            if test_current_line:
                                test_lines.append(test_current_line)
                                if len(test_lines) >= max_lines:
                                    break
                            test_current_line = word
                    
                    if test_current_line and len(test_lines) < max_lines:
                        test_lines.append(test_current_line)
                    
                    if len(test_lines) <= max_lines:
                        lines = test_lines
                        font_scale = scale
                        thickness = test_thickness
                        break
            
            # 只保留前3行
            lines = lines[:max_lines]
            
            # 计算每行的高度
            line_heights = []
            for line in lines:
                (_, text_height), baseline = cv2.getTextSize(line, font, font_scale, thickness)
                line_heights.append(text_height + baseline)
            
            # 计算总高度
            total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)
            
            # 绘制固定黑色矩形框背景
            cv2.rectangle(
                overlay,
                (box_x, box_y),
                (box_x + box_width, box_y + box_height),
                (0, 0, 0),
                -1
            )
            
            # 计算垂直居中位置
            start_y = box_y + padding + (box_height - padding * 2 - total_text_height) // 2
            
            # 绘制每一行文字（在矩形框内居中）
            current_y = start_y
            for i, line in enumerate(lines):
                (text_width, text_height), baseline = cv2.getTextSize(line, font, font_scale, thickness)
                text_x = box_x + box_width // 2 - text_width // 2  # 水平居中
                
                # 绘制文字（白色）
                cv2.putText(
                    overlay,
                    line,
                    (text_x, current_y + text_height),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA
                )
                
                current_y += line_heights[i] + line_spacing
        
        # 创建GIF动画帧（闪烁+光晕效果）
        frames = []
        num_frames = 10  # GIF帧数
        base_output_path = os.path.join(self.output_dir, "highlight")
        
        print(f"\n💾 正在创建GIF动画（{num_frames}帧，带光晕效果）...")
        
        # 创建多帧动画（闪烁+光晕效果）
        for i in range(num_frames):
            # 创建当前帧（从半透明背景开始，可以看到书架）
            # 注意：overlay已经包含书名，所以需要从原始背景开始重新绘制
            frame_with_glow = cv2.addWeighted(frame, 0.4, np.zeros_like(frame), 0.6, 0)
            
            # 计算闪烁强度（0.5到1.0之间循环）
            cycle = (i / num_frames) * 2 * np.pi
            intensity = 0.5 + 0.5 * np.sin(cycle)  # 0.5到1.0之间
            
            # 根据强度调整白色矩形的亮度
            white_intensity = int(255 * intensity)
            
            # 创建光晕mask
            glow_mask = np.zeros_like(frame_with_glow)
            
            # 绘制主区域（白色填充）
            if use_points:
                # 使用四点绘制多边形
                pts = np.array(pixel_points, np.int32)
                cv2.fillPoly(glow_mask, [pts], 
                           (white_intensity, white_intensity, white_intensity))
            else:
                # 使用矩形
                cv2.rectangle(glow_mask, (x, y), (x + w, y + h), 
                            (white_intensity, white_intensity, white_intensity), -1)
            
            # 绘制多层光晕（外层逐渐变透明）
            glow_size = int(30 * intensity)  # 光晕大小随强度变化
            for j in range(1, glow_size + 1, 2):
                # 计算当前层的透明度（外层更透明）
                alpha = max(0.1, 0.6 * (1 - j / glow_size) * intensity)
                glow_intensity = int(white_intensity * alpha)
                
                # 绘制外层光晕
                if use_points:
                    # 四点模式：沿着每条边向外扩展
                    expanded_points = []
                    num_points = len(pixel_points)
                    
                    for idx in range(num_points):
                        # 当前点
                        p1 = pixel_points[idx]
                        # 下一个点
                        p2 = pixel_points[(idx + 1) % num_points]
                        # 前一个点
                        p0 = pixel_points[(idx - 1) % num_points]
                        
                        # 计算两条边的方向向量
                        edge1 = [p1[0] - p0[0], p1[1] - p0[1]]  # 从p0到p1
                        edge2 = [p2[0] - p1[0], p2[1] - p1[1]]  # 从p1到p2
                        
                        # 归一化
                        len1 = np.sqrt(edge1[0]**2 + edge1[1]**2) + 1e-6
                        len2 = np.sqrt(edge2[0]**2 + edge2[1]**2) + 1e-6
                        edge1_norm = [edge1[0] / len1, edge1[1] / len1]
                        edge2_norm = [edge2[0] / len2, edge2[1] / len2]
                        
                        # 计算每条边的法向量（向外）
                        # 对于edge1，法向量是旋转90度（顺时针）
                        normal1 = [edge1_norm[1], -edge1_norm[0]]
                        # 对于edge2，法向量是旋转90度（顺时针）
                        normal2 = [edge2_norm[1], -edge2_norm[0]]
                        
                        # 使用两条法向量的平均方向
                        avg_normal = [(normal1[0] + normal2[0]) / 2, (normal1[1] + normal2[1]) / 2]
                        avg_len = np.sqrt(avg_normal[0]**2 + avg_normal[1]**2) + 1e-6
                        avg_normal = [avg_normal[0] / avg_len, avg_normal[1] / avg_len]
                        
                        # 向外扩展
                        expanded_x = int(p1[0] + avg_normal[0] * j)
                        expanded_y = int(p1[1] + avg_normal[1] * j)
                        expanded_points.append([expanded_x, expanded_y])
                    
                    # 绘制扩展后的多边形
                    if len(expanded_points) >= 3:
                        pts_expanded = np.array(expanded_points, np.int32)
                        cv2.fillPoly(glow_mask, [pts_expanded], 
                                   (glow_intensity, glow_intensity, glow_intensity))
                else:
                    # 矩形模式：直接扩展矩形
                    cv2.rectangle(glow_mask, 
                                 (x - j, y - j), 
                                 (x + w + j, y + h + j), 
                                 (glow_intensity, glow_intensity, glow_intensity), 
                                 2)
            
            # 应用高斯模糊创建柔和的光晕效果
            blur_size = int(15 * intensity)
            if blur_size > 0:
                blur_size = blur_size if blur_size % 2 == 1 else blur_size + 1  # 必须是奇数
                glow_blur = cv2.GaussianBlur(glow_mask, (blur_size, blur_size), 
                                             sigmaX=blur_size/3, sigmaY=blur_size/3)
            else:
                glow_blur = glow_mask
            
            # 将光晕效果叠加到背景上
            frame_with_glow = cv2.addWeighted(frame_with_glow, 1.0, glow_blur, 0.8, 0)
            
            # 绘制主区域（60%透明度，可以看到书架）
            white_overlay_frame = frame_with_glow.copy()
            if use_points:
                # 使用四点绘制多边形
                pts = np.array(pixel_points, np.int32)
                cv2.fillPoly(white_overlay_frame, [pts], 
                           (white_intensity, white_intensity, white_intensity))
            else:
                # 使用矩形
                cv2.rectangle(white_overlay_frame, (x, y), (x + w, y + h), 
                             (white_intensity, white_intensity, white_intensity), -1)
            # 将白色区域以60%透明度叠加（原图60% + 白色40%）
            frame_with_glow = cv2.addWeighted(frame_with_glow, 0.6, white_overlay_frame, 0.4, 0)
            
            # 重新绘制书名（固定宽度400，最多3行）
            if book_name:
                # 固定背景框大小（所有书名都使用相同大小）
                center_x = x + w // 2
                box_width = 600  # 固定宽度：600像素
                box_height = 180  # 固定高度：足够3行显示（与第一次绘制保持一致）
                box_x = center_x - box_width // 2
                box_y = max(50, y - box_height - 60)  # 在白色块上方至少60像素
                
                # 确保不超出图片边界
                box_x = max(10, min(box_x, self.width - box_width - 10))
                box_y = max(10, min(box_y, self.height - box_height - 10))
                
                # 固定字体大小
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.5
                thickness = 3
                max_lines = 3
                line_spacing = 8
                padding = 15  # 内边距
                
                # 可用宽度和高度（固定背景框内的可用空间）
                available_width = box_width - padding * 2
                
                # 分割长文本为多行（最多3行）
                words = book_name.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    (text_width, _), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
                    
                    if text_width <= available_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                            if len(lines) >= max_lines:
                                break
                        current_line = word
                
                if current_line and len(lines) < max_lines:
                    lines.append(current_line)
                
                # 如果超过3行，缩小字体以适应
                if len(lines) > max_lines:
                    # 尝试缩小字体
                    for scale in [1.2, 1.0, 0.8, 0.6]:
                        test_thickness = max(1, int(scale * 2))
                        test_lines = []
                        test_current_line = ""
                        
                        for word in words:
                            test_line = test_current_line + " " + word if test_current_line else word
                            (text_width, _), _ = cv2.getTextSize(test_line, font, scale, test_thickness)
                            
                            if text_width <= available_width:
                                test_current_line = test_line
                            else:
                                if test_current_line:
                                    test_lines.append(test_current_line)
                                    if len(test_lines) >= max_lines:
                                        break
                                test_current_line = word
                        
                        if test_current_line and len(test_lines) < max_lines:
                            test_lines.append(test_current_line)
                        
                        if len(test_lines) <= max_lines:
                            lines = test_lines
                            font_scale = scale
                            thickness = test_thickness
                            break
                
                # 只保留前3行
                lines = lines[:max_lines]
                
                # 计算每行的高度
                line_heights = []
                for line in lines:
                    (_, text_height), baseline = cv2.getTextSize(line, font, font_scale, thickness)
                    line_heights.append(text_height + baseline)
                
                # 计算总高度
                total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)
                
                # 绘制固定黑色矩形框背景
                cv2.rectangle(
                    frame_with_glow,
                    (box_x, box_y),
                    (box_x + box_width, box_y + box_height),
                    (0, 0, 0),
                    -1
                )
                
                # 计算垂直居中位置
                start_y = box_y + padding + (box_height - padding * 2 - total_text_height) // 2
                
                # 绘制每一行文字（在矩形框内居中）
                current_y = start_y
                for i, line in enumerate(lines):
                    (text_width, text_height), baseline = cv2.getTextSize(line, font, font_scale, thickness)
                    text_x = box_x + box_width // 2 - text_width // 2  # 水平居中
                    
                    # 绘制文字（白色）
                    cv2.putText(
                        frame_with_glow,
                        line,
                        (text_x, current_y + text_height),
                        font,
                        font_scale,
                (255, 255, 255),
                        thickness,
                cv2.LINE_AA
                    )
                    
                    current_y += line_heights[i] + line_spacing
            
            # 转换为RGB格式（PIL需要）
            frame_rgb = cv2.cvtColor(frame_with_glow, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
        
        # 保存静态图片（第一帧）
        static_output_path = base_output_path + ".jpg"
        success_static = cv2.imwrite(static_output_path, overlay)
        
        # 创建GIF动画
        gif_output_path = base_output_path + ".gif"
        saved_files = []
        
        try:
            from PIL import Image
            
            # 将numpy数组转换为PIL Image
            pil_frames = [Image.fromarray(f) for f in frames]
            
            # 保存为GIF（循环播放，每帧100ms）
            pil_frames[0].save(
                gif_output_path,
                save_all=True,
                append_images=pil_frames[1:],
                duration=100,  # 每帧100毫秒
                loop=0,  # 无限循环
                optimize=True
            )
            
            gif_size = os.path.getsize(gif_output_path)
            print(f"✅ GIF动画已保存: {gif_output_path} ({gif_size} 字节)")
            saved_files.append(gif_output_path)
            
        except ImportError:
            print("⚠️  Pillow未安装，无法创建GIF动画")
            print("   安装命令: pip install Pillow")
            if success_static:
                saved_files.append(static_output_path)
        except Exception as e:
            print(f"⚠️  创建GIF失败: {e}")
            import traceback
            traceback.print_exc()
            if success_static:
                saved_files.append(static_output_path)
        
        if success_static:
            static_size = os.path.getsize(static_output_path)
            print(f"✅ 静态图片已保存: {static_output_path} ({static_size} 字节)")
        
        print(f"\n{'='*60}")
        print(f"📚 找到书籍: {book_name}")
        if saved_files:
            print(f"✨ GIF动画已保存: {saved_files[0]}")
        print(f"   高亮区域: ({x}, {y}) 尺寸: {w}x{h}")
        print(f"   闪烁效果: 白色矩形闪烁动画")
        print(f"{'='*60}\n")
        
        # 尝试自动打开GIF（使用浏览器HTML页面，确保自动播放）
        if saved_files and os.path.exists(saved_files[0]):
            try:
                import subprocess
                import time
                
                open_path = saved_files[0]
                
                # 如果是GIF文件，创建HTML页面在浏览器中打开
                if open_path.endswith('.gif'):
                    # 获取绝对路径
                    abs_path = os.path.abspath(open_path)
                    gif_filename = os.path.basename(abs_path)
                    
                    # 创建HTML文件来显示GIF
                    html_path = os.path.join(self.output_dir, "highlight_viewer.html")
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Book Highlight - {book_name}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }}
        img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
    </style>
</head>
<body>
    <img src="{gif_filename}" alt="Book Highlight" />
</body>
</html>"""
                    
                    # 保存HTML文件
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    html_abs_path = os.path.abspath(html_path)
                    html_url = f"file://{html_abs_path}"
                    
                    print(f"   正在用浏览器打开GIF动画...")
                    
                    # 先关闭可能已打开的浏览器窗口（可选）
                    try:
                        subprocess.run(['killall', 'Preview'], check=False, capture_output=True, timeout=1)
                        time.sleep(0.1)
                    except:
                        pass
                    
                    # 尝试使用默认浏览器打开HTML
                    result = subprocess.run(['open', html_url], check=False, capture_output=True)
                    if result.returncode == 0:
                        print("   ✅ 已用浏览器打开GIF动画（自动播放）")
                    else:
                        # 如果失败，尝试指定浏览器
                        browsers = ['Safari', 'Google Chrome', 'Firefox', 'Microsoft Edge', 'Chromium']
                        opened = False
                        for browser in browsers:
                            try:
                                result = subprocess.run(['open', '-a', browser, html_url], 
                                                      check=False, capture_output=True, timeout=2)
                                if result.returncode == 0:
                                    print(f"   ✅ 已用 {browser} 打开GIF动画（自动播放）")
                                    opened = True
                                    break
                            except:
                                continue
                        
                        if not opened:
                            print(f"   ⚠️  无法用浏览器打开，请手动打开: {html_path}")
                            print(f"   或者直接打开GIF文件: {open_path}")
                else:
                    # 静态图片，使用Preview打开
                    print(f"   正在打开图片...")
                    result = subprocess.run(['open', '-a', 'Preview', open_path], check=False, capture_output=True)
                    if result.returncode == 0:
                        print("   ✅ 已打开图片")
                    else:
                        result = subprocess.run(['open', open_path], check=False, capture_output=True)
                        if result.returncode == 0:
                            print("   ✅ 已打开图片")
            except Exception as e:
                print(f"   ⚠️  打开GIF时出错: {e}")
                import traceback
                traceback.print_exc()
        
        success = len(saved_files) > 0
        
        self.current_highlight = {
            'position': (x, y, w, h),
            'book_name': book_name,
            'start_time': time.time()
        }
        self.highlight_start_time = time.time()
    
    def clear_highlight(self):
        """清除高亮，恢复原图"""
        if self.original_image is not None:
            output_path = os.path.join(self.output_dir, "highlight.jpg")
            cv2.imwrite(output_path, self.original_image)
            print("📸 已恢复原图")
        self.current_highlight = None
    
    def run(self, stop_event=None):
        """运行（简单模式不需要持续运行）"""
        pass
    
    def update_display(self):
        """更新显示（简单模式不需要）"""
        pass

