"""
Arithmancy — Multi-Tradition Numerology & Astro System
=================================================
Integrates 4 World Systems:
1. Pythagorean (Western) System: Life Path, Expression, Soul Urge, Personality.
2. Chaldean (Babylonian) System: 1-8 letter vibration, compound numbers, occult meanings.
3. Chinese (Eight Mansions) Kua: Gregorian-year approximation, East/West Group and Element; no BaZi chart or Lo Shu grid.
4. Indian / Vedic (Ank Jyotish) System: Mulank (Driver), Bhagyank (Conductor), Namank (Name), Navagraha Planetary Rulers.

Supports:
- Individual Profile Calculation across all 4 traditions.
- Couple Compatibility Synastry across all 4 traditions with an aggregated Global Multi-System Score.
"""

from datetime import date
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import unicodedata
import json
import sys


# ============================================================================
# 1. CORE HELPER FUNCTIONS & LETTER TABLES
# ============================================================================

PYTHAGOREAN_TABLE = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9,
}

# Chaldean: Numbers 1-8 only (9 is considered sacred/divine and not assigned to letters)
CHALDEAN_TABLE = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

VOWELS = set('AEIOU')
MASTER_NUMBERS = {11, 22, 33}


def clean_string(text: str) -> str:
    """Normalize and strip non-alphabetical characters."""
    text = text.translate(str.maketrans({'ß':'ss','ẞ':'SS','Æ':'AE','æ':'ae','Ø':'O','ø':'o','Ł':'L','ł':'l','Œ':'OE','œ':'oe'}))
    normalized = unicodedata.normalize('NFKD', text)
    ascii_only = normalized.encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(c.upper() for c in ascii_only if c.isalpha())



def reduce_number(num: int, keep_master: bool = True) -> int:
    """Reduce a number by repeatedly summing its digits until a single digit or master number."""
    if isinstance(num, bool) or not isinstance(num, int) or num < 0:
        raise ValueError("Number must be a non-negative integer.")
    while num > 9:
        if keep_master and num in MASTER_NUMBERS:
            return num
        num = sum(int(digit) for digit in str(num))
    return num



def base_root(num: int) -> int:
    """Get the single-digit root (reduces master numbers 11->2, 22->4, 33->6)."""
    if isinstance(num, bool) or not isinstance(num, int) or num < 0:
        raise ValueError("Number must be a non-negative integer.")
    while num > 9:
        num = sum(int(d) for d in str(num))
    return num



# ============================================================================
# 2. CHALDEAN (BABYLONIAN) SYSTEM
# ============================================================================

CHALDEAN_COMPOUND_MEANINGS = {
    10: "Wheel of Fortune - Honor, faith, self-reliance, and rise to success.",
    11: "Clenched Ox - High intuition, trials of fortitude, hidden perils.",
    12: "The Sacrifice - Deep anxiety of mind, philosophical sacrifice for higher wisdom.",
    13: "Regeneration - Upheaval leading to powerful transformation and rebirth.",
    14: "Movement & Challenge - High adaptability, business acumen, cautionary travel.",
    15: "The Magician - Eloquence, artistic gifts, magnetic personal magnetism.",
    16: "The Shattered Citadel - Sudden warnings, spiritual awakening through humility.",
    17: "The Star of the Magi - Hope, peace, celestial blessings, enduring reputation.",
    18: "Spiritual Conflict - Material deception, intuitive defense against betrayal.",
    19: "The Prince of Heaven - Radiant victory, supreme honor, happiness, and vitality.",
    20: "The Awakening - High spiritual calling, renewed purpose, justice.",
    21: "The Crown of the Magi - Culmination of victory, world recognition, mastery.",
    22: "Master Visionary - Great dreams, requires steadfast alertness to illusion.",
    23: "The Royal Star of the Lion - Guaranteed protection, royal favor, success.",
    24: "Love & Abundance - Mutual attraction, financial comfort, harmonious fortune.",
    25: "Strength Through Trial - Wisdom earned through overcoming difficulties.",
    26: "The Partnership Anchor - Powerful alliances, caution with ungrounded speculation.",
    27: "The Sceptre - High intellect, creative leadership, command over crowds.",
    28: "The Contradiction - High potential tested by unexpected rivalry.",
    29: "Uncertainty & Insight - Heavy emotional tests, deep mystical perceptions.",
    30: "Philosophical Superiority - Mental mastery, literary brilliance, detachment.",
    31: "The Solitary Thinker - Deep intellect, prefers quiet autonomy over crowds.",
    32: "The Communicator - International fame, persuasive speech, social charm.",
    33: "Universal Protection - Master vibration of unconditional wisdom and grace."
}


