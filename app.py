import streamlit as st
import qrcode
from io import BytesIO
import json
import os
import shutil
from datetime import datetime

import whisper
from PIL import Image, ImageOps, ImageEnhance
import pytesseract


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Patient Case-Taking System",
    page_icon="🏥",
    layout="wide"
)

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

PATIENTS_FOLDER = "patients"

PATIENT_URL = "http://192.168.1.3:8502/?entry=patient"


# ============================================================
# CREATE PATIENT STORAGE FOLDER
# ============================================================

os.makedirs(
    PATIENTS_FOLDER,
    exist_ok=True
)


# ============================================================
# TRANSLATIONS
# ============================================================

TEXT = {

    "English": {

        "patient_portal": "👤 Patient Portal",
        "welcome": "Welcome to the Patient Case-Taking System",

        "consent": "🔐 Consent",
        "consent_text":
            "I consent to providing my information for "
            "pre-consultation case-taking.",

        "consent_required":
            "Please provide consent to continue.",

        "consent_recorded":
            "Consent recorded.",

        "patient_information":
            "🧑 Patient Information",

        "patient_name":
            "Patient Name",

        "patient_id":
            "Patient ID",

        "case_taking":
            "🩺 Patient Case-Taking",

        "type_answer":
            "Type your answer",

        "voice_input":
            "🎤 Voice Input",

        "record_answer":
            "Record your answer",

        "convert_voice":
            "Convert Voice to Text",

        "converting":
            "Converting speech to text...",

        "voice_success":
            "Voice converted successfully.",

        "transcribed_text":
            "Transcribed Text",

        "save_next":
            "Save Answer & Next →",

        "completed":
            "🎉 Patient case-taking completed.",

        "upload_document":
            "📄 Upload Previous Medical Documents",

        "upload_description":
            "Upload previous prescriptions, laboratory reports "
            "or other medical documents.",

        "upload_file":
            "Upload medical documents",

        "extract":
            "🔍 Extract Medical Information",

        "ocr_running":
            "Running OCR...",

        "document_processed":
            "Medical document processed.",

        "extracted_text":
            "Extracted Text",

        "review":
            "📋 Review Your Information",

        "safety":
            "🚨 Preliminary Safety Review",

        "safety_description":
            "This prototype does not diagnose the patient. "
            "It only highlights information that may require "
            "review by a qualified healthcare professional.",

        "red_flag":
            "⚠️ Potential red-flag information detected.",

        "human_review":
            "Human review required",

        "no_red_flag":
            "No predefined red-flag phrase detected.",

        "submit":
            "💾 Submit Patient Case",

        "enter_name":
            "Please enter the patient name.",

        "submitted":
            "✅ Patient case submitted successfully.",

        "doctor_can_review":
            "The doctor can now review the case from "
            "the doctor dashboard."
    },


    "Hindi": {

        "patient_portal":
            "👤 रोगी पोर्टल",

        "welcome":
            "रोगी केस लेने की प्रणाली में आपका स्वागत है",

        "consent":
            "🔐 सहमति",

        "consent_text":
            "मैं प्री-कंसल्टेशन केस लेने के लिए "
            "अपनी जानकारी प्रदान करने की सहमति देता/देती हूँ।",

        "consent_required":
            "जारी रखने के लिए कृपया सहमति दें।",

        "consent_recorded":
            "सहमति दर्ज कर ली गई है।",

        "patient_information":
            "🧑 रोगी की जानकारी",

        "patient_name":
            "रोगी का नाम",

        "patient_id":
            "रोगी आईडी",

        "case_taking":
            "🩺 रोगी की केस जानकारी",

        "type_answer":
            "अपना उत्तर लिखें",

        "voice_input":
            "🎤 आवाज़ द्वारा जानकारी",

        "record_answer":
            "अपना उत्तर रिकॉर्ड करें",

        "convert_voice":
            "आवाज़ को टेक्स्ट में बदलें",

        "converting":
            "आवाज़ को टेक्स्ट में बदला जा रहा है...",

        "voice_success":
            "आवाज़ सफलतापूर्वक टेक्स्ट में बदल दी गई।",

        "transcribed_text":
            "ट्रांसक्राइब किया गया टेक्स्ट",

        "save_next":
            "उत्तर सहेजें और आगे बढ़ें →",

        "completed":
            "🎉 रोगी की केस जानकारी पूरी हो गई।",

        "upload_document":
            "📄 पिछली मेडिकल रिपोर्ट अपलोड करें",

        "upload_description":
            "पिछली प्रिस्क्रिप्शन, लैब रिपोर्ट या अन्य "
            "मेडिकल दस्तावेज़ अपलोड करें।",

        "upload_file":
            "मेडिकल दस्तावेज़ अपलोड करें",

        "extract":
            "🔍 मेडिकल जानकारी निकालें",

        "ocr_running":
            "OCR चलाया जा रहा है...",

        "document_processed":
            "मेडिकल दस्तावेज़ प्रोसेस हो गया है।",

        "extracted_text":
            "निकाला गया टेक्स्ट",

        "review":
            "📋 अपनी जानकारी की समीक्षा करें",

        "safety":
            "🚨 प्रारंभिक सुरक्षा समीक्षा",

        "safety_description":
            "यह प्रोटोटाइप रोगी का निदान नहीं करता। "
            "सिस्टम केवल ऐसी जानकारी को चिन्हित करता है "
            "जिसकी योग्य स्वास्थ्य पेशेवर द्वारा समीक्षा "
            "आवश्यक हो सकती है।",

        "red_flag":
            "⚠️ संभावित जोखिम वाली जानकारी मिली है।",

        "human_review":
            "मानवीय समीक्षा आवश्यक है",

        "no_red_flag":
            "कोई पूर्वनिर्धारित जोखिम संकेत नहीं मिला।",

        "submit":
            "💾 रोगी की केस जानकारी जमा करें",

        "enter_name":
            "कृपया रोगी का नाम दर्ज करें।",

        "submitted":
            "✅ रोगी की केस जानकारी सफलतापूर्वक जमा हो गई।",

        "doctor_can_review":
            "अब डॉक्टर इस केस को डॉक्टर डैशबोर्ड से देख सकते हैं।"
    },


    "Marathi": {

        "patient_portal":
            "👤 रुग्ण पोर्टल",

        "welcome":
            "रुग्ण केस घेण्याच्या प्रणालीमध्ये आपले स्वागत आहे",

        "consent":
            "🔐 संमती",

        "consent_text":
            "प्री-कन्सल्टेशन केस घेण्यासाठी "
            "माझी माहिती देण्यास मी संमती देतो/देते.",

        "consent_required":
            "पुढे जाण्यासाठी कृपया संमती द्या.",

        "consent_recorded":
            "संमती नोंदवली गेली आहे.",

        "patient_information":
            "🧑 रुग्णाची माहिती",

        "patient_name":
            "रुग्णाचे नाव",

        "patient_id":
            "रुग्ण आयडी",

        "case_taking":
            "🩺 रुग्णाची केस माहिती",

        "type_answer":
            "आपले उत्तर लिहा",

        "voice_input":
            "🎤 आवाजाद्वारे माहिती",

        "record_answer":
            "आपले उत्तर रेकॉर्ड करा",

        "convert_voice":
            "आवाजाचे टेक्स्टमध्ये रूपांतर करा",

        "converting":
            "आवाजाचे टेक्स्टमध्ये रूपांतर केले जात आहे...",

        "voice_success":
            "आवाजाचे यशस्वीरित्या टेक्स्टमध्ये रूपांतर झाले.",

        "transcribed_text":
            "रूपांतरित केलेला टेक्स्ट",

        "save_next":
            "उत्तर जतन करा आणि पुढे जा →",

        "completed":
            "🎉 रुग्णाची केस माहिती पूर्ण झाली.",

        "upload_document":
            "📄 मागील वैद्यकीय कागदपत्रे अपलोड करा",

        "upload_description":
            "मागील प्रिस्क्रिप्शन, प्रयोगशाळा अहवाल "
            "किंवा इतर वैद्यकीय कागदपत्रे अपलोड करा.",

        "upload_file":
            "वैद्यकीय कागदपत्रे अपलोड करा",

        "extract":
            "🔍 वैद्यकीय माहिती काढा",

        "ocr_running":
            "OCR चालू आहे...",

        "document_processed":
            "वैद्यकीय कागदपत्र प्रक्रिया पूर्ण झाली.",

        "extracted_text":
            "काढलेला टेक्स्ट",

        "review":
            "📋 आपल्या माहितीचे पुनरावलोकन करा",

        "safety":
            "🚨 प्राथमिक सुरक्षा तपासणी",

        "safety_description":
            "हा प्रोटोटाइप रुग्णाचे निदान करत नाही. "
            "सिस्टम फक्त अशा माहितीवर लक्ष देते "
            "जिचे पात्र आरोग्य व्यावसायिकांकडून "
            "पुनरावलोकन आवश्यक असू शकते.",

        "red_flag":
            "⚠️ संभाव्य धोक्याची माहिती आढळली.",

        "human_review":
            "मानवी पुनरावलोकन आवश्यक आहे",

        "no_red_flag":
            "पूर्वनिर्धारित धोक्याचे कोणतेही संकेत आढळले नाहीत.",

        "submit":
            "💾 रुग्णाची केस माहिती सबमिट करा",

        "enter_name":
            "कृपया रुग्णाचे नाव टाका.",

        "submitted":
            "✅ रुग्णाची केस माहिती यशस्वीरित्या सबमिट झाली.",

        "doctor_can_review":
            "आता डॉक्टर डॉक्टर डॅशबोर्डमधून केसचे "
            "पुनरावलोकन करू शकतात."
    }
}


