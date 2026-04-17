from fastmcp import FastMCP
import os
import sys
import logging
from core.engine import PaperReplicator
from core.processors.dual_stage_processor import DualStageProcessor
from core.utils.arxiv_downloader import ArxivDownloader
from core.utils.pdf_processor import PdfProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PureRepro-MCP")

# 初始化 FastMCP
mcp = FastMCP("PureRepro")

# 初始化核心引擎
engine = PaperReplicator()
processor = DualStageProcessor(engine)
arxiv_downloader = ArxivDownloader()
pdf_processor = PdfProcessor()

@mcp.tool()
def replicate_from_arxiv(arxiv_id: str) -> str:
    """
    通过 ArXiv ID 自动下载论文，识别其中的算法框图 (Algorithms)，并将其转化为 Python 类定义。
    
    Args:
        arxiv_id: ArXiv 编号 (例如 '2305.16300')
    """
    try:
        # 1. 下载 PDF
        pdf_path = arxiv_downloader.download(arxiv_id)
        
        # 2. PDF 转图像 (前 10 页)
        image_paths = pdf_processor.pdf_to_images(pdf_path, max_pages=10)
        
        results = []
        results.append(f"## ArXiv ID: {arxiv_id} 自动复现报告\n")
        
        found_algorithm = False
        for img_path in image_paths:
            # 3. 询问 Gemini 该页是否有算法框图
            check_prompt = "请判断这张论文页面中是否包含算法伪代码框图 (Algorithm/Pseudocode)？只需回答'是'或'否'。"
            is_algo = engine.infer(img_path, check_prompt)
            
            if "是" in is_algo or "Yes" in is_algo:
                found_algorithm = True
                page_num = img_path.split("_p")[-1].split(".")[0]
                results.append(f"### 发现算法：第 {int(page_num)+1} 页")
                
                # 4. 使用 DualStageProcessor 处理该页
                # 调整 prompt 使其输出为 Python Class
                processor.action_b_template = (
                    "Convert the following LaTeX/Pseudocode into a clean Python Class.\n"
                    "Formula/Algo: {latex}\n"
                    "Requirements:\n"
                    "1. Use a Class structure, implement the main logic in a method.\n"
                    "2. Include docstrings and shape annotations.\n"
                    "3. Provide the Shape Dictionary and Logic Spec JSONs at the end."
                )
                
                res = processor.process(img_path)
                
                if res.get("validated"):
                    results.append(f"```python\n{res.get('code')}\n```")
                    results.append("✅ **自动验证通过**")
                else:
                    results.append(f"```python\n{res.get('code')}\n```")
                    results.append(f"⚠️ **验证未完全通过**: {res.get('error', '未知错误')}")
                
                results.append("---\n")
        
        if not found_algorithm:
            return f"在论文 {arxiv_id} 的前 10 页中未检测到明显的算法框图。"
            
        return "\n".join(results)
        
    except Exception as e:
        return f"自动复现流程失败：{str(e)}"

@mcp.tool()
def analyze_equation(image_path: str) -> str:
    """
    分析论文插图中的数学公式，并将其转换为 LaTeX 和经过维度验证的 PyTorch 代码。
    
    Args:
        image_path: 论文插图的本地绝对路径。
    """
    if not os.path.exists(image_path):
        return f"错误：找不到文件 {image_path}"
    
    logger.info(f"正在分析公式：{image_path}")
    try:
        result = processor.process(image_path)
        
        output = []
        output.append("### 1. LaTeX 公式")
        output.append(f"```latex\n{result.get('latex')}\n```")
        
        output.append("\n### 2. PyTorch 代码实现")
        output.append(f"```python\n{result.get('code')}\n```")
        
        if result.get("validated"):
            output.append("\n✅ **维度验证通过**：该代码已通过 torch.randn 静态检查。")
        else:
            output.append(f"\n❌ **维度验证失败**：\n```\n{result.get('error')}\n```")
            output.append("\n提示：AI 已尝试自动修复但未成功，请检查公式复杂度。")
            
        return "\n".join(output)
    except Exception as e:
        return f"处理过程中发生异常：{str(e)}"

@mcp.tool()
def extract_architecture_graph(image_path: str) -> str:
    """
    提取论文中的模型架构图，并尝试生成其逻辑描述。
    
    Args:
        image_path: 架构图的本地绝对路径。
    """
    # 目前先实现一个基础的视觉描述逻辑
    prompt = "请详细描述这张模型架构图的层级结构、输入输出维度以及关键组件之间的连接关系。"
    try:
        response = engine.infer(image_path, prompt)
        return f"### 模型架构分析\n\n{response}"
    except Exception as e:
        return f"架构分析失败：{str(e)}"

@mcp.tool()
def read_and_fix_error(error_log_path: str, source_code_path: str) -> str:
    """
    读取本地报错日志和源代码，结合论文背景进行自动修复分析。
    
    Args:
        error_log_path: 错误日志文件的路径。
        source_code_path: 对应的源代码文件路径。
    """
    try:
        with open(error_log_path, 'r', encoding='utf-8') as f:
            error_log = f.read()
        with open(source_code_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            
        prompt = (
            f"我的 PyTorch 代码运行报错了。\n\n"
            f"--- 源代码 ---\n{source_code}\n\n"
            f"--- 错误日志 ---\n{error_log}\n\n"
            f"请根据报错信息修改代码，确保张量维度匹配。"
        )
        
        # 使用引擎进行修复建议
        response = engine._generate_with_retry(prompt)
        return f"### 修复建议\n\n{response.text}"
    except Exception as e:
        return f"修复分析失败：{str(e)}"

if __name__ == "__main__":
    mcp.run()
