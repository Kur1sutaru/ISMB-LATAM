// Build the bilingual lecture slides (English + Spanish) for the tutorial.
//   node tools/build_slides.js            -> slides/en/*.pptx, slides/es/*.pptx
// Requires pptxgenjs, react-icons, react, react-dom, sharp.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const SKILL = process.env.PPTX_SKILL || "/mnt/skills/public/pptx";
const { applyTheme } = require(path.join(SKILL, "scripts/apply_theme.js"));

const ROOT = path.resolve(__dirname, "..");
const THEME = {
  name: "Cells to Clusters",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "17262B", lt1: "FFFFFF", dk2: "0B3C49", lt2: "EAF4F3",
    accent1: "2A9D8F", accent2: "E76F51", accent3: "F4A261", accent4: "264653",
    accent5: "8AB17D", accent6: "6C5B7B", hlink: "1D7874", folHlink: "6C5B7B",
  },
};
const HEX = THEME.colors;
const MUTED = "5B6B70";

// ---------------------------------------------------------------- helpers
const iconCache = {};
async function icon(name, color = "FFFFFF") {
  const key = name + color;
  if (!iconCache[key]) {
    const svg = ReactDOMServer.renderToStaticMarkup(
      React.createElement(fa[name], { color: "#" + color, size: 256 }));
    const buf = await sharp(Buffer.from(svg)).png().toBuffer();
    iconCache[key] = "image/png;base64," + buf.toString("base64");
  }
  return iconCache[key];
}