# ============================================================
# QUESTIONS
# ============================================================

QUESTIONS = {

    "English": [

        "What is your main health problem or complaint?",
        "When did this problem start?",
        "How severe is the problem?",
        "Have you experienced this problem before?",
        "Do you have any previous medical conditions?",
        "Are you currently taking any medicines?",
        "Do you have any known allergies?",
        "Have you undergone any previous surgery?",
        "Do any major diseases run in your family?",
        "Is there anything else you want the doctor to know?"
    ],

    "Hindi": [

        "आपकी मुख्य स्वास्थ्य समस्या या शिकायत क्या है?",
        "यह समस्या कब शुरू हुई?",
        "यह समस्या कितनी गंभीर है?",
        "क्या आपको पहले भी यह समस्या हुई है?",
        "क्या आपको पहले से कोई बीमारी है?",
        "क्या आप वर्तमान में कोई दवा ले रहे हैं?",
        "क्या आपको किसी चीज़ से एलर्जी है?",
        "क्या आपकी पहले कोई सर्जरी हुई है?",
        "क्या आपके परिवार में कोई गंभीर बीमारी है?",
        "क्या आप डॉक्टर को और कुछ बताना चाहते हैं?"
    ],

    "Marathi": [

        "तुमची मुख्य आरोग्य समस्या किंवा तक्रार काय आहे?",
        "ही समस्या कधी सुरू झाली?",
        "ही समस्या किती गंभीर आहे?",
        "तुम्हाला यापूर्वीही ही समस्या झाली आहे का?",
        "तुम्हाला आधीपासून कोणता आजार आहे का?",
        "तुम्ही सध्या कोणती औषधे घेत आहात?",
        "तुम्हाला कोणत्याही गोष्टीची ॲलर्जी आहे का?",
        "तुमची यापूर्वी कोणती शस्त्रक्रिया झाली आहे का?",
        "तुमच्या कुटुंबात कोणता गंभीर आजार आहे का?",
        "तुम्हाला डॉक्टरांना आणखी काही सांगायचे आहे का?"
    ]
}


