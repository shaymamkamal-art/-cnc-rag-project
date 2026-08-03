export type Lang = "en" | "ar";

export interface SourceDoc {
  file: string;
  section: string;
  score: number;
  snippet: string;
}

export interface KBEntry {
  id: string;
  keywords: string[];
  answer: Record<Lang, string>;
  sources: SourceDoc[];
}

export const KB: KBEntry[] = [
  {
    id: "hex",
    keywords: ["hex", "wrench", "driver", "broach", "سداسي", "مفتاح", "برواش"],
    answer: {
      en:
        "The Z1 implant receives a 1.25 mm internal hex connection, broached during Path 2 finishing on the CITIZEN L20.\n\nKey specs from the machining record:\n• Hex across-flats: 1.25 mm (ISO 2768-mK)\n• Broach depth: 2.10 mm below the platform face\n• Tool: T14 hex broach @ 420 RPM, 0.8 s dwell\n• Driver engagement torque: 15–25 N·cm\n\nThe broach runs after thread forming so the hex axis stays concentric with the Ø4.2 platform within 0.02 mm TIR.",
      ar:
        "الزرعة Z1 مزودة بوصل سداسي داخلي مقاس 1.25 مم، يتم تشكيله بالبرواش أثناء مسار التشطيب Path 2 على ماكينة CITIZEN L20.\n\nأهم المواصفات من سجل التشغيل:\n• عرض السداسي: 1.25 مم (ISO 2768-mK)\n• عمق البرواش: 2.10 مم أسفل سطح المنصة\n• الأداة: برواش سداسي T14 بسرعة 420 لفة/دقيقة وزمن ثبات 0.8 ث\n• عزم التعشيق للمفتاح: 15–25 نيوتن·سم\n\nتتم عملية البرواش بعد تشكيل القلاووظ ليبقى محور السداسي متمركزًا مع منصة Ø4.2 ضمن 0.02 مم.",
    },
    sources: [
      { file: "Z1_Machining_Spec_Rev4.pdf", section: "§3.2 — Internal hex connection", score: 0.94,
        snippet: "…broach a 1.25 A/F hex to 2.10 ±0.05 depth; verify concentricity ≤ 0.02 TIR…" },
      { file: "Path2_Broach_Cycle_O0013.cnc", section: "N140–N180", score: 0.89,
        snippet: "T1414 M6 / S420 M3 / G84 dwell P800 — hex broach pass" },
      { file: "QC_Torque_Log_Oct.xlsx", section: "Sheet1 · Col D", score: 0.71,
        snippet: "Driver seat torque 15–25 N·cm, pass rate 99.2% (n=412)" },
    ],
  },
  {
    id: "platform",
    keywords: ["platform", "dimension", "diameter", "collar", "منصة", "قطر", "أبعاد", "مقاس"],
    answer: {
      en: "The Z1 platform is a Ø4.20 mm collar with a platform-switched Ø3.4 abutment seat.\n\n• Platform diameter: Ø4.20 mm ±0.01\n• Collar height: 0.60 mm\n• Abutment seat: Ø3.4 mm, 11° internal taper\n• Micro-thread lead-in: 3 turns × 0.25 pitch\n\nAll dimensions are verified in-process by the Marposs gauge at station 4.",
      ar: "منصة الزرعة Z1 عبارة عن طوق بقطر Ø4.20 مم مع مقر دعامة مُضيَّق Ø3.4 مم.\n\n• قطر المنصة: Ø4.20 مم ±0.01\n• ارتفاع الطوق: 0.60 مم\n• مقر الدعامة: Ø3.4 مم بتدبيب داخلي 11°\n• مدخل القلاووظ الدقيق: 3 لفات × خطوة 0.25\n\nجميع الأبعاد تُفحص أثناء التشغيل بواسطة مقياس Marposs في المحطة 4.",
    },
    sources: [
      { file: "Z1_Platform_Dwg_D-114.dwg", section: "View A-A", score: 0.96,
        snippet: "Ø4.20 ±0.01 collar, 11° taper seat Ø3.4, break edges 0.05 max" },
      { file: "InProcess_Gauge_Marposs.cfg", section: "Station 4", score: 0.82,
        snippet: "Tolerance band platform Ø: 4.19–4.21 → PASS flag to PLC" },
    ],
  },
  {
    id: "cnc",
    keywords: ["cnc", "program", "g-code", "gcode", "path", "machine", "برنامج", "ماكينة", "كود"],
    answer: {
      en: "Three programs run the Z1 on the L20 Swiss-type lathe:\n\n• O0011 — Roughing: bar feed, OD turn to Ø4.6, drill Ø1.1 core\n• O0012 — Path 1: thread forming M1.4 × 0.25, 3 passes\n• O0013 — Path 2: finish platform Ø4.20, seat taper, T14 hex broach\n\nCurrent revision is O0013 rev E, deployed 12 Oct. Cycle time 48 s/part.",
      ar: "ثلاثة برامج تشغّل الزرعة Z1 على مخرطة L20 السويسرية:\n\n• O0011 — تخشين: تغذية القضيب، خرط خارجي حتى Ø4.6، ثقب نواة Ø1.1\n• O0012 — مسار 1: تشكيل قلاووظ M1.4 × 0.25 على 3 تمريرات\n• O0013 — مسار 2: تشطيب المنصة Ø4.20، تدبيب المقر، برواش السداسي T14\n\nالمراجعة الحالية O0013 rev E، تم اعتمادها في 12 أكتوبر. زمن الدورة 48 ث/قطعة.",
    },
    sources: [
      { file: "L20_Program_Register.csv", section: "Rows 11–13", score: 0.93,
        snippet: "O0011 v9 / O0012 v6 / O0013 vE — status RELEASED" },
      { file: "O0013_Path2_Finish.cnc", section: "Header", score: 0.87,
        snippet: "(Z1 PATH2 FINISH + HEX BROACH) REV E 48.0S" },
    ],
  },
];

