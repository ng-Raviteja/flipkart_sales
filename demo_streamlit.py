import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import requests
import io
import google.generativeai as genai
import json
genai.configure(api_key="AIzaSyA7gh0ANlePJTQSbLUqSVbxT6jwlh1Hu_E")
model = genai.GenerativeModel("gemini-1.5-pro")
def transcribe_audio(audio_file):
    # Implement your reamlitaudio transcription logic here
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": "Bearer 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","task":"translate","language":"english","return_timestamps":"True"}

    data =audio_file.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

analysis_prompt="""
Act as a conversation analyzer for sales call transcripts. For each provided conversation, analyze and extract the following features and present them in a structured JSON format:
Required Analysis Parameters:
1. sentiment : Based on overall conversation,Must classify as: Positive/Negative/Neutral
2. product : Strictly output should be specific product mentioned (e.g : "Samsung 55-inch TV", "iPhone 16"),if no specific product mentioned,return  None and do no return the product category
3.product_category: choose from :  Electronics,Home Appliances,Computers and Peripherals,if no specific product mentioned,return  None
4.sub_product_category : choose the relevant subcategory from below : 
   a. Electronics category : Televisions,Smartphones,Tablets,CamerasAudio Devices
   b. Home Appliances category : Refrigerators,Washing Machines,Air Conditioners,Microwaves
   c. Computers and Peripherals : Laptops,Desktops,Monitors,Printers
   if no specific product mentioned,return  None
5. brand: Extract specific brand names discussed,if no specific brand mentioned,return None
6. customer_engagement_level : High (active participation, asking questions),Low (passive listening, few responses)
7. customer_intent : Identify the customer’s primary intent. Choose from : Inquiry/Purchase/Support/Uninterested
8. discussion : Classify the primary discussion in conversation as one of the following: : Negotiation,Returns and Exchanges,Additional Issues,Uninterested,Others
9. outcome : Determine the main outcome of the call. Choose from: Purchase(if the customer has made a purchase or is committed to purchasing),Resolved(if the customers query or issue is resolved),Follow-Up Scheduled,Rejected
10.rejection_reason : Briefly provide the rejection reason,if coversation results in a successful purchase or you didnt find the reason for rejection,return None
Analyze the conversation step by step : {transcription}
strictly follow this json format:
analysis ={'sentiment': enum("Positive/Negative/Neutral"),"product":str,"product_category":enum(Electronics,Home Appliances,Computers and Peripherals),
sub_product_category:enum(Televisions,Smartphones,Laptops,Tablets,Cameras or Refrigerators,Washing Machines,Air Conditioners or Desktops,Monitors,Printers ),"brand":str(null,if not mentioned),customer_engagement_level:enum(High/Low),customer_intent:enum(Inquiry/Purchase/Support/Not Interested),discussion:enum(Negotiation,Returns and Exchanges,Additional Issues Addressed,Not Interested,Others),outcome:enum(Purchased,,Resolved,Follow-Up Scheduled,Rejected),rejection_reason:str}
Return: analysis
"""

def analyze_transcription(transcription):
    analysis_prompt_updated=analysis_prompt.replace("{transcription}",str(transcription))
    try:
        response = model.generate_content(analysis_prompt_updated)
        json_response=json.loads(response.text.replace("```json","").replace("```",""))
    except:
        response = model.generate_content(analysis_prompt_updated)
        json_response=json.loads(response.text.replace("```json","").replace("```",""))
    return json_response

# Set page config
st.set_page_config(page_title="Audio Transcription & Analysis", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        background-color: #f0f2f6;
    }
    .css-1d391kg {
        padding-top: 3rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎙️ Audio Transcription & Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg","m4a"])

if uploaded_file is not None:
    # Display audio player
    st.audio(uploaded_file)

    # Transcribe button
    if st.button("Transcribe and Analyze"):
        with st.spinner("Transcribing and analyzing..."):
            # Transcribe audio
            transcription = transcribe_audio(uploaded_file)

            # Analyze transcription
            analysis = analyze_transcription(transcription)

        # Display results
        st.success("Transcription and analysis complete!")

        # Create two columns for layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 Transcription")
            st.text_area("", value=transcription, height=300, disabled=True)

        with col2:
            st.subheader("🔍 Analysis Results")
            for key, value in analysis.items():
                st.metric(label=key.replace("_", " ").title(), value=value)

        # Create a pie chart for customer engagement level
        engagement_data = pd.DataFrame({
            "Level": ["Engaged", "Not Engaged"],
            "Value": [1 if analysis["customer_engagement_level"] == "High" else 0,
                      1 if analysis["customer_engagement_level"] == "Low" else 0]
        })

        fig = px.pie(engagement_data, values="Value", names="Level", title="Customer Engagement Level",
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig)

        # Create a bar chart for sentiment
        sentiment_data = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Value": [1 if analysis["sentiment"] == "Positive" else 0,
                      1 if analysis["sentiment"] == "Neutral" else 0,
                      1 if analysis["sentiment"] == "Negative" else 0]
        })

        fig = px.bar(sentiment_data, x="Sentiment", y="Value", title="Sentiment Analysis",
                     color="Sentiment", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig)

else:
    st.info("Please upload an audio file to begin.")