def calculate_chaldean_profile(first_name: str, last_name: str) -> Tuple[int, int, str]:
    clean_full = clean_string(first_name) + clean_string(last_name)
    raw_sum = sum(CHALDEAN_TABLE.get(ch, 0) for ch in clean_full)
    root = base_root(raw_sum)
    compound_desc = CHALDEAN_COMPOUND_MEANINGS.get(
        raw_sum, f"Compound {raw_sum}: Harmonious planetary vibration reducing to root {root}."
    )
    return raw_sum, root, compound_desc


# ============================================================================
# 3. CHINESE NUMEROLOGY SYSTEM (KUA & LO SHU GRID)
# ============================================================================

KUA_DATA = {
    1: {"element": "Water", "trigram": "Kan (☵)", "group": "East", "direction": "North", "traits": "Deeply intuitive, adaptable, wise, career-focused."},
    2: {"element": "Earth", "trigram": "Kun (☷)", "group": "West", "direction": "Southwest", "traits": "Receptive, nurturing, patient, marital loyalty."},
    3: {"element": "Wood", "trigram": "Zhen (☳)", "group": "East", "direction": "East", "traits": "Dynamic, innovative, impulsive, growth-oriented."},
    4: {"element": "Wood", "trigram": "Xun (☴)", "group": "East", "direction": "Southeast", "traits": "Gentle, communicative, flexible, wealth-attracting."},
    6: {"element": "Metal", "trigram": "Qian (☰)", "group": "West", "direction": "Northwest", "traits": "Authoritative, dignified, disciplined, executive."},
    7: {"element": "Metal", "trigram": "Dui (☱)", "group": "West", "direction": "West", "traits": "Joyful, persuasive, artistic, loves socializing."},
    8: {"element": "Earth", "trigram": "Gen (☶)", "group": "West", "direction": "Northeast", "traits": "Steadfast, contemplative, trustworthy, scholarly."},
    9: {"element": "Fire", "trigram": "Li (☲)", "group": "East", "direction": "South", "traits": "Passionate, radiant, enlightened, charismatic."}
}


def calculate_chinese_kua(year: int, gender: str) -> Tuple[int, Dict[str, str]]:
    """Calculates Chinese Kua (Gua) number using a Gregorian birth-year approximation and a selected gender formula."""
    if not isinstance(year,int) or not 1 <= year <= 9999:
        raise ValueError("Invalid birth year.")
    # Gregorian-year approximation; no solar-term boundary correction.
    g = gender.strip().lower()
    if g not in ["male","m","female","f","non-binary","nonbinary","nb"]:
        raise ValueError("Unknown gender.")
    male = g in ["male","m"]
    kua = ((2-year) if male else (year-5)) % 9 or 9
    if kua == 5: kua = 2 if male else 8

    kua_info = KUA_DATA.get(kua, KUA_DATA[1])
    return kua, kua_info


def evaluate_chinese_kua_compatibility(kua1: int, kua2: int) -> Tuple[int, str, str]:
    info1 = KUA_DATA.get(kua1, KUA_DATA[1])
    info2 = KUA_DATA.get(kua2, KUA_DATA[1])
    
    # Same Feng Shui Group (East+East or West+West)
    if info1["group"] == info2["group"]:
        score = 92
        title = f"Harmonious {info1['group']} Group Resonance"
        desc = f"Both belong to the {info1['group']} Group ({info1['element']} & {info2['element']}), sharing natural spatial and energetic rhythms."
    else:
        score = 74
        title = "Complementary East-West Interplay"
        desc = f"East Group meets West Group. Different elemental orientations require conscious mutual adjustment in lifestyle and home energy."

    return score, title, desc


# ============================================================================
# 4. INDIAN / VEDIC NUMEROLOGY SYSTEM (ANK JYOTISH & NAVAGRAHA)
# ============================================================================