# ============================================================
# WHISPER
# ============================================================

@st.cache_resource
def load_whisper_model():

    return whisper.load_model("base")


WHISPER_LANGUAGES = {

    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr"
}


# ============================================================
# OCR
# ============================================================

def extract_text_from_image(image_bytes):

    try:

        image = Image.open(
            BytesIO(image_bytes)
        )

        image = image.convert("RGB")

        image = ImageOps.grayscale(
            image
        )

        image = ImageEnhance.Contrast(
            image
        ).enhance(2)

        width, height = image.size

        if width < 1500:

            scale = 1500 / width

            image = image.resize(
                (
                    int(width * scale),
                    int(height * scale)
                )
            )

        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        return text.strip()

    except Exception as e:

        return f"ERROR: {str(e)}"


# ============================================================
# PATIENT FOLDER
# ============================================================

def get_patient_folder(patient_id):

    safe_id = "".join(
        c for c in patient_id
        if c.isalnum() or c in ("-", "_")
    )

    if not safe_id:

        safe_id = "PATIENT_UNKNOWN"

    folder = os.path.join(
        PATIENTS_FOLDER,
        safe_id
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder


# ============================================================
# SAVE PATIENT
# ============================================================

def save_patient_record(patient_data):

    patient_id = patient_data.get(
        "Patient ID",
        "PATIENT_UNKNOWN"
    )

    folder = get_patient_folder(
        patient_id
    )

    json_path = os.path.join(
        folder,
        "patient_case.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            patient_data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# LOAD PATIENT
# ============================================================

def load_patient_record(patient_id):

    folder = get_patient_folder(
        patient_id
    )

    json_path = os.path.join(
        folder,
        "patient_case.json"
    )

    if not os.path.exists(
        json_path
    ):

        return None

    try:

        with open(
            json_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return None


# ============================================================
# GET ALL PATIENTS
# ============================================================

def get_all_patients():

    patients = []

    if not os.path.exists(
        PATIENTS_FOLDER
    ):

        return patients

    for folder_name in os.listdir(
        PATIENTS_FOLDER
    ):

        folder_path = os.path.join(
            PATIENTS_FOLDER,
            folder_name
        )

        if not os.path.isdir(
            folder_path
        ):

            continue

        json_path = os.path.join(
            folder_path,
            "patient_case.json"
        )

        if os.path.exists(
            json_path
        ):

            try:

                with open(
                    json_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    patient = json.load(
                        file
                    )

                patients.append(
                    patient
                )

            except Exception:

                pass

    return patients


# ============================================================
# QR CODE
# ============================================================

def generate_qr():

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(
        PATIENT_URL
    )

    qr.make(
        fit=True
    )

    return qr.make_image(
        fill_color="black",
        back_color="white"
    )


# ============================================================
# SESSION STATE
# ============================================================

if "current_question" not in st.session_state:

    st.session_state.current_question = 0


if "answers" not in st.session_state:

    st.session_state.answers = {}


if "language" not in st.session_state:

    st.session_state.language = "English"


if "uploaded_documents" not in st.session_state:

    st.session_state.uploaded_documents = []


if "doctor_logged_in" not in st.session_state:

    st.session_state.doctor_logged_in = False


if "selected_patient" not in st.session_state:

    st.session_state.selected_patient = None


# ============================================================
# ENTRY
# ============================================================

entry = st.query_params.get(
    "entry",
    "home"
)


# ============================================================
# HOME
# ============================================================

if entry == "home":

    st.title(
        "🏥 AI Patient Case-Taking System"
    )

    st.write(
        """
        Pre-consultation intelligent clinical intake
        for multilingual patient history collection.
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "👤 Patient"
        )

        if st.button(
            "Open Patient Portal",
            use_container_width=True
        ):

            st.query_params["entry"] = "patient"

            st.rerun()

    with col2:

        st.subheader(
            "👨‍⚕️ Doctor"
        )

        if st.button(
            "Open Doctor Dashboard",
            use_container_width=True
        ):

            st.query_params["entry"] = "doctor"

            st.rerun()

    st.divider()

    st.subheader(
        "📱 Patient QR Code"
    )

    qr_image = generate_qr()

    buffer = BytesIO()

    qr_image.save(
        buffer,
        format="PNG"
    )

    st.image(
        buffer.getvalue(),
        width=280
    )

    st.code(
        PATIENT_URL
    )


# ============================================================
# PATIENT PORTAL
# ============================================================

elif entry == "patient":

    language = st.selectbox(
        "🌐 Language / भाषा / भाषा",
        [
            "English",
            "Hindi",
            "Marathi"
        ],
        index=[
            "English",
            "Hindi",
            "Marathi"
        ].index(
            st.session_state.language
        )
    )

    st.session_state.language = language

    t = TEXT[language]

    questions = QUESTIONS[language]

    st.header(
        t["patient_portal"]
    )

    # --------------------------------------------------------
    # BACK TO HOMEPAGE
    # --------------------------------------------------------

    if st.button(
        "🏠 Back to Homepage",
        use_container_width=True
    ):

        st.query_params["entry"] = "home"
        st.rerun()

    st.write(
        t["welcome"]
    )

    # --------------------------------------------------------
    # CONSENT
    # --------------------------------------------------------

    st.subheader(
        t["consent"]
    )

    consent = st.checkbox(
        t["consent_text"]
    )

    if not consent:

        st.warning(
            t["consent_required"]
        )

        st.stop()

    st.success(
        t["consent_recorded"]
    )

    st.divider()

    # --------------------------------------------------------
    # PATIENT INFORMATION
    # --------------------------------------------------------

    st.subheader(
        t["patient_information"]
    )

    col1, col2 = st.columns(2)

    with col1:

        patient_name = st.text_input(
            t["patient_name"]
        )

    with col2:

        patient_id = st.text_input(
            t["patient_id"],
            value="PAT-DEMO-001"
        )

    st.divider()

    # --------------------------------------------------------
    # CASE TAKING
    # --------------------------------------------------------

    st.subheader(
        t["case_taking"]
    )

    current = st.session_state.current_question

    st.progress(
        current / len(questions)
    )

    if current < len(questions):

        question = questions[current]

        st.markdown(
            f"### {current + 1} / {len(questions)}"
        )

        st.write(
            f"### {question}"
        )

        answer = st.text_area(
            t["type_answer"],
            key=f"answer_{current}"
        )

        # ----------------------------------------------------
        # VOICE
        # ----------------------------------------------------

        st.markdown(
            f"#### {t['voice_input']}"
        )

        audio = st.audio_input(
            t["record_answer"]
        )

        if audio is not None:

            st.audio(
                audio
            )

            if st.button(
                t["convert_voice"],
                key=f"transcribe_{current}"
            ):

                with st.spinner(
                    t["converting"]
                ):

                    try:

                        model = load_whisper_model()

                        temp_audio = (
                            "temp_audio.wav"
                        )

                        with open(
                            temp_audio,
                            "wb"
                        ) as file:

                            file.write(
                                audio.getvalue()
                            )

                        result = model.transcribe(
                            temp_audio,
                            language=WHISPER_LANGUAGES[
                                language
                            ],
                            fp16=False
                        )

                        voice_text = (
                            result["text"].strip()
                        )

                        st.success(
                            t["voice_success"]
                        )

                        st.text_area(
                            t["transcribed_text"],
                            value=voice_text,
                            key=f"voice_result_{current}"
                        )

                        st.session_state.answers[
                            current
                        ] = voice_text

                    except Exception as e:

                        st.error(
                            f"Voice transcription error: {e}"
                        )

        # ----------------------------------------------------
        # NEXT
        # ----------------------------------------------------

        if st.button(
            t["save_next"],
            type="primary",
            use_container_width=True
        ):

            final_answer = answer

            if current in st.session_state.answers:

                final_answer = (
                    st.session_state.answers[
                        current
                    ]
                )

            st.session_state.answers[
                current
            ] = final_answer

            st.session_state.current_question += 1

            st.rerun()

    # ========================================================
    # COMPLETED
    # ========================================================

    else:

        st.success(
            t["completed"]
        )

        st.divider()

        # ----------------------------------------------------
        # MULTIPLE DOCUMENT UPLOAD
        # ----------------------------------------------------

        st.subheader(
            t["upload_document"]
        )

        st.write(
            t["upload_description"]
        )

        uploaded_files = st.file_uploader(
            t["upload_file"],
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            accept_multiple_files=True
        )

        if uploaded_files:

            for uploaded_file in uploaded_files:

                already_processed = any(
                    d["filename"] == uploaded_file.name
                    for d in st.session_state.uploaded_documents
                )

                if not already_processed:

                    st.image(
                        uploaded_file,
                        caption=uploaded_file.name,
                        width=400
                    )

                    if st.button(
                        f"{t['extract']} - {uploaded_file.name}",
                        key=f"ocr_{uploaded_file.name}"
                    ):

                        with st.spinner(
                            t["ocr_running"]
                        ):

                            extracted_text = (
                                extract_text_from_image(
                                    uploaded_file.getvalue()
                                )
                            )

                        st.session_state.uploaded_documents.append(
                            {
                                "filename":
                                    uploaded_file.name,

                                "uploaded_at":
                                    datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),

                                "ocr_text":
                                    extracted_text
                            }
                        )

                        st.success(
                            t["document_processed"]
                        )

        # ----------------------------------------------------
        # SHOW PROCESSED DOCUMENTS
        # ----------------------------------------------------

        if st.session_state.uploaded_documents:

            st.markdown(
                "### 📚 Uploaded Documents"
            )

            for doc in st.session_state.uploaded_documents:

                with st.expander(
                    f"📄 {doc['filename']}"
                ):

                    st.write(
                        f"Uploaded: {doc['uploaded_at']}"
                    )

                    st.text_area(
                        t["extracted_text"],
                        value=doc["ocr_text"],
                        height=200,
                        key=f"show_{doc['filename']}"
                    )

        # ----------------------------------------------------
        # CASE HISTORY
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            t["review"]
        )

        case_history = {}

        for i, question in enumerate(questions):

            case_history[
                question
            ] = st.session_state.answers.get(
                i,
                ""
            )

        # ----------------------------------------------------
        # SAFETY
        # ----------------------------------------------------

        case_for_safety = json.dumps(
            case_history,
            ensure_ascii=False
        ).lower()

        red_flags = [

            "chest pain",
            "difficulty breathing",
            "shortness of breath",
            "unconscious",
            "severe bleeding",
            "stroke",
            "seizure",

            "सीने में दर्द",
            "सांस लेने में कठिनाई",
            "बेहोश",

            "छातीत दुखणे",
            "श्वास घेण्यास त्रास",
            "बेशुद्ध"
        ]

        detected_flags = []

        for flag in red_flags:

            if flag.lower() in case_for_safety:

                detected_flags.append(
                    flag
                )

        st.subheader(
            t["safety"]
        )

        st.info(
            t["safety_description"]
        )

        if detected_flags:

            st.error(
                t["red_flag"]
            )

            for flag in detected_flags:

                st.warning(
                    f"{t['human_review']}: {flag}"
                )

        else:

            st.success(
                t["no_red_flag"]
            )

        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        st.divider()

        if st.button(
            t["submit"],
            type="primary",
            use_container_width=True
        ):

            if not patient_name:

                st.warning(
                    t["enter_name"]
                )

            else:

                patient_data = {

                    "Patient Name":
                        patient_name,

                    "Patient ID":
                        patient_id,

                    "Selected Language":
                        language,

                    "Consent":
                        True,

                    "Timestamp":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "Case History":
                        case_history,

                    "Documents":
                        st.session_state.uploaded_documents,

                    "Doctor Notes":
                        "",

                    "Doctor Verified":
                        False
                }

                # Save patient record
                save_patient_record(
                    patient_data
                )

                # Save uploaded document files
                patient_folder = (
                    get_patient_folder(
                        patient_id
                    )
                )

                documents_folder = os.path.join(
                    patient_folder,
                    "documents"
                )

                os.makedirs(
                    documents_folder,
                    exist_ok=True
                )

                for uploaded_file in uploaded_files or []:

                    file_path = os.path.join(
                        documents_folder,
                        uploaded_file.name
                    )

                    with open(
                        file_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_file.getvalue()
                        )

                st.success(
                    t["submitted"]
                )

                st.info(
                    t["doctor_can_review"]
                )


# ============================================================
# DOCTOR
# ============================================================

elif entry == "doctor":

    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.doctor_logged_in:

        st.header(
            "👨‍⚕️ Doctor Login"
        )

        st.write(
            "Demo login for the SIH prototype."
        )

        doctor_id = st.text_input(
            "Doctor ID"
        )

        doctor_password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            type="primary"
        ):

            if (
                doctor_id == "DOC1001"
                and doctor_password == "1234"
            ):

                st.session_state.doctor_logged_in = True

                st.success(
                    "Login successful."
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Doctor ID or Password."
                )

        st.info(
            """
            Demo credentials:

            Doctor ID: DOC1001
            Password: 1234
            """
        )

    # ========================================================
    # DOCTOR DASHBOARD
    # ========================================================

    else:

        st.header(
            "👨‍⚕️ Doctor Dashboard"
        )

        patients = get_all_patients()

        # ----------------------------------------------------
        # PATIENT LIST
        # ----------------------------------------------------

        if not patients:

            st.warning(
                "No patient records available."
            )

        else:

            st.subheader(
                "👥 Patient List"
            )

            patient_options = []

            for patient in patients:

                name = patient.get(
                    "Patient Name",
                    "Unknown"
                )

                pid = patient.get(
                    "Patient ID",
                    "Unknown"
                )

                patient_options.append(
                    f"{name} | {pid}"
                )

            selected = st.selectbox(
                "Select Patient",
                patient_options
            )

            selected_index = (
                patient_options.index(
                    selected
                )
            )

            patient_data = patients[
                selected_index
            ]

            # ------------------------------------------------
            # PATIENT INFO
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "👤 Patient Information"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Patient",
                    patient_data.get(
                        "Patient Name",
                        "Unknown"
                    )
                )

            with col2:

                st.metric(
                    "Patient ID",
                    patient_data.get(
                        "Patient ID",
                        "Unknown"
                    )
                )

            with col3:

                st.metric(
                    "Language",
                    patient_data.get(
                        "Selected Language",
                        "Unknown"
                    )
                )

            with col4:

                documents_count = len(
                    patient_data.get(
                        "Documents",
                        []
                    )
                )

                st.metric(
                    "Documents",
                    documents_count
                )

            # ------------------------------------------------
            # CASE HISTORY
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "🩺 Complete Patient History"
            )

            history = patient_data.get(
                "Case History",
                {}
            )

            for question, answer in history.items():

                st.markdown(
                    f"**{question}**"
                )

                if answer:

                    st.write(
                        answer
                    )

                else:

                    st.caption(
                        "No answer provided."
                    )

            # ------------------------------------------------
            # DOCUMENTS
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "📄 All Submitted Medical Documents"
            )

            documents = patient_data.get(
                "Documents",
                []
            )

            if documents:

                for number, document in enumerate(
                    documents,
                    start=1
                ):

                    filename = document.get(
                        "filename",
                        "Unknown document"
                    )

                    upload_time = document.get(
                        "uploaded_at",
                        "Unknown"
                    )

                    ocr_text = document.get(
                        "ocr_text",
                        ""
                    )

                    with st.expander(
                        f"📄 Document {number}: {filename}"
                    ):

                        st.write(
                            f"**Uploaded:** {upload_time}"
                        )

                        # Try to display actual file
                        patient_folder = (
                            get_patient_folder(
                                patient_data.get(
                                    "Patient ID"
                                )
                            )
                        )

                        document_path = os.path.join(
                            patient_folder,
                            "documents",
                            filename
                        )

                        if os.path.exists(
                            document_path
                        ):

                            st.image(
                                document_path,
                                caption=filename,
                                width=500
                            )

                        st.markdown(
                            "### 🔍 OCR Extracted Information"
                        )

                        if ocr_text:

                            st.text_area(
                                "Extracted Text",
                                value=ocr_text,
                                height=220,
                                key=f"doctor_ocr_{number}"
                            )

                        else:

                            st.info(
                                "No OCR text available."
                            )

            else:

                st.info(
                    "No medical documents submitted."
                )

            # ------------------------------------------------
            # SAFETY REVIEW
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "🚨 Safety Review"
            )

            all_patient_text = json.dumps(
                patient_data,
                ensure_ascii=False
            ).lower()

            red_flags = [

                "chest pain",
                "difficulty breathing",
                "shortness of breath",
                "unconscious",
                "severe bleeding",
                "stroke",
                "seizure",

                "सीने में दर्द",
                "सांस लेने में कठिनाई",
                "बेहोश",

                "छातीत दुखणे",
                "श्वास घेण्यास त्रास",
                "बेशुद्ध"
            ]

            found_flags = []

            for flag in red_flags:

                if flag.lower() in all_patient_text:

                    found_flags.append(
                        flag
                    )

            if found_flags:

                st.error(
                    "⚠️ Potential red-flag information "
                    "requires physician review."
                )

                for flag in found_flags:

                    st.warning(
                        f"Human review required: {flag}"
                    )

            else:

                st.success(
                    "No predefined red-flag phrase detected."
                )

            # ------------------------------------------------
            # PRE-CONSULTATION SUMMARY
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "🤖 Pre-Consultation Summary"
            )

            history_values = list(
                history.values()
            )

            complaint = (
                history_values[0]
                if len(history_values) > 0
                else "Not provided"
            )

            onset = (
                history_values[1]
                if len(history_values) > 1
                else "Not provided"
            )

            medicines = (
                history_values[5]
                if len(history_values) > 5
                else "Not provided"
            )

            allergies = (
                history_values[6]
                if len(history_values) > 6
                else "Not provided"
            )

            st.markdown(
                f"""
                **Chief Complaint:**  
                {complaint}

                **Onset:**  
                {onset}

                **Current Medicines:**  
                {medicines}

                **Allergies:**  
                {allergies}

                **Number of Previous Documents:**  
                {len(documents)}

                **Patient Language:**  
                {patient_data.get("Selected Language", "Unknown")}
                """
            )

            # ------------------------------------------------
            # DOCTOR NOTES
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "✏️ Doctor Verification"
            )

            existing_notes = patient_data.get(
                "Doctor Notes",
                ""
            )

            doctor_notes = st.text_area(
                "Doctor Notes",
                value=existing_notes,
                placeholder=(
                    "Doctor can edit, verify or add "
                    "clinical information here."
                )
            )

            existing_verified = patient_data.get(
                "Doctor Verified",
                False
            )

            verified = st.checkbox(
                "I have reviewed and verified the patient information.",
                value=existing_verified
            )

            if verified:

                st.success(
                    "Patient information marked as verified."
                )

            if st.button(
                "💾 Save Doctor Review",
                type="primary",
                use_container_width=True
            ):

                patient_data[
                    "Doctor Notes"
                ] = doctor_notes

                patient_data[
                    "Doctor Verified"
                ] = verified

                patient_data[
                    "Doctor Review Timestamp"
                ] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                save_patient_record(
                    patient_data
                )

                st.success(
                    "✅ Doctor review saved successfully."
                )

        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        st.divider()

        if st.button(
            "🚪 Logout / Back to Login",
            use_container_width=True
        ):

            st.session_state.doctor_logged_in = False

            st.query_params["entry"] = "doctor"

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "SIH PS ID 26047 | AI Patient Case-Taking Software | "
    "Prototype | AI assists data collection and documentation; "
    "healthcare professionals remain responsible for clinical decisions."
)