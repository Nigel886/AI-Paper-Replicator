import arxiv
import os
import logging

logger = logging.getLogger("ArxivDownloader")

class ArxivDownloader:
    """
    通过 ArXiv ID 下载 PDF 文件并保存到本地。
    """
    def __init__(self, download_dir="downloads"):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def download(self, arxiv_id: str) -> str:
        """
        下载 PDF。
        Args:
            arxiv_id: ArXiv 编号 (例如 '2305.16300')
        Returns:
            本地 PDF 文件路径。
        """
        try:
            logger.info(f"正在检索 ArXiv ID: {arxiv_id}")
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(client.results(search))
            
            # 清理 ID 中的斜杠以用作文件名
            safe_id = arxiv_id.replace("/", "_")
            file_path = paper.download_pdf(dirpath=self.download_dir, filename=f"{safe_id}.pdf")
            logger.info(f"下载成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            raise e
