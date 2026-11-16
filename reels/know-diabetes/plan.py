"""Know Diabetes: one short public reel (9:16) covering the owner's 11-scene storyboard. Visuals are re-cut from the
'Follow the Sugar' station render (Raju + see-through body). Each line: caption text, spoken text, keywords, stations."""
import json, os
os.makedirs('brief', exist_ok=True)
L = [
 ("Always thirsty? Always tired? Running to the bathroom again and again? Raju has all three.",
  "Always thirsty? Always tired? Running to the bathroom, again and again? Raju has all three.", ["thirsty?", "tired?", "three."], [["room_in", 1]]),
 ("These can be warning signs of diabetes.",
  "These can be warning signs... of diabetes.", ["warning", "diabetes."], [["body_wide", 1]]),
 ("When we eat, the body breaks food down into glucose, the sugar in our blood. It is fuel for muscles, the brain and every organ.",
  "When we eat, the body breaks food down into glucose, the sugar in our blood. It is fuel for muscles, the brain, and every organ.", ["glucose,", "fuel"], [["gut", 0.55], ["vessels", 0.45]]),
 ("To get inside the cells, glucose needs insulin, a hormone made by the pancreas.",
  "To get inside the cells, glucose needs insulin... a hormone made by the pancreas.", ["insulin,", "pancreas."], [["pancreas", 0.5], ["muscle", 0.5]]),
 ("In Type 1 diabetes, the immune system destroys the cells that make insulin.",
  "In type one diabetes, the immune system destroys the cells that make insulin.", ["Type", "1", "destroys"], [["pancreas_tired", 1]]),
 ("In Type 2, insulin is there, but the cells stop responding to it.",
  "In type two, insulin is there... but the cells stop responding to it.", ["Type", "2,", "stop"], [["vessels_stuck", 1]]),
 ("And in pregnancy, hormones can cause gestational diabetes.",
  "And in pregnancy, hormones can cause gestational diabetes.", ["pregnancy,", "gestational"], [["body_wide", 1]]),
 ("The signs: thirst, frequent urination, hunger, tiredness, blurred vision, and wounds that heal slowly. But many people with Type 2 notice nothing for years.",
  "The signs: thirst, frequent urination, hunger, tiredness, blurred vision, and wounds that heal slowly. But many people with type two, notice nothing for years.", ["signs:", "nothing", "years."], [["room_out", 1]]),
 ("Family history, age, inactivity and excess weight raise the risk. It is not simply caused by eating sweets.",
  "Family history, age, inactivity, and excess weight, raise the risk. It is not simply caused by eating sweets.", ["risk.", "not", "sweets."], [["fat", 1]]),
 ("Left high for years, blood sugar damages the heart, kidneys, eyes and nerves.",
  "Left high for years, blood sugar damages the heart, kidneys, eyes, and nerves.", ["heart,", "kidneys,", "eyes", "nerves."], [["heart", 0.25], ["kidney", 0.25], ["eye", 0.25], ["feet", 0.25]]),
 ("Doctors confirm it with blood tests: fasting glucose 126 or above, 200 or above two hours after a glucose drink, or HbA1c 6.5 percent or above. Don't diagnose yourself from one home reading.",
  "Doctors confirm it with blood tests: fasting glucose, one twenty-six or above. Two hundred or above, two hours after a glucose drink. Or H-b-A-one-c, six point five percent or above. Don't diagnose yourself from one home reading.", ["126", "200", "6.5", "Don't"], [["body_wide", 1]]),
 ("The good news: diabetes can be managed. Eat balanced meals, stay active, check your sugar as advised, and never stop your medicines on your own.",
  "The good news: diabetes can be managed. Eat balanced meals, stay active, check your sugar as advised, and never stop your medicines on your own.", ["managed.", "active,", "never"], [["room_healthy", 1]]),
 ("Type 1 can't be prevented by lifestyle. But the risk of Type 2 can often be reduced.",
  "Type one can't be prevented by lifestyle. But the risk of type two, can often be reduced.", ["can't", "reduced."], [["room_healthy", 1]]),
 ("Know diabetes. Control diabetes. Live a healthier life.",
  "Know diabetes. Control diabetes. Live a healthier life.", ["Know", "Control", "healthier"], [["room_healthy", 1]]),
]
lines = [{"text": t, "tts": s, "keywords": k, "audio": f"audio/l{i + 1:02d}.wav", "st": st} for i, (t, s, k, st) in enumerate(L)]
json.dump({"gap": 0.05, "font": "Poppins", "lines": lines}, open('brief/plan.json', 'w'), indent=1, ensure_ascii=False)
print('ok', len(lines))
