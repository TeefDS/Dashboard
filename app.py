import streamlit as st
import torch
import numpy as np
import pandas as pd
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification
)

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Food Safety Dashboard", layout="wide")

device = "cuda" if torch.cuda.is_available() else "cpu"

# =========================================================
# MODEL PATHS
# =========================================================
BERTWEET_PATH = "models/bertweet_final"
BIOBERT_PATH = "models/biobert_best_ner"
QWEN_PATH = "models/qwen_final_model"

# =========================================================
# LABEL MAPS
# =========================================================
bertweet_label_map = {
    0: "Noise",
    1: "Alert"
}

bio_id2label = {
    0: "O",
    1: "B-food",
    2: "I-food",
    3: "B-symptom",
    4: "I-symptom",
    5: "B-loc",
    6: "I-loc"
}

# عدلي هذا بالمابينق الحقيقي حق Qwen
qwen_id2label = {
    0: "Category 0",
    1: "Category 1",
    2: "Category 2",
    3: "Category 3"
}

# =========================================================
# DUMMY DATA
# =========================================================
dummy_data = pd.DataFrame([
    {
        "text": "Customer in Riyadh reported vomiting after eating chicken shawarma from a local restaurant last night.",
        "expected_type": "alert"
    },
    {
        "text": "Several people in Jeddah complained of diarrhea after consuming shrimp sandwiches from a seaside cafe.",
        "expected_type": "alert"
    },
    {
        "text": "Recall notice: frozen mixed berries may be contaminated with salmonella in Dubai supermarkets.",
        "expected_type": "alert"
    },
    {
        "text": "Food poisoning suspected after families in London ate chicken tenders from a street market.",
        "expected_type": "alert"
    },
    {
        "text": "Public health warning in New York for lettuce products linked to E. coli symptoms.",
        "expected_type": "alert"
    },
    {
        "text": "A child in Virginia became nauseous after drinking spoiled milk bought from a corner store.",
        "expected_type": "alert"
    },
    {
        "text": "Multiple complaints from Woking about sushi causing vomiting and stomach pain.",
        "expected_type": "alert"
    },
    {
        "text": "Restaurant in Midlothian under investigation after customers got sick from beef burgers.",
        "expected_type": "alert"
    },
    {
        "text": "Ministry notice: imported eggs may carry contamination; consumers in Riyadh advised to discard them.",
        "expected_type": "alert"
    },
    {
        "text": "People on social media say they felt sick after eating ice cream from a festival in Jeddah.",
        "expected_type": "alert"
    },
    {
        "text": "Cluster of diarrhea cases reported after a wedding meal served rice and chicken in Dammam.",
        "expected_type": "alert"
    },
    {
        "text": "Recall expanded for packaged salad due to possible listeria contamination in the UK.",
        "expected_type": "alert"
    },
    {
        "text": "Parents in Jeddah reported children vomiting after eating school cafeteria noodles.",
        "expected_type": "alert"
    },
    {
        "text": "A food market in London is being reviewed after several visitors experienced food poisoning.",
        "expected_type": "alert"
    },
    {
        "text": "Consumer complaint: cheese burger from a highway stop caused nausea and vomiting.",
        "expected_type": "alert"
    },
    {
        "text": "Frozen chicken product recalled after salmonella found during routine testing.",
        "expected_type": "alert"
    },
    {
        "text": "Residents in New York reported upset stomach after eating meat pies from a bakery.",
        "expected_type": "alert"
    },
    {
        "text": "Festival food stall in Riyadh linked to diarrhea cases after serving chicken wraps.",
        "expected_type": "alert"
    },
    {
        "text": "Tuna salad recall announced after reports of nausea in multiple cities.",
        "expected_type": "alert"
    },
    {
        "text": "Several students in Jeddah got sick after lunch and reported stomach hurts and vomiting.",
        "expected_type": "alert"
    },
    {
        "text": "I had the best pizza in Riyadh today and would definitely order again.",
        "expected_type": "noise"
    },
    {
        "text": "Trying a new sushi place in Jeddah tonight, hope it is good.",
        "expected_type": "noise"
    },
    {
        "text": "This chicken burger is amazing, no notes.",
        "expected_type": "noise"
    },
    {
        "text": "Anyone know a good food market in London for weekend shopping?",
        "expected_type": "noise"
    },
    {
        "text": "Bought frozen berries for smoothies and they taste great.",
        "expected_type": "noise"
    },
    {
        "text": "My mom made rice and beans and it was perfect comfort food.",
        "expected_type": "noise"
    },
    {
        "text": "Craving ice cream after work in Dubai.",
        "expected_type": "noise"
    },
    {
        "text": "New cafe in New York serves excellent sandwiches and coffee.",
        "expected_type": "noise"
    },
    {
        "text": "I need recommendations for salad places in Riyadh.",
        "expected_type": "noise"
    },
    {
        "text": "Made beef noodles at home and the whole family loved it.",
        "expected_type": "noise"
    },
    {
        "text": "Guys I think that shrimp wrap from Jeddah corniche made me feel sick.",
        "expected_type": "alert"
    },
    {
        "text": "Not sure if it was the milk or the egg sandwich but I got nauseous after breakfast.",
        "expected_type": "alert"
    },
    {
        "text": "Riyadh burger spot gave me food poisoning fr.",
        "expected_type": "alert"
    },
    {
        "text": "Chicken tenders were so oily I felt bad after, maybe just me though.",
        "expected_type": "noise"
    },
    {
        "text": "The sushi was fresh and delicious, no issues at all.",
        "expected_type": "noise"
    },
    {
        "text": "Warning circulating online about contaminated frozen fish in local stores.",
        "expected_type": "alert"
    },
    {
        "text": "My little brother threw up after eating salad from the cafeteria.",
        "expected_type": "alert"
    },
    {
        "text": "Do not buy that garlic dip, something tasted off and we all got stomach pain.",
        "expected_type": "alert"
    },
    {
        "text": "The noodles were spicy but really tasty.",
        "expected_type": "noise"
    },
    {
        "text": "We all ate pizza and nobody got sick, thankfully.",
        "expected_type": "noise"
    }
])

