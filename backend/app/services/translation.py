"""
AgroVisor Edge — Farmer Language & Multilingual Translation Service
Offline-first translation engine with caching and Indian agricultural domain dictionaries.
"""

from typing import Any

SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English"},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
    {"code": "mr", "name": "Marathi", "native_name": "मराठी"},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা"},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు"},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"},
    {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ"},
    {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી"},
    {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ"},
]

# Agricultural Farmer-Facing Domain Corpus across 9 Indian Languages
AGRICULTURAL_CORPUS: dict[str, dict[str, str]] = {
    # Soil Moisture Explanations
    "soil moisture is low. irrigation recommended.": {
        "en": "Soil moisture is low. Irrigation is recommended.",
        "hi": "मिट्टी में पानी की कमी है। इस क्षेत्र में सिंचाई की जरूरत है।",
        "mr": "मातीत ओलावा कमी आहे. या भागात पाणी देण्याची गरज आहे.",
        "bn": "মাটিতে রসের ঘাটতি আছে। সেচ দেওয়ার পরামর্শ দেওয়া হচ্ছে।",
        "te": "నేలలో తేమ తక్కువగా ఉంది. నీరు పెట్టడం అవసరం.",
        "ta": "மண்ணில் ஈரம் குறைவாக உள்ளது. பாசனம் செய்ய பரிந்துரைக்கப்படுகிறது.",
        "kn": "ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶ ಕಡಿಮೆಯಾಗಿದೆ. ನೀರುಣಿಸುವುದು ಅಗತ್ಯವಿದೆ.",
        "gu": "માટીમાં ભેજ ઓછો છે. પિયત આપવાની જરૂર છે.",
        "pa": "ਮਿੱਟੀ ਵਿੱਚ ਨਮੀ ਘੱਟ ਹੈ। ਸਿੰਚਾਈ ਕਰਨ ਦੀ ਸਲਾਹ ਦਿੱਤੀ ਜਾਂਦੀ ਹੈ।",
    },
    "soil moisture is optimal. crops are healthy.": {
        "en": "Soil moisture is optimal. Crops are healthy.",
        "hi": "मिट्टी में नमी बिल्कुल सही है। फसल स्वस्थ है।",
        "mr": "मातीतील ओलावा योग्य आहे. पीक निरोगी आहे.",
        "bn": "মাটিতে আর্দ্রতা ঠিক আছে। ফসল ভালো অবস্থায় আছে।",
        "te": "నేలలో తేమ సరిపడా ఉంది. పంట ఆరోగ్యంగా ఉంది.",
        "ta": "மண்ணில் ஈரப்பதம் சரியாக உள்ளது. பயிர் ஆரோக்கியமாக உள்ளது.",
        "kn": "ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶ ಸರಿಯಾಗಿದೆ. ಬೆಳೆ ಆರೋಗ್ಯಕರವಾಗಿದೆ.",
        "gu": "માટીમાં ભેજ બરાબર છે. પાક સ્વસ્થ છે.",
        "pa": "ਮਿੱਟੀ ਵਿੱਚ ਨਮੀ ਬਿਲਕੁਲ ਠੀਕ ਹੈ। ਫਸਲ ਤੰਦਰੁਸਤ ਹੈ।",
    },
    "soil temperature is high. heat stress possible.": {
        "en": "Soil temperature is high. Heat stress is possible.",
        "hi": "मिट्टी का तापमान अधिक है। तेज धूप और गर्मी से फसल पर असर पड़ सकता है।",
        "mr": "मातीचे तापमान जास्त आहे. उष्णतेमुळे पिकावर ताण येऊ शकतो.",
        "bn": "মাটির তাপমাত্রা বেশি। অতিরিক্ত গরমে ফসলের ক্ষতি হতে পারে।",
        "te": "నేల ఉష్ణోగ్రత ఎక్కువగా ఉంది. ఎండ వేడిమి ప్రభావం పడవచ్చు.",
        "ta": "மண்ணின் வெப்பநிலை அதிகம். வெப்பத்தால் பயிருக்கு பாதிப்பு ஏற்படலாம்.",
        "kn": "ಮಣ್ಣಿನ ತಾಪಮಾನ ಹೆಚ್ಚಾಗಿದೆ. ಬಿಸಿಲಿನಿಂದ ಬೆಳೆಗೆ ತೊಂದರೆಯಾಗಬಹುದು.",
        "gu": "માટીનું તાપમાન વધારે છે. ગરમીથી પાક પર અસર થઈ શકે છે.",
        "pa": "ਮਿੱਟੀ ਦਾ ਤਾਪਮਾਨ ਜ਼ਿਆਦਾ ਹੈ। ਗਰਮੀ ਕਾਰਨ ਫਸਲ 'ਤੇ ਅਸਰ ਪੈ ਸਕਦਾ ਹੈ।",
    },
    # Flow Failure (Zero Flow Anomaly)
    "pump on but flow is zero. check water supply, pipes, and pump.": {
        "en": "Pump is running, but no water flow detected. Please inspect pipes, pump, and water supply.",
        "hi": "पंप चालू है, लेकिन पानी नहीं आ रहा है। कृपया पाइप, पंप और पानी की आपूर्ति जांचें।",
        "mr": "पंप सुरू आहे, पण पाणी येत नाहीये. कृपया पाईप, पंप आणि पाण्याची तपासणी करा.",
        "bn": "পাম্প চলছে, কিন্তু পানি আসছে না। অনুগ্রহ করে পাইপ, পাম্প ও পানি সরবরাহ পরীক্ষা করুন।",
        "te": "పంప్ నడుస్తోంది, కానీ నీరు రావడం లేదు. దయచేసి పైపులు, పంప్ మరియు నీటి సరఫరాను తనిఖీ చేయండి.",
        "ta": "மோட்டார் ஓடுகிறது, ஆனால் தண்ணீர் வரவில்லை. பைப், பம்ப் மற்றும் தண்ணீர் இணைப்பை சரிபார்க்கவும்.",
        "kn": "ಪಂಪ್ ಚಾಲನೆಯಲ್ಲಿದೆ, ಆದರೆ ನೀರು ಹರಿಯುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ಪೈಪ್, ಪಂಪ್ ಮತ್ತು ನೀರಿನ ಪೂರೈಕೆ ಪರಿಶೀಲಿಸಿ.",
        "gu": "પંપ ચાલુ છે, પરંતુ પાણી આવતું નથી. કૃપા કરીને પાઇપ, પંપ અને પાણીની તપાસ કરો.",
        "pa": "ਪੰਪ ਚੱਲ ਰਿਹਾ ਹੈ, ਪਰ ਪਾਣੀ ਨਹੀਂ ਆ ਰਿਹਾ। ਕਿਰਪਾ ਕਰਕੇ ਪਾਈਪ, ਪੰਪ ਅਤੇ ਪਾਣੀ ਦੀ ਜਾਂਚ ਕਰੋ।",
    },
    # Irrigation Status
    "irrigation is in progress. water flow verified.": {
        "en": "Irrigation is in progress. Water flow verified.",
        "hi": "सिंचाई चल रही है। पानी का प्रवाह ठीक से शुरू हो चुका है।",
        "mr": "पाणी देणे सुरू आहे. पाण्याचा प्रवाह सुरळीत चालू आहे.",
        "bn": "সেচ চলছে। পানি প্রবাহ নিশ্চিত করা হয়েছে।",
        "te": "నీటి పారుదల జరుగుతోంది. నీటి ప్రవాహం సరిగ్గా ఉంది.",
        "ta": "பாசனம் நடைபெறுகிறது. தண்ணீர் சீராக பாய்கிறது.",
        "kn": "ನೀರುಣಿಸುವಿಕೆ ಪ್ರಗತಿಯಲ್ಲಿದೆ. ನೀರಿನ ಹರಿವು ಸರಿಯಾಗಿದೆ.",
        "gu": "પિયત ચાલુ છે. પાણીનો પ્રવાહ બરાબર છે.",
        "pa": "ਸਿੰਚਾਈ ਚੱਲ ਰਹੀ ਹੈ। ਪਾਣੀ ਦਾ ਵਹਾਅ ਠੀਕ ਹੈ।",
    },
    "irrigation completed. target water delivered.": {
        "en": "Irrigation completed. Target water delivered.",
        "hi": "सिंचाई पूरी हो चुकी है। आवश्यक पानी पौधों तक पहुंच चुका है।",
        "mr": "पाणी देणे पूर्ण झाले आहे. पिकाला लागणारे पुरेसे पाणी पोहोचले आहे.",
        "bn": "সেচ সম্পন্ন হয়েছে। প্রয়োজনীয় পানি পৌঁছে গেছে।",
        "te": "నీటి పారుదల పూర్తయింది. అవసరమైన నీరు అందింది.",
        "ta": "பாசனம் முடிவடைந்தது. தேவையான அளவு தண்ணீர் வழங்கப்பட்டது.",
        "kn": "ನೀರುಣಿಸುವಿಕೆ ಪೂರ್ಣಗೊಂಡಿದೆ. ನಿಗದಿತ ನೀರು ತಲುಪಿದೆ.",
        "gu": "પિયત પૂરું થઈ ગયું છે. જરૂરી પાણી પહોંચી ગયું છે.",
        "pa": "ਸਿੰਚਾਈ ਪੂਰੀ ਹੋ ਚੁੱਕੀ ਹੈ। ਲੋੜੀਂਦਾ ਪਾਣੀ ਮਿਲ ਗਿਆ ਹੈ।",
    },
    # AI Pathology & Crop Vision (Preserving Uncertainty)
    "possible early signs of crop disease detected. inspect leaves and field.": {
        "en": "Possible early signs of crop disease detected. Inspect leaves and field.",
        "hi": "फसल में बीमारी के शुरुआती लक्षण दिखाई दे सकते हैं। पत्तियों और खेत की जांच करने की सलाह दी जाती है।",
        "mr": "पिकावर रोगाची प्राथमिक लक्षणे दिसण्याची शक्यता आहे. पाने व शेताची पाहणी करा.",
        "bn": "ফসলে রোগের প্রাথমিক লক্ষণ দেখা যেতে পারে। পাতা ও জমি পরীক্ষা করার পরামর্শ দেওয়া হচ্ছে।",
        "te": "పంటలో తెగులు ప్రారంభ లక్షణాలు కనిపించే అవకాశం ఉంది. ఆకులను పరిశీలించండి.",
        "ta": "பயிரில் நோய் தொடக்க அறிகுறிகள் தென்படலாம். இலைகளை ஆய்வு செய்யவும்.",
        "kn": "ಬೆಳೆಯಲ್ಲಿ ರೋಗದ ಆರಂಭಿಕ ಲಕ್ಷಣಗಳು ಕಾಣಿಸಬಹುದು. ಎಲೆಗಳನ್ನು ಪರೀಕ್ಷಿಸಿ.",
        "gu": "પાકમાં રોગના પ્રારંભિક ચિહ્નો દેખાઈ શકે છે. પાંદડા અને ખેતરની તપાસ કરો.",
        "pa": "ਫਸਲ ਵਿੱਚ ਬਿਮਾਰੀ ਦੇ ਸ਼ੁਰੂਆਤੀ ਲੱਛਣ ਹੋ ਸਕਦੇ ਹਨ। ਪੱਤਿਆਂ ਅਤੇ ਖੇਤ ਦੀ ਜਾਂਚ ਕਰੋ।",
    },
    "crop leaves appear clear. no significant disease detected.": {
        "en": "Crop leaves appear clear. No significant disease detected.",
        "hi": "फसल की पत्तियां साफ और स्वस्थ दिख रही हैं। किसी गंभीर बीमारी के लक्षण नहीं मिले हैं।",
        "mr": "पिकाची पाने निरोगी दिसत आहेत. कोणत्याही गंभीर रोगाची लक्षणे आढळली नाहीत.",
        "bn": "ফসলের পাতা পরিষ্কার ও স্বাভাবিক রয়েছে। কোনো বড় রোগ শনাক্ত হয়নি।",
        "te": "పంట ఆకులు ఆరోగ్యంగా ఉన్నాయి. ఎటువంటి తెగుళ్లు కనిపించలేదు.",
        "ta": "பயிர் இலைகள் ஆரோக்கியமாக உள்ளன. குறிப்பிடத்தக்க நோய் எதுவும் இல்லை.",
        "kn": "ಬೆಳೆಯ ಎಲೆಗಳು ಆರೋಗ್ಯವಾಗಿವೆ. ಯಾವುದೇ ಗಂಭೀರ ರೋಗ ಕಂಡುಬಂದಿಲ್ಲ.",
        "gu": "પાકના પાંદડા સ્વસ્થ દેખાય છે. કોઈ ગંભીર રોગ જણાયો નથી.",
        "pa": "ਫਸਲ ਦੇ ਪੱਤੇ ਸਾਫ਼ ਅਤੇ ਤੰਦਰੁਸਤ ਹਨ। ਕੋਈ ਗੰਭੀਰ ਬਿਮਾਰੀ ਨਹੀਂ ਮਿਲੀ।",
    },
    # Core UI Concepts
    "farmer view": {
        "en": "Farmer View",
        "hi": "किसान दृश्य",
        "mr": "शेतकरी दृश्य",
        "bn": "কৃষক দর্শন",
        "te": "రైతు వీక్షణ",
        "ta": "விவசாயி பார்வை",
        "kn": "ರೈತರ ನೋಟ",
        "gu": "ખેડૂત દ્રષ્ટિકોણ",
        "pa": "ਕਿਸਾਨ ਦ੍ਰਿਸ਼ਟੀ",
    },
    "technical view": {
        "en": "Technical View",
        "hi": "तकनीकी दृश्य",
        "mr": "तांत्रिक दृश्य",
        "bn": "প্রযুক্তিগত দর্শন",
        "te": "సాంకేతిక వీక్షణ",
        "ta": "தொழில்நுட்ப பார்வை",
        "kn": "ತಾಂತ್ರಿಕ ನೋಟ",
        "gu": "તકનીકી દ્રષ્ટિકોણ",
        "pa": "ਤਕਨੀਕੀ ਦ੍ਰਿਸ਼ਟੀ",
    },
    "what is happening": {
        "en": "What is happening",
        "hi": "क्या हो रहा है?",
        "mr": "काय घडत आहे?",
        "bn": "কী ঘটছে?",
        "te": "ఏమి జరుగుతోంది?",
        "ta": "என்ன நடக்கிறது?",
        "kn": "ಏನು ನಡೆಯುತ್ತಿದೆ?",
        "gu": "શું થઈ રહ્યું છે?",
        "pa": "ਕੀ ਹੋ ਰਿਹਾ ਹੈ?",
    },
    "why is it happening": {
        "en": "Why is it happening",
        "hi": "यह क्यों हो रहा है?",
        "mr": "हे का होत आहे?",
        "bn": "এটি কেন হচ্ছে?",
        "te": "ఎందుకు జరుగుతోంది?",
        "ta": "ஏன் நடக்கிறது?",
        "kn": "ಏಕೆ ನಡೆಯುತ್ತಿದೆ?",
        "gu": "આ કેમ થઈ રહ્યું છે?",
        "pa": "ਇਹ ਕਿਉਂ ਹੋ ਰਿਹਾ ਹੈ?",
    },
    "what should the farmer do": {
        "en": "What should the farmer do",
        "hi": "किसान को क्या करना चाहिए?",
        "mr": "शेतकऱ्याने काय करावे?",
        "bn": "কৃষকের কী করা উচিত?",
        "te": "రైతు ఏమి చేయాలి?",
        "ta": "விவசாயி என்ன செய்ய வேண்டும்?",
        "kn": "ರೈತರು ಏನು ಮಾಡಬೇಕು?",
        "gu": "ખેડૂતે શું કરવું જોઈએ?",
        "pa": "ਕਿਸਾਨ ਨੂੰ ਕੀ ਕਰਨਾ ਚਾਹੀਦਾ ਹੈ?",
    },
    "is there a problem": {
        "en": "Is there a problem",
        "hi": "क्या कोई समस्या है?",
        "mr": "काही अडचण आहे का?",
        "bn": "কোনো সমস্যা আছে কি?",
        "te": "ఏదైనా సమస్య ఉందా?",
        "ta": "ஏதேனும் பிரச்சனை உள்ளதா?",
        "kn": "ಏನಾದರೂ ಸಮಸ್ಯೆಯಿದೆಯೇ?",
        "gu": "કોઈ સમસ્યા છે?",
        "pa": "ਕੀ ਕੋਈ ਸਮੱਸਿਆ ਹੈ?",
    },
    "urgency: normal": {
        "en": "Urgency: Normal",
        "hi": "स्थिति: सामान्य",
        "mr": "स्थिती: सामान्य",
        "bn": "জরুরি অবস্থা: স্বাভাবিক",
        "te": "స్థితి: సాధారణం",
        "ta": "நிலை: இயல்பு",
        "kn": "ಸ್ಥಿತಿ: ಸಾಮಾನ್ಯ",
        "gu": "સ્થિતિ: સામાન્ય",
        "pa": "ਸਥਿਤੀ: ਆਮ",
    },
    "urgency: high": {
        "en": "Urgency: High",
        "hi": "स्थिति: जरूरी (शीघ्र ध्यान दें)",
        "mr": "स्थिती: तातडीची (लगेच लक्ष द्या)",
        "bn": "জরুরি অবস্থা: গুরুত্বপূর্ণ (দ্রুত ব্যবস্থা নিন)",
        "te": "స్థితి: అత్యవసరం (వెంటనే చర్య తీసుకోండి)",
        "ta": "நிலை: அவசரம் (உடனே கவனிக்கவும்)",
        "kn": "ಸ್ಥಿತಿ: ತುರ್ತು (ತಕ್ಷಣ ಗಮನಿಸಿ)",
        "gu": "સ્થિતિ: તાત્કાલિક (તરત ધ્યાન આપો)",
        "pa": "ਸਥਿਤੀ: ਜ਼ਰੂਰੀ (ਤੁਰੰਤ ਧਿਆਨ ਦਿਓ)",
    },
    "urgency: critical": {
        "en": "Urgency: Critical",
        "hi": "स्थिति: अति गंभीर (तुरंत कार्रवाई करें)",
        "mr": "स्थिती: अत्यंत गंभीर (त्वरित कृती करा)",
        "bn": "জরুরি অবস্থা: অত্যন্ত সংকটজনক (অবিলম্বে ব্যবস্থা নিন)",
        "te": "స్థితి: అత్యంత ప్రమాదకరం (తక్షణ చర్య అవసరం)",
        "ta": "நிலை: தீவிர பிரச்சனை (உடனடி நடவடிக்கை தேவை)",
        "kn": "ಸ್ಥಿತಿ: ಗಂಭೀರ (ತಕ್ಷಣ ಕಾರ್ಯನಿರ್ವಹಿಸಿ)",
        "gu": "સ્થિતિ: અતિ ગંભીર (તરત પગલાં લો)",
        "pa": "ਸਥਿਤੀ: ਬਹੁਤ ਗੰਭੀਰ (ਤੁਰੰਤ ਕਾਰਵਾਈ ਕਰੋ)",
    },
}

# Translation cache keyed by (normalized_source_text, source_lang, target_lang)
_TRANSLATION_CACHE: dict[tuple[str, str, str], str] = {}


class TranslationService:
    def __init__(self) -> None:
        self._corpus = AGRICULTURAL_CORPUS
        self._cache = _TRANSLATION_CACHE
        self._languages = SUPPORTED_LANGUAGES

    def get_supported_languages(self) -> list[dict[str, str]]:
        return self._languages

    def translate_text(
        self, text: str, source_lang: str = "en", target_lang: str = "hi"
    ) -> dict[str, Any]:
        """
        Translates farmer intelligence text into the desired language.
        Preserves offline reliability and caches lookups.
        """
        source_lang = source_lang.lower().strip()
        target_lang = target_lang.lower().strip()
        clean_text = text.strip()

        if not clean_text:
            return {
                "original_text": text,
                "translated_text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "cached": False,
                "provider": "identity",
            }

        # If source and target are the same, return as is
        if source_lang == target_lang or (target_lang == "en" and source_lang == "en"):
            return {
                "original_text": text,
                "translated_text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "cached": False,
                "provider": "identity",
            }

        cache_key = (clean_text.lower(), source_lang, target_lang)

        # 1. Check in-memory cache
        if cache_key in self._cache:
            return {
                "original_text": text,
                "translated_text": self._cache[cache_key],
                "source_lang": source_lang,
                "target_lang": target_lang,
                "cached": True,
                "provider": "agrovisor-cache",
            }

        # 2. Check localized agricultural domain corpus
        clean_norm = clean_text.lower().strip().rstrip(".")

        found_translation: str | None = None

        for corpus_key, lang_map in self._corpus.items():
            en_val = lang_map.get("en", "").lower().strip().rstrip(".")
            norm_key = corpus_key.lower().strip().rstrip(".")
            if clean_norm == norm_key or clean_norm == en_val:
                if target_lang in lang_map:
                    found_translation = lang_map[target_lang]
                    break
            elif norm_key in clean_norm or (en_val and en_val in clean_norm):
                if target_lang in lang_map:
                    found_translation = lang_map[target_lang]
                    break

        if found_translation:
            self._cache[cache_key] = found_translation
            return {
                "original_text": text,
                "translated_text": found_translation,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "cached": False,
                "provider": "agrovisor-edge-dictionary",
            }

        # 3. Fallback: return original text without crashing
        self._cache[cache_key] = text
        return {
            "original_text": text,
            "translated_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "cached": False,
            "provider": "offline-fallback",
        }


_service_instance = TranslationService()


def get_translation_service() -> TranslationService:
    return _service_instance
