/**
 * English to Kannada Real-Time Phonetic Transliteration Engine
 * Dual-Mode:
 *  1. Online Mode: Google Input Tools API (kn-t-i0-und) for ultra-accurate Indian name transliteration.
 *  2. Offline Mode: Complete rule-based phonetic engine + common names dictionary for 100% offline support.
 */

(function(window) {
  // Common Karnataka student and staff names dictionary for instant offline lookup
  const COMMON_NAMES_DICT = {
    "ananya": "ಅನನ್ಯ",
    "ramesh": "ರಮೇಶ್",
    "suresh": "ಸುರೇಶ್",
    "mahesh": "ಮಹೇಶ್",
    "ganesh": "ಗಣೇಶ್",
    "kavya": "ಕಾವ್ಯ",
    "pooja": "ಪೂಜಾ",
    "puja": "ಪೂಜಾ",
    "sneha": "ಸ್ನೇಹ",
    "bhavya": "ಭವ್ಯ",
    "divya": "ದಿವ್ಯ",
    "chaitra": "ಚೈತ್ರ",
    "deepa": "ದೀಪಾ",
    "kiran": "ಕಿರಣ್",
    "sanjay": "ಸಂಜಯ್",
    "vijay": "ವಿಜಯ್",
    "manoj": "ಮನೋಜ್",
    "manjunath": "ಮಂಜುನಾಥ್",
    "manjunatha": "ಮಂಜುನಾಥ",
    "kumar": "ಕುಮಾರ್",
    "gowda": "ಗೌಡ",
    "shree": "ಶ್ರೀ",
    "sri": "ಶ್ರೀ",
    "lakshmi": "ಲಕ್ಷ್ಮಿ",
    "laxmi": "ಲಕ್ಷ್ಮಿ",
    "rahul": "ರಾಹುಲ್",
    "rohit": "ರೋಹಿತ್",
    "priya": "ಪ್ರಿಯ",
    "priyanka": "ಪ್ರಿಯಾಂಕ",
    "shreya": "ಶ್ರೇಯಾ",
    "sahana": "ಸಹನ",
    "shweta": "ಶ್ವೇತ",
    "swathi": "ಸ್ವಾತಿ",
    "swati": "ಸ್ವಾತಿ",
    "chetan": "ಚೇತನ್",
    "pavan": "ಪವನ್",
    "prasad": "ಪ್ರಸಾದ್",
    "rakesh": "ರಾಕೇಶ್",
    "naveen": "ನವೀನ್",
    "darshan": "ದರ್ಶನ್",
    "yashas": "ಯಶಸ್",
    "harish": "ಹರೀಶ್",
    "anita": "ಅನಿತಾ",
    "geeta": "ಗೀತಾ",
    "meena": "ಮೀನಾ",
    "sumalatha": "ಸುಮಲತಾ",
    "roopa": "ರೂಪ",
    "asha": "ಆಶಾ",
    "rekha": "ರೇಖಾ",
    "varun": "ವರುಣ್",
    "tarun": "ತರುಣ್",
    "arun": "ಅರುಣ್",
    "anil": "ಅನಿಲ್",
    "sunil": "ಸುನಿಲ್",
    "vinay": "ವಿನಯ್",
    "akash": "ಆಕಾಶ್",
    "abhinav": "ಅಭಿನವ್",
    "abhishek": "ಅಭಿಷೇಕ್",
    "bharath": "ಭರತ್",
    "bharat": "ಭರತ್",
    "chandana": "ಚಂದನ",
    "dhanush": "ಧನುಷ್",
    "nandini": "ನಂದಿನಿ",
    "pallavi": "ಪಲ್ಲವಿ",
    "rashmi": "ರಶ್ಮಿ",
    "soundarya": "ಸೌಂದರ್ಯ",
    "tejas": "ತೇಜಸ್",
    "ujjwal": "ಉಜ್ವಲ್",
    "vidya": "ವಿದ್ಯಾ",
    "yamuna": "ಯಮುನಾ"
  };

  // Rule-based phonetic transliteration mapping
  const VOWELS = {
    "aa": "ಆ", "a": "ಅ",
    "ee": "ಈ", "ii": "ಈ", "i": "ಇ",
    "oo": "ಊ", "uu": "ಊ", "u": "ಉ",
    "ai": "ಐ", "ay": "ಐ",
    "au": "ಔ", "ou": "ಔ",
    "ea": "ಏ", "ee": "ಈ",
    "e": "ಎ", "o": "ಒ",
    "am": "ಅಂ", "ah": "ಅಃ"
  };

  const VOWEL_SIGNS = {
    "aa": "ಾ", "a": "",
    "ee": "ೀ", "ii": "ೀ", "i": "ಿ",
    "oo": "ೂ", "uu": "ೂ", "u": "ು",
    "ai": "ೈ", "ay": "ೈ",
    "au": "ೌ", "ou": "ೌ",
    "e": "ೆ", "o": "ೊ"
  };

  const CONSONANTS = {
    "k": "ಕ್", "kh": "ಖ್", "g": "ಗ್", "gh": "ಘ್", "ng": "ಙ್",
    "ch": "ಚ್", "chh": "ಛ್", "j": "ಜ್", "jh": "ಝ್", "ny": "ಞ್",
    "t": "ತ್", "th": "ಥ್", "d": "ದ್", "dh": "ಧ್", "n": "ನ್",
    "p": "ಪ್", "ph": "ಫ್", "f": "ಫ್", "b": "ಬ್", "bh": "ಭ್", "m": "ಮ್",
    "y": "ಯ್", "r": "ರ್", "l": "ಲ್", "v": "ವ್", "w": "ವ್",
    "sh": "ಶ್", "s": "ಸ್", "h": "ಹ್", "zh": "ಳ್",
    "c": "ಕ್", "x": "ಕ್ಸ್", "z": "ಜ್"
  };

  // Offline phonetic fallback converter
  function offlineTransliterateWord(word) {
    if (!word) return "";
    const lower = word.toLowerCase().trim();
    if (COMMON_NAMES_DICT[lower]) {
      return COMMON_NAMES_DICT[lower];
    }

    // Capitalized single letter initials (e.g. "S", "K", "R")
    if (word.length === 1 && /[A-Za-z]/.test(word)) {
      const initials = {
        "A": "ಎ", "B": "ಬಿ", "C": "ಸಿ", "D": "ಡಿ", "E": "ಇ", "F": "ಎಫ್",
        "G": "ಜಿ", "H": "ಎಚ್", "I": "ಐ", "J": "ಜೆ", "K": "ಕೆ", "L": "ಎಲ್",
        "M": "ಎಂ", "N": "ಎನ್", "O": "ಒ", "P": "ಪಿ", "Q": "ಕ್ಯೂ", "R": "ಆರ್",
        "S": "ಎಸ್", "T": "ಟಿ", "U": "ಯು", "V": "ವಿ", "W": "ಡಬ್ಲ್ಯೂ", "X": "ಎಕ್ಸ್",
        "Y": "ವೈ", "Z": "ಝಡ್"
      };
      return initials[word.toUpperCase()] || word;
    }

    let result = "";
    let i = 0;
    const len = lower.length;

    while (i < len) {
      // 3-char lookahead
      let c3 = lower.substr(i, 3);
      let c2 = lower.substr(i, 2);
      let c1 = lower.substr(i, 1);

      // Check consonants
      let cons = CONSONANTS[c3] || CONSONANTS[c2] || CONSONANTS[c1];
      let consLen = CONSONANTS[c3] ? 3 : (CONSONANTS[c2] ? 2 : (CONSONANTS[c1] ? 1 : 0));

      if (cons) {
        let baseConsonant = cons.replace("್", "");
        i += consLen;

        // Check if followed by vowel
        let v2 = lower.substr(i, 2);
        let v1 = lower.substr(i, 1);

        if (VOWEL_SIGNS[v2] !== undefined) {
          result += baseConsonant + VOWEL_SIGNS[v2];
          i += 2;
        } else if (VOWEL_SIGNS[v1] !== undefined) {
          result += baseConsonant + VOWEL_SIGNS[v1];
          i += 1;
        } else {
          // No vowel: if at end of word, keep halant for most consonants
          if (i >= len) {
            result += cons;
          } else {
            result += cons;
          }
        }
      } else {
        // Independent Vowel at start or after vowel
        let v2 = lower.substr(i, 2);
        let v1 = lower.substr(i, 1);
        if (VOWELS[v2]) {
          result += VOWELS[v2];
          i += 2;
        } else if (VOWELS[v1]) {
          result += VOWELS[v1];
          i += 1;
        } else {
          result += c1;
          i += 1;
        }
      }
    }

    return result;
  }

  function offlineTransliterate(text) {
    if (!text) return "";
    const tokens = text.split(/(\s+)/);
    return tokens.map(t => /^\s+$/.test(t) ? t : offlineTransliterateWord(t)).join("");
  }

  // Cache for Google Input Tools API requests
  const apiCache = new Map();

  /**
   * Transliterate English text to Kannada with Google Input Tools API + instant offline fallback
   */
  async function transliterateToKannada(englishText) {
    const text = (englishText || "").trim();
    if (!text) return "";

    // Check memory cache
    if (apiCache.has(text)) {
      return apiCache.get(text);
    }

    // Try online Google Input Tools API
    if (navigator.onLine) {
      try {
        const url = `https://inputtools.google.com/request?text=${encodeURIComponent(text)}&itc=kn-t-i0-und&num=1`;
        const res = await fetch(url, { signal: AbortSignal.timeout(1800) });
        if (res.ok) {
          const data = await res.json();
          if (data && data[0] === "SUCCESS" && data[1] && data[1][0] && data[1][0][1] && data[1][0][1][0]) {
            const knResult = data[1][0][1][0];
            apiCache.set(text, knResult);
            return knResult;
          }
        }
      } catch (err) {
        // Fall through to offline transliterator seamlessly
      }
    }

    // High quality offline fallback
    const offlineResult = offlineTransliterate(text);
    apiCache.set(text, offlineResult);
    return offlineResult;
  }

  /**
   * Bind real-time auto-fill from an English input to a Kannada input field
   */
  function bindTransliteration(sourceId, targetId) {
    const sourceEl = document.getElementById(sourceId);
    const targetEl = document.getElementById(targetId);
    if (!sourceEl || !targetEl) return;

    let debounceTimer = null;
    let isUserManuallyEditingTarget = false;

    // Track if user explicitly edited target
    targetEl.addEventListener("input", () => {
      isUserManuallyEditingTarget = targetEl.value.trim().length > 0;
    });

    sourceEl.addEventListener("input", (e) => {
      const enText = sourceEl.value;

      // If source cleared, reset target and allow auto-transliteration again
      if (!enText.trim()) {
        targetEl.value = "";
        isUserManuallyEditingTarget = false;
        return;
      }

      if (isUserManuallyEditingTarget) return;

      // Immediate offline preview for fast instant typing feedback
      const fastPreview = offlineTransliterate(enText);
      if (fastPreview) {
        targetEl.value = fastPreview;
      }

      // Debounced high-precision online transliteration
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(async () => {
        if (isUserManuallyEditingTarget) return;
        const preciseKn = await transliterateToKannada(sourceEl.value);
        if (preciseKn && !isUserManuallyEditingTarget && sourceEl.value.trim()) {
          targetEl.value = preciseKn;
        }
      }, 150);
    });
  }

  // Initialize auto-transliteration on DOM ready
  function initAutoTransliteration() {
    // 1. Add Student Modal: English Student Name -> Kannada Student Name
    bindTransliteration("student-name", "student-name-kn");

    // 2. School Setup Modal: English School Name -> Kannada School Name
    bindTransliteration("setup-school-name", "setup-school-name-kn");

    // 3. School Setup Modal: Head Master Name
    bindTransliteration("setup-hm-name", "setup-hm-name-kn");
  }

  window.transliterateToKannada = transliterateToKannada;
  window.bindTransliteration = bindTransliteration;
  window.initAutoTransliteration = initAutoTransliteration;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAutoTransliteration);
  } else {
    setTimeout(initAutoTransliteration, 100);
  }

})(window);
