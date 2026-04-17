const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const replicateBtn = document.getElementById('replicate-btn');
const btnText = document.getElementById('btn-text');
const previewContainer = document.getElementById('preview-container');
const resultArea = document.getElementById('result-area');
const stopBtn = document.getElementById('stop-btn');
const langToggle = document.getElementById('lang-toggle');
const langText = document.getElementById('lang-text');

const modeUpload = document.getElementById('mode-upload');
const modeArxiv = document.getElementById('mode-arxiv');
const uploadContainer = document.getElementById('upload-container');
const arxivContainer = document.getElementById('arxiv-container');
const arxivInput = document.getElementById('arxiv-input');
const frameworkSelect = document.getElementById('framework-select');

let currentMode = 'upload'; // 'upload' or 'arxiv'
let currentLang = 'en'; // 'en' or 'zh'

const translations = {
    en: {
        subtitle: "Professional AI Paper Replication Engine",
        dropTitle: "Drag & drop paper excerpts here",
        dropDesc: "Upload architecture diagrams, formulas, or method descriptions for concurrent analysis",
        arxivTitle: "Enter ArXiv ID",
        arxivDesc: "Download paper automatically and extract all algorithm blocks",
        targetFramework: "Target Framework",
        startBtn: "Start Replication",
        runningBtn: "Running Engine...",
        stopBtn: "Emergency Stop Engine",
        resultOverview: "Research Overview",
        resultCode: "Implementation Code",
        resultInsights: "Key Engineering Insights",
        copyBtn: "Copy Source",
        copiedBtn: "Copied!",
        alertUpload: "Please upload paper excerpts first.",
        alertArxiv: "Please enter an ArXiv ID.",
        alertFail: "Analysis failed: ",
        alertConnect: "Could not connect to PureRepro Backend!",
        alertResult: "Could not retrieve final results.",
        // Progress Messages
        progInit: "Initializing...",
        progSaving: "Saving files...",
        progAnalyzing: "Analyzing with Gemini...",
        progDownloading: "Downloading PDF...",
        progConverting: "Converting PDF...",
        progScanning: "Scanning page ",
        progFound: "Algorithm found!",
        progExtracting: "Extracting LaTeX...",
        progGenerating: "Generating code...",
        progValidating: "Validating...",
        progSuccess: "Success!",
        progCompleted: "COMPLETED"
    },
    zh: {
        subtitle: "专业级 AI 论文复现引擎",
        dropTitle: "拖拽论文截图到此处",
        dropDesc: "上传模型架构图、数学公式或方法描述进行并发分析",
        arxivTitle: "输入 ArXiv ID",
        arxivDesc: "自动下载论文并提取所有算法逻辑",
        targetFramework: "目标框架",
        startBtn: "开始复现",
        runningBtn: "引擎运行中...",
        stopBtn: "紧急停止引擎",
        resultOverview: "研究概览",
        resultCode: "实现代码",
        resultInsights: "核心工程洞察",
        copyBtn: "复制源码",
        copiedBtn: "已复制!",
        alertUpload: "请先上传论文截图。",
        alertArxiv: "请输入 ArXiv ID。",
        alertFail: "分析失败: ",
        alertConnect: "无法连接到 PureRepro 后端！",
        alertResult: "无法获取最终结果。",
        // Progress Messages
        progInit: "初始化中...",
        progSaving: "保存文件中...",
        progAnalyzing: "Gemini 分析中...",
        progDownloading: "下载 PDF 中...",
        progConverting: "PDF 转换中...",
        progScanning: "正在扫描第 ",
        progFound: "发现算法逻辑！",
        progExtracting: "提取 LaTeX 中...",
        progGenerating: "生成代码中...",
        progValidating: "维度/逻辑验证中...",
        progSuccess: "验证成功！",
        progCompleted: "已完成"
    }
};