VEDIC_GRAHAS = {
    1: {"planet": "Surya (Sun)", "deity": "The Solar King", "nature": "Sattvic", "element": "Fire", "role": "Leadership, soul authority, self-respect."},
    2: {"planet": "Chandra (Moon)", "deity": "The Lunar Queen", "nature": "Sattvic", "element": "Water", "role": "Mind, emotional depth, sensitivity, grace."},
    3: {"planet": "Guru (Jupiter)", "deity": "The Supreme Preceptor", "nature": "Sattvic", "element": "Ether", "role": "Wisdom, counselor, knowledge, morality."},
    4: {"planet": "Rahu (North Node)", "deity": "The Cosmic Rebel", "nature": "Tamasic", "element": "Air", "role": "Unconventional genius, sudden shifts, worldly fame."},
    5: {"planet": "Budh (Mercury)", "deity": "The Prince of Commerce", "nature": "Rajasic", "element": "Earth", "role": "Intellect, business, wit, communication."},
    6: {"planet": "Shukra (Venus)", "deity": "The Master of Arts", "nature": "Rajasic", "element": "Water", "role": "Love, luxury, romance, beauty, diplomacy."},
    7: {"planet": "Ketu (South Node)", "deity": "The Mystic Ascetic", "nature": "Tamasic", "element": "Fire", "role": "Intuition, spiritual research, detachment, occult depth."},
    8: {"planet": "Shani (Saturn)", "deity": "The Lord of Karma", "nature": "Tamasic", "element": "Air", "role": "Justice, discipline, patience, endurance, long-term mastery."},
    9: {"planet": "Mangal (Mars)", "deity": "The Commander-in-Chief", "nature": "Rajasic", "element": "Fire", "role": "Courage, energy, protective warrior, decisive action."}
}

# Vedic Planetary Friendship Matrix: {Number: (Friends, Neutrals, Enemies)}
VEDIC_RELATIONS = {
    1: ([2, 3, 9], [5], [4, 6, 7, 8]),
    2: ([1, 3], [4, 7, 8, 9], [5, 6]),
    3: ([1, 2, 9], [5, 8], [6]),
    4: ([5, 6, 8], [7], [1, 2, 9]),
    5: ([1, 4, 6], [3, 8], [2]),
    6: ([4, 5, 7, 8], [3], [1, 2]),
    7: ([4, 6], [1, 2, 3, 5, 8], [9]),
    8: ([4, 5, 6], [3, 7], [1, 2, 9]),
    9: ([1, 2, 3], [5, 7], [4, 8])
}


def calculate_vedic_profile(birth_day: int, birth_month: int, birth_year: int, full_name: str) -> Tuple[int, int, int, Dict[str, str]]:
    date(birth_year,birth_month,birth_day)
    mulank = base_root(birth_day)  # Driver / Psychic Number
    bhagyank = base_root(birth_day + birth_month + birth_year)  # Conductor / Destiny Number
    
    # Namank calculated via Chaldean values (standard in Vedic Ank Jyotish)
    clean_n = clean_string(full_name)
    namank = base_root(sum(CHALDEAN_TABLE.get(ch, 0) for ch in clean_n))
    
    graha_info = VEDIC_GRAHAS.get(mulank, VEDIC_GRAHAS[1])
    return mulank, bhagyank, namank, graha_info


def evaluate_vedic_compatibility(mul1: int, mul2: int) -> Tuple[int, str, str]:
    friends1, neutrals1, enemies1 = VEDIC_RELATIONS.get(mul1, ([1], [2], [3]))
    g1 = VEDIC_GRAHAS[mul1]
    g2 = VEDIC_GRAHAS[mul2]

    def directional(a,b):
        friends,neutral,enemies=VEDIC_RELATIONS[a]
        return 92 if b in friends else (80 if b in neutral or a==b else 65)
    score=int(round((directional(mul1,mul2)+directional(mul2,mul1))/2))
    status="Mutual planetary affinity" if score>=85 else ("Mixed planetary bond" if score>=75 else "Challenging planetary pair")
    desc=f"{g1['planet']} and {g2['planet']}: average of both directional relationship scores."

    return score, status, desc


# ============================================================================
# 5. ASTROLOGY (ZODIAC) CALCULATION FROM BIRTHDAY
# ============================================================================

def calculate_zodiac_sign(month: int, day: int) -> str:
    date(2000, month, day)
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "Aries"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "Taurus"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "Gemini"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "Cancer"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "Leo"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "Virgo"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "Libra"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "Scorpio"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "Sagittarius"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19): return "Capricorn"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "Aquarius"
    return "Pisces"


