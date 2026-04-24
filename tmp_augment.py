import pandas as pd
import random

new_data = [
    # Emergencies to boost red-flag understanding (they map to conditions, red flag logic handles the emergency banner)
    ("Heart Attack", "I have a crushing chest pain that radiates to my left arm, and I am sweating a lot."),
    ("Heart Attack", "Severe chest pressure, difficulty breathing, and my jaw hurts."),
    ("Heart Attack", "I feel like an elephant is sitting on my chest, very dizzy and nauseous."),
    ("Heart Attack", "Extreme tightness in my chest and shortness of breath."),
    ("Stroke", "Half of my face is drooping and my right arm feels totally numb and weak."),
    ("Stroke", "I suddenly can't speak properly, my words are slurred and I can't lift my arm."),
    ("Stroke", "Sudden severe headache, blurred vision, and unable to balance."),
    ("Stroke", "My face looks lopsided, I feel very confused and dizzy."),
    
    # Influenza
    ("Influenza", "I've got this terrible fever along with chills and body aches all over my back."),
    ("Influenza", "It feels like I was hit by a truck. High temperature, weak muscles, dry cough."),
    ("Influenza", "Sweating rapidly, freezing chills, and an annoying dry cough."),
    ("Influenza", "Started suddenly: fever, chills, aching joints, and profound fatigue."),
    
    # Common Cold
    ("Common Cold", "Just a normal sniffle, slightly blocked nose, and a tickle in my throat."),
    ("Common Cold", "I keep blowing my nose and sneezing. No fever, just feeling a bit congested."),
    ("Common Cold", "Slight sore throat, very mild cough, running nose but I can still work."),
    ("Common Cold", "A stuffy head cold with lots of sneezing and watery eyes."),

    # COVID-19
    ("COVID-19", "I completely lost my sense of taste and smell yesterday, accompanied by a dry cough."),
    ("COVID-19", "Testing positive soon maybe: lack of taste, fever, and breathing is slightly hard."),
    ("COVID-19", "Fever, loss of smell, and a very persistent dry cough for the last week."),
    ("COVID-19", "Anosmia and ageusia along with fatigue and a slight fever."),

    # Migraine
    ("Migraine", "Pounding painful headache on the left temple, bright lights make it much worse."),
    ("Migraine", "I see auras and flashes of light followed by a severe throbbing head pain."),
    ("Migraine", "Extreme sensitivity to sound and light, pulsing headache that causes nausea."),
    ("Migraine", "My head is throbbing so badly that I feel like throwing up, need a dark room."),

    # Gastroenteritis
    ("Gastroenteritis", "I've been vomiting all morning and having watery diarrhea."),
    ("Gastroenteritis", "Stomach cramps, diarrhea, and feeling very nauseous after eating out."),
    ("Gastroenteritis", "Food poisoning symptoms: vomiting, stomach cramps, and loose stools."),
    ("Gastroenteritis", "Frequent trips to the bathroom with watery diarrhea and abdominal pain."),

    # Urinary Tract Infection
    ("Urinary Tract Infection", "It burns a lot when I urinate, and I feel the urge to go constantly."),
    ("Urinary Tract Infection", "Cloudy and strong-smelling urine, painful burning urination."),
    ("Urinary Tract Infection", "Lower abdominal pain, frequent urination but only small amounts come out, burns."),
    ("Urinary Tract Infection", "Burning sensation during peeing and feeling like my bladder is never empty."),

    # Allergic Rhinitis
    ("Allergic Rhinitis", "Every spring I get constant sneezing, itchy eyes, and a very runny nose."),
    ("Allergic Rhinitis", "Dust triggers my allergies: non-stop sneezing and clear nasal drip."),
    ("Allergic Rhinitis", "My eyes are incredibly itchy, watery, and I have a constant sneezes."),
    ("Allergic Rhinitis", "Seasonal allergies acting up: stuffy nose and itchy throat/eyes."),

    # Bronchitis
    ("Bronchitis", "A deep, chesty cough that brings up thick yellowish-green mucus."),
    ("Bronchitis", "My chest feels tight and I have a barking persistent cough with phlegm."),
    ("Bronchitis", "Coughing up a lot of sputum, slight fever, and wheezing when I breathe."),
    ("Bronchitis", "Lingering cough after a cold that produces thick mucus from my chest."),

    # Diabetes
    ("Diabetes", "I am incredibly thirsty all the time and have to pee very frequently especially at night."),
    ("Diabetes", "Unexplained weight loss, blurry vision, and I am drinking gallons of water."),
    ("Diabetes", "Feeling constantly hungry and thirsty, frequent urination, cuts healing very slowly."),
    ("Diabetes", "Tingling in my feet, excessive thirst, and feeling very fatigued without reason."),
    
    # Hypertension
    ("Hypertension", "My doctor says my blood pressure is very high. I sometimes get dizzy and have headaches."),
    ("Hypertension", "Ringing in my ears, flushed face, and frequent morning headaches."),
    ("Hypertension", "I feel a pounding sensation in my chest and neck, and get unexpected nosebleeds."),
    ("Hypertension", "No major symptoms but my home BP monitor keeps showing 160 over 100."),

    # Asthma
    ("Asthma", "I have sudden fits of wheezing, my chest feels tight, and I can't catch my breath."),
    ("Asthma", "Exercise-induced breathlessness and whistling sound when I exhale."),
    ("Asthma", "Chest tightness, wheezing, and coughing fits mostly at night."),
    ("Asthma", "Using my inhaler a lot because of chest tightness and difficulty breathing deeply."),

    # Pneumonia
    ("Pneumonia", "High fever, chills, and I'm coughing up rust-colored phlegm. Breathing hurts my chest."),
    ("Pneumonia", "Sharp chest pain when I inhale, productive cough, and feeling extremely weak and feverish."),
    ("Pneumonia", "Difficulty breathing, rapid heartbeat, and a wet cough with high fever."),
    ("Pneumonia", "My lips look a bit bluish, high fever, and very painful breathing/coughing."),

    # Sinusitis
    ("Sinusitis", "Pressure and pain right behind my eyes and forehead, thick green nasal discharge."),
    ("Sinusitis", "Facial pain around my nose and cheeks, congested, and a bad taste in my mouth."),
    ("Sinusitis", "Throbbing pain in my forehead when I bend over, stuffy nose, and reduced sense of smell."),
    ("Sinusitis", "Severe sinus pressure, headache, and congestion that has lasted over two weeks."),

    # Anxiety Disorder
    ("Anxiety Disorder", "I feel constantly on edge, my heart races for no reason, and I can't stop worrying."),
    ("Anxiety Disorder", "Panic attacks out of nowhere, sweating, trembling, and feeling impending doom."),
    ("Anxiety Disorder", "Restless, difficulty concentrating, and muscle tension from constant worry."),
    ("Anxiety Disorder", "My mind races at night, I feel tight in my chest from stress and panic."),

    # Depression
    ("Depression", "I feel an overwhelming sadness, zero energy, and I've lost interest in my hobbies."),
    ("Depression", "Can't get out of bed, feeling hopeless and worthless for weeks now."),
    ("Depression", "Sleeping all the time but still exhausted, crying spells, and deep sadness."),
    ("Depression", "No motivation to eat or socialize, just feeling empty and profoundly sad."),

    # Tonsillitis
    ("Tonsillitis", "My tonsils are huge and covered in white spots. Swallowing is excruciating."),
    ("Tonsillitis", "Very sore throat, swollen glands in my neck, and bad breath with fever."),
    ("Tonsillitis", "Painful swallowing, red swollen tonsils, and chills/fever."),
    ("Tonsillitis", "Difficulty swallowing, swollen lymph nodes, and white patches on the back of my throat."),

    # Strep Throat
    ("Strep Throat", "Sudden severe sore throat, pain when swallowing, and tiny red spots on the roof of my mouth."),
    ("Strep Throat", "Throat feels like swallowing glass, fever, and swollen neck glands. No cough though."),
    ("Strep Throat", "Intense sore throat, fever, and a rash on my chest."),
    ("Strep Throat", "Swollen lymph nodes, very red tonsils, high fever, and sudden sore throat."),

    # Ear Infection
    ("Ear Infection", "Sharp piercing pain in my right ear, especially when lying down. Muffled hearing."),
    ("Ear Infection", "My ear is draining fluid, throbbing pain, and I feel slightly dizzy."),
    ("Ear Infection", "Earache, feeling of fullness in the ear, and some hearing loss."),
    ("Ear Infection", "Intense pain inside the ear canal, fever, and difficulty hearing clearly."),

    # Conjunctivitis
    ("Conjunctivitis", "My left eye is extremely pink, itchy, and has a crusty discharge in the morning."),
    ("Conjunctivitis", "Redness in both eyes, feels gritty like there's sand in them, highly contagious pink eye."),
    ("Conjunctivitis", "Watery, itchy, and red eyes with swollen eyelids."),
    ("Conjunctivitis", "Thick yellow discharge from my eye, the white part is very red and inflamed."),

    # Chickenpox
    ("Chickenpox", "Itchy fluid-filled blisters are popping up all over my torso and face."),
    ("Chickenpox", "Red itchy rash turning into scabs, accompanied by a mild fever."),
    ("Chickenpox", "Lots of small itchy pimples that became blisters, fever, and tiredness."),
    ("Chickenpox", "Classic childhood rash: red spots becoming itchy blisters all over the body."),

    # Dengue Fever
    ("Dengue Fever", "High fever, severe joint and muscle pain (breakbone fever), and a rash."),
    ("Dengue Fever", "Pain behind the eyes, high fever, and extreme fatigue after a mosquito bite."),
    ("Dengue Fever", "Bleeding gums, extremely high temperature, and severe headaches and body aches."),
    ("Dengue Fever", "Rash spreading rapidly, excruciating joint pain, vomiting, and high fever."),

    # Malaria
    ("Malaria", "Cyclical periods of intense shaking chills followed by a very high fever and sweating."),
    ("Malaria", "Fevers spiking every two days with massive sweating and extreme shivering."),
    ("Malaria", "Travelled recently, now having severe chills, high fever, and body aches."),
    ("Malaria", "Profuse sweating, headache, nausea, and recurring fevers/chills."),

    # Typhoid
    ("Typhoid", "A sustained high fever, weakness, stomach pain, and a rose-colored rash."),
    ("Typhoid", "Persistent fever that gets higher every day, diarrhea, and extreme fatigue."),
    ("Typhoid", "High fever, headache, abdominal pain, and poor appetite over a week."),
    ("Typhoid", "Feeling very weak, prolonged fever, constipation followed by diarrhea."),

    # Tuberculosis
    ("Tuberculosis", "A persistent cough lasting more than 3 weeks, coughing up blood, and night sweats."),
    ("Tuberculosis", "Losing weight without trying, severe night sweats, and a chesty cough with blood."),
    ("Tuberculosis", "Chronic cough, chest pain, fever, and drenching night sweats."),
    ("Tuberculosis", "Coughing up pinkish sputum, extreme fatigue, and night sweats."),

    # Anemia
    ("Anemia", "I am always tired, look very pale, and get dizzy when I stand up."),
    ("Anemia", "Craving ice to chew, extreme fatigue, pale skin, and cold hands/feet."),
    ("Anemia", "Shortness of breath with minimal exertion, weakness, and lightheadedness."),
    ("Anemia", "Lack of energy, brittle nails, pale eyelids, and constant exhaustion."),

    # Gastritis
    ("Gastritis", "A burning ache in my upper abdomen that gets worse after I eat."),
    ("Gastritis", "Nausea, feeling overly full in the upper stomach after eating just a little."),
    ("Gastritis", "Stomach upset, burning indigestion, and occasional vomiting."),
    ("Gastritis", "Gnawing pain in the stomach, bloating, and loss of appetite."),

    # Irritable Bowel Syndrome
    ("Irritable Bowel Syndrome", "Constant cramping, gas, and alternating between diarrhea and constipation."),
    ("Irritable Bowel Syndrome", "Bloating and abdominal pain that is relieved after having a bowel movement."),
    ("Irritable Bowel Syndrome", "Frequent changes in bowel habits, excessive gas, and stomach cramps."),
    ("Irritable Bowel Syndrome", "IBS acting up: cramping and urgent need to go to the bathroom."),

    # Scabies
    ("Scabies", "Intense itching all over my body, especially at night. Little red burrows between my fingers."),
    ("Scabies", "Very itchy rash on my wrists and between fingers, worse at night."),
    ("Scabies", "Relentless itching, small pimple-like bumps that look like tiny tracks on my skin."),
    ("Scabies", "Pimple-like rash around waist and hands that itches like crazy when I go to bed."),

    # Eczema
    ("Eczema", "Dry, red, extremely itchy patches of skin on the inside of my elbows and behind my knees."),
    ("Eczema", "Skin is thick, scaly, and very itchy, flares up with stress or certain soaps."),
    ("Eczema", "Intensely itchy rash that gets crusty if I scratch it, mainly on my arms/face."),
    ("Eczema", "Chronic dry flaky skin that is inflamed and red."),

    # Psoriasis
    ("Psoriasis", "Thick red plaques of skin covered with silvery scales on my elbows and scalp."),
    ("Psoriasis", "Dry, cracked skin that may bleed, itchy scaly patches on my knees."),
    ("Psoriasis", "Silvery scales on my skin, pitted nails, and stiff joints."),
    ("Psoriasis", "Raised, red, scaly patches that sting and itch heavily on my back/scalp."),

    # Kidney Stones
    ("Kidney Stones", "The most severe, sharp pain in my side/back radiating down to my groin. Urine is pink."),
    ("Kidney Stones", "Excruciating flank pain coming in waves, nausea, and blood in urine."),
    ("Kidney Stones", "Incredible pain in lower back and sides, frequent urge to urinate but it hurts."),
    ("Kidney Stones", "Agonizing pain in the right kidney area, throwing up from the pain."),

    # Appendicitis
    ("Appendicitis", "Sharp sudden pain that started around my belly button and moved to the lower right abdomen."),
    ("Appendicitis", "Pain in the lower right side of my stomach, getting worse if I cough. Rebound tenderness."),
    ("Appendicitis", "Nausea, fever, and acute pain in the right lower quadrant of my belly."),
    ("Appendicitis", "Severe abdominal pain on the right side, vomiting, and lack of appetite."),

    # Vertigo
    ("Vertigo", "The room is spinning violently when I turn my head, keeping my balance is impossible."),
    ("Vertigo", "I feel incredibly dizzy and nauseous, like I am on a fast merry-go-round."),
    ("Vertigo", "Sudden spinning sensation, ringing in ears, and vomiting from dizziness."),
    ("Vertigo", "Loss of balance and extreme spinning feeling when I sit up in bed."),

    # Gout
    ("Gout", "My big toe is incredibly swollen, red, hot, and the pain is excruciating if anything touches it."),
    ("Gout", "Sudden severe attack of pain, redness, and tenderness in the joint of the big toe."),
    ("Gout", "My foot joint is inflamed and so painful I can't bear weight or put on a sock."),
    ("Gout", "Intense joint pain at night in my toe, looks very red and feels warm."),
]

df_original = pd.read_csv("backend/data/Symptom2Disease.csv")
df_new = pd.DataFrame(new_data, columns=["label", "text"])

# Combine and remove exact duplicate texts
df_combined = pd.concat([df_original, df_new]).drop_duplicates(subset=["text"])
df_combined.to_csv("backend/data/Symptom2Disease.csv", index=False)

print(f"Added new diverse samples. Total dataset size is now: {len(df_combined)}")