function translateProgress(msg) {
    const t = translations[currentLang];
    if (msg.includes("Initializing")) return t.progInit;
    if (msg.includes("Saving")) return t.progSaving;
    if (msg.includes("Analyzing")) return t.progAnalyzing;
    if (msg.includes("Downloading")) return t.progDownloading;
    if (msg.includes("Converting")) return t.progConverting;
    if (msg.includes("Scanning page")) return t.progScanning + msg.split("page")[1];
    if (msg.includes("found")) return t.progFound;
    if (msg.includes("Extracting")) return t.progExtracting;
    if (msg.includes("Generating")) return t.progGenerating;
    if (msg.includes("Validating") || msg.includes("Verifying")) return t.progValidating;
    if (msg.includes("Success")) return t.progSuccess;
    if (msg.includes("COMPLETED")) return t.progCompleted;
    return msg;
}

function updateLanguageUI() {
    const t = translations[currentLang];
    langText.innerText = currentLang === 'en' ? 'English' : '中文';
    
    document.getElementById('t-subtitle').innerText = t.subtitle;
    document.getElementById('t-drop-title').innerText = t.dropTitle;
    document.getElementById('t-drop-desc').innerText = t.dropDesc;
    document.getElementById('t-arxiv-title').innerText = t.arxivTitle;
    document.getElementById('t-arxiv-desc').innerText = t.arxivDesc;
    document.getElementById('t-target-framework').innerText = t.targetFramework;
    document.getElementById('btn-text').innerText = t.startBtn;
    document.getElementById('t-stop-engine').innerText = t.stopBtn;
    document.getElementById('t-result-overview').innerText = t.resultOverview;
    document.getElementById('t-result-code').innerText = t.resultCode;
    document.getElementById('t-result-insights').innerText = t.resultInsights;
    document.getElementById('t-copy-btn').innerText = t.copyBtn;

    // Update buttons with data attributes
    document.querySelectorAll('[data-en]').forEach(el => {
        el.innerText = el.getAttribute(`data-${currentLang}`);
    });
}

langToggle.onclick = () => {
    currentLang = currentLang === 'en' ? 'zh' : 'en';
    updateLanguageUI();
};

// --- Mode Switching ---
modeUpload.onclick = () => {
    currentMode = 'upload';
    modeUpload.className = "px-6 py-2 rounded-full font-bold transition-all bg-slate-900 text-white shadow-lg";
    modeArxiv.className = "px-6 py-2 rounded-full font-bold transition-all bg-white text-slate-600 border border-slate-200 hover:bg-slate-50";
    uploadContainer.classList.remove('hidden');
    arxivContainer.classList.add('hidden');
};

modeArxiv.onclick = () => {
    currentMode = 'arxiv';
    modeArxiv.className = "px-6 py-2 rounded-full font-bold transition-all bg-slate-900 text-white shadow-lg";
    modeUpload.className = "px-6 py-2 rounded-full font-bold transition-all bg-white text-slate-600 border border-slate-200 hover:bg-slate-50";
    arxivContainer.classList.remove('hidden');
    uploadContainer.classList.add('hidden');
};

const overviewOutput = document.getElementById('overview-output');
const codeOutput = document.getElementById('code-output');
const insightsOutput = document.getElementById('insights-output');

const progressContainer = document.getElementById('progress-container');
const progressStatus = document.getElementById('progress-status');
const progressPercent = document.getElementById('progress-percent');
const progressBar = document.getElementById('progress-bar');
const progressLog = document.getElementById('progress-log');

let selectedFiles = [];