ZODIAC_DATA = {
    "Aries": {"symbol": "♈", "element": "Fire", "modality": "Cardinal", "ruler": "Mars", "keywords": ["Bold", "Pioneering", "Direct", "Passionate"], "archetype": "The Trailblazer"},
    "Taurus": {"symbol": "♉", "element": "Earth", "modality": "Fixed", "ruler": "Venus", "keywords": ["Grounded", "Reliable", "Patient", "Devoted"], "archetype": "The Anchor"},
    "Gemini": {"symbol": "♊", "element": "Air", "modality": "Mutable", "ruler": "Mercury", "keywords": ["Witty", "Curious", "Adaptable", "Communicative"], "archetype": "The Messenger"},
    "Cancer": {"symbol": "♋", "element": "Water", "modality": "Cardinal", "ruler": "Moon", "keywords": ["Empathetic", "Nurturing", "Intuitive", "Protective"], "archetype": "The Guardian"},
    "Leo": {"symbol": "♌", "element": "Fire", "modality": "Fixed", "ruler": "Sun", "keywords": ["Charismatic", "Generous", "Confident", "Expressive"], "archetype": "The Sovereign"},
    "Virgo": {"symbol": "♍", "element": "Earth", "modality": "Mutable", "ruler": "Mercury", "keywords": ["Analytical", "Diligent", "Practical", "Meticulous"], "archetype": "The Craftsman"},
    "Libra": {"symbol": "♎", "element": "Air", "modality": "Cardinal", "ruler": "Venus", "keywords": ["Diplomatic", "Fair-minded", "Charming", "Harmonious"], "archetype": "The Harmonizer"},
    "Scorpio": {"symbol": "♏", "element": "Water", "modality": "Fixed", "ruler": "Pluto / Mars", "keywords": ["Intense", "Perceptive", "Loyal", "Transformative"], "archetype": "The Alchemist"},
    "Sagittarius": {"symbol": "♐", "element": "Fire", "modality": "Mutable", "ruler": "Jupiter", "keywords": ["Adventurous", "Optimistic", "Philosophical", "Honest"], "archetype": "The Explorer"},
    "Capricorn": {"symbol": "♑", "element": "Earth", "modality": "Cardinal", "ruler": "Saturn", "keywords": ["Ambitious", "Disciplined", "Strategic", "Enduring"], "archetype": "The Master Builder"},
    "Aquarius": {"symbol": "♒", "element": "Air", "modality": "Fixed", "ruler": "Uranus / Saturn", "keywords": ["Innovative", "Independent", "Humanitarian", "Intellectual"], "archetype": "The Visionary"},
    "Pisces": {"symbol": "♓", "element": "Water", "modality": "Mutable", "ruler": "Neptune / Jupiter", "keywords": ["Compassionate", "Intuitive", "Artistic", "Tender"], "archetype": "The Dreamer"}
}

SIGN_INDICES = {name: i for i, name in enumerate([
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
])}


def get_astrological_aspect(sign1: str, sign2: str) -> Tuple[str, int]:
    diff = abs(SIGN_INDICES[sign1] - SIGN_INDICES[sign2])
    dist = min(diff, 12 - diff)
    aspects = {
        0: ("Conjunction", 0), 1: ("Semi-Sextile", 30), 2: ("Sextile", 60),
        3: ("Square", 90), 4: ("Trine", 120), 5: ("Quincunx", 150), 6: ("Opposition", 180)
    }
    return aspects.get(dist, ("Aspect", 0))


# ============================================================================
# 6. COMPREHENSIVE DATA STRUCTURES
# ============================================================================

@dataclass
class MultiTraditionPerson:
    first_name: str
    last_name: str
    birth_year: int
    birth_month: int
    birth_day: int
    gender: str
    
    # 1. Pythagorean (Western)
    pythagorean_life_path: int
    pythagorean_expression: int
    pythagorean_soul_urge: int
    pythagorean_personality: int
    
    # 2. Chaldean (Babylonian)
    chaldean_compound: int
    chaldean_root: int
    chaldean_meaning: str
    
    # 3. Chinese (Feng Shui / BaZi)
    chinese_kua: int
    chinese_group: str
    chinese_element: str
    chinese_trigram: str
    
    # 4. Indian / Vedic (Ank Jyotish)
    vedic_mulank: int     # Driver / Psychic
    vedic_bhagyank: int   # Conductor / Destiny
    vedic_namank: int     # Name Number
    vedic_planet: str     # Navagraha Deity
    
    # Astrology & Polarity
    zodiac_sign: str
    zodiac_element: str
    zodiac_symbol: str
    polarity: str