export const FALLBACK: Record<Lang, string> = {
  en: "I couldn't match that to an indexed chunk. Try one of the quick topics above — hex wrench size, platform dimensions, or CNC programs — or rephrase with a part number such as Z1 or O0013.",
  ar: "لم أجد مطابقة في الفهرس. جرّب أحد المواضيع السريعة بالأعلى — مقاس السداسي، أبعاد المنصة، أو برامج CNC — أو أعد الصياغة برقم قطعة مثل Z1 أو O0013.",
};

export function matchEntry(text: string): KBEntry | null {
  const q = text.toLowerCase();
  let best: KBEntry | null = null;
  let bestScore = 0;
  for (const entry of KB) {
    const score = entry.keywords.reduce((n, k) => (q.includes(k.toLowerCase()) ? n + 1 : n), 0);
    if (score > bestScore) { best = entry; bestScore = score; }
  }
  return best;
}

export const CHIP_QUESTIONS: Record<string, Record<Lang, string>> = {
  hex:      { en: "What internal hex wrench size is broached into the implant?",
              ar: "ما مقاس المفتاح السداسي الداخلي المشكَّل في الزرعة؟" },
  platform: { en: "What are the Z1 platform dimensions?",
              ar: "ما أبعاد منصة الزرعة Z1؟" },
  cnc:      { en: "Which CNC programs run the Z1 part?",
              ar: "ما برامج CNC التي تشغّل قطعة Z1؟" },
};

export const UI = {
  brand: "EG Medical Z1",
  system: "CNC Industrial RAG Assistant",
  statusOnline: { en: "Index online", ar: "الفهرس متصل" },
  chunks:       { en: "1,284 chunks", ar: "1,284 مقطع" },
  askArabic:    "اسأل بالعربي",
  askEnglish:   "Ask in English",
  chips:        { en: ["Hex wrench size", "Platform dimensions", "CNC programs"],
                  ar: ["مقاس المفتاح السداسي", "أبعاد المنصة", "برامج CNC"] },
  placeholder:  { en: "Ask about specs, tools, or programs…", ar: "اسأل عن المواصفات أو الأدوات أو البرامج…" },
  send:         { en: "Send", ar: "إرسال" },
  retrieved:    { en: "Retrieved Sources", ar: "المصادر المسترجعة" },
  noSources:    { en: "Sources: none in index.", ar: "المصادر: لا يوجد في الفهرس." },
  relevance:    { en: "relevance", ar: "مطابقة" },
  thinking:     { en: ["Embedding query…", "Searching 1,284 chunks…", "Reranking top-k…"],
                  ar: ["تحويل الاستعلام…", "البحث في 1,284 مقطع…", "إعادة ترتيب النتائج…"] },
  you:          { en: "Engineer", ar: "المهندس" },
  assistant:    { en: "Z1 Assistant", ar: "مساعد Z1" },
  footer:       { en: "Built for precision manufacturing intelligence · Powered by RAG + LLM",
                  ar: "صُمم لاستخبارات التصنيع الدقيق · يعمل بتقنية RAG + LLM" },
  hint:         { en: "Answers are grounded in the Z1 document index. Always verify against the released drawing.",
                  ar: "الإجابات مستندة إلى فهرس مستندات Z1. تحقّق دائمًا من الرسم المعتمد." },
};