// --- Progress Tracking Helper ---
function startProgressTracking(taskId, onComplete) {
    progressContainer.classList.remove('hidden');
    stopBtn.classList.remove('hidden'); // Show stop button
    progressLog.innerHTML = '';
    
    const eventSource = new EventSource(`/progress/${taskId}`);
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.message === "COMPLETED") {
            eventSource.close();
            progressContainer.classList.add('hidden');
            stopBtn.classList.add('hidden');
            if (onComplete) onComplete();
            return;
        }

        if (data.message.startsWith("FAILED")) {
            eventSource.close();
            progressContainer.classList.add('hidden');
            stopBtn.classList.add('hidden');
            alert(data.message);
            if (onComplete) onComplete(new Error(data.message));
            return;
        }
        
        const translatedMsg = translateProgress(data.message);

        // Update UI
        progressStatus.innerText = translatedMsg;
        const percent = Math.round((data.step / data.total_steps) * 100);
        progressPercent.innerText = `${percent}%`;
        progressBar.style.width = `${percent}%`;
        
        // Add log entry
        const logEntry = document.createElement('div');
        logEntry.className = "mb-1 border-l-2 border-blue-200 pl-2";
        logEntry.innerText = `[${new Date().toLocaleTimeString()}] ${translatedMsg}`;
        progressLog.appendChild(logEntry);
        progressLog.scrollTop = progressLog.scrollHeight;
    };

    eventSource.onerror = () => {
        eventSource.close();
    };

    return eventSource;
}

// --- Emergency Stop Logic ---
stopBtn.onclick = async () => {
    try {
        await fetch('/stop', { method: 'POST' });
        alert(currentLang === 'en' ? "Stop signal sent!" : "停止信号已发送！");
        location.reload(); // Simple way to reset UI state
    } catch (err) {
        console.error("Stop failed:", err);
    }
};

// --- UI Interaction Logic ---
dropZone.onclick = () => fileInput.click();

dropZone.ondragover = (e) => { 
    e.preventDefault(); 
    dropZone.classList.add('drag-over'); 
};

dropZone.ondragleave = () => dropZone.classList.remove('drag-over');

dropZone.ondrop = (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
};

fileInput.onchange = (e) => handleFiles(e.target.files);

/**
 * Renders thumbnail previews of uploaded images
 */
function handleFiles(files) {
    selectedFiles = Array.from(files);
    previewContainer.innerHTML = '';
    selectedFiles.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = "h-24 w-24 object-cover rounded-xl border-2 border-white shadow-md transform hover:rotate-3 transition";
            previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
}

// --- Core Parsing Logic ---

/**
 * Splits the raw AI Markdown response into structured segments
 */