@dataclass
class GlobalCompatibilityResult:
    person_1: MultiTraditionPerson
    person_2: MultiTraditionPerson
    
    global_score: int             # Aggregate of all 4 traditions (0-100)
    pythagorean_score: int
    chaldean_score: int
    chinese_score: int
    vedic_score: int
    
    partner_score: int
    friend_score: int
    colleague_score: int
    
    chaldean_dynamic: str
    chinese_dynamic: str
    vedic_dynamic: str
    astrological_dynamic: str
    advice: str


def build_multi_tradition_person(
    first: str, last: str, year: int, month: int, day: int, gender: str
) -> MultiTraditionPerson:
    date(year,month,day)
    if not clean_string(first) or not clean_string(last):
        raise ValueError("First and last names must contain Latin letters.")
    full_clean = clean_string(first) + clean_string(last)
    
    # 1. Pythagorean
    pyth_exp = reduce_number(sum(PYTHAGOREAN_TABLE.get(c, 0) for c in full_clean))
    pyth_soul = reduce_number(sum(PYTHAGOREAN_TABLE.get(c, 0) for c in full_clean if c in VOWELS))
    pyth_pers = reduce_number(sum(PYTHAGOREAN_TABLE.get(c, 0) for c in full_clean if c not in VOWELS))
    m_r = reduce_number(month)
    d_r = reduce_number(day)
    y_r = reduce_number(year)
    pyth_lp = reduce_number(m_r + d_r + y_r)
    
    # 2. Chaldean
    ch_comp, ch_root, ch_desc = calculate_chaldean_profile(first, last)
    
    # 3. Chinese
    kua, kua_info = calculate_chinese_kua(year, gender)
    
    # 4. Vedic
    mul, bhag, nam, graha = calculate_vedic_profile(day, month, year, f"{first} {last}")
    
    # Astrology & Polarity
    z_sign = calculate_zodiac_sign(month, day)
    z_info = ZODIAC_DATA[z_sign]
    
    g_norm = "Female" if gender.upper().startswith("F") else ("Male" if gender.upper().startswith("M") else "Non-Binary")
    polarity = "Yin (Magnetic)" if g_norm == "Female" else ("Yang (Projective)" if g_norm == "Male" else "Unified")

    return MultiTraditionPerson(
        first_name=first.strip(),
        last_name=last.strip(),
        birth_year=year,
        birth_month=month,
        birth_day=day,
        gender=g_norm,
        pythagorean_life_path=pyth_lp,
        pythagorean_expression=pyth_exp,
        pythagorean_soul_urge=pyth_soul,
        pythagorean_personality=pyth_pers,
        chaldean_compound=ch_comp,
        chaldean_root=ch_root,
        chaldean_meaning=ch_desc,
        chinese_kua=kua,
        chinese_group=kua_info["group"],
        chinese_element=kua_info["element"],
        chinese_trigram=kua_info["trigram"],
        vedic_mulank=mul,
        vedic_bhagyank=bhag,
        vedic_namank=nam,
        vedic_planet=graha["planet"],
        zodiac_sign=z_sign,
        zodiac_element=z_info["element"],
        zodiac_symbol=z_info["symbol"],
        polarity=polarity
    )


