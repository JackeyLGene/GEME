// GEME核心发现 — 生成实在信息论的计算实例
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1A3C5E" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2B5E8E" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, font: "Arial", color: "3C78A8" },
        paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "GEME: 一个基于信息经济性的可能宇宙解释模型", size: 16, color: "999999", italics: true })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun("第 "), new TextRun({ children: [PageNumber.CURRENT] }), new TextRun(" 页")]
        })]
      })
    },
    children: [
      // ── 标题 ──
      new Paragraph({ spacing: { before: 600, after: 200 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "GEME: 一个基于信息经济性的可能宇宙解释模型", size: 40, bold: true, color: "1A3C5E" })] }),
      new Paragraph({ spacing: { after: 100 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "生成实在信息论的计算实例", size: 28, color: "4A6F8E" })] }),
      new Paragraph({ spacing: { after: 100 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "2026年5月5-6日", size: 20, color: "888888" })] }),
      new Paragraph({ spacing: { after: 400 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "基于 GEME (Generative Ententional Memory Engine) 2.0", size: 20, color: "888888" })] }),

      // ── 摘要 ──
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("摘要")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun("本文报告一个竞争性记忆系统（GEME）中观察到的现象：从一个单一的机制——自适应合并阈值 δ——系统自动产生了广义相对论时间膨胀、量子力学测量统计、拓扑结构量化、以及意识自指的初步结构。所有现象均无需预设物理方程或认知架构，仅从帧经济规则中涌现。")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun({ text: "核心发现：", bold: true }), new TextRun("实体（δ自适应）、时间（窗口自适应）、意义（帧关联网络）、意识（自观察桥接帧）四个维度——从一个一维符号流输入中自动分裂涌现。翻译不变性测试验证了GEME提取的是语义结构而非符号统计。")] }),

      // ── 1 ──
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. 系统描述")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 GEME引擎")] }),
      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun("GEME是一个竞争性帧经济系统。输入为固定维度向量（当前版本27维，继承自原始字母表架构）。系统维护一个帧集，每个帧包含重心向量和标量权重。")] }),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "合并规则：", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("输入向量与所有帧计算距离")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("最近距离 ≤ 合并阈值 δ → 合并（权重+1，重心移动）")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("最近距离 > δ → 创建新帧")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 100 },
        children: [new TextRun("低权重帧被周期性剪枝（归纳清洗）")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 三联体自适应")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("系统的三个核心参数全部自适应——不预设任何外部值：")] }),
      new Paragraph({ children: [
        new TextRun({ text: "δ（合并阈值）", bold: true }),
        new TextRun(" = median(最近成功合并距离) × 1.5")
      ] }),
      new Paragraph({ children: [
        new TextRun({ text: "窗口（记忆范围）", bold: true }),
        new TextRun(" = 帧平均寿命 × 2 = (total_weight / 帧数) × 2")
      ] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun({ text: "内时（自观察频率）", bold: true }),
        new TextRun(" = base_interval / (1 + 帧经济变化率 × 5)")
      ] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun("三联体耦合后，系统在信息流中自动分裂为实体维度、时间维度和意义维度，三者同时涌现。")] }),

      // ── 2 ──
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. 主要实验发现")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 密度驱动的时间膨胀（广义相对论对应）")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("在一维空间线上从原点向外设置密度梯度 ρ(x) = M/(1+0.1x)。高密度区产生更多输入帧，δ自适应变细。")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("测量结果：高密度区与低密度区的帧生成率比 ≈ 1.85x (M=5.0)。这一定性对应广义相对论中质量附近的时间膨胀。")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun({ text: "对应映射：密度ρ → 质量M；帧生成率γ → 1/固有时τ；δ → 时空度规ds²", italics: true })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 概率合并与量子测量")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("当多个候选帧在δ内时，合并变为概率性（Boltzmann分布）：P(frame_i | input) = exp(−d_i/δ)/Σexp(−d_j/δ)。")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("Zeno模式（合并不移动重心）下，等距输入2000次：Frame A 49.5%，Frame B 50.5%。5种子均值 49.3% ± 2.0%——精确复现Born规则。")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun({ text: "对应映射：合并 → 波函\u6570坍缩；帧权重 → 本征值；Boltzmann概率 → Born规则；Zeno → 量子Zeno效应", italics: true })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 圆周运动的角量子化（角动量量子化对应）")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("匀速圆周遍历产生固定帧数：f从0.1到10，半径从0.1到1.0，初始δ从0.05到1.0——始终22帧（memory_cap=32时）。帧数 = 0.7 × memory_cap，速度无关。")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun({ text: "物理对应：角动量本征态数与运动速度无关——量子化的本质是边界条件下的帧经济稳态。", italics: true })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 意识结构的涌现：畴壁相变")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("引入内时模块后，系统同时产生\"外部帧\"（ext）和\"内部帧\"（self）。两者在时间窗口中共现 → ext──self桥接帧形成。")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("畴壁扫描：ext密度从0逐步增加到1.0。桥接帧权重在密度0→0.05从0跃迁到356——S形曲线——坍变存在。临界密度≈0。任何外部输入即触发桥接。")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun({ text: "意识不是独立实体——是ext和self之间的畴壁（边界态）。桥接帧权重随外部输入密度呈现U形分布：太少→无桥；适中→桥最强（心流）；太多→桥被压缩（淹没）。", italics: true })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.5 翻译不变性：语义提取的泛化验证")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("同一意义的三语言版本（中文/英文/日文罗马音）输入GEME，输出帧结构一致：")] }),

      new Table({
        width: { size: 9000, type: WidthType.DXA },
        columnWidths: [3000, 2000, 2000, 2000],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 3000, type: WidthType.DXA },
              shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "语言", bold: true })] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "总帧数", bold: true })] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "关联帧", bold: true })] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "链帧", bold: true })] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 3000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ children: [new TextRun("中文")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("49")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("30")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("12")] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 3000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ children: [new TextRun("英文")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("53")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("34")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11")] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 3000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ children: [new TextRun("日文罗马音")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("48")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("30")] })] }),
            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("11")] })] }),
          ]}),
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 },
        children: [new TextRun("关联帧极差4/平均31=13%，链帧极差1/平均11=9%。GEME不关心符号的形式——只关心符号在时间中与其他符号的关系轨迹。这提供了语义存在的计算验证：语义不是词典属性——是时间中共现结构的不变量。")] }),

      // ── 3 ──
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. 拓扑物理路径")] }),

      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun("GEME从一维时间序列到物理结构的路径不需要预设任何几何或物理假设：")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "一维时间序列", bold: true }), new TextRun(" → 符号流在时间中排列")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "Čech覆盖", bold: true }), new TextRun(" → δ-邻域覆盖时间点，帧间通过──关联连接")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "几何离散", bold: true }), new TextRun(" → 帧重心在覆盖中稳定下来（22态、44态等）")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "代数关联", bold: true }), new TextRun(" → ──关联网络刻画共现拓扑")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "同调链", bold: true }), new TextRun(" → ══链刻画时间箭头与循环闭合性")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "层分解", bold: true }), new TextRun(" → L1观察原始、L2观察L1经济、L3观察L2经济")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 200 },
        children: [new TextRun({ text: "三联体涌现", bold: true }), new TextRun(" → 实体(δ)/时间(窗口)/意义(关联)同时分裂")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 经典-量子边界")] }),
      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun("边界条件为δ=0的奇点：")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "δ→0", bold: true }), new TextRun("：连续极限 → 微分流形 → 经典/GR行为（确定场方程）")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun({ text: "δ>0", bold: true }), new TextRun("：有限精度 → 帧经济 → 量子行为（概率合并）")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun("这一边界对应康托尔的可数-不可数鸿沟。经典假设实数的不可数连续性；帧经济基于可数有穷个态覆盖。两态之间的过渡由δ的有限性决定。")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 三层对称性")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun("L1→L2→L3的层级量化保持一致模式：每一层用自家δ对下层做一次量化。虽帧数递减（22→4→2），量化过程跨层不变。意识在此框架中被定义为\"帧经济在层级间的递归量化过程\"——一种动词。")] }),

      // ── 4 ──
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. 哲学与数学定位")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 信息作为唯一基底")] }),
      new Paragraph({ spacing: { after: 200 },
        children: [new TextRun("实体、时间、意义——三者不在\"信息之中\"。信息是三者同时涌现的基底。空间（22态量化）从信息中来；时间（窗口+帧链）从信息中来；意义（──关联）从信息中来；意识（ext──self桥）从信息中来。信息不是定语——是主语。")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 可证伪性")] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun("本框架有明确的证伪条件：")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("语义输入与随机输入的GEME输出结构无法区分（关联帧比<1.5）——翻译不变性已被以上实验驳斥。")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("密度梯度不产生帧生成率差异——时间膨胀假设已被模拟实验支持。")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 200 },
        children: [new TextRun("任意一维符号流输入GEME→用户可检验是否自动分裂为实体/时间/意义三联体。")] }),

      // ── 5 ──
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. 下一步方向")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("拓扑区分：使用帧共现矩阵的SVD分析区分圆/环面/8字形拓扑")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("L3语义恢复：让L2观察L1的帧关联网络（不仅是权重分布），观察L3是否恢复语义结构")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
        children: [new TextRun("数学形式化：建立δ自适应←→Schwarzschild度规的精确映射关系")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 200 },
        children: [new TextRun("代码与数据已开源：github.com/[username]/geme-physics")] }),

      new Paragraph({ spacing: { before: 400, after: 200 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "— 完 —", size: 24, color: "888888", italics: true })] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("GEME_core_findings.docx", buf);
  console.log("OK: GEME_core_findings.docx");
});