function parsePureReproResponse(text) {
    const overviewMatch = text.match(/##\s*1\.\s*Overview([\s\S]*?)(?=##\s*2\.)/i);
    const codeMatch = text.match(/##\s*2\.\s*Implementation Code([\s\S]*?)(?=##\s*3\.)/i);
    const insightsMatch = text.match(/##\s*3\.\s*Key Engineering Insights([\s\S]*)/i);

    return {
        overview: overviewMatch ? overviewMatch[1].trim() : "Analysis complete. Review the sections below.",
        code: codeMatch ? codeMatch[1].trim() : text, 
        insights: insightsMatch ? insightsMatch[1].trim() : "No specific insights extracted."
    };
}

/**
 * Sanitizes code blocks by stripping Markdown triple-backticks
 */
function cleanCodeBlocks(codeText) {
    return codeText.replace(/```[a-z]*\n?/gi, '').replace(/```/g, '').trim();
}

/**
 * A helper to render content by protecting LaTeX from Markdown interference
 * FIXED: Ensures placeholder replacement handles special regex characters correctly
 */
function renderContentWithMath(element, rawText, isInline = false) {
    const latexBlocks = [];
    // 1. Extract and hide LaTeX blocks to protect them from marked.js
    // Use a unique string that won't be mangled by marked.js
    const placeholderText = rawText.replace(/(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/g, (match) => {
        latexBlocks.push(match);
        return `@@LATEX${latexBlocks.length - 1}@@`;
    });

    // 2. Render the surrounding Markdown
    let renderedHtml = isInline ? marked.parseInline(placeholderText) : marked.parse(placeholderText);

    // 3. Put the raw LaTeX back into the rendered HTML
    // Fixed with a safer split/join or loop to avoid regex substitution issues
    latexBlocks.forEach((block, i) => {
        const target = `@@LATEX${i}@@`;
        renderedHtml = renderedHtml.split(target).join(block);
    });

    element.innerHTML = renderedHtml;
}

// --- Global Action Handlers ---
window.copyCode = () => {
    const code = codeOutput.innerText;
    const t = translations[currentLang];
    navigator.clipboard.writeText(code).then(() => {
        const copyBtn = document.getElementById('t-copy-btn');
        const originalText = copyBtn.innerText;
        copyBtn.innerText = t.copiedBtn;
        setTimeout(() => copyBtn.innerText = originalText, 2000);
    });
};

// --- Execution Flow & API Integration ---
replicateBtn.onclick = async () => {
    const t = translations[currentLang];
    if (currentMode === 'upload' && selectedFiles.length === 0) {
        alert(t.alertUpload);
        return;
    }
    if (currentMode === 'arxiv' && !arxivInput.value.trim()) {
        alert(t.alertArxiv);
        return;
    }

    // UI State: Loading Initialization
    replicateBtn.disabled = true;
    btnText.innerHTML = `<span class="loader"></span>${t.runningBtn}`;
    resultArea.classList.add('hidden');
    
    // Reset any previous shutdown signal
    await fetch('/reset', { method: 'POST' });

    // Generate a unique task ID for this session
    const taskId = 'task_' + Math.random().toString(36).substr(2, 9);

    // 定义任务完成后的回调逻辑
    const onTaskFinished = async (error) => {
        if (error) {
            replicateBtn.disabled = false;
            btnText.innerText = t.startBtn;
            return;
        }

        try {
            // 任务在后台完成后，主动去请求最终结果
            const response = await fetch(`/result/${taskId}`);
            const data = await response.json();

            if (data.status === "success") {
                const result = parsePureReproResponse(data.analysis);
                renderContentWithMath(overviewOutput, result.overview);
                
                const insightLines = result.insights.split('\n').filter(l => l.trim());
                insightsOutput.innerHTML = '';
                insightLines.forEach(line => {
                    const container = document.createElement('div');
                    container.className = "flex items-start mb-2";
                    container.innerHTML = `<span class="mr-2 text-amber-500">•</span><span class="insight-text"></span>`;
                    const textSpan = container.querySelector('.insight-text');
                    renderContentWithMath(textSpan, line.replace(/^[*-]\s*/, ''), true);
                    insightsOutput.appendChild(container);
                });

                codeOutput.innerText = cleanCodeBlocks(result.code);
                resultArea.classList.remove('hidden');

                setTimeout(() => {
                    if (typeof renderMathInElement === 'function') {
                        renderMathInElement(resultArea, {
                            delimiters: [
                                {left: '$$', right: '$$', display: true},
                                {left: '$', right: '$', display: false},
                                {left: '\\(', right: '\\)', display: false},
                                {left: '\\[', right: '\\]', display: true}
                            ],
                            throwOnError: false, trust: true, strict: false
                        });
                    }
                }, 100);

                resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                alert(t.alertResult);
            }
        } catch (err) {
            console.error("Result Fetch Error:", err);
            alert(t.alertResult);
        } finally {
            replicateBtn.disabled = false;
            btnText.innerText = t.startBtn;
        }
    };

    startProgressTracking(taskId, onTaskFinished);

    try {
        if (currentMode === 'upload') {
            const formData = new FormData();
            selectedFiles.forEach(file => formData.append('files', file));
            formData.append('output_name', 'model.py');
            formData.append('framework', frameworkSelect.value);
            formData.append('task_id', taskId);

            await fetch('/replicate', { method: 'POST', body: formData });
        } else {
            await fetch('/replicate_arxiv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    arxiv_id: arxivInput.value.trim(),
                    framework: frameworkSelect.value,
                    task_id: taskId
                })
            });
        }
    } catch (error) {
        console.error("Submission Error:", error);
        alert(t.alertConnect);
        replicateBtn.disabled = false;
        btnText.innerText = t.startBtn;
    }
};

// Initialize language
updateLanguageUI();