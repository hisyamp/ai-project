import re
from dataclasses import dataclass

INJECTION_PATTERNS = [
    r"\babaikan\s+(semua\s+|seluruh\s+)?instruksi\b",
    r"\bignore\s+(all\s+|previous\s+|above\s+)?instructions?\b",
    r"\bdisregard\s+(all\s+|previous\s+|above\s+)?instructions?\b",
    r"\blupakan\s+(semua\s+|seluruh\s+)?(instruksi|aturan|perintah)\b",
    r"\bkamu\s+(sekarang\s+)?adalah\b",
    r"\byou\s+are\s+now\b",
    r"\bact\s+as\b",
    r"\bberperan\s*lah\s+sebagai\b",
    r"\btampilkan\s+(system\s*prompt|instruksi\s+sistem|prompt\s+asli)\b",
    r"\bshow\s+(me\s+)?(your\s+)?(system\s*prompt|instructions?)\b",
    r"\breveal\s+(your\s+)?(system\s*prompt|instructions?)\b",
    r"\bapa\s+(itu\s+)?system\s*prompt\s*(mu|kamu)?\b",
    r"\bapi\s*key\b",
    r"\bcetak\s+(api\s*key|kredensial|token)\b",
    r"\bprint\s+(the\s+)?(api\s*key|credentials?|token)\b",
    r"\bjailbreak\b",
    r"\bdeveloper\s+mode\b",
    r"\bmode\s+pengembang\b",
    r"\bbypass\s+(filter|aturan|instruksi)\b",
]

_INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), flags=re.IGNORECASE)

ARCHIVE_QUERY_KEYWORDS = [
    "v1.4",
    "versi 1.4",
    "versi lama",
    "kebijakan lama",
    "sebelum revisi",
    "sebelum direvisi",
    "sebelum diperbarui",
    "riwayat perubahan",
    "apa bedanya",
    "apa perbedaan",
    "dibandingkan versi",
    "dulu bagaimana",
]


@dataclass
class RouteDecision:
    is_prompt_injection: bool
    include_archive: bool


def route(question: str) -> RouteDecision:
    is_injection = bool(_INJECTION_REGEX.search(question))
    question_lower = question.lower()
    include_archive = any(keyword in question_lower for keyword in ARCHIVE_QUERY_KEYWORDS)
    return RouteDecision(is_prompt_injection=is_injection, include_archive=include_archive)