async function build(lang) {
  const L = (t) => (typeof t === "string" ? t : t[lang]);
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
  pres.title = L({ en: "From Cells to Clusters", es: "De Células a Clústeres" });
  pres.author = "Gerda Cristal Villalba Silva";
  pres.subject = "ISCB-LATAM SolBio SPBBC 2026 tutorial";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  const footer = L({ en: "ISCB-LATAM SolBio SPBBC 2026 · From Cells to Clusters",
                     es: "ISCB-LATAM SolBio SPBBC 2026 · De Células a Clústeres" });

  pres.defineSlideMaster({
    title: "Title", background: { color: HEX.dk2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.7, w: 11.7, h: 1.9, fontSize: 44, align: "left",
          bold: true, color: C.background1, valign: "bottom", fontFace: THEME.headFontFace }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.8, w: 11.7, h: 2.6, fontSize: 20,
          color: "CFE8E4", valign: "top" }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "Section", background: { color: HEX.dk2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.5, w: 11.7, h: 1.3, fontSize: 40,
          bold: true, color: C.background1, valign: "bottom", fontFace: THEME.headFontFace }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.95, w: 11.7, h: 1.6, fontSize: 20,
          color: "CFE8E4", valign: "top" }, text: "" } },
    ],
    slideNumber: { x: 12.3, y: 6.95, w: 0.6, h: 0.35, fontSize: 10, color: "CFE8E4", align: "right" },
  });
  pres.defineSlideMaster({
    title: "Content", background: { color: HEX.lt1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.3, w: 12.1, h: 0.95, fontSize: 32,
          bold: true, color: C.text2, valign: "middle", fontFace: THEME.headFontFace }, text: "" } },
      { text: { text: footer, options: { x: 0.6, y: 6.95, w: 8, h: 0.35, fontSize: 10, color: MUTED } } },
    ],
    slideNumber: { x: 12.3, y: 6.95, w: 0.6, h: 0.35, fontSize: 10, color: MUTED, align: "right" },
  });

  let section = null;
  const add = (master) => pres.addSlide({ masterName: master, sectionTitle: section });
  const newSection = (t) => { section = L(t); pres.addSection({ title: section }); };
  const notes = (s, t) => s.addNotes(L(t));
  const tb = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, ...o });

  async function circleIcon(s, name, x, y, d, fill) {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
    s.addImage({ data: await icon(name), x: x + d * 0.25, y: y + d * 0.25, w: d * 0.5, h: d * 0.5 });
  }

  async function card(s, opts) {
    const { x, y, w, h, iconName, iconHex = HEX.accent1, title, body, fill = C.background2 } = opts;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill },
      line: { color: fill } });
    let ty = y + 0.25;
    if (iconName) {
      await circleIcon(s, iconName, x + 0.25, y + 0.25, 0.65, iconHex);
      tb(s, L(title), { x: x + 1.05, y: y + 0.25, w: w - 1.3, h: 0.65, fontSize: 17, bold: true,
        color: C.text2, valign: "middle" });
      ty = y + 1.05;
    } else {
      tb(s, L(title), { x: x + 0.25, y: ty, w: w - 0.5, h: 0.5, fontSize: 17, bold: true, color: C.text2 });
      ty += 0.6;
    }
    if (body) {
      const items = Array.isArray(body) ? body : [body];
      tb(s, items.map((b, i) => ({ text: L(b), options: { bullet: Array.isArray(body) ? { indent: 14 } : false,
        breakLine: i < items.length - 1, paraSpaceAfter: 4 } })),
        { x: x + 0.25, y: ty, w: w - 0.5, h: y + h - ty - 0.15, fontSize: opts.bodySize || 16, color: C.text1, valign: "top" });
    }
  }

  function flow(s, steps, { y = 2.0, h = 1.5, x0 = 0.6, x1 = 12.73, fills, fontSize = 15 } = {}) {
    const n = steps.length, gap = 0.35;
    const w = (x1 - x0 - gap * (n - 1)) / n;
    steps.forEach((st, i) => {
      const x = x0 + i * (w + gap);
      const f = fills ? fills[i % fills.length] : C.accent1;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: f }, line: { color: f } });
      tb(s, [{ text: L(st[0]), options: { bold: true, breakLine: true, fontSize: fontSize + 1 } },
             { text: L(st[1]), options: { fontSize: fontSize - 2 } }],
        { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: h - 0.16, color: C.background1, align: "center", valign: "middle" });
      if (i < n - 1) {
        s.addShape(pres.shapes.ISOSCELES_TRIANGLE, { x: x + w + 0.035, y: y + h / 2 - 0.1, w: 0.28, h: 0.2, rotate: 90,
          fill: { color: C.text2 }, line: { color: C.text2 }, flipH: false });
      }
    });
  }

  function table(s, rows, { x = 0.6, y = 1.5, w = 12.13, colW, fontSize = 13, rowH = 0.38 } = {}) {
    const data = rows.map((r, i) => r.map((c) => ({
      text: L(c), options: i === 0
        ? { bold: true, color: HEX.lt1, fill: { color: HEX.dk2 }, fontSize }
        : { color: HEX.dk1, fill: { color: i % 2 ? HEX.lt2 : HEX.lt1 }, fontSize } })));
    s.addTable(data, { x, y, w, colW, rowH, border: { type: "solid", pt: 0.5, color: "C9DEDB" },
      valign: "middle", margin: 0.06 });
  }

  // ================================================================ SLIDES
  newSection({ en: "Welcome", es: "Bienvenida" });
  let s = add("Title");
  s.addText(L({ en: "From Cells to Clusters", es: "De Células a Clústeres" }), { placeholder: "title" });
  s.addText([
    { text: L({ en: "An Introduction to Single-Cell RNA-seq Analysis in Python",
                es: "Introducción al Análisis de Single-Cell RNA-seq en Python" }), options: { breakLine: true, fontSize: 24, bold: true } },
    { text: " ", options: { breakLine: true, fontSize: 10 } },
    { text: L({ en: "Dr. Cristal Villalba Silva · UT Health San Antonio", es: "Dra. Cristal Villalba Silva · UT Health San Antonio" }),
      options: { breakLine: true } },
    { text: L({ en: "ISCB-LATAM SolBio SPBBC 2026 · Lima, Peru · November 9, 2026",
                es: "ISCB-LATAM SolBio SPBBC 2026 · Lima, Perú · 9 de noviembre de 2026" }), options: { breakLine: true } },
    { text: "github.com/Kur1sutaru/ISMB-LATAM", options: { color: HEX.accent3 } },
  ], { placeholder: "body" });
  s.addImage({ data: await icon("FaDna", "2A9D8F"), x: 11.2, y: 0.6, w: 1.4, h: 1.4, transparency: 20 });
  notes(s, { en: "Welcome. While I introduce the tutorial, please open notebook 00 from the README and run the Setup cell: it installs packages for about one minute.",
             es: "Bienvenida. Mientras presento el tutorial, abran el notebook 00 desde el README y ejecuten la celda de Configuración: instala paquetes durante aproximadamente un minuto." });

  // Agenda
  s = add("Content");
  s.addText(L({ en: "Today's plan", es: "El plan de hoy" }), { placeholder: "title" });
  const agenda = [
    ["9:00", { en: "Introduction (slides)", es: "Introducción (diapositivas)" }, "FaLightbulb", HEX.accent4],
    ["9:20", { en: "00 · Cell Ranger & AnnData", es: "00 · Cell Ranger y AnnData" }, "FaLaptopCode", HEX.accent1],
    ["9:40", { en: "01 · Quality control", es: "01 · Control de calidad" }, "FaFilter", HEX.accent1],
    ["10:15", { en: "02 · PCA, UMAP, clustering", es: "02 · PCA, UMAP, clustering" }, "FaProjectDiagram", HEX.accent1],
    ["10:45", { en: "Coffee break", es: "Pausa para café" }, "FaCoffee", HEX.accent3],
    ["11:00", { en: "03 · Cell type annotation", es: "03 · Anotación de tipos celulares" }, "FaTags", HEX.accent2],
    ["11:35", { en: "04 · Plots, DEGs, pathways", es: "04 · Gráficos, DEGs, vías" }, "FaChartBar", HEX.accent2],
    ["12:05", { en: "05 · Integration · R vs Python", es: "05 · Integración · R vs Python" }, "FaBalanceScale", HEX.accent6],
  ];
  for (let i = 0; i < agenda.length; i++) {
    const col = i < 4 ? 0 : 1, row = i % 4;
    const x = 0.6 + col * 6.2, y = 1.55 + row * 1.3;
    await circleIcon(s, agenda[i][2], x, y, 0.9, agenda[i][3]);
    tb(s, agenda[i][0], { x: x + 1.15, y: y + 0.02, w: 1.1, h: 0.86, fontSize: 20, bold: true, color: C.text2, valign: "middle" });
    tb(s, L(agenda[i][1]), { x: x + 2.25, y: y + 0.02, w: 3.7, h: 0.86, fontSize: 17, color: C.text1, valign: "middle" });
  }
  tb(s, L({ en: "~65 % hands-on in Google Colab · materials in English and Spanish",
            es: "~65 % práctico en Google Colab · materiales en inglés y español" }),
    { x: 0.6, y: 6.45, w: 12, h: 0.4, fontSize: 14, italic: true, color: MUTED });
  notes(s, { en: "Half-day, 9:00 to 12:30. Notebook 05 is a live demo; the rest is hands-on. Exercises have hidden solutions.",
             es: "Medio día, de 9:00 a 12:30. El notebook 05 es una demostración en vivo; el resto es práctico. Los ejercicios tienen soluciones ocultas." });

  // Learning objectives
  s = add("Content");
  s.addText(L({ en: "By 12:30 you will be able to…", es: "A las 12:30 podrás…" }), { placeholder: "title" });
  const objs = [
    ["FaDna", { en: "Go from a Cell Ranger matrix to an AnnData object", es: "Pasar de una matriz de Cell Ranger a un objeto AnnData" }],
    ["FaFilter", { en: "Remove low-quality cells and doublets, normalize", es: "Eliminar células de baja calidad y dobletes, normalizar" }],
    ["FaProjectDiagram", { en: "Reduce dimensions, build UMAPs, cluster cells", es: "Reducir dimensiones, construir UMAPs, agrupar células" }],
    ["FaTags", { en: "Annotate cell types with markers, databases and atlases", es: "Anotar tipos celulares con marcadores, bases de datos y atlas" }],
    ["FaChartBar", { en: "Make clear figures, find DEGs, interpret pathways", es: "Hacer figuras claras, encontrar DEGs, interpretar vías" }],
    ["FaBalanceScale", { en: "Integrate samples, compare conditions, translate to R", es: "Integrar muestras, comparar condiciones, traducir a R" }],
  ];
  for (let i = 0; i < objs.length; i++) {
    const col = i % 2, row = Math.floor(i / 2);
    await card(s, { x: 0.6 + col * 6.17, y: 1.55 + row * 1.7, w: 5.96, h: 1.45, iconName: objs[i][0],
      iconHex: [HEX.accent1, HEX.accent2, HEX.accent4][row], title: objs[i][1] });
  }
  notes(s, { en: "Six outcomes, one per notebook.", es: "Seis resultados, uno por notebook." });

  // Why single cell
  newSection({ en: "Single-cell technology", es: "Tecnología single-cell" });
  s = add("Content");
  s.addText(L({ en: "Why single-cell? Smoothie vs. fruit salad", es: "¿Por qué single-cell? Batido vs. ensalada de frutas" }), { placeholder: "title" });
  await card(s, { x: 0.6, y: 1.6, w: 5.9, h: 4.9, iconName: "FaBlender", iconHex: HEX.accent3,
    title: { en: "Bulk RNA-seq", es: "RNA-seq bulk" },
    body: [{ en: "One average profile per sample", es: "Un perfil promedio por muestra" },
           { en: "A change could be a shift in expression or in cell composition, and you cannot tell which", es: "Un cambio puede ser de expresión o de composición celular, y no se puede distinguir" },
           { en: "Rare cells (< 5 %) are invisible", es: "Las células raras (< 5 %) son invisibles" },
           { en: "Cheap, deep, many replicates", es: "Barato, profundo, muchas réplicas" }] });
  await card(s, { x: 6.83, y: 1.6, w: 5.9, h: 4.9, iconName: "FaAppleAlt", iconHex: HEX.accent2,
    title: { en: "Single-cell RNA-seq", es: "Single-cell RNA-seq" },
    body: [{ en: "One profile per cell: thousands to millions of cells", es: "Un perfil por célula: de miles a millones de células" },
           { en: "Discover cell types and states, including rare ones", es: "Descubrir tipos y estados celulares, incluso raros" },
           { en: "Measure composition and cell-type-specific responses", es: "Medir composición y respuestas específicas de cada tipo" },
           { en: "Sparse (most values are 0), noisy, more expensive", es: "Disperso (la mayoría de valores son 0), ruidoso, más caro" }] });
  notes(s, { en: "Bulk tells you the average; single-cell tells you who is in the sample and what each of them is doing.",
             es: "El bulk te da el promedio; single-cell te dice quién está en la muestra y qué hace cada uno." });

  // Technologies
  s = add("Content");
  s.addText(L({ en: "Main technologies", es: "Principales tecnologías" }), { placeholder: "title" });
  const techs = [
    ["FaTint", { en: "Droplets", es: "Gotas" }, { en: "10x Chromium, Drop-seq. 1k–20k cells per channel, 3' or 5' counts with UMIs. The most common choice.", es: "10x Chromium, Drop-seq. 1k–20k células por canal, conteos 3' o 5' con UMIs. La opción más común." }, HEX.accent1],
    ["FaTh", { en: "Plates", es: "Placas" }, { en: "Smart-seq2/3. Hundreds of cells, full-length transcripts: isoforms, mutations, high sensitivity.", es: "Smart-seq2/3. Cientos de células, transcritos completos: isoformas, mutaciones, alta sensibilidad." }, HEX.accent4],
    ["FaRandom", { en: "Combinatorial indexing", es: "Indexado combinatorio" }, { en: "SPLiT-seq, Parse, sci-RNA-seq. Up to millions of cells and many samples, fixed cells.", es: "SPLiT-seq, Parse, sci-RNA-seq. Hasta millones de células y muchas muestras, células fijadas." }, HEX.accent6],
    ["FaMapMarkedAlt", { en: "Spatial", es: "Espacial" }, { en: "Visium HD, Xenium, MERFISH, CosMx. Expression with its position in the tissue.", es: "Visium HD, Xenium, MERFISH, CosMx. Expresión con su posición en el tejido." }, HEX.accent2],
  ];
  for (let i = 0; i < techs.length; i++) {
    await card(s, { x: 0.6 + i * 3.08, y: 1.6, w: 2.9, h: 4.6, iconName: techs[i][0], iconHex: techs[i][3],
      title: techs[i][1], body: techs[i][2] });
  }
  tb(s, L({ en: "Single-nucleus RNA-seq (snRNA-seq) works on frozen tissue and cells that are hard to dissociate (neurons, adipocytes); the analysis is almost identical.",
            es: "El single-nucleus RNA-seq (snRNA-seq) funciona con tejido congelado y células difíciles de disociar (neuronas, adipocitos); el análisis es casi idéntico." }),
    { x: 0.6, y: 6.35, w: 12.1, h: 0.5, fontSize: 14, italic: true, color: MUTED });
  notes(s, { en: "Today we use 10x droplet data, but the analysis applies to all count-based methods.",
             es: "Hoy usamos datos de gotas de 10x, pero el análisis aplica a todos los métodos basados en conteos." });

  // How 10x works
  s = add("Content");
  s.addText(L({ en: "How 10x Chromium works", es: "Cómo funciona 10x Chromium" }), { placeholder: "title" });
  flow(s, [
    [{ en: "1 · Encapsulate", es: "1 · Encapsular" }, { en: "Cell + barcoded gel bead in an oil droplet (GEM)", es: "Célula + perla con códigos en una gota de aceite (GEM)" }],
    [{ en: "2 · Lyse & tag", es: "2 · Lisar y marcar" }, { en: "mRNA captured by poly(dT); each molecule gets cell barcode + UMI", es: "mRNA capturado por poli(dT); cada molécula recibe código celular + UMI" }],
    [{ en: "3 · Pool & amplify", es: "3 · Juntar y amplificar" }, { en: "Break droplets, reverse-transcribe, PCR, build the library", es: "Romper gotas, transcripción reversa, PCR, construir la biblioteca" }],
    [{ en: "4 · Sequence", es: "4 · Secuenciar" }, { en: "Illumina paired-end, ~20–50k reads per cell", es: "Illumina paired-end, ~20–50k lecturas por célula" }],
  ], { y: 1.65, h: 1.9, fills: [C.accent1, C.accent4, C.accent1, C.accent4] });
  // read structure diagram
  tb(s, L({ en: "Read structure (3' v3/v4)", es: "Estructura de las lecturas (3' v3/v4)" }),
    { x: 0.6, y: 4.0, w: 6, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  const seg = [[{ en: "Cell barcode · 16 bp", es: "Código celular · 16 pb" }, 3.2, HEX.accent2],
               [{ en: "UMI · 12 bp", es: "UMI · 12 pb" }, 2.4, HEX.accent3],
               ["poly(dT)", 1.6, "9FB8B4"]];
  let sx = 1.9;
  tb(s, "Read 1", { x: 0.6, y: 4.6, w: 1.2, h: 0.55, fontSize: 15, bold: true, color: C.text1, valign: "middle" });
  for (const [lab, w, col] of seg) {
    s.addShape(pres.shapes.RECTANGLE, { x: sx, y: 4.6, w, h: 0.55, fill: { color: col }, line: { color: "FFFFFF", width: 1.5 } });
    tb(s, L(lab), { x: sx, y: 4.6, w, h: 0.55, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    sx += w;
  }
  tb(s, "Read 2", { x: 0.6, y: 5.35, w: 1.2, h: 0.55, fontSize: 15, bold: true, color: C.text1, valign: "middle" });
  s.addShape(pres.shapes.RECTANGLE, { x: 1.9, y: 5.35, w: 7.2, h: 0.55, fill: { color: HEX.accent1 }, line: { color: HEX.accent1 } });
  tb(s, L({ en: "cDNA · ~90 bp → which gene", es: "cDNA · ~90 pb → qué gen" }), { x: 1.9, y: 5.35, w: 7.2, h: 0.55, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  tb(s, [{ text: L({ en: "Barcode → which cell", es: "Código → qué célula" }), options: { breakLine: true } },
         { text: L({ en: "UMI → which molecule (removes PCR duplicates)", es: "UMI → qué molécula (elimina duplicados de PCR)" }), options: { breakLine: true } },
         { text: L({ en: "cDNA → which gene", es: "cDNA → qué gen" }) }],
    { x: 9.5, y: 4.55, w: 3.3, h: 1.45, fontSize: 14, color: C.text1, valign: "middle", paraSpaceAfter: 6 });
  notes(s, { en: "Barcode, UMI and cDNA: three pieces of information per read pair. The UMI is what makes the counts quantitative.",
             es: "Código, UMI y cDNA: tres piezas de información por par de lecturas. El UMI es lo que hace que los conteos sean cuantitativos." });

  // Cell Ranger
  s = add("Content");
  s.addText(L({ en: "Cell Ranger: from FASTQ to count matrix", es: "Cell Ranger: de FASTQ a matriz de conteos" }), { placeholder: "title" });
  flow(s, [
    [{ en: "Align", es: "Alinear" }, { en: "STAR to genome + annotation", es: "STAR al genoma + anotación" }],
    [{ en: "Barcodes", es: "Códigos" }, { en: "Correct against the 10x whitelist", es: "Corregir contra la lista de 10x" }],
    [{ en: "Count UMIs", es: "Contar UMIs" }, { en: "Same barcode + UMI + gene = 1 molecule", es: "Mismo código + UMI + gen = 1 molécula" }],
    [{ en: "Call cells", es: "Identificar células" }, { en: "Separate cells from empty droplets", es: "Separar células de gotas vacías" }],
  ], { y: 1.6, h: 1.45, fills: [C.accent4] });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 3.4, w: 7.4, h: 1.25, rectRadius: 0.1, fill: { color: "17262B" }, line: { color: "17262B" } });
  tb(s, "cellranger count --id=sample1 \\\n  --transcriptome=refdata-gex-GRCh38-2024-A \\\n  --fastqs=fastqs/ --sample=sample1 --create-bam=true",
    { x: 0.8, y: 3.45, w: 7.1, h: 1.15, fontFace: "Courier New", fontSize: 13, color: "D7F2EE", valign: "middle" });
  await card(s, { x: 8.3, y: 3.4, w: 4.43, h: 3.25, iconName: "FaCogs", iconHex: HEX.accent6,
    title: { en: "Open-source alternatives", es: "Alternativas abiertas" },
    body: ["STARsolo", "alevin-fry / simpleaf", "kallisto | bustools",
           { en: "Faster, free, run anywhere", es: "Más rápidas, gratuitas, en cualquier servidor" }] });
  tb(s, [{ text: L({ en: "Needs a Linux server (≥ 64 GB RAM), not Colab. ", es: "Necesita un servidor Linux (≥ 64 GB de RAM), no Colab. " }), options: { bold: true } },
         { text: L({ en: "One run per sample; use cellranger multi for multiplexed or multi-modal libraries.", es: "Una ejecución por muestra; usa cellranger multi para bibliotecas multiplexadas o multimodales." }) }],
    { x: 0.6, y: 4.9, w: 7.4, h: 1.0, fontSize: 15, color: C.text1, valign: "top" });
  notes(s, { en: "Cell Ranger is free to download but requires a 10x license agreement and a powerful machine.",
             es: "Cell Ranger es gratuito pero requiere aceptar la licencia de 10x y una máquina potente." });

  // outputs + metrics
  s = add("Content");
  s.addText(L({ en: "What Cell Ranger gives you", es: "Lo que te entrega Cell Ranger" }), { placeholder: "title" });
  table(s, [
    [{ en: "File in outs/", es: "Archivo en outs/" }, { en: "Use it for", es: "Úsalo para" }],
    ["web_summary.html", { en: "QC report: always open it first", es: "Reporte de calidad: ábrelo siempre primero" }],
    ["filtered_feature_bc_matrix(.h5)", { en: "Counts of called cells → our analysis", es: "Conteos de células identificadas → nuestro análisis" }],
    ["raw_feature_bc_matrix(.h5)", { en: "All barcodes → ambient RNA removal", es: "Todos los códigos → eliminar RNA ambiental" }],
    ["metrics_summary.csv", { en: "Compare samples", es: "Comparar muestras" }],
    ["possorted_genome_bam.bam", { en: "Velocity, genotyping (rarely)", es: "Velocidad, genotipado (rara vez)" }],
    ["cloupe.cloupe", { en: "Loupe Browser exploration", es: "Exploración en Loupe Browser" }],
  ], { x: 0.6, y: 1.55, w: 7.3, colW: [3.3, 4.0], fontSize: 13, rowH: 0.5 });
  const stats = [
    ["> 70 %", { en: "reads in cells", es: "lecturas en células" }],
    ["> 60 %", { en: "reads mapped to transcriptome", es: "lecturas mapeadas al transcriptoma" }],
    ["≥ 1,000", { en: "median genes per cell (tissue-dependent)", es: "mediana de genes por célula (según tejido)" }],
  ];
  tb(s, L({ en: "Check in web_summary.html", es: "Revisa en web_summary.html" }), { x: 8.4, y: 1.55, w: 4.3, h: 0.45, fontSize: 17, bold: true, color: C.text2 });
  stats.forEach(([v, lab], i) => {
    tb(s, v, { x: 8.4, y: 2.1 + i * 1.45, w: 4.3, h: 0.75, fontSize: 40, bold: true, color: C.accent2, fontFace: THEME.headFontFace });
    tb(s, L(lab), { x: 8.4, y: 2.85 + i * 1.45, w: 4.3, h: 0.5, fontSize: 14, color: C.text1 });
  });
  notes(s, { en: "Also look at the barcode rank (knee) plot: a clear knee separates cells from empty droplets.",
             es: "Revisa también el gráfico de rango de códigos (rodilla): una rodilla clara separa células de gotas vacías." });

  // Workflow
  newSection({ en: "The analysis workflow", es: "El flujo de análisis" });
  s = add("Content");
  s.addText(L({ en: "The workflow we follow today", es: "El flujo que seguimos hoy" }), { placeholder: "title" });
  flow(s, [
    ["00", { en: "Load matrix · AnnData", es: "Cargar matriz · AnnData" }],
    ["01", { en: "QC · doublets · normalize · HVGs", es: "QC · dobletes · normalizar · HVGs" }],
    ["02", { en: "PCA · kNN · UMAP · Leiden", es: "PCA · kNN · UMAP · Leiden" }],
    ["03", { en: "Annotate cell types", es: "Anotar tipos celulares" }],
    ["04", { en: "Plots · DEGs · pathways", es: "Gráficos · DEGs · vías" }],
    ["05", { en: "Integrate · conditions · R", es: "Integrar · condiciones · R" }],
  ], { y: 1.7, h: 1.8, fills: [C.accent4, C.accent1, C.accent1, C.accent2, C.accent2, C.accent6], fontSize: 16 });
  await card(s, { x: 0.6, y: 3.95, w: 5.9, h: 2.7, iconName: "FaDatabase", iconHex: HEX.accent1,
    title: { en: "Datasets", es: "Datos" },
    body: [{ en: "PBMC 3k (10x): 2,700 blood cells, healthy donor → notebooks 00–04", es: "PBMC 3k (10x): 2.700 células de sangre, donante sano → notebooks 00–04" },
           { en: "Kang 2018: 8 donors, control vs IFN-β → notebook 05", es: "Kang 2018: 8 donantes, control vs IFN-β → notebook 05" }] });
  await card(s, { x: 6.83, y: 3.95, w: 5.9, h: 2.7, iconName: "FaPython", iconHex: HEX.accent4,
    title: { en: "Tools (scverse)", es: "Herramientas (scverse)" },
    body: [{ en: "Scanpy + AnnData for the core analysis", es: "Scanpy + AnnData para el análisis central" },
           { en: "decoupler, CellTypist, harmonypy, BBKNN, PyDESeq2", es: "decoupler, CellTypist, harmonypy, BBKNN, PyDESeq2" }] });
  notes(s, { en: "Each box is one Colab notebook. Every notebook can rebuild the previous step automatically.",
             es: "Cada caja es un notebook de Colab. Cada notebook puede reconstruir automáticamente el paso anterior." });

  // AnnData
  s = add("Content");
  s.addText(L({ en: "AnnData: one object for everything", es: "AnnData: un objeto para todo" }), { placeholder: "title" });
  // matrix X
  s.addShape(pres.shapes.RECTANGLE, { x: 3.0, y: 2.3, w: 4.2, h: 3.2, fill: { color: HEX.accent1 }, line: { color: HEX.accent1 } });
  tb(s, [{ text: "X", options: { bold: true, fontSize: 30, breakLine: true } },
         { text: L({ en: "cells × genes", es: "células × genes" }), options: { fontSize: 16 } }],
    { x: 3.0, y: 2.3, w: 4.2, h: 3.2, color: "FFFFFF", align: "center", valign: "middle" });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.0, y: 1.6, w: 4.2, h: 0.6, fill: { color: HEX.accent3 }, line: { color: HEX.accent3 } });
  tb(s, L({ en: "var · one row per gene", es: "var · una fila por gen" }), { x: 3.0, y: 1.6, w: 4.2, h: 0.6, fontSize: 14, bold: true, color: C.text1, align: "center", valign: "middle" });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 2.3, w: 2.3, h: 3.2, fill: { color: HEX.accent2 }, line: { color: HEX.accent2 } });
  tb(s, L({ en: "obs\none row per cell\n(QC, clusters, cell types)", es: "obs\nuna fila por célula\n(QC, clústeres, tipos)" }), { x: 0.65, y: 2.3, w: 2.2, h: 3.2, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  const slots = [
    ["layers", { en: "other matrices of the same shape (raw counts)", es: "otras matrices de igual forma (conteos crudos)" }],
    ["obsm", { en: "embeddings per cell (X_pca, X_umap)", es: "embeddings por célula (X_pca, X_umap)" }],
    ["obsp", { en: "cell–cell graphs (neighbors)", es: "grafos célula–célula (vecinos)" }],
    ["uns", { en: "everything else (colors, parameters, DE results)", es: "todo lo demás (colores, parámetros, resultados de DE)" }],
    ["raw", { en: "frozen copy of log-normalized data, all genes", es: "copia fija de los datos log-normalizados, todos los genes" }],
  ];
  slots.forEach(([k, v], i) => {
    tb(s, [{ text: "adata." + k, options: { bold: true, fontFace: "Courier New", color: HEX.dk2, breakLine: true } },
           { text: L(v), options: { color: HEX.dk1 } }],
      { x: 7.75, y: 1.6 + i * 0.98, w: 5.0, h: 0.9, fontSize: 14, valign: "top" });
  });
  tb(s, L({ en: "Saved as .h5ad · R equivalents: Seurat, SingleCellExperiment", es: "Se guarda como .h5ad · Equivalentes en R: Seurat, SingleCellExperiment" }),
    { x: 0.6, y: 5.85, w: 6.6, h: 0.5, fontSize: 14, italic: true, color: MUTED });
  notes(s, { en: "obs and var are pandas DataFrames, so everything you know about pandas works here.",
             es: "obs y var son DataFrames de pandas, así que todo lo que sabes de pandas funciona aquí." });

  // QC
  s = add("Content");
  s.addText(L({ en: "01 · Quality control: not every barcode is a good cell", es: "01 · Control de calidad: no todo código es una buena célula" }), { placeholder: "title" });
  const qc = [
    ["FaExclamationTriangle", { en: "Dying / broken cells", es: "Células muriendo / rotas" }, { en: "Few genes, high % mitochondrial reads. Filter with % MT and min. genes.", es: "Pocos genes, alto % de lecturas mitocondriales. Filtrar por % MT y mín. de genes." }, HEX.accent2],
    ["FaRegClone", { en: "Doublets", es: "Dobletes" }, { en: "Two cells in one droplet: too many UMIs and mixed markers. Detect with Scrublet / scDblFinder.", es: "Dos células en una gota: demasiados UMIs y marcadores mezclados. Detectar con Scrublet / scDblFinder." }, HEX.accent6],
    ["FaTint", { en: "Ambient RNA", es: "RNA ambiental" }, { en: "Free mRNA in every droplet. Correct with SoupX, CellBender, scAR.", es: "mRNA libre en todas las gotas. Corregir con SoupX, CellBender, scAR." }, HEX.accent3],
  ];
  for (let i = 0; i < 3; i++) {
    await card(s, { x: 0.6 + i * 4.11, y: 1.6, w: 3.9, h: 2.9, iconName: qc[i][0], iconHex: qc[i][3], title: qc[i][1], body: qc[i][2] });
  }
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.8, w: 12.13, h: 1.8, rectRadius: 0.1, fill: { color: HEX.dk2 }, line: { color: HEX.dk2 } });
  tb(s, [{ text: L({ en: "Choosing thresholds", es: "Elegir umbrales" }), options: { bold: true, fontSize: 18, breakLine: true, color: HEX.accent3 } },
         { text: L({ en: "Fixed cut-offs (e.g. 200–2,500 genes, < 5 % MT for PBMCs) or data-driven: > 5 MADs from the median. Tissue matters: neurons and cardiomyocytes have naturally high % MT. Always report what you used.",
                      es: "Cortes fijos (p. ej. 200–2.500 genes, < 5 % MT para PBMCs) o basados en los datos: > 5 MADs de la mediana. El tejido importa: neuronas y cardiomiocitos tienen naturalmente alto % MT. Reporta siempre lo que usaste." }), options: { fontSize: 15 } }],
    { x: 0.9, y: 4.9, w: 11.6, h: 1.6, color: "FFFFFF", valign: "middle" });
  notes(s, { en: "QC is iterative: you may come back after clustering if a cluster is defined only by low quality.",
             es: "El QC es iterativo: puedes volver después del clustering si un clúster se define solo por baja calidad." });

  // Normalization, HVG, PCA
  s = add("Content");
  s.addText(L({ en: "01–02 · From counts to a low-dimensional space", es: "01–02 · De conteos a un espacio de baja dimensión" }), { placeholder: "title" });
  flow(s, [
    [{ en: "Raw counts", es: "Conteos crudos" }, { en: "~30k genes, depth differs per cell", es: "~30k genes, profundidad distinta por célula" }],
    [{ en: "Normalize + log", es: "Normalizar + log" }, { en: "counts per 10k → log(x+1)", es: "conteos por 10k → log(x+1)" }],
    [{ en: "HVGs", es: "HVGs" }, { en: "keep ~2,000 informative genes", es: "conservar ~2.000 genes informativos" }],
    [{ en: "PCA", es: "PCA" }, { en: "~30 axes capture the biology", es: "~30 ejes capturan la biología" }],
  ], { y: 1.6, h: 1.6, fills: [C.accent4, C.accent1, C.accent1, C.accent2] });
  await card(s, { x: 0.6, y: 3.55, w: 5.9, h: 3.05, iconName: "FaLayerGroup", iconHex: HEX.accent1,
    title: { en: "Keep the raw counts!", es: "¡Guarda los conteos crudos!" },
    body: [{ en: "adata.layers[\"counts\"] before normalizing", es: "adata.layers[\"counts\"] antes de normalizar" },
           { en: "Pseudobulk DE and scVI need integers", es: "El DE pseudobulk y scVI necesitan enteros" },
           { en: "Alternatives: scran, Pearson residuals, SCTransform", es: "Alternativas: scran, residuos de Pearson, SCTransform" }] });
  await card(s, { x: 6.83, y: 3.55, w: 5.9, h: 3.05, iconName: "FaChartBar", iconHex: HEX.accent2,
    title: { en: "How many PCs?", es: "¿Cuántos PCs?" },
    body: [{ en: "Look for the elbow in the variance plot", es: "Busca el codo en el gráfico de varianza" },
           { en: "A few too many is safer than too few", es: "Unos pocos de más es más seguro que de menos" },
           { en: "PBMC 3k: elbow ~10–15, we use 30", es: "PBMC 3k: codo ~10–15, usamos 30" }] });
  notes(s, { en: "HVGs are only flagged, not removed; all genes stay in the object for plotting and DE.",
             es: "Los HVGs solo se marcan, no se eliminan; todos los genes quedan en el objeto para gráficos y DE." });

  // Graph, UMAP, Leiden
  s = add("Content");
  s.addText(L({ en: "02 · Neighbors, UMAP and Leiden clustering", es: "02 · Vecinos, UMAP y clustering con Leiden" }), { placeholder: "title" });
  // mini graph illustration
  const pts = [[1.2, 2.2], [1.8, 1.9], [1.6, 2.8], [2.3, 2.5], [1.1, 3.1], [3.9, 2.0], [4.5, 2.3], [4.1, 2.8], [4.7, 1.8], [2.6, 4.4], [3.2, 4.1], [2.9, 4.9], [3.6, 4.7]];
  const cl = [0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2];
  const edges = [[0, 1], [0, 2], [1, 3], [2, 3], [2, 4], [0, 4], [5, 6], [6, 7], [5, 7], [6, 8], [5, 8], [9, 10], [10, 11], [9, 11], [11, 12], [10, 12], [3, 5], [3, 10]];
  const cc = [HEX.accent1, HEX.accent2, HEX.accent6];
  edges.forEach(([a, b]) => {
    const [x1, y1] = pts[a], [x2, y2] = pts[b];
    s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2) + 0.6, y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.01, h: Math.abs(y2 - y1) || 0.01,
      flipH: (x2 - x1) * (y2 - y1) < 0, line: { color: "9FB8B4", width: 1.25 } });
  });
  pts.forEach(([x, y], i) => s.addShape(pres.shapes.OVAL, { x: x + 0.6 - 0.14, y: y - 0.14, w: 0.28, h: 0.28, fill: { color: cc[cl[i]] }, line: { color: "FFFFFF", width: 1 } }));
  tb(s, L({ en: "kNN graph: each cell linked to its 15 most similar cells; Leiden finds densely connected communities",
            es: "Grafo kNN: cada célula unida a sus 15 células más parecidas; Leiden encuentra comunidades densamente conectadas" }),
    { x: 0.6, y: 5.35, w: 5.0, h: 1.2, fontSize: 14, italic: true, color: MUTED });
  await card(s, { x: 6.0, y: 1.6, w: 6.73, h: 2.4, iconName: "FaCompressArrowsAlt", iconHex: HEX.accent4,
    title: { en: "UMAP is a picture, not a measurement", es: "UMAP es un dibujo, no una medición" },
    body: [{ en: "Local neighborhoods are preserved", es: "Se conservan los vecindarios locales" },
           { en: "Distances between clusters and cluster sizes are not reliable", es: "Las distancias entre clústeres y sus tamaños no son confiables" }] });
  await card(s, { x: 6.0, y: 4.2, w: 6.73, h: 2.4, iconName: "FaSitemap", iconHex: HEX.accent2,
    title: { en: "Resolution is a choice", es: "La resolución es una elección" },
    body: [{ en: "Higher resolution → more, smaller clusters", es: "Mayor resolución → más clústeres, más pequeños" },
           { en: "Compare several (0.3, 0.8, 1.5) and follow the biology", es: "Compara varias (0,3, 0,8, 1,5) y guíate por la biología" }] });
  notes(s, { en: "Clusters are computed on the graph, not on the UMAP. Changing UMAP parameters does not change the clusters.",
             es: "Los clústeres se calculan sobre el grafo, no sobre el UMAP. Cambiar parámetros del UMAP no cambia los clústeres." });

  // Annotation strategies
  newSection({ en: "Cell type annotation", es: "Anotación de tipos celulares" });
  s = add("Content");
  s.addText(L({ en: "03 · Three ways to name your clusters", es: "03 · Tres formas de nombrar tus clústeres" }), { placeholder: "title" });
  const ann = [
    ["FaSearch", { en: "Manual · marker genes", es: "Manual · genes marcadores" },
      [{ en: "rank_genes_groups → top genes per cluster", es: "rank_genes_groups → genes top por clúster" }, { en: "Compare with known markers (dot plot)", es: "Comparar con marcadores conocidos (dot plot)" }, { en: "Transparent, uses your expertise", es: "Transparente, usa tu experiencia" }], HEX.accent1],
    ["FaDatabase", { en: "Marker databases", es: "Bases de marcadores" },
      [{ en: "PanglaoDB, CellMarker 2.0", es: "PanglaoDB, CellMarker 2.0" }, { en: "Score every cell (decoupler ULM)", es: "Puntuar cada célula (ULM de decoupler)" }, { en: "Fast, but generic lists", es: "Rápido, pero listas genéricas" }], HEX.accent4],
    ["FaUsers", { en: "References & classifiers", es: "Referencias y clasificadores" },
      [{ en: "CellTypist, sc.tl.ingest, scANVI", es: "CellTypist, sc.tl.ingest, scANVI" }, { en: "R: SingleR, Azimuth", es: "R: SingleR, Azimuth" }, { en: "Reproducible; cannot find new types", es: "Reproducible; no encuentra tipos nuevos" }], HEX.accent2],
  ];
  for (let i = 0; i < 3; i++) {
    await card(s, { x: 0.6 + i * 4.11, y: 1.6, w: 3.9, h: 3.6, iconName: ann[i][0], iconHex: ann[i][3], title: ann[i][1], body: ann[i][2] });
  }
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.45, w: 12.13, h: 1.15, rectRadius: 0.1, fill: { color: HEX.dk2 }, line: { color: HEX.dk2 } });
  tb(s, L({ en: "Combine them: agreement between independent methods is your evidence; disagreement tells you where to look closer.",
            es: "Combínalos: la concordancia entre métodos independientes es tu evidencia; las discrepancias te dicen dónde mirar con más cuidado." }),
    { x: 0.9, y: 5.45, w: 11.6, h: 1.15, fontSize: 17, color: "FFFFFF", valign: "middle", bold: true });
  notes(s, { en: "In the notebook we run all three on PBMC 3k and compare them with cross-tables.",
             es: "En el notebook ejecutamos los tres sobre PBMC 3k y los comparamos con tablas cruzadas." });

  // Annotation resources
  s = add("Content");
  s.addText(L({ en: "03 · Where to find references and record annotations", es: "03 · Dónde encontrar referencias y registrar anotaciones" }), { placeholder: "title" });
  const res = [
    ["FaTags", "PanglaoDB", { en: "Curated markers, human & mouse · panglaodb.se", es: "Marcadores curados, humano y ratón · panglaodb.se" }, HEX.accent1],
    ["FaGlobeAmericas", "CZ CELLxGENE", { en: "> 100 M standardized cells; Explorer, Gene Expression, Census API", es: "> 100 M células estandarizadas; Explorer, Gene Expression, API Census" }, HEX.accent4],
    ["FaMicroscope", "Single Cell Portal", { en: "Broad Institute: hundreds of studies, plots and downloads", es: "Broad Institute: cientos de estudios, gráficos y descargas" }, HEX.accent2],
    ["FaClipboardCheck", "Cell Annotation Platform", { en: "CAP · celltype.info: record labels with evidence and share them", es: "CAP · celltype.info: registra etiquetas con evidencia y compártelas" }, HEX.accent6],
    ["FaUserMd", "CellTypist", { en: "Pre-trained classifiers: immune, lung, gut, brain…", es: "Clasificadores preentrenados: inmune, pulmón, intestino, cerebro…" }, HEX.accent3],
    ["FaLink", "Cell Ontology", { en: "Standard IDs (CL:0000236 = B cell) that make labels reusable", es: "IDs estándar (CL:0000236 = célula B) que hacen reutilizables las etiquetas" }, HEX.accent5],
  ];
  for (let i = 0; i < res.length; i++) {
    const col = i % 3, row = Math.floor(i / 3);
    await card(s, { x: 0.6 + col * 4.11, y: 1.6 + row * 2.6, w: 3.9, h: 2.4, iconName: res[i][0], iconHex: res[i][3],
      title: res[i][1], body: res[i][2] });
  }
  notes(s, { en: "Show CELLxGENE Gene Expression live: type a marker and see which cell types express it across tissues.",
             es: "Muestra en vivo Gene Expression de CELLxGENE: escribe un marcador y mira qué tipos celulares lo expresan en todos los tejidos." });

  // Visualization
  newSection({ en: "Visualization and downstream analysis", es: "Visualización y análisis posteriores" });
  s = add("Content");
  s.addText(L({ en: "04 · Pick the plot for the question", es: "04 · Elige el gráfico según la pregunta" }), { placeholder: "title" });
  table(s, [
    [{ en: "Plot", es: "Gráfico" }, { en: "Question it answers", es: "Pregunta que responde" }, "Scanpy"],
    ["UMAP", { en: "Where are the cell types? Where is gene X expressed?", es: "¿Dónde están los tipos celulares? ¿Dónde se expresa el gen X?" }, "sc.pl.umap"],
    [{ en: "Violin / stacked violin", es: "Violin / stacked violin" }, { en: "How is a gene distributed in each group?", es: "¿Cómo se distribuye un gen en cada grupo?" }, "sc.pl.violin, sc.pl.stacked_violin"],
    ["Dot plot", { en: "Many markers × groups: % expressing and mean level", es: "Muchos marcadores × grupos: % que expresa y nivel medio" }, "sc.pl.dotplot"],
    [{ en: "Matrix plot / heatmap", es: "Matrix plot / heatmap" }, { en: "Compact means, or cell-level heterogeneity", es: "Medias compactas, o heterogeneidad célula a célula" }, "sc.pl.matrixplot, sc.pl.heatmap"],
    [{ en: "Proportion bars", es: "Barras de proporción" }, { en: "How does composition change between samples?", es: "¿Cómo cambia la composición entre muestras?" }, "pandas + matplotlib"],
    [{ en: "Volcano plot", es: "Volcano plot" }, { en: "Which genes change, how much, how significantly?", es: "¿Qué genes cambian, cuánto y con qué significancia?" }, "matplotlib / decoupler"],
  ], { x: 0.6, y: 1.6, w: 12.13, colW: [2.6, 6.0, 3.53], fontSize: 14, rowH: 0.62 });
  tb(s, L({ en: "Tips: colorblind-safe palettes (viridis), labels on the data, vmax=\"p99\" to tame outliers, save as PDF/SVG.",
            es: "Consejos: paletas seguras para daltonismo (viridis), etiquetas sobre los datos, vmax=\"p99\" para controlar valores extremos, guarda en PDF/SVG." }),
    { x: 0.6, y: 6.2, w: 12.1, h: 0.55, fontSize: 14, italic: true, color: MUTED });
  notes(s, { en: "All of these are one line in Scanpy; the notebook shows each with the PBMC markers.",
             es: "Todos son una línea en Scanpy; el notebook muestra cada uno con los marcadores de PBMC." });

  // DE
  s = add("Content");
  s.addText(L({ en: "04–05 · Differential expression: which test?", es: "04–05 · Expresión diferencial: ¿qué prueba?" }), { placeholder: "title" });
  await card(s, { x: 0.6, y: 1.6, w: 5.9, h: 3.6, iconName: "FaBullseye", iconHex: HEX.accent1,
    title: { en: "Markers between clusters", es: "Marcadores entre clústeres" },
    body: [{ en: "Wilcoxon per cell: rank_genes_groups", es: "Wilcoxon por célula: rank_genes_groups" },
           { en: "Good for describing and annotating clusters", es: "Útil para describir y anotar clústeres" },
           { en: "p-values are optimistic: genes were used to build the clusters", es: "Los p-valores son optimistas: los genes se usaron para formar los clústeres" }] });
  await card(s, { x: 6.83, y: 1.6, w: 5.9, h: 3.6, iconName: "FaBalanceScale", iconHex: HEX.accent2,
    title: { en: "Conditions (disease vs. control)", es: "Condiciones (enfermedad vs. control)" },
    body: [{ en: "Pseudobulk: sum counts per sample × cell type", es: "Pseudobulk: sumar conteos por muestra × tipo celular" },
           { en: "DESeq2 / edgeR with the donor as the replicate", es: "DESeq2 / edgeR con el donante como réplica" },
           { en: "Needs ≥ 3 biological replicates per condition", es: "Necesita ≥ 3 réplicas biológicas por condición" }] });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.45, w: 12.13, h: 1.15, rectRadius: 0.1, fill: { color: HEX.accent2 }, line: { color: HEX.accent2 } });
  tb(s, L({ en: "Cells from one person are not independent replicates. Treating them as such produces thousands of false positives (Squair et al. 2021).",
            es: "Las células de una persona no son réplicas independientes. Tratarlas así produce miles de falsos positivos (Squair et al. 2021)." }),
    { x: 0.9, y: 5.45, w: 11.6, h: 1.15, fontSize: 16, bold: true, color: "FFFFFF", valign: "middle" });
  notes(s, { en: "This is the most common statistical mistake in single-cell papers. With one sample per condition you cannot test conditions at all.",
             es: "Es el error estadístico más común en artículos de single-cell. Con una muestra por condición no se pueden probar condiciones." });

  // Downstream
  s = add("Content");
  s.addText(L({ en: "04 · What do the genes mean?", es: "04 · ¿Qué significan los genes?" }), { placeholder: "title" });
  const ds = [
    ["FaFilter", { en: "Over-representation (ORA)", es: "Sobrerrepresentación (ORA)" }, [{ en: "Top DEGs vs. gene sets (Fisher test)", es: "DEGs top vs. conjuntos de genes (prueba de Fisher)" }, { en: "MSigDB Hallmark, GO, Reactome", es: "MSigDB Hallmark, GO, Reactome" }, { en: "Simple; depends on a cut-off", es: "Simple; depende de un corte" }], HEX.accent1],
    ["FaRoute", { en: "Pathway activity", es: "Actividad de vías" }, [{ en: "PROGENy footprints: weighted target genes", es: "Huellas de PROGENy: genes blanco con peso" }, { en: "Score per cell or per contrast (ULM)", es: "Puntaje por célula o por contraste (ULM)" }, { en: "Uses direction and strength", es: "Usa dirección e intensidad" }], HEX.accent2],
    ["FaVials", { en: "Gene signatures", es: "Firmas génicas" }, [{ en: "Any list from a paper", es: "Cualquier lista de un artículo" }, { en: "sc.tl.score_genes per cell", es: "sc.tl.score_genes por célula" }, { en: "e.g. interferon response", es: "p. ej. respuesta a interferón" }], HEX.accent6],
  ];
  for (let i = 0; i < 3; i++) {
    await card(s, { x: 0.6 + i * 4.11, y: 1.6, w: 3.9, h: 3.4, iconName: ds[i][0], iconHex: ds[i][3], title: ds[i][1], body: ds[i][2] });
  }
  tb(s, L({ en: "Beyond today: cell–cell communication (LIANA+, CellChat), trajectories (PAGA, scVelo, CellRank), TF activity (CollecTRI), spatial (Squidpy).",
            es: "Más allá de hoy: comunicación célula–célula (LIANA+, CellChat), trayectorias (PAGA, scVelo, CellRank), actividad de TFs (CollecTRI), espacial (Squidpy)." }),
    { x: 0.6, y: 5.35, w: 12.1, h: 1.2, fontSize: 15, color: C.text1, valign: "top" });
  notes(s, { en: "decoupler gives one interface for all these methods and downloads the gene sets from OmniPath.",
             es: "decoupler ofrece una sola interfaz para todos estos métodos y descarga los conjuntos de genes desde OmniPath." });

  // Integration
  newSection({ en: "Integration and R vs Python", es: "Integración y R vs Python" });
  s = add("Content");
  s.addText(L({ en: "05 · Integration: align samples, keep biology", es: "05 · Integración: alinear muestras, conservar la biología" }), { placeholder: "title" });
  table(s, [
    [{ en: "Method", es: "Método" }, { en: "Works on", es: "Trabaja sobre" }, { en: "Strengths", es: "Fortalezas" }, { en: "Languages", es: "Lenguajes" }],
    ["Harmony", "PCA", { en: "Fast, simple, robust default", es: "Rápido, simple, buena opción por defecto" }, "R · Python"],
    ["BBKNN", { en: "kNN graph", es: "Grafo kNN" }, { en: "Very fast; graph only (clustering, UMAP)", es: "Muy rápido; solo grafo (clustering, UMAP)" }, "Python"],
    ["scVI / scANVI", { en: "Raw counts", es: "Conteos crudos" }, { en: "Complex batches, atlases; label transfer; GPU", es: "Lotes complejos, atlas; transferencia de etiquetas; GPU" }, "Python"],
    ["Seurat CCA / RPCA", { en: "Anchors", es: "Anclas" }, { en: "Well documented, widely used", es: "Bien documentado, muy usado" }, "R"],
  ], { x: 0.6, y: 1.6, w: 12.13, colW: [2.4, 2.1, 5.43, 2.2], fontSize: 14, rowH: 0.58 });
  await card(s, { x: 0.6, y: 4.75, w: 5.9, h: 1.9, iconName: "FaRandom", iconHex: HEX.accent1,
    title: { en: "Batch mixing ↑", es: "Mezcla de lotes ↑" },
    body: { en: "Cells of the same type from different samples are neighbors", es: "Células del mismo tipo de distintas muestras son vecinas" } });
  await card(s, { x: 6.83, y: 4.75, w: 5.9, h: 1.9, iconName: "FaObjectGroup", iconHex: HEX.accent2,
    title: { en: "Bio conservation ↑", es: "Conservación biológica ↑" },
    body: { en: "Different cell types stay apart (scIB metrics)", es: "Los distintos tipos celulares siguen separados (métricas scIB)" } });
  notes(s, { en: "Integration changes the embedding only. Differential expression always uses the original counts.",
             es: "La integración solo cambia el embedding. La expresión diferencial siempre usa los conteos originales." });

  // R vs Python
  s = add("Content");
  s.addText(L({ en: "R or Python? Both, and you can move between them", es: "¿R o Python? Ambos, y puedes moverte entre ellos" }), { placeholder: "title" });
  table(s, [
    [{ en: "Step", es: "Paso" }, "Python (scverse)", "R (Seurat / Bioconductor)"],
    [{ en: "Object", es: "Objeto" }, "AnnData (.h5ad)", "Seurat (.rds) · SingleCellExperiment"],
    ["QC · doublets", "calculate_qc_metrics · scrublet", "PercentageFeatureSet · scDblFinder"],
    [{ en: "Normalize · HVG", es: "Normalizar · HVG" }, "normalize_total + log1p · highly_variable_genes", "NormalizeData / SCTransform · FindVariableFeatures"],
    [{ en: "Graph · clusters", es: "Grafo · clústeres" }, "neighbors · leiden · umap", "FindNeighbors · FindClusters · RunUMAP"],
    [{ en: "Markers", es: "Marcadores" }, "rank_genes_groups", "FindAllMarkers"],
    [{ en: "Annotation", es: "Anotación" }, "CellTypist · ingest · scANVI", "SingleR · Azimuth"],
    [{ en: "Pseudobulk DE", es: "DE pseudobulk" }, "decoupler + PyDESeq2", "muscat · DESeq2 · edgeR"],
  ], { x: 0.6, y: 1.55, w: 8.3, colW: [1.9, 3.2, 3.2], fontSize: 12, rowH: 0.52 });
  await card(s, { x: 9.2, y: 1.55, w: 3.53, h: 2.45, iconName: "FaPython", iconHex: HEX.accent1,
    bodySize: 14, title: "Python", body: { en: "Millions of cells, GPUs, deep learning (scvi-tools), ML pipelines", es: "Millones de células, GPUs, aprendizaje profundo (scvi-tools), pipelines de ML" } });
  await card(s, { x: 9.2, y: 4.2, w: 3.53, h: 2.45, iconName: "FaRProject", iconHex: HEX.accent4,
    bodySize: 14, title: "R", body: { en: "Bioconductor statistics, many specialized methods, polished vignettes", es: "Estadística de Bioconductor, muchos métodos especializados, viñetas pulidas" } });
  tb(s, L({ en: "Convert: zellkonverter::readH5AD() · anndata2ri · rpy2. Defaults differ, so results are similar, not identical.",
            es: "Convertir: zellkonverter::readH5AD() · anndata2ri · rpy2. Los valores por defecto difieren: resultados parecidos, no idénticos." }),
    { x: 0.6, y: 5.85, w: 8.3, h: 0.8, fontSize: 14, italic: true, color: MUTED });
  notes(s, { en: "Use the ecosystem your collaborators use; .h5ad files move between both.",
             es: "Usa el ecosistema de tus colaboradores; los archivos .h5ad se mueven entre ambos." });

  // Practical
  newSection({ en: "Hands-on", es: "Práctica" });
  s = add("Content");
  s.addText(L({ en: "Let's start: Google Colab in 4 steps", es: "Empecemos: Google Colab en 4 pasos" }), { placeholder: "title" });
  flow(s, [
    [{ en: "1 · Open", es: "1 · Abrir" }, { en: "github.com/Kur1sutaru/ISMB-LATAM → Open in Colab", es: "github.com/Kur1sutaru/ISMB-LATAM → Abrir en Colab" }],
    [{ en: "2 · Copy", es: "2 · Copiar" }, { en: "File → Save a copy in Drive", es: "Archivo → Guardar una copia en Drive" }],
    [{ en: "3 · Setup", es: "3 · Configurar" }, { en: "Run the first code cell (~1 min)", es: "Ejecuta la primera celda de código (~1 min)" }],
    [{ en: "4 · Run", es: "4 · Ejecutar" }, { en: "Shift + Enter, cell by cell, in order", es: "Shift + Enter, celda por celda, en orden" }],
  ], { y: 1.65, h: 2.0, fills: [C.accent1, C.accent4, C.accent1, C.accent2], fontSize: 17 });
  await card(s, { x: 0.6, y: 4.0, w: 5.9, h: 2.6, iconName: "FaCloud", iconHex: HEX.accent1,
    title: { en: "Good to know", es: "Para tener en cuenta" },
    body: [{ en: "🟢 Core = live · 🔎 Extra = self-study", es: "🟢 Core = en vivo · 🔎 Extra = estudio individual" },
           { en: "Each notebook rebuilds the previous step if needed", es: "Cada notebook reconstruye el paso anterior si es necesario" },
           { en: "USE_DRIVE = True keeps results in Drive", es: "USE_DRIVE = True guarda resultados en Drive" }] });
  await card(s, { x: 6.83, y: 4.0, w: 5.9, h: 2.6, iconName: "FaExclamationTriangle", iconHex: HEX.accent2,
    title: { en: "If something breaks", es: "Si algo falla" },
    body: [{ en: "Runtime → Restart session and run all", es: "Entorno de ejecución → Reiniciar sesión y ejecutar todo" },
           { en: "\"Not authored by Google\" → Run anyway", es: "\"Google no creó este notebook\" → Ejecutar de todos modos" },
           { en: "Raise your hand: helpers are around", es: "Levanta la mano: hay ayudantes en la sala" }] });
  notes(s, { en: "Switch to the browser now and open notebook 00.", es: "Cambia al navegador y abre el notebook 00." });

  // Resources
  s = add("Content");
  s.addText(L({ en: "Keep learning", es: "Sigue aprendiendo" }), { placeholder: "title" });
  const learn = [
    ["FaBook", "Single-cell best practices", "sc-best-practices.org", HEX.accent1],
    ["FaPython", { en: "Scanpy & scverse tutorials", es: "Tutoriales de Scanpy y scverse" }, "scanpy.readthedocs.io · scverse.org", HEX.accent4],
    ["FaRProject", "OSCA (Bioconductor) · Seurat", "bioconductor.org/books/release/OSCA · satijalab.org/seurat", HEX.accent6],
    ["FaLaptopCode", "Galaxy Training Network", { en: "single-cell track, no code needed", es: "sección single-cell, sin código" }, HEX.accent2],
    ["FaGlobeAmericas", { en: "Community", es: "Comunidad" }, { en: "ISCB-LATAM, ISCB Regional Student Groups (RSG-Brasil, RSG-Peru…)", es: "ISCB-LATAM, Regional Student Groups de ISCB (RSG-Brasil, RSG-Peru…)" }, HEX.accent3],
    ["FaGithub", { en: "These materials", es: "Estos materiales" }, "github.com/Kur1sutaru/ISMB-LATAM", HEX.dk2],
  ];
  for (let i = 0; i < learn.length; i++) {
    const col = i % 2, row = Math.floor(i / 2);
    await card(s, { x: 0.6 + col * 6.17, y: 1.55 + row * 1.72, w: 5.96, h: 1.55, iconName: learn[i][0], iconHex: learn[i][3],
      title: learn[i][1] });
    tb(s, L(learn[i][2]), { x: 0.6 + col * 6.17 + 1.05, y: 1.55 + row * 1.72 + 0.9, w: 4.7, h: 0.5, fontSize: 14, color: MUTED });
  }
  notes(s, { en: "The repository will stay online after the conference, in English and Spanish.", es: "El repositorio seguirá disponible después del congreso, en inglés y español." });

  // Thanks
  s = add("Title");
  s.addText(L({ en: "Thank you! ¡Gracias! Obrigada!", es: "¡Gracias! Thank you! Obrigada!" }), { placeholder: "title" });
  s.addText([
    { text: L({ en: "Questions, feedback, bugs: open an issue on GitHub", es: "Preguntas, comentarios, errores: abre un issue en GitHub" }), options: { breakLine: true } },
    { text: "github.com/Kur1sutaru/ISMB-LATAM", options: { breakLine: true, color: HEX.accent3, bold: true } },
    { text: " ", options: { breakLine: true, fontSize: 10 } },
    { text: L({ en: "Dr. Cristal Villalba Silva · ORCID 0000-0003-0283-7982", es: "Dra. Cristal Villalba Silva · ORCID 0000-0003-0283-7982" }), options: { breakLine: true } },
    { text: L({ en: "Code: MIT · Slides and text: CC BY 4.0", es: "Código: MIT · Diapositivas y textos: CC BY 4.0" }), options: { fontSize: 14 } },
  ], { placeholder: "body" });
  s.addImage({ data: await icon("FaDna", "2A9D8F"), x: 11.2, y: 0.6, w: 1.4, h: 1.4, transparency: 20 });

  const out = path.join(ROOT, "slides", lang);
  fs.mkdirSync(out, { recursive: true });
  const file = path.join(out, lang === "en" ? "from_cells_to_clusters_slides_EN.pptx" : "de_celulas_a_clusteres_diapositivas_ES.pptx");
  await pres.writeFile({ fileName: file });
  await applyTheme(file, THEME);
  console.log("wrote", path.relative(ROOT, file));
}

(async () => { for (const l of ["en", "es"]) await build(l); })().catch((e) => { console.error(e); process.exit(1); });