def evaluate_global_compatibility(p1: MultiTraditionPerson, p2: MultiTraditionPerson) -> GlobalCompatibilityResult:
    # 1. Pythagorean Western Score (approx from Life Path + Soul Urge + Expression)
    # Simple harmonic root delta
    diff_lp = abs(base_root(p1.pythagorean_life_path) - base_root(p2.pythagorean_life_path))
    pyth_score = max(60, 96 - (diff_lp * 4))
    
    # 2. Chaldean Babylonian Score (harmony of roots)
    diff_ch = abs(p1.chaldean_root - p2.chaldean_root)
    chaldean_score = max(62, 95 - (diff_ch * 5))
    chaldean_dyn = f"Compound {p1.chaldean_compound} meets Compound {p2.chaldean_compound} (Roots {p1.chaldean_root} & {p2.chaldean_root})"
    
    # 3. Chinese Kua Score
    chinese_score, chinese_title, chinese_desc = evaluate_chinese_kua_compatibility(p1.chinese_kua, p2.chinese_kua)
    chinese_dyn = f"{chinese_title} ({p1.chinese_element} Kua {p1.chinese_kua} & {p2.chinese_element} Kua {p2.chinese_kua})"
    
    # 4. Vedic Ank Jyotish Score
    vedic_score, vedic_status, vedic_desc = evaluate_vedic_compatibility(p1.vedic_mulank, p2.vedic_mulank)
    vedic_dyn = f"{vedic_status}: {p1.vedic_planet} & {p2.vedic_planet} (Mulanks {p1.vedic_mulank} & {p2.vedic_mulank})"
    
    # Astrological Aspect
    asp_name, _ = get_astrological_aspect(p1.zodiac_sign, p2.zodiac_sign)
    astro_dyn = f"{p1.zodiac_symbol} {p1.zodiac_sign} ({p1.zodiac_element}) & {p2.zodiac_symbol} {p2.zodiac_sign} ({p2.zodiac_element}) in {asp_name}"
    
    # Global Aggregate Score
    global_score = int(round(0.30 * pyth_score + 0.25 * chaldean_score + 0.25 * vedic_score + 0.20 * chinese_score))
    
    # Role Scores
    partner_score = int(round(global_score * 0.98 + (4 if p1.polarity != p2.polarity else 0)))
    partner_score = min(100, max(50, partner_score))
    friend_score = int(round(global_score * 0.96 + (3 if p1.chinese_group == p2.chinese_group else 0)))
    friend_score = min(100, max(50, friend_score))
    colleague_score = int(round(global_score * 0.95 + (4 if vedic_score >= 85 else 0)))
    colleague_score = min(100, max(50, colleague_score))

    advice = (
        f"Harmonize through the strengths of each tradition: Western Life Path {p1.pythagorean_life_path} & {p2.pythagorean_life_path} "
        f"define your road; Vedic {p1.vedic_planet} and {p2.vedic_planet} govern temperament; "
        f"Chaldean compounds bring mystical protection; Chinese {p1.chinese_element}/{p2.chinese_element} energies establish daily balance."
    )

    return GlobalCompatibilityResult(
        person_1=p1,
        person_2=p2,
        global_score=global_score,
        pythagorean_score=pyth_score,
        chaldean_score=chaldean_score,
        chinese_score=chinese_score,
        vedic_score=vedic_score,
        partner_score=partner_score,
        friend_score=friend_score,
        colleague_score=colleague_score,
        chaldean_dynamic=chaldean_dyn,
        chinese_dynamic=chinese_dyn,
        vedic_dynamic=vedic_dyn,
        astrological_dynamic=astro_dyn,
        advice=advice
    )


# ============================================================================
# 7. FORMATTERS
# ============================================================================

COLOR_NUMEROLOGY = {1: {'name': 'Ruby red', 'hex': '#fca5a5', 'hue': 0, 'reading': 'Initiative, courage and independent expression.'}, 2: {'name': 'Amber orange', 'hex': '#fdba74', 'hue': 27, 'reading': 'Warmth, cooperation and sensitivity.'}, 3: {'name': 'Sunshine yellow', 'hex': '#fde68a', 'hue': 48, 'reading': 'Creativity, optimism and communication.'}, 4: {'name': 'Emerald green', 'hex': '#6ee7b7', 'hue': 155, 'reading': 'Steadiness, growth and practical foundations.'}, 5: {'name': 'Sky blue', 'hex': '#7dd3fc', 'hue': 199, 'reading': 'Curiosity, freedom and adaptable thinking.'}, 6: {'name': 'Indigo', 'hex': '#a5b4fc', 'hue': 235, 'reading': 'Care, responsibility and thoughtful harmony.'}, 7: {'name': 'Amethyst purple', 'hex': '#d8b4fe', 'hue': 275, 'reading': 'Reflection, intuition and inner exploration.'}, 8: {'name': 'Rose pink', 'hex': '#f9a8d4', 'hue': 330, 'reading': 'Ambition balanced with kindness and connection.'}, 9: {'name': 'Golden light', 'hex': '#fcd34d', 'hue': 44, 'reading': 'Generosity, compassion and a wider perspective.'}}

