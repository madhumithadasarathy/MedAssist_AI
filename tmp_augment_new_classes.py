import pandas as pd
import random

new_data = [
    # Lyme Disease
    ("Lyme Disease", "I have a bullseye rash on my leg, fever, and my joints are very stiff."),
    ("Lyme Disease", "Got bitten by a tick, now I have severe fatigue, joint aches, and a circular red rash."),
    ("Lyme Disease", "Extreme tiredness, swollen lymph nodes, and a strange expanding red rash."),
    ("Lyme Disease", "Joint pain, fever, and a red rash with a clear center after walking in the woods."),
    ("Lyme Disease", "Muscle aches, stiff neck, and a large bullseye-shaped rash on my arm."),

    # Celiac Disease
    ("Celiac Disease", "Severe bloating, diarrhea, and stomach cramps whenever I eat pasta or bread."),
    ("Celiac Disease", "Chronic diarrhea, abdominal pain, and an itchy blistering skin rash after eating gluten."),
    ("Celiac Disease", "I get extreme fatigue and digestive issues like gas and bloating after consuming wheat."),
    ("Celiac Disease", "Stomach pains, weight loss, and anemia. Eating bread makes me feel very sick."),
    ("Celiac Disease", "Greasy, foul-smelling stools, bloating, and stomach cramps due to gluten intake."),

    # Endometriosis
    ("Endometriosis", "Extremely painful periods, pain during intercourse, and lower back pain."),
    ("Endometriosis", "Pelvic pain that gets worse during my menstrual cycle, heavy bleeding."),
    ("Endometriosis", "Severe cramps during my period that radiate to my back and legs, and painful urination."),
    ("Endometriosis", "Extremely painful menstrual cramps, fatigue, and pain with bowel movements."),
    ("Endometriosis", "Chronic pelvic pain throughout the month, very heavy and painful periods."),

    # PCOS (Polycystic Ovary Syndrome)
    ("PCOS", "Irregular periods, excessive facial hair growth, and unexplained weight gain."),
    ("PCOS", "I miss my periods for months, have bad acne, and thinning hair on my head."),
    ("PCOS", "Irregular menstrual cycles, weight gain especially around the belly, and dark patches of skin."),
    ("PCOS", "Infrequent periods, struggling to lose weight, and noticeable hair growth on my face."),
    ("PCOS", "Skipping periods, severe acne, and weight gain that is very hard to lose."),

    # Crohn's Disease
    ("Crohn's Disease", "Severe abdominal pain, persistent diarrhea, and noticeable weight loss without trying."),
    ("Crohn's Disease", "Cramping in the stomach, diarrhea containing blood, and extreme fatigue."),
    ("Crohn's Disease", "Fever, chronic diarrhea often with blood, and severe stomach cramps."),
    ("Crohn's Disease", "Abdominal cramping, frequent trips to the bathroom, and losing weight quickly."),
    ("Crohn's Disease", "Persistent watery diarrhea, severe gas pains, and feeling constantly tired."),

    # Ulcerative Colitis
    ("Ulcerative Colitis", "Diarrhea with blood and pus, abdominal pain, and urgent need to defecate."),
    ("Ulcerative Colitis", "Rectal pain and bleeding, diarrhea, and feverish feelings."),
    ("Ulcerative Colitis", "Bloody diarrhea occurring frequently, stomach cramps, and sudden urge to pass stool."),
    ("Ulcerative Colitis", "Severe urgency to go to the bathroom, diarrhea with mucus and blood."),
    ("Ulcerative Colitis", "Abdominal cramping, persistent bloody diarrhea, and overall fatigue."),

    # Parkinson's Disease
    ("Parkinson's Disease", "My hands are constantly trembling, and my muscles feel very stiff when I try to walk."),
    ("Parkinson's Disease", "Shaking in my fingers, slow movement, and shuffling when I walk."),
    ("Parkinson's Disease", "Noticeable tremor in one hand, stiffness in my arms, and loss of automated movements."),
    ("Parkinson's Disease", "Slurred speech, stiff facial expression, and a resting tremor in my hand."),
    ("Parkinson's Disease", "Slowed movement, muscle rigidity, and impaired balance or posture."),

    # Alzheimer's Disease
    ("Alzheimer's Disease", "I keep forgetting recent events and names of family members, feeling very confused."),
    ("Alzheimer's Disease", "Severe memory loss, getting lost in familiar places, and repeating questions."),
    ("Alzheimer's Disease", "Misplacing items in strange places, struggling with words, and memory decline."),
    ("Alzheimer's Disease", "Confusion about time and place, forgetting recent conversations completely."),
    ("Alzheimer's Disease", "Trouble handling money, wandering, and increased memory gaps every day."),

    # Hyperthyroidism
    ("Hyperthyroidism", "My heart is always racing, I'm losing weight rapidly despite eating a lot, and sweating."),
    ("Hyperthyroidism", "Tremors in my hands, feeling very anxious all the time, and unexpected weight loss."),
    ("Hyperthyroidism", "Fast heartbeat, feeling very hot all the time, completely restless and jittery."),
    ("Hyperthyroidism", "Bulging eyes, rapid weight loss, heat intolerance, and nervousness."),
    ("Hyperthyroidism", "Rapid heart rate, constantly sweating, very anxious, and trouble sleeping."),

    # Hypothyroidism
    ("Hypothyroidism", "I feel incredibly tired all the time, gaining weight for no reason, and feeling very cold."),
    ("Hypothyroidism", "Dry skin, unexpected weight gain, fatigue, and feeling cold when others are warm."),
    ("Hypothyroidism", "Extreme lethargy, constipation, puffiness in the face, and weight gain."),
    ("Hypothyroidism", "Sluggishness, unexplained weight gain, brittle nails, and constant feeling of coldness."),
    ("Hypothyroidism", "Memory problems, muscle weakness, very dry skin, and constant exhaustion."),
]

df_original = pd.read_csv("backend/data/Symptom2Disease.csv")
df_new = pd.DataFrame(new_data, columns=["label", "text"])

df_combined = pd.concat([df_original, df_new]).drop_duplicates(subset=["text"])
df_combined.to_csv("backend/data/Symptom2Disease.csv", index=False)

print(f"Added 10 new diseases! Total dataset size is now: {len(df_combined)}")