# =========================================================
# LOAD MODELS
# =========================================================
@st.cache_resource
def load_bertweet():
    tokenizer = AutoTokenizer.from_pretrained(BERTWEET_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(BERTWEET_PATH)
    model.to(device)
    model.eval()
    return tokenizer, model

@st.cache_resource
def load_biobert():
    tokenizer = AutoTokenizer.from_pretrained(BIOBERT_PATH)
    model = AutoModelForTokenClassification.from_pretrained(BIOBERT_PATH)
    model.to(device)
    model.eval()
    return tokenizer, model

@st.cache_resource
def load_qwen():
    tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, trust_remote_code=True)
    model = AutoModelForSequenceClassification.from_pretrained(QWEN_PATH, trust_remote_code=True)
    model.to(device)
    model.eval()
    return tokenizer, model

bertweet_tokenizer, bertweet_model = load_bertweet()
biobert_tokenizer, biobert_model = load_biobert()
qwen_tokenizer, qwen_model = load_qwen()

# =========================================================
# BERTWEET PREDICTION
# =========================================================
def predict_alert(text):
    inputs = bertweet_tokenizer(
        str(text),
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = bertweet_model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)[0].cpu().numpy()
        pred = int(np.argmax(probs))

    return bertweet_label_map[pred], float(probs[pred]), probs

