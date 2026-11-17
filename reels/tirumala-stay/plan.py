"""Telugu script: Tirumala's guest houses — how many rooms, the names and why, how many can stay. Voiced by Datta via Swaram.
Each line = one shot; parts = (mood, sentence). Moods: story, talk, happy, sad, fear, surprise, anger, disgust (+ slow).
Facts (Nov 2026): ~7,800 rooms (TTD, May 2026); ~1 lakh pilgrims/day (Deccan Chronicle 2025); no private hotels on the hill;
45 donor guest houses renamed with divine names (TTD board 2024-25); Nandakam 340, Panchajanyam 386, Vakulamatha 270 rooms (tirumala.org);
those three + Kausthubham = 1,228 rooms (TTD board note); Vakulamatha accommodates 1,400 (TTD, 2019);
PAC-5 Venkatadri Nilayam free, 2,500 at a time, more in peak rush (2025); 5 PACs in all; Seshadri/Garudadri/Anjanadri Nagar cottages."""
import json
P = [
 ("hook", [("surprise", "తిరుమల కొండ మీద… ఒక్క ప్రైవేట్ హోటల్ కూడా లేదు తెలుసా?"),
           ("talk", "మరి రోజూ వచ్చే లక్ష మంది భక్తులు… రాత్రి ఎక్కడ ఉంటారు?")], ["హోటల్", "లక్ష"]),
 ("count", [("story", "సమాధానం… దేవస్థానమే కట్టిన దాదాపు ఏడు వేల ఎనిమిది వందల గదులు."),
            ("talk", "కాటేజీలు, అతిథి గృహాలు, సత్రాలు… అన్నీ కలిపి.")], ["7,800", "కాటేజీలు,"]),
 ("rename", [("story", "కానీ అసలు విశేషం… వాటి పేర్లలో ఉంది."),
             ("talk", "దాతలు కట్టిన నలభై ఐదు అతిథి గృహాలకు ఒకప్పుడు వాళ్ళ పేర్లే ఉండేవి."),
             ("happy", "ఇప్పుడు వాటికి… స్వామివారి పేర్లే పెట్టారు.")], ["పేర్లలో", "45", "స్వామివారి"]),
 ("nandakam", [("story", "నందకం."), ("talk", "శ్రీ మహావిష్ణువు చేతిలోని ఖడ్గం పేరు. ఇక్కడ మూడు వందల నలభై గదులు.")], ["నందకం.", "ఖడ్గం", "340"]),
 ("panchajanyam", [("story", "పాంచజన్యం."), ("talk", "స్వామి ఊదే దివ్య శంఖం. మూడు వందల ఎనభై ఆరు గదులు.")], ["పాంచజన్యం.", "శంఖం.", "386"]),
 ("kausthubham", [("story", "కౌస్తుభం."), ("happy", "స్వామి వక్షస్థలం మీద మెరిసే మణి.")], ["కౌస్తుభం.", "మణి."]),
 ("vakula", [("story, slow", "మాతృశ్రీ వకుళమాత."),
             ("happy", "శ్రీనివాసుణ్ణి కన్నబిడ్డలా పెంచిన తల్లి. రెండు వందల డెబ్భై గదుల్లో… ఒకేసారి పద్నాలుగు వందల మంది ఉండొచ్చు.")], ["వకుళమాత.", "తల్లి.", "1,400"]),
 ("four", [("surprise", "ఈ నాలుగు అతిథి గృహాల్లోనే… వెయ్యి రెండు వందల ఇరవై ఎనిమిది గదులు!"),
           ("talk", "ఒక్కో గదిలో ఒక కుటుంబం హాయిగా ఉండొచ్చు.")], ["1,228", "కుటుంబం"]),
 ("pac", [("talk", "మరి గది దొరకని వాళ్ళ సంగతి?"),
          ("happy", "వేంకటాద్రి నిలయం. ఏడో కొండ పేరు. ఇక్కడ ఉండటానికి ఒక్క రూపాయి కూడా అక్కర్లేదు."),
          ("surprise", "ఒకేసారి రెండున్నర వేల మంది! ఇలాంటి ఉచిత యాత్రికుల సముదాయాలు తిరుమలలో మొత్తం ఐదు.")], ["వేంకటాద్రి", "రూపాయి", "2,500!"]),
 ("hills", [("story", "కాటేజీల కాలనీలకీ… ఏడు కొండల పేర్లే."),
            ("happy", "శేషాద్రి నగర్. గరుడాద్రి నగర్. అంజనాద్రి నగర్.")], ["ఏడు", "శేషాద్రి", "అంజనాద్రి"]),
 ("finale", [("story, slow", "అంటే… తిరుమలలో మనం నిద్రపోయే గది పేరు కూడా… ఒక నామస్మరణే."),
             ("happy", "ఏడుకొండల వాడా… వెంకటరమణా… గోవిందా, గోవిందా!")], ["నామస్మరణే.", "గోవిందా!"]),
]
NUM = {"ఏడు వేల ఎనిమిది వందల": "7,800", "నలభై ఐదు": "45", "మూడు వందల నలభై": "340", "మూడు వందల ఎనభై ఆరు": "386",
       "రెండు వందల డెబ్భై": "270", "పద్నాలుగు వందల": "1,400", "వెయ్యి రెండు వందల ఇరవై ఎనిమిది": "1,228", "రెండున్నర వేల": "2,500"}
def disp(t):
    for k, v in NUM.items(): t = t.replace(k, v)
    return t
lines = [{"shot": s, "parts": [list(p) for p in parts], "text": disp(" ".join(t for _, t in parts)), "tts": " ".join(t for _, t in parts),
          "keywords": k, "audio": f"audio/l{i+1:02d}.wav"} for i, (s, parts, k) in enumerate(P)]
json.dump({"gap": 0.0, "lang": "te", "lines": lines}, open('brief/plan.json', 'w'), indent=1, ensure_ascii=False)
print(len(lines), sum(len(l['tts'].split()) for l in lines), 'words')