def calculate_color_numerology(life_path: int) -> dict:
    number = base_root(life_path)
    if number not in COLOR_NUMEROLOGY:
        raise ValueError("Life Path must have a root between 1 and 9.")
    return {"number": number, **COLOR_NUMEROLOGY[number]}

ROOT_READINGS = {1: {'theme': 'Independence and initiative', 'strength': 'Starting projects and expressing a clear direction.', 'growth': 'Make room for other viewpoints before taking the lead.', 'relationship': 'Balance personal freedom with shared decisions.'}, 2: {'theme': 'Cooperation and sensitivity', 'strength': 'Listening carefully and noticing other people’s needs.', 'growth': 'State your own needs rather than avoiding disagreement.', 'relationship': 'Build trust through clear, gentle communication.'}, 3: {'theme': 'Expression and creativity', 'strength': 'Sharing ideas, humour and imaginative solutions.', 'growth': 'Follow inspiration with practical commitments.', 'relationship': 'Use conversation and shared creativity to connect.'}, 4: {'theme': 'Structure and reliability', 'strength': 'Planning, steady effort and dependable routines.', 'growth': 'Leave room for flexibility when plans change.', 'relationship': 'Discuss routines and expectations openly.'}, 5: {'theme': 'Adaptability and exploration', 'strength': 'Learning through variety and new experiences.', 'growth': 'Choose priorities so change does not become distraction.', 'relationship': 'Agree on a balance between adventure and consistency.'}, 6: {'theme': 'Care and responsibility', 'strength': 'Supporting others and creating a welcoming atmosphere.', 'growth': 'Help without taking responsibility for everyone.', 'relationship': 'Give care while respecting mutual boundaries.'}, 7: {'theme': 'Reflection and insight', 'strength': 'Research, thoughtful questions and independent study.', 'growth': 'Share your thinking rather than withdrawing completely.', 'relationship': 'Balance quiet time with emotional availability.'}, 8: {'theme': 'Organisation and ambition', 'strength': 'Managing resources and working towards concrete goals.', 'growth': 'Measure success through relationships as well as results.', 'relationship': 'Discuss power, responsibilities and shared goals.'}, 9: {'theme': 'Compassion and perspective', 'strength': 'Seeing the wider picture and contributing to others.', 'growth': 'Set limits so generosity remains sustainable.', 'relationship': 'Connect through shared values while accepting differences.'}}

def format_multi_tradition_individual(p: MultiTraditionPerson) -> str:
    lines = []
    lines.append("=" * 76)
    lines.append(f"     GLOBAL 4-TRADITION PROFILE: {p.first_name.upper()} {p.last_name.upper()}")
    lines.append("=" * 76)
    lines.append(f"Born: {p.birth_year:04d}-{p.birth_month:02d}-{p.birth_day:02d} | Gender: {p.gender} ({p.polarity})")
    lines.append(f"Zodiac: {p.zodiac_symbol} {p.zodiac_sign} ({p.zodiac_element} Element)")
    lines.append("-" * 76)
    color=calculate_color_numerology(p.pythagorean_life_path)
    lines.append(f"COLOR NUMEROLOGY: {color['name']} (Color number {color['number']}) — {color['reading']}")
    lines.append("Color mapping is an authored symbolic convention based on the Life Path root.")
    lines.append("1. PYTHAGOREAN (WESTERN) TRADITION:")
    lines.append(f"   • Life Path Number     : {p.pythagorean_life_path}")
    lines.append(f"   • Expression (Destiny) : {p.pythagorean_expression}")
    lines.append(f"   • Soul Urge (Heart)    : {p.pythagorean_soul_urge}")
    lines.append(f"   • Personality (Outer)  : {p.pythagorean_personality}")
    lines.append("\n2. CHALDEAN (BABYLONIAN) TRADITION:")
    lines.append(f"   • Name Vibration       : Compound {p.chaldean_compound} (Root {p.chaldean_root})")
    lines.append(f"   • Ancient Meaning      : {p.chaldean_meaning}")
    reading = ROOT_READINGS[p.chaldean_root]
    lines.append(f"   • Root Reading         : {reading['theme']}. {reading['strength']}")
    lines.append(f"   • Growth Reflection    : {reading['growth']}")
    lines.append("\n3. CHINESE (EIGHT MANSIONS KUA) NUMEROLOGY:")
    lines.append(f"   • Kua (Gua) Number     : {p.chinese_kua} ({p.chinese_trigram})")
    lines.append(f"   • Feng Shui Group      : {p.chinese_group} Group ({p.chinese_element} Element)")
    lines.append(f"   • Kua Reading          : {KUA_DATA[p.chinese_kua]['traits']}")
    lines.append("   • Convention           : Gregorian year; no Li Chun correction. Non-binary uses female formula.")
    lines.append("\n4. INDIAN / VEDIC (ANK JYOTISH) TRADITION:")
    lines.append(f"   • Mulank (Driver)      : {p.vedic_mulank} (Ruled by {p.vedic_planet})")
    lines.append(f"   • Bhagyank (Conductor) : {p.vedic_bhagyank}")
    lines.append(f"   • Namank (Name Sound)  : {p.vedic_namank}")
    for label, number in [("Mulank",p.vedic_mulank),("Bhagyank",p.vedic_bhagyank),("Namank",p.vedic_namank)]:
        info=VEDIC_GRAHAS[number]
        lines.append(f"   • {label} Reading: {info['planet']} — {info['role']}")
    lines.append("For entertainment: readings and scores are symbolic, not predictions.")
    lines.append("=" * 76)
    return "\n".join(lines)


