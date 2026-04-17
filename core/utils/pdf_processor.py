import fitz  # PyMuPDF
import os
import logging

logger = logging.getLogger("PdfProcessor")

class PdfProcessor:
    """
    将 PDF 页面转换为图像，以便 Gemini 进行视觉分析。
    """
    def __init__(self, output_dir="temp_images"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def pdf_to_images(self, pdf_path: str, max_pages=10) -> list:
        """
        将 PDF 的前 N 页转换为图像。
        Returns:
            图像路径列表。
        """
        image_paths = []
        try:
            doc = fitz.open(pdf_path)
            # 限制页数，避免处理过慢
            num_pages = min(len(doc), max_pages)
            
            base_name = os.path.basename(pdf_path).replace(".pdf", "")
            
            for i in range(num_pages):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x 缩放以提高清晰度
                img_path = os.path.join(self.output_dir, f"{base_name}_p{i}.png")
                pix.save(img_path)
                image_paths.append(img_path)
                
            doc.close()
            return image_paths
        except Exception as e:
            logger.error(f"PDF 转换图像失败: {str(e)}")
            return []
