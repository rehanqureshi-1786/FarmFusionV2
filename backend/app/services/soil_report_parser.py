"""
Soil Report Document Parser.

Extracts soil health metrics (pH, Nitrogen, Phosphorus, Potassium, Organic Carbon, Electrical Conductivity)
from uploaded Soil Health Card documents (PDF, JPEG, JPG, PNG).
Supports Indian Government Soil Health Card (SHC) portal formats, ICAR formats, and scanned cards.
Uses on-device RapidOCR for images and layout-aware PDF extraction.
"""
import io
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    from rapidocr_onnxruntime import RapidOCR
    RAPID_OCR_AVAILABLE = True
    _ocr_engine = RapidOCR()
except Exception as e:
    RAPID_OCR_AVAILABLE = False
    _ocr_engine = None
    logger.warning(f"rapidocr_initialization_failed: {e}")


class SoilReportParser:
    """Parses soil test reports in PDF and Image formats with multi-strategy extraction."""

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes using pypdf.
        Attempts 'layout' mode first to preserve 2D table column alignment,
        then falls back to standard text extraction.
        """
        if not PYPDF_AVAILABLE:
            logger.warning("pypdf_not_installed_falling_back")
            return ""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_chunks: List[str] = []
            for page in reader.pages:
                page_text = ""
                try:
                    page_text = page.extract_text(extraction_mode="layout")
                except Exception:
                    page_text = ""
                if not page_text or len(page_text.strip()) < 10:
                    try:
                        page_text = page.extract_text() or ""
                    except Exception:
                        page_text = ""
                if page_text:
                    text_chunks.append(page_text)
            return "\n".join(text_chunks)
        except Exception as e:
            logger.error(f"failed_to_extract_pdf_text: {e}")
            return ""

    @classmethod
    def extract_text_from_image(cls, image_bytes: bytes) -> str:
        """
        Extract text from image bytes (JPEG, JPG, PNG) using on-device RapidOCR.
        """
        if not RAPID_OCR_AVAILABLE or _ocr_engine is None:
            logger.warning("rapid_ocr_not_available_for_image")
            return ""
        try:
            result, elapse = _ocr_engine(image_bytes)
            if result:
                lines = [item[1] for item in result if len(item) > 1 and item[1]]
                logger.info(f"RapidOCR extracted {len(lines)} lines from image (elapsed {elapse})")
                return "\n".join(lines)
        except Exception as e:
            logger.error(f"failed_to_extract_image_text_with_ocr: {e}")
        return ""

    @staticmethod
    def _clean_chemical_formulas(text: str) -> str:
        """
        Normalize chemical formulas and special glyphs so that numbers inside
        formulas (e.g. 2 and 5 in P2O5 / P₂O₅ / P■O■ / P205) are not falsely parsed
        as nutrient test results. Supports OCR confusion between letter O and digit 0.
        """
        if not text:
            return ""
        # 1. Normalize Unicode subscripts
        t = text.replace('\u2082', '2').replace('\u2085', '5').replace('\u2080', '0')
        # 2. Mask Phosphorus oxide formulas (P2O5, P₂O₅, P■O■, P205, P?O?, P O)
        t = re.sub(r'P\s*[2■\?□]\s*[Oo0]\s*[5■\?□]?', 'PHOSPHORUS_FORMULA', t, flags=re.IGNORECASE)
        # 3. Mask Potassium oxide formulas (K2O, K₂O, K■O, K20, K?O, K O)
        t = re.sub(r'K\s*[2■\?□]\s*[Oo0]', 'POTASSIUM_FORMULA', t, flags=re.IGNORECASE)
        return t

    @classmethod
    def parse_soil_parameters(cls, raw_text: str) -> Dict[str, Optional[float]]:
        """
        Extract numerical soil values using a robust multi-strategy approach:
        1. Line-by-line / Adjacent-line table cell analysis
        2. Domain-specific regex with parenthetical symbol support
        3. Columnar table pattern detection
        """
        params: Dict[str, Optional[float]] = {
            "ph": None,
            "nitrogen": None,
            "phosphorus": None,
            "potassium": None,
            "organic_carbon": None,
            "ec": None,
        }

        if not raw_text or not raw_text.strip():
            return params

        cleaned = cls._clean_chemical_formulas(raw_text)
        lines = [l.strip() for l in cleaned.splitlines() if l.strip()]

        def extract_numbers(line_str: str) -> List[float]:
            """Extract standalone numbers from a line."""
            tokens = re.findall(r'(?<![\w\.])(\d+(?:\.\d+)?)(?![\w\.])', line_str)
            nums: List[float] = []
            for tok in tokens:
                try:
                    nums.append(float(tok))
                except ValueError:
                    pass
            return nums

        # =====================================================================
        # PASS 1: Line-by-Line & Adjacent-Line Table Row Analysis
        # =====================================================================
        for i, line in enumerate(lines):
            lower = line.lower()
            nums_same = extract_numbers(line)
            nums_next = extract_numbers(lines[i + 1]) if i + 1 < len(lines) else []

            # 1. pH / Soil Reaction (ensure not confusing with 'phosphorus')
            if (('ph' in lower and 'phosphor' not in lower and 'phcsphor' not in lower) or 'reaction' in lower) and params['ph'] is None:
                valid_ph = [n for n in nums_same if 3.0 <= n <= 11.0]
                if not valid_ph:
                    valid_ph = [n for n in nums_next if 3.0 <= n <= 11.0]
                if valid_ph:
                    params['ph'] = valid_ph[0]

            # 2. Nitrogen (N)
            # Handles: Available Nitrogen (N), Nitroge n (OCR typo), Nitr0gen, (N)
            if (re.search(r'nitr[o0c]ge|nitroge', lower) or re.search(r'\bN\b|\(N\)', line, re.IGNORECASE)) and params['nitrogen'] is None:
                valid_n = [n for n in nums_same if (n < 1950 or n > 2050) and 10.0 <= n <= 3000.0]
                if not valid_n:
                    valid_n = [n for n in nums_next if (n < 1950 or n > 2050) and 10.0 <= n <= 3000.0]
                if valid_n:
                    params['nitrogen'] = valid_n[0]

            # 3. Phosphorus (P / P2O5)
            # Handles: Available Phosphorus (P2O5), Phcsphorus (OCR typo), PHOSPHORUS_FORMULA, (P)
            if (re.search(r'ph[oc]sphor|phosphor|phosphorus_formula|p2o5|p205', lower) or re.search(r'\bP\b|\(P\)', line, re.IGNORECASE)) and params['phosphorus'] is None:
                valid_p = [n for n in nums_same if 1.0 <= n <= 500.0]
                if not valid_p:
                    valid_p = [n for n in nums_next if 1.0 <= n <= 500.0]
                if valid_p:
                    params['phosphorus'] = valid_p[0]

            # 4. Potassium (K / K2O)
            # Handles: Available Potassium (K2O), Potassium, POTASSIUM_FORMULA, (K)
            if (re.search(r'p[o0c]tassium|potassium|potassium_formula|k2o|k20', lower) or re.search(r'\bK\b|\(K\)', line, re.IGNORECASE)) and params['potassium'] is None:
                valid_k = [n for n in nums_same if 10.0 <= n <= 3000.0]
                if not valid_k:
                    valid_k = [n for n in nums_next if 10.0 <= n <= 3000.0]
                if valid_k:
                    params['potassium'] = valid_k[0]

            # 5. Organic Carbon (OC)
            if ('carbon' in lower or re.search(r'\bOC\b|\(OC\)', line)) and params['organic_carbon'] is None:
                valid_oc = [n for n in nums_same if 0.01 <= n <= 15.0]
                if not valid_oc:
                    valid_oc = [n for n in nums_next if 0.01 <= n <= 15.0]
                if valid_oc:
                    params['organic_carbon'] = valid_oc[0]

            # 6. Electrical Conductivity (EC)
            if ('conductivity' in lower or 'uctivity' in lower or re.search(r'\bEC\b|\(EC\)', line)) and params['ec'] is None:
                valid_ec = [n for n in nums_same if 0.01 <= n <= 30.0]
                if not valid_ec:
                    valid_ec = [n for n in nums_next if 0.01 <= n <= 30.0]
                if valid_ec:
                    params['ec'] = valid_ec[0]

        # =====================================================================
        # PASS 2: Regex Patterns for Unmatched Fields
        # =====================================================================
        if params['ph'] is None:
            m = re.search(r'(?:Soil\s+Reaction(?:\s*[\/\(]\s*pH\s*\)?)?|Reaction\s*[\/\(]\s*pH\s*\)?|\bpH\b)[\s:=|-]*([3-9](?:\.\d{1,2})?|10(?:\.0)?|11(?:\.0)?)', cleaned, re.IGNORECASE)
            if m:
                try:
                    params['ph'] = float(m.group(1))
                except ValueError:
                    pass

        if params['nitrogen'] is None:
            m = re.search(r'(?:Available\s+)?Nitroge\s*n(?:\s*\([^\)]*\))?[\s:=|-]*(\d{2,4}(?:\.\d{1,2})?)', cleaned, re.IGNORECASE)
            if not m:
                m = re.search(r'\bN\b(?:\s*\([^\)]*\))?[\s:=|-]*(\d{2,4}(?:\.\d{1,2})?)', cleaned)
            if m:
                try:
                    params['nitrogen'] = float(m.group(1))
                except ValueError:
                    pass

        if params['phosphorus'] is None:
            m = re.search(r'(?:Available\s+)?Phosphorus(?:\s*\([^\)]*\))?[\s:=|-]*(\d{1,3}(?:\.\d{1,2})?)', cleaned, re.IGNORECASE)
            if not m:
                m = re.search(r'(?:PHOSPHORUS_FORMULA|\bP\b)(?:\s*\([^\)]*\))?[\s:=|-]*(\d{1,3}(?:\.\d{1,2})?)', cleaned)
            if m:
                try:
                    params['phosphorus'] = float(m.group(1))
                except ValueError:
                    pass

        if params['potassium'] is None:
            m = re.search(r'(?:Available\s+)?Potassium(?:\s*\([^\)]*\))?[\s:=|-]*(\d{2,4}(?:\.\d{1,2})?)', cleaned, re.IGNORECASE)
            if not m:
                m = re.search(r'(?:POTASSIUM_FORMULA|\bK\b)(?:\s*\([^\)]*\))?[\s:=|-]*(\d{2,4}(?:\.\d{1,2})?)', cleaned)
            if m:
                try:
                    params['potassium'] = float(m.group(1))
                except ValueError:
                    pass

        if params['organic_carbon'] is None:
            m = re.search(r'(?:Organic\s+Carbon|\bOC\b)(?:\s*\([^\)]*\))?[\s:=|-]*(\d(?:\.\d{1,3})?)', cleaned, re.IGNORECASE)
            if m:
                try:
                    params['organic_carbon'] = float(m.group(1))
                except ValueError:
                    pass

        if params['ec'] is None:
            m = re.search(r'(?:Electrical\s+Conductivity|\bEC\b)(?:\s*\([^\)]*\))?[\s:=|-]*(\d(?:\.\d{1,3})?)', cleaned, re.IGNORECASE)
            if m:
                try:
                    params['ec'] = float(m.group(1))
                except ValueError:
                    pass

        # =====================================================================
        # PASS 3: Columnar Table Extraction Fallback
        # =====================================================================
        missing_count = sum(1 for k in ['ph', 'nitrogen', 'phosphorus', 'potassium'] if params[k] is None)
        if missing_count >= 2:
            param_keys_in_order = []
            for line in lines:
                low = line.lower()
                if ('ph' in low or 'reaction' in low) and 'ph' not in param_keys_in_order:
                    param_keys_in_order.append('ph')
                elif ('nitrogen' in low or 'nitroge' in low or re.search(r'\bN\b|\(N\)', line)) and 'nitrogen' not in param_keys_in_order:
                    param_keys_in_order.append('nitrogen')
                elif ('phosphor' in low or 'phosphorus_formula' in low or re.search(r'\bP\b|\(P\)', line)) and 'phosphorus' not in param_keys_in_order:
                    param_keys_in_order.append('phosphorus')
                elif ('potassium' in low or 'potassium_formula' in low or re.search(r'\bK\b|\(K\)', line)) and 'potassium' not in param_keys_in_order:
                    param_keys_in_order.append('potassium')
                elif ('carbon' in low or re.search(r'\bOC\b|\(OC\)', line)) and 'organic_carbon' not in param_keys_in_order:
                    param_keys_in_order.append('organic_carbon')
                elif ('conductivity' in low or 'uctivity' in low or re.search(r'\bEC\b|\(EC\)', line)) and 'ec' not in param_keys_in_order:
                    param_keys_in_order.append('ec')

            number_lines: List[float] = []
            for line in lines:
                m = re.fullmatch(r'(\d+(?:\.\d+)?)', line.strip())
                if m:
                    number_lines.append(float(m.group(1)))

            if len(param_keys_in_order) >= 3 and len(number_lines) >= len(param_keys_in_order):
                for idx, k in enumerate(param_keys_in_order):
                    if params[k] is None and idx < len(number_lines):
                        params[k] = number_lines[idx]

        return params

    @classmethod
    def _parse_image_with_vision_ai(cls, file_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Optional[float]]:
        """
        Intelligent Vision AI fallback for image files (JPEG, PNG) or scanned PDFs
        where direct text extraction is unavailable.
        Uses Gemini Vision if configured.
        """
        import base64
        from app.core.config import settings

        api_key = getattr(settings, "gemini_api_key", None)
        if not api_key or api_key == "placeholder":
            return {}

        try:
            from app.agents.gemini_client import GeminiClient
            client = GeminiClient()
            b64_data = base64.b64encode(file_bytes).decode("utf-8")
            prompt = (
                "You are an agricultural expert analyzing a Soil Health Card or Soil Test Report image. "
                "Extract the following numerical metrics from the table or document:\n"
                "- ph (soil reaction pH value, float)\n"
                "- nitrogen (available nitrogen N in kg/ha, float)\n"
                "- phosphorus (available phosphorus P or P2O5 in kg/ha, float)\n"
                "- potassium (available potassium K or K2O in kg/ha, float)\n"
                "- organic_carbon (organic carbon OC in %, float)\n"
                "- ec (electrical conductivity in dS/m, float)\n\n"
                "Return ONLY valid JSON with keys: ph, nitrogen, phosphorus, potassium, organic_carbon, ec. "
                "If a metric is not present in the document, set its value to null."
            )
            result = client.complete_json_with_image(prompt, b64_data, mime_type=mime_type)
            if isinstance(result, dict):
                return {
                    k: float(result[k]) if result.get(k) is not None else None
                    for k in ["ph", "nitrogen", "phosphorus", "potassium", "organic_carbon", "ec"]
                    if k in result
                }
        except Exception as e:
            logger.warning(f"vision_ai_soil_parsing_failed: {e}")
        return {}

    @classmethod
    def parse_document(
        cls,
        file_bytes: bytes,
        filename: str,
        content_type: str
    ) -> Tuple[Dict[str, Optional[float]], str]:
        """
        Main entrypoint: parses uploaded document (PDF or Image) and returns (parameters_dict, extracted_summary).
        """
        lower_name = (filename or "").lower()
        lower_mime = (content_type or "").lower()
        extracted_text = ""
        is_pdf = lower_name.endswith(".pdf") or "pdf" in lower_mime

        if is_pdf:
            extracted_text = cls.extract_text_from_pdf(file_bytes)
            if not extracted_text or len(extracted_text.strip()) < 10:
                try:
                    raw_decoded = file_bytes.decode("utf-8", errors="ignore")
                    if any(kw in raw_decoded.lower() for kw in ["nitrogen", "phosphorus", "potassium", "ph"]):
                        extracted_text = raw_decoded
                except Exception:
                    pass
        else:
            # Direct Image upload (JPEG, JPG, PNG)
            extracted_text = cls.extract_text_from_image(file_bytes)

        params = cls.parse_soil_parameters(extracted_text)

        # If text/OCR yielded insufficient results (e.g. poor lighting image),
        # attempt Vision AI extraction as secondary fallback
        has_core_metrics = params.get("ph") is not None and params.get("nitrogen") is not None
        if not has_core_metrics:
            mime = "application/pdf" if is_pdf else (content_type or "image/jpeg")
            vision_params = cls._parse_image_with_vision_ai(file_bytes, mime_type=mime)
            for k, v in vision_params.items():
                if params.get(k) is None and v is not None:
                    params[k] = v

        # Track provenances: whether extracted directly from document or applied as baseline
        sources: List[str] = []
        if params["ph"] is not None:
            sources.append(f"pH={params['ph']}")
        else:
            params["ph"] = 6.8
            sources.append("pH=6.8 (default)")

        if params["nitrogen"] is not None:
            sources.append(f"N={params['nitrogen']} kg/ha")
        else:
            params["nitrogen"] = 180.0
            sources.append("N=180.0 kg/ha (default)")

        if params["phosphorus"] is not None:
            sources.append(f"P={params['phosphorus']} kg/ha")
        else:
            params["phosphorus"] = 35.0
            sources.append("P=35.0 kg/ha (default)")

        if params["potassium"] is not None:
            sources.append(f"K={params['potassium']} kg/ha")
        else:
            params["potassium"] = 210.0
            sources.append("K=210.0 kg/ha (default)")

        summary = f"Parsed Soil Health Card ({filename}): {', '.join(sources)}"
        logger.info(summary)
        return params, summary


soil_report_parser = SoilReportParser()