# =========================================================
# BIOBERT NER
# =========================================================
def predict_ner(text):
    tokens = str(text).split()

    enc = biobert_tokenizer(
        tokens,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    word_ids = enc.word_ids(batch_index=0)
    inputs = {k: v.to(device) for k, v in enc.items()}

    with torch.no_grad():
        outputs = biobert_model(**inputs)

    pred_ids = outputs.logits.argmax(dim=-1)[0].cpu().tolist()

    first_subword_preds = {}
    for i, word_id in enumerate(word_ids):
        if word_id is None:
            continue
        if word_id not in first_subword_preds:
            first_subword_preds[word_id] = pred_ids[i]

    tags = [
        bio_id2label[first_subword_preds[i]] if i in first_subword_preds else "O"
        for i in range(len(tokens))
    ]

    return tokens, tags

def extract_entities(tokens, tags):
    entities = {"food": [], "symptom": [], "loc": []}
    current_tokens = []
    current_type = None

    for tok, tag in zip(tokens, tags):
        if tag == "O":
            if current_tokens and current_type in entities:
                entities[current_type].append(" ".join(current_tokens))
            current_tokens = []
            current_type = None
            continue

        prefix, ent_type = tag.split("-", 1)

        if prefix == "B":
            if current_tokens and current_type in entities:
                entities[current_type].append(" ".join(current_tokens))
            current_tokens = [tok]
            current_type = ent_type

        elif prefix == "I" and current_type == ent_type:
            current_tokens.append(tok)

    if current_tokens and current_type in entities:
        entities[current_type].append(" ".join(current_tokens))

    return entities

# =========================================================
# QWEN CATEGORY PREDICTION
# =========================================================
def predict_category(text):
    formatted_text = f"Title:  Text: {str(text)}"

    inputs = qwen_tokenizer(
        formatted_text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = qwen_model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)[0].cpu().numpy()
        pred = int(np.argmax(probs))

    label = qwen_id2label.get(pred, f"Class {pred}")
    return label, float(probs[pred]), probs

# =========================================================
# FULL PIPELINE
# =========================================================
def run_pipeline(text):
    alert_label, alert_conf, alert_probs = predict_alert(text)

    result = {
        "alert_label": alert_label,
        "alert_conf": alert_conf,
        "alert_probs": alert_probs,
        "entities": None,
        "category_label": None,
        "category_conf": None,
        "category_probs": None
    }

    if alert_label == "Alert":
        tokens, tags = predict_ner(text)
        entities = extract_entities(tokens, tags)

        category_label, category_conf, category_probs = predict_category(text)

        result["entities"] = entities
        result["category_label"] = category_label
        result["category_conf"] = category_conf
        result["category_probs"] = category_probs

    return result

# =========================================================
# UI
# =========================================================
st.title("Food Safety Monitoring Dashboard")

tab1, tab2, tab3 = st.tabs(["Single Text Analysis", "CSV Upload", "Dummy Data"])

# =========================================================
# TAB 1: SINGLE TEXT
# =========================================================
with tab1:
    user_text = st.text_area("Enter text", height=180)

    if st.button("Analyze Text"):
        if user_text.strip():
            result = run_pipeline(user_text)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Alert Detection")
                st.metric("Prediction", result["alert_label"])
                st.metric("Confidence", f"{result['alert_conf']:.4f}")

            with col2:
                st.subheader("Product Category")
                if result["category_label"] is not None:
                    st.metric("Category", result["category_label"])
                    st.metric("Confidence", f"{result['category_conf']:.4f}")
                else:
                    st.info("Skipped because prediction is Noise.")

            st.subheader("Named Entity Recognition")
            if result["entities"] is not None:
                st.json(result["entities"])
            else:
                st.info("Skipped because prediction is Noise.")

# =========================================================
# TAB 2: CSV
# =========================================================
with tab2:
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        df_upload = pd.read_csv(uploaded_file)
        st.write("Uploaded data preview:")
        st.dataframe(df_upload.head())

        text_column = st.selectbox("Select text column", df_upload.columns)

        if st.button("Run Batch Analysis on CSV"):
            output_rows = []

            for _, row in df_upload.iterrows():
                text = str(row[text_column])
                result = run_pipeline(text)

                entities = result["entities"] if result["entities"] is not None else {
                    "food": [],
                    "symptom": [],
                    "loc": []
                }

                output_rows.append({
                    "text": text,
                    "alert_label": result["alert_label"],
                    "alert_confidence": result["alert_conf"],
                    "food_entities": ", ".join(entities["food"]),
                    "symptom_entities": ", ".join(entities["symptom"]),
                    "location_entities": ", ".join(entities["loc"]),
                    "product_category": result["category_label"] if result["category_label"] is not None else "",
                    "category_confidence": result["category_conf"] if result["category_conf"] is not None else ""
                })

            results_df = pd.DataFrame(output_rows)

            st.subheader("Batch Results")
            st.dataframe(results_df)

            csv = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Results CSV",
                data=csv,
                file_name="csv_predictions.csv",
                mime="text/csv"
            )

# =========================================================
# TAB 3: DUMMY DATA
# =========================================================
with tab3:
    st.subheader("Dummy Data Preview")
    st.dataframe(dummy_data)

    if st.button("Run Batch Analysis on Dummy Data"):
        output_rows = []

        for _, row in dummy_data.iterrows():
            text = str(row["text"])
            result = run_pipeline(text)

            entities = result["entities"] if result["entities"] is not None else {
                "food": [],
                "symptom": [],
                "loc": []
            }

            output_rows.append({
                "text": text,
                "expected_type": row["expected_type"],
                "alert_label": result["alert_label"],
                "alert_confidence": result["alert_conf"],
                "food_entities": ", ".join(entities["food"]),
                "symptom_entities": ", ".join(entities["symptom"]),
                "location_entities": ", ".join(entities["loc"]),
                "product_category": result["category_label"] if result["category_label"] is not None else "",
                "category_confidence": result["category_conf"] if result["category_conf"] is not None else ""
            })

        results_df = pd.DataFrame(output_rows)

        st.subheader("Dummy Data Results")
        st.dataframe(results_df)

        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Dummy Results CSV",
            data=csv,
            file_name="dummy_predictions.csv",
            mime="text/csv"
        )