def format_global_compatibility_report(res: GlobalCompatibilityResult) -> str:
    p1 = res.person_1
    p2 = res.person_2
    lines = []
    lines.append("=" * 76)
    lines.append("      GLOBAL 4-TRADITION COMPATIBILITY SYNTHESIS")
    lines.append("=" * 76)
    lines.append(f"Person 1: {p1.first_name} {p1.last_name} | Kua {p1.chinese_kua} | Mulank {p1.vedic_mulank} ({p1.vedic_planet})")
    lines.append(f"Person 2: {p2.first_name} {p2.last_name} | Kua {p2.chinese_kua} | Mulank {p2.vedic_mulank} ({p2.vedic_planet})")
    lines.append("-" * 76)
    lines.append(f"★ GLOBAL HARMONY SCORE: {res.global_score}%")
    lines.append(f"  • Pythagorean (Western) : {res.pythagorean_score}%")
    lines.append(f"  • Chaldean (Babylonian) : {res.chaldean_score}%")
    lines.append(f"  • Indian (Vedic)        : {res.vedic_score}%")
    lines.append(f"  • Chinese (Feng Shui)   : {res.chinese_score}%")
    lines.append("-" * 76)
    lines.append("RELATIONSHIP BREAKDOWN:")
    lines.append(f"  ❤️ Partners   : {res.partner_score}%")
    lines.append(f"  🤝 Friends    : {res.friend_score}%")
    lines.append(f"  💼 Colleagues : {res.colleague_score}%")
    lines.append("-" * 76)
    lines.append("CROSS-TRADITION DYNAMICS:")
    lines.append(f"  • Astrology : {res.astrological_dynamic}")
    lines.append(f"  • Vedic     : {res.vedic_dynamic}")
    lines.append(f"  • Chinese   : {res.chinese_dynamic}")
    lines.append(f"  • Chaldean  : {res.chaldean_dynamic}")
    lines.append(f"\nGUIDANCE: {res.advice}")
    lines.append("=" * 76)
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) >= 13:
        p1 = build_multi_tradition_person(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
        p2 = build_multi_tradition_person(sys.argv[7], sys.argv[8], int(sys.argv[9]), int(sys.argv[10]), int(sys.argv[11]), sys.argv[12])
        print(format_global_compatibility_report(evaluate_global_compatibility(p1, p2)))
    elif len(sys.argv) >= 7:
        p = build_multi_tradition_person(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
        print(format_multi_tradition_individual(p))
    else:
        print("\n--- [INDIVIDUAL 4-TRADITION PROFILE DEMO (Marie Curie)] ---")
        p_demo = build_multi_tradition_person("Marie", "Curie", 1867, 11, 7, "Female")
        print(format_multi_tradition_individual(p_demo))
        
        print("\n--- [GLOBAL 4-TRADITION COUPLE COMPATIBILITY DEMO] ---")
        p2_demo = build_multi_tradition_person("Pierre", "Curie", 1859, 5, 15, "Male")
        print(format_global_compatibility_report(evaluate_global_compatibility(p_demo, p2_demo)))
